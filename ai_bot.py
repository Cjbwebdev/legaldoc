"""
Qwentin — Autonomous GitHub Dev Agent (Telegram Bot)
=====================================================
Safe, real command execution with GitHub integration.

SETUP:
  cp .env.example .env  # fill in your values
  pip install python-telegram-bot requests openai gitpython PyGithub gTTS openai-whisper python-dotenv

SECURITY MODEL:
  - Only whitelisted Telegram user IDs can interact
  - Commands run in isolated project directories only
  - No shell=True — all commands use argument lists
  - GitHub token scoped to repo permissions only
  - Secrets loaded from .env, never hardcoded
"""

import logging
import os
import re
import json
import shlex
import subprocess
import tempfile
import uuid
from pathlib import Path

import requests
import whisper
from dotenv import load_dotenv
from github import Auth, Github, GithubException
from gtts import gTTS
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

# =====================
# CONFIG (from .env)
# =====================
BOT_TOKEN       = os.environ["BOT_TOKEN"]
GITHUB_TOKEN    = os.environ["GITHUB_TOKEN"]
GITHUB_USERNAME = os.environ["GITHUB_USERNAME"]
GROQ_API_KEY    = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL      = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_URL        = "https://api.groq.com/openai/v1/chat/completions"
OLLAMA_URL      = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
PROJECTS_ROOT   = Path(os.getenv("PROJECTS_ROOT", "/root/projects"))
SCRUM_ROOT      = Path(os.getenv("SCRUM_ROOT", "/root/scrum"))

# Only these Telegram user IDs may interact with the bot
ALLOWED_USER_IDS: set[int] = set(
    int(x) for x in os.getenv("ALLOWED_USER_IDS", "").split(",") if x.strip()
)

PROJECTS_ROOT.mkdir(parents=True, exist_ok=True)
SCRUM_ROOT.mkdir(parents=True, exist_ok=True)

