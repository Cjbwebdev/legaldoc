# LegalDoc — Full Project Roadmap
> Autonomous sprint roadmap for Qwentin. Work through phases in order.
> Each sprint = 1 hour. If a sprint completes early, begin the next immediately.
> Commit after every completed task. Push after every sprint.

## PHASE 0 — Project Foundations
*Goal: Clean, working base before any feature work begins.*

### Sprint 0.1 — Repo & Environment Audit
- [x] Read entire repo structure — map every file and folder
- [ ] Verify `settings.py` / `config/` loads correctly from `.env`
- [ ] Confirm `.env.example` has all required keys documented
- [ ] Check `requirements.txt` — pin all unpinned versions
- [ ] Verify `entrypoint.sh` is executable and correct
- [ ] Confirm `railway.toml`, `nixpacks.toml`, `Procfile` are valid
- [ ] Run `python manage.py check` — fix all warnings
- [ ] Commit: `chore: environment and config audit`

### Sprint 0.2 — Database & Migrations
- [ ] Confirm database engine configured (PostgreSQL for production)
- [ ] Run `python manage.py showmigrations` — identify missing migrations
- [ ] Create and apply any missing migrations
- [ ] Confirm all models have `__str__` methods
- [ ] Add database indexes to high-query fields (user email, subscription status)
- [ ] Commit: `chore: migrations and database audit`

### Sprint 0.3 — Dependency & Security Baseline
- [ ] Run `pip audit` — fix any known vulnerabilities
- [ ] Add `django-environ` or `python-decouple` if not present
- [ ] Ensure `DEBUG=False` path is tested
- [ ] Set `A