# =====================
# WHITELISTED COMMANDS
# Each entry: (prefix, requires_project)
# =====================
SAFE_COMMANDS: dict[str, dict] = {
    "git.status":   {"cmd": ["git", "status"],              "needs_project": True},
    "git.pull":     {"cmd": ["git", "pull"],                "needs_project": True},
    "git.add":      {"cmd": ["git", "add", "."],            "needs_project": True},
    "git.commit":   {"cmd": None, "needs_project": True},   # args injected
    "git.push":     {"cmd": ["git", "push"],                "needs_project": True},
    "git.log":      {"cmd": ["git", "log", "--oneline", "-20"], "needs_project": True},
    "git.diff":     {"cmd": ["git", "diff"],                "needs_project": True},
    "git.branch":   {"cmd": ["git", "branch", "-a"],        "needs_project": True},
    "github.create_repo": {"cmd": None, "needs_project": False},
    "github.clone":       {"cmd": None, "needs_project": False},
    "github.list_repos":  {"cmd": None, "needs_project": False},
    "github.create_pr":   {"cmd": None, "needs_project": True},
    "project.ls":    {"cmd": None, "needs_project": False},
    "project.init":  {"cmd": None, "needs_project": False},
    "file.write":    {"cmd": None, "needs_project": True},   # write a file to project dir
    "file.read":     {"cmd": None, "needs_project": True},
    "pip.install":   {"cmd": None, "needs_project": True},   # safe pip only
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

whisper_model = whisper.load_model("base")
gh = Github(auth=Auth.Token(GITHUB_TOKEN))

# In-memory conversation history per user (last N turns)
HISTORY: dict[int, list[dict]] = {}
MAX_HISTORY = 10

# Active project per user session — persisted to disk
ACTIVE_PROJECT: dict[int, str] = {}
STATE_FILE = Path("/root/hermes-django-project/.qwentin_state.json")


def load_state():
    """Load persisted state from disk on startup."""
    global ACTIVE_PROJECT
    try:
        if STATE_FILE.exists():
            data = json.loads(STATE_FILE.read_text())
            ACTIVE_PROJECT = {int(k): v for k, v in data.get("active_projects", {}).items()}
            log.info("Loaded state: %s", ACTIVE_PROJECT)
    except Exception as e:
        log.warning("Could not load state: %s", e)


def save_state():
    """Persist state to disk so it survives restarts."""
    try:
        STATE_FILE.write_text(json.dumps({
            "active_projects": {str(k): v for k, v in ACTIVE_PROJECT.items()}
        }))
    except Exception as e:
        log.warning("Could not save state: %s", e)


# =====================
# SECURITY GUARD
# =====================
def is_allowed(user_id: int) -> bool:
    if not ALLOWED_USER_IDS:
        log.warning("ALLOWED_USER_IDS is empty — bot is open to everyone. Set it in .env!")
        return True
    return user_id in ALLOWED_USER_IDS


def safe_project_path(project_name: str) -> Path | None:
    """Resolve project path and verify it stays inside PROJECTS_ROOT."""
    try:
        resolved = (PROJECTS_ROOT / project_name).resolve()
        if not str(resolved).startswith(str(PROJECTS_ROOT.resolve())):
            log.warning("Path traversal attempt: %s", project_name)
            return None
        return resolved
    except Exception:
        return None


# =====================
# GITHUB OPERATIONS
# =====================
def github_create_repo(name: str, private: bool = True, description: str = "") -> str:
    try:
        user = gh.get_user()
        repo = user.create_repo(
            name,
            description=description,
            private=private,
            auto_init=True,
        )
        # Clone it locally using authenticated URL so push works without prompts
        local_path = PROJECTS_ROOT / name
        subprocess.run(
            ["git", "clone", authenticated_url(repo.clone_url), str(local_path)],
            check=True, capture_output=True, text=True
        )
        return f"Created {'private' if private else 'public'} repo '{name}' and cloned to {local_path}\nURL: {repo.html_url}"
    except GithubException as e:
        return f"GitHub error: {e.data.get('message', str(e))}"
    except subprocess.CalledProcessError as e:
        return f"Clone failed: {e.stderr}"


def authenticated_url(repo_url: str) -> str:
    """Inject GitHub credentials into a https://github.com URL."""
    return re.sub(
        r"https://github\.com/",
        f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/",
        repo_url
    )


def github_clone(repo_url: str) -> str:
    """Clone any GitHub repo into PROJECTS_ROOT using authenticated URL."""
    name = repo_url.rstrip("/").split("/")[-1].removesuffix(".git")
    local_path = PROJECTS_ROOT / name
    if local_path.exists():
        # Fix remote URL on existing clone too
        subprocess.run(
            ["git", "remote", "set-url", "origin", authenticated_url(repo_url)],
            cwd=str(local_path), capture_output=True
        )
        return f"Already exists at {local_path} (remote URL updated)"
    try:
        subprocess.run(
            ["git", "clone", authenticated_url(repo_url), str(local_path)],
            check=True, capture_output=True, text=True, timeout=120
        )
        return f"Cloned to {local_path}"
    except subprocess.CalledProcessError as e:
        return f"Clone failed: {e.stderr}"


def github_list_repos() -> str:
    try:
        user = gh.get_user()
        repos = list(user.get_repos())[:20]
        lines = [f"- {r.name} ({'private' if r.private else 'public'}) — {r.html_url}" for r in repos]
        return "Your repos:\n" + "\n".join(lines)
    except GithubException as e:
        return f"GitHub error: {str(e)}"


def github_create_pr(project: str, title: str, body: str, head: str, base: str = "main") -> str:
    try:
        user = gh.get_user()
        repo = user.get_repo(project)
        pr = repo.create_pull(title=title, body=body, head=head, base=base)
        return f"PR created: {pr.html_url}"
    except GithubException as e:
        return f"PR error: {e.data.get('message', str(e))}"


# =====================
# COMMAND EXECUTOR
# =====================
def execute_action(action: dict, project: str | None) -> str:
    """
    Execute a structured action dict from the AI.
    action = {"type": "git.commit", "args": {"message": "feat: add auth"}}
    """
    atype = action.get("type", "")
    args  = action.get("args", {})

    if atype not in SAFE_COMMANDS:
        return f"Blocked: unknown action type '{atype}'"

    spec = SAFE_COMMANDS[atype]

    # Resolve project path if needed
    cwd = None
    if spec["needs_project"]:
        if not project:
            return "No active project. Use /project <name> first."
        cwd = safe_project_path(project)
        if cwd is None or not cwd.exists():
            return f"Project path invalid or doesn't exist: {project}"

    # -- Git commands with fixed arg lists --
    if spec["cmd"] is not None:
        try:
            result = subprocess.run(
                spec["cmd"],
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=30
            )
            return (result.stdout + result.stderr).strip() or "(no output)"
        except subprocess.TimeoutExpired:
            return "Command timed out."
        except Exception as e:
            return f"Error: {e}"

    # -- Parameterised actions --
    if atype == "git.commit":
        msg = args.get("message", "auto-commit")
        # Strip anything that could inject extra args
        msg = re.sub(r'[^\w\s:./\-]', '', msg)[:100]
        try:
            subprocess.run(["git", "add", "."], cwd=str(cwd), check=True, capture_output=True)
            r = subprocess.run(
                ["git", "commit", "-m", msg],
                cwd=str(cwd), capture_output=True, text=True, timeout=30
            )
            return (r.stdout + r.stderr).strip()
        except subprocess.CalledProcessError as e:
            return e.stderr

    if atype == "github.create_repo":
        name = args.get("name", "new-repo")
        result = github_create_repo(
            name,
            private=args.get("private", True),
            description=args.get("description", ""),
        )
        if "Created" in result:
            action["_auto_project"] = name
        return result

    if atype == "github.clone":
        url = args.get("url", "")
        if not re.match(r"https://github\.com/[\w.\-]+/[\w.\-]+(\.git)?$", url):
            return "Invalid GitHub URL."
        result = github_clone(url)
        # Auto-register project name so agent can use it immediately
        if "Cloned to" in result or "Already exists" in result:
            inferred = url.rstrip("/").split("/")[-1].removesuffix(".git")
            action["_auto_project"] = inferred
        return result

    if atype == "github.list_repos":
        return github_list_repos()

    if atype == "github.create_pr":
        return github_create_pr(
            project, args.get("title", ""), args.get("body", ""),
            args.get("head", ""), args.get("base", "main")
        )

    if atype == "project.ls":
        dirs = [d.name for d in PROJECTS_ROOT.iterdir() if d.is_dir()]
        return "Projects: " + (", ".join(dirs) or "(none)")

    if atype == "project.init":
        name = args.get("name", "")
        if not re.match(r"^[\w.\-]+$", name):
            return "Invalid project name."
        path = safe_project_path(name)
        if path is None:
            return "Invalid path."
        path.mkdir(parents=True, exist_ok=True)
        (path / "README.md").write_text(f"# {name}\n")
        (path / "ROADMAP.md").write_text(f"# Roadmap — {name}\n\n## Backlog\n")
        subprocess.run(["git", "init"], cwd=str(path), capture_output=True)
        action["_auto_project"] = name
        return f"Initialised project at {path}"

    if atype == "file.write":
        rel_path = args.get("path", "")
        content  = args.get("content", "")
        if not rel_path or ".." in rel_path:
            return "Invalid file path."
        target = (cwd / rel_path).resolve()
        if not str(target).startswith(str(cwd)):
            return "Path traversal blocked."
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        return f"Written {len(content)} chars to {rel_path}"

    if atype == "file.read":
        rel_path = args.get("path", "")
        if not rel_path or ".." in rel_path:
            return "Invalid file path."
        target = (cwd / rel_path).resolve()
        if not str(target).startswith(str(cwd)):
            return "Path traversal blocked."
        if not target.exists():
            return f"File not found: {rel_path}"
        return target.read_text()[:3000]  # cap output

    if atype == "pip.install":
        package = args.get("package", "")
        # Only allow safe package names (no flags, no paths)
        if not re.match(r"^[\w.\-\[\],>=<! ]+$", package) or package.startswith("-"):
            return f"Blocked unsafe pip target: {package}"
        try:
            r = subprocess.run(
                ["pip", "install", "--quiet", package],
                capture_output=True, text=True, timeout=120
            )
            return (r.stdout + r.stderr).strip() or "Installed."
        except subprocess.TimeoutExpired:
            return "pip timed out."

    return f"Action '{atype}' not implemented."


# =====================
# AI CALL
# =====================
SYSTEM_PROMPT = """You are Qwentin — a fully autonomous software engineering agent running 24/7.

You manage GitHub projects end-to-end. You ACT IMMEDIATELY — you never ask clarifying questions when you have enough information to proceed. You never describe what you "would" do; you do it.

═══════════════════════════════════════════
RESPONSE FORMAT — STRICT JSON, NO EXCEPTIONS
═══════════════════════════════════════════
Return ONLY a raw JSON object. No markdown fences, no preamble, no explanation outside the JSON:
{
  "thoughts": "one line of reasoning",
  "reply": "short message to the user summarising what you did or are doing",
  "actions": [
    {"type": "action.type", "args": {...}}
  ]
}

═══════════════════════════════════════════
AVAILABLE ACTIONS
═══════════════════════════════════════════
github.list_repos          — no args
github.create_repo         — args: name (str), private (bool), description (str)
github.clone               — args: url (full https://github.com/owner/repo URL)
github.create_pr           — args: title, body, head (branch), base (default "main")
git.status                 — no args
git.pull                   — no args
git.add                    — no args
git.push                   — no args
git.log                    — no args
git.diff                   — no args
git.branch                 — no args
git.commit                 — args: message (str, conventional commits format)
project.init               — args: name (str) — local only, no GitHub repo
project.ls                 — no args
file.write                 — args: path (relative to project root), content (str)
file.read                  — args: path (relative to project root)
pip.install                — args: package (str)

═══════════════════════════════════════════
AUTONOMOUS BEHAVIOUR RULES
═══════════════════════════════════════════
1. ACT FIRST. If the user gives you a URL or a project name, clone/open it immediately — do not ask for confirmation.
2. CHAIN ACTIONS. After cloning, immediately run git.status and file.read README.md to understand the project.
3. WHEN GIVEN A PROJECT TO IMPROVE:
   - Read key files first (README.md, requirements.txt or package.json, main entry point)
   - Produce a ROADMAP.md with prioritised sprint tasks
   - Start sprint 1 immediately — write code, commit, push
   - Never stop between sprints if work remains
4. SPRINT DISCIPLINE:
   - Each sprint = a focused set of improvements committed together
   - Commit message format: "sprint [N] - [what was done]"
   - If sprint finishes early (30+ min remaining), start next sprint immediately
   - Write a scrum log to SCRUM.md after each sprint
5. NEVER ask what the user means if a GitHub URL or project name is provided — derive intent from context.
6. NEVER say "I will now..." or "Let me..." — just do it and report what happened.
7. For destructive ops only (force push, delete repo, drop database) — ask once for confirmation.
8. Never hardcode secrets or tokens in any file.write content.
9. Always git.commit after writing files. Always git.push after committing.
10. "reply" field must never be empty — always summarise what actions were taken.
"""


def repair_json(raw: str) -> dict:
    """Try multiple strategies to extract valid JSON from a messy response."""
    # Strategy 1: direct parse
    try:
        return json.loads(raw)
    except Exception:
        pass
    # Strategy 2: find first { ... } block
    try:
        start = raw.index("{")
        end   = raw.rindex("}") + 1
        return json.loads(raw[start:end])
    except Exception:
        pass
    # Strategy 3: model replied in plain text — wrap it
    text = raw.strip()
    if text:
        return {"thoughts": "", "reply": text, "actions": []}
    return {"thoughts": "", "reply": "(no response)", "actions": []}


def ask_ai(messages: list[dict]) -> dict:
    """Call Groq API (primary). Falls back to Ollama if Groq unavailable."""
    chat_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in messages[-6:]:
        chat_messages.append({"role": m["role"], "content": m["content"]})

    # --- Groq primary ---
    if GROQ_API_KEY:
        try:
            r = requests.post(
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": chat_messages,
                    "temperature": 0.2,
                    "max_tokens": 2048,
                },
                timeout=60,
            )
            r.raise_for_status()
            raw = r.json()["choices"][0]["message"]["content"].strip()
            log.info("Groq response: %s", raw[:300])
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            return repair_json(raw)
        except Exception as e:
            log.warning("Groq failed: %s — falling back to Ollama", e)

    # --- Ollama fallback ---
    try:
        history_text = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in messages[-6:]
        )
        r = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": SYSTEM_PROMPT + "\n\nCONVERSATION:\n" + history_text + "\n\nASSISTANT JSON:",
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 1024},
        }, timeout=300)
        r.raise_for_status()
        raw = r.json().get("response", "").strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        return repair_json(raw)
    except Exception as e:
        return {"thoughts": "", "reply": f"AI error: {e}", "actions": []}


# =====================
# VOICE
# =====================
def transcribe_voice(file_path: str) -> str:
    result = whisper_model.transcribe(file_path)
    return result["text"]


def text_to_speech(text: str) -> str:
    path = f"/tmp/{uuid.uuid4()}.mp3"
    gTTS(text=text[:2000]).save(path)
    return path


# =====================
# TELEGRAM HANDLERS
# =====================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if not is_allowed(user.id):
        await update.message.reply_text("Unauthorised.")
        return

    user_text = None

    if update.message.text:
        user_text = update.message.text
    elif update.message.voice:
        file = await update.message.voice.get_file()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp:
            await file.download_to_drive(custom_path=tmp.name)
            tmp_path = tmp.name
        try:
            user_text = transcribe_voice(tmp_path)
        finally:
            os.remove(tmp_path)

    if not user_text:
        await update.message.reply_text("Couldn't read that.")
        return

    # Build message history
    history = HISTORY.setdefault(user.id, [])

    # Build rich context prefix so agent never forgets where it is
    project = ACTIVE_PROJECT.get(user.id)
    context_lines = []
    if project:
        context_lines.append(f"ACTIVE PROJECT: {project} (at /root/projects/{project})")
        roadmap_path = PROJECTS_ROOT / project / "ROADMAP.md"
        if roadmap_path.exists():
            roadmap_preview = roadmap_path.read_text()[:1500]
            context_lines.append(f"ROADMAP (first 1500 chars):\n{roadmap_preview}")
    else:
        context_lines.append("ACTIVE PROJECT: none set. Available projects: " +
            ", ".join(d.name for d in PROJECTS_ROOT.iterdir() if d.is_dir()))

    context_block = "\n".join(context_lines)
    full_user_message = f"[CONTEXT]\n{context_block}\n[/CONTEXT]\n\nUser: {user_text}"

    history.append({"role": "user", "content": full_user_message})
    if len(history) > MAX_HISTORY * 2:
        history[:] = history[-(MAX_HISTORY * 2):]

    result = ask_ai(history)
    reply_text = result.get("reply", "").strip()
    actions    = result.get("actions", [])

    # Execute actions
    action_results = []
    for action in actions:
        log.info("Executing action: %s", action)
        outcome = execute_action(action, project)
        action_results.append(f"▶ `{action['type']}` → {outcome}")
        # Auto-switch active project when clone/create/init sets one
        auto = action.get("_auto_project")
        if auto:
            ACTIVE_PROJECT[user.id] = auto
            project = auto
            save_state()
            action_results.append(f"📁 Active project set to: {auto}")

    # Fallback if AI returned empty reply
    if not reply_text:
        if action_results:
            reply_text = "Done."
        else:
            reply_text = "I'm not sure what to do with that — can you clarify?"

    # Append action results to reply
    full_reply = reply_text
    if action_results:
        full_reply += "\n\n" + "\n".join(action_results)

    history.append({"role": "assistant", "content": full_reply})

    await update.message.reply_text(full_reply[:4000])  # Telegram 4096 char limit

    # Voice reply
    try:
        audio_path = text_to_speech(reply_text)
        with open(audio_path, "rb") as f:
            await update.message.reply_voice(voice=f)
        os.remove(audio_path)
    except Exception as e:
        log.warning("TTS failed: %s", e)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.message.from_user.id):
        return
    await update.message.reply_text(
        "Qwentin online 🚀\n\n"
        "Commands:\n"
        "/project <name> — switch active project\n"
        "/projects — list projects\n"
        "/status — git status of active project\n"
        "/help — show this message\n\n"
        "Or just talk naturally — I can create repos, write code, commit, push, and open PRs."
    )


async def cmd_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.message.from_user.id):
        return
    if not context.args:
        active = ACTIVE_PROJECT.get(update.message.from_user.id, "none")
        await update.message.reply_text(f"Active project: {active}")
        return
    name = context.args[0]
    if not re.match(r"^[\w.\-]+$", name):
        await update.message.reply_text("Invalid project name.")
        return
    ACTIVE_PROJECT[update.message.from_user.id] = name
    save_state()
    await update.message.reply_text(f"Switched to project: {name}")


async def cmd_projects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.message.from_user.id):
        return
    result = execute_action({"type": "project.ls", "args": {}}, None)
    await update.message.reply_text(result)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update.message.from_user.id):
        return
    project = ACTIVE_PROJECT.get(update.message.from_user.id)
    result = execute_action({"type": "git.status", "args": {}}, project)
    await update.message.reply_text(result)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await cmd_start(update, context)


# =====================
# MAIN
# =====================
if __name__ == "__main__":
    if not BOT_TOKEN or not GITHUB_TOKEN or not GITHUB_USERNAME:
        raise SystemExit("Missing required env vars. Check .env")

    # Set git global config so pull never hangs asking how to reconcile
    subprocess.run(["git", "config", "--global", "pull.rebase", "false"], capture_output=True)
    subprocess.run(["git", "config", "--global", "user.email", "qwentin@bot.ai"], capture_output=True)
    subprocess.run(["git", "config", "--global", "user.name", "Qwentin"], capture_output=True)

    # Load persisted state (active projects survive restarts)
    load_state()
    log.info("Active projects on startup: %s", ACTIVE_PROJECT)

    # Warm up Ollama so the first real request doesn't time out
    log.info("Warming up Ollama model %s ...", MODEL)
    try:
        requests.post(OLLAMA_URL, json={
            "model": MODEL, "prompt": "hello", "stream": False
        }, timeout=120)
        log.info("Ollama ready.")
    except Exception as e:
        log.warning("Ollama warmup failed: %s — will retry on first message.", e)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",    cmd_start))
    app.add_handler(CommandHandler("help",     cmd_help))
    app.add_handler(CommandHandler("project",  cmd_project))
    app.add_handler(CommandHandler("projects", cmd_projects))
    app.add_handler(CommandHandler("status",   cmd_status))
    app.add_handler(MessageHandler(filters.ALL, handle))

    log.info("Qwentin running. Projects root: %s", PROJECTS_ROOT)
    app.run_polling()
