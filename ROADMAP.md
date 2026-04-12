# LegalDoc — Full Project Roadmap
> Autonomous sprint roadmap for Qwentin. Work through phases in order.
> Each sprint = 1 hour. If a sprint completes early, begin the next immediately.
> Commit after every completed task. Push after every sprint.

---

## PHASE 0 — Project Foundations
*Goal: Clean, working base before any feature work begins.*

### Sprint 0.1 — Repo & Environment Audit
- [ ] Read entire repo structure — map every file and folder
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
- [ ] Set `ALLOWED_HOSTS`, `SECURE_SSL_REDIRECT`, `CSRF_COOKIE_SECURE`
- [ ] Add `django-csp` for Content Security Policy headers
- [ ] Commit: `security: baseline hardening`

---

## PHASE 1 — Authentication & User Management
*Goal: Secure, production-grade auth with full user lifecycle.*

### Sprint 1.1 — Core Auth Flows
- [ ] Audit `users/` app — map all views, models, URLs
- [ ] Verify signup flow — form validation, password hashing, email uniqueness
- [ ] Verify login flow — session creation, remember me, failed attempt handling
- [ ] Verify logout — session destruction, redirect
- [ ] Add rate limiting to login endpoint (django-ratelimit or similar)
- [ ] Commit: `auth: audit and harden core login/signup flows`

### Sprint 1.2 — Password & Email
- [ ] Implement password reset flow (email token, expiry, one-time use)
- [ ] Implement email verification on signup (send token, verify endpoint)
- [ ] Add resend verification email endpoint
- [ ] Template all auth emails (welcome, verify, reset) — plain text + HTML
- [ ] Commit: `auth: password reset and email verification`

### Sprint 1.3 — User Profiles
- [ ] Confirm `UserProfile` model exists with: name, avatar, company, timezone
- [ ] Build profile edit view with form validation
- [ ] Add avatar upload with file type and size validation
- [ ] Add account deletion flow with confirmation and data wipe
- [ ] Commit: `users: profile management`

### Sprint 1.4 — OAuth & SSO (Future-Proofing)
- [ ] Install `django-allauth`
- [ ] Configure Google OAuth provider (client ID/secret in `.env`)
- [ ] Add GitHub OAuth provider
- [ ] Ensure OAuth users are linked to existing accounts by email
- [ ] Document LinkedIn/Microsoft SSO as future integration points in `research/oauth.md`
- [ ] Commit: `auth: OAuth via django-allauth`

### Sprint 1.5 — Permissions & Roles
- [ ] Define user roles: `free`, `pro`, `enterprise`, `admin`
- [ ] Add `role` field to UserProfile
- [ ] Create `@requires_role` decorator for view-level gating
- [ ] Add admin-only views behind role check
- [ ] Commit: `auth: roles and permissions system`

---

## PHASE 2 — Subscription & Billing
*Goal: Working Stripe integration with plan gating, webhooks, and trials.*

### Sprint 2.1 — Stripe Setup
- [ ] Install `stripe` Python SDK
- [ ] Add `STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` to `.env.example`
- [ ] Create Stripe products and prices: Free, Pro (£9/mo), Enterprise (£29/mo)
- [ ] Store Stripe price IDs in settings
- [ ] Commit: `billing: Stripe SDK and product setup`

### Sprint 2.2 — Subscription Flows
- [ ] Build checkout session creation view (POST → redirect to Stripe)
- [ ] Build success and cancel return URL views
- [ ] Store `stripe_customer_id` and `stripe_subscription_id` on UserProfile
- [ ] Build subscription status check helper: `user.has_active_subscription()`
- [ ] Commit: `billing: checkout and subscription creation`

### Sprint 2.3 — Webhooks
- [ ] Create `/billing/webhook/` endpoint
- [ ] Verify Stripe signature on every webhook
- [ ] Handle events:
  - `checkout.session.completed` → activate subscription
  - `invoice.payment_succeeded` → renew subscription
  - `invoice.payment_failed` → flag account, email user
  - `customer.subscription.deleted` → downgrade to free
- [ ] Log all webhook events to database
- [ ] Commit: `billing: webhook handler`

### Sprint 2.4 — Trials & Plan Management
- [ ] Add 14-day free trial on Pro signup
- [ ] Build `/billing/portal/` → Stripe Customer Portal redirect
- [ ] Build plan comparison page (Free vs Pro vs Enterprise)
- [ ] Add upgrade prompt banners for free users hitting limits
- [ ] Commit: `billing: trials and customer portal`

### Sprint 2.5 — Usage Limits & Gating
- [ ] Define limits per plan:
  - Free: 3 documents/month
  - Pro: unlimited documents
  - Enterprise: unlimited + team seats
- [ ] Add `DocumentQuota` model tracking monthly usage per user
- [ ] Enforce quota in document creation view
- [ ] Show usage meter in dashboard sidebar
- [ ] Commit: `billing: usage limits and quota enforcement`

---

## PHASE 3 — Document Engine
*Goal: Full document generation system with all 6 core templates.*

### Sprint 3.1 — Document Model & Storage
- [ ] Audit existing `templates/` and `dashboard/` apps
- [ ] Create `Document` model: user, type, title, content, status, created_at, updated_at
- [ ] Add document type choices: privacy_policy, terms, cookie_policy, nda, service_agreement, disclaimer
- [ ] Create migrations
- [ ] Commit: `docs: Document model and migrations`

### Sprint 3.2 — Template Engine
- [ ] Build `DocumentGenerator` class in `documents/generator.py`
- [ ] Accept: document type + user input dict → rendered string output
- [ ] Use Django template engine for variable substitution in legal text
- [ ] Add input validation per document type (required fields, character limits)
- [ ] Commit: `docs: DocumentGenerator engine`

### Sprint 3.3 — Privacy Policy Template
- [ ] Build input form: company name, website, data types collected, retention period, contact email
- [ ] Write full Privacy Policy template (GDPR-compliant)
- [ ] Include sections: data collection, cookies, retention, user rights, contact
- [ ] Render and save to `Document` model on submission
- [ ] Commit: `docs: Privacy Policy template`

### Sprint 3.4 — Terms & Conditions Template
- [ ] Build input form: company name, service description, billing terms, jurisdiction
- [ ] Write full T&C template
- [ ] Include sections: acceptance, services, payment, cancellation, liability, governing law
- [ ] Commit: `docs: Terms and Conditions template`

### Sprint 3.5 — Cookie Policy Template
- [ ] Build input form: company name, cookie types used, third-party tools
- [ ] Write Cookie Policy template (ePrivacy Directive compliant)
- [ ] Include sections: what are cookies, types used, third parties, opt-out
- [ ] Commit: `docs: Cookie Policy template`

### Sprint 3.6 — NDA Template
- [ ] Build input form: party names, confidential info description, duration, governing law
- [ ] Write mutual NDA template
- [ ] Include sections: definition, obligations, exclusions, term, remedies
- [ ] Commit: `docs: NDA template`

### Sprint 3.7 — Service Agreement Template
- [ ] Build input form: provider, client, scope, fees, payment terms, termination notice
- [ ] Write Service Agreement / Engagement Letter template
- [ ] Include sections: services, fees, IP ownership, termination, liability cap
- [ ] Commit: `docs: Service Agreement template`

### Sprint 3.8 — Disclaimer Template
- [ ] Build input form: company name, website, disclaimer type
- [ ] Write Website Disclaimer template
- [ ] Include sections: no legal advice, liability limitation, accuracy, external links
- [ ] Commit: `docs: Disclaimer template`

### Sprint 3.9 — Export & Download
- [ ] Add PDF export using `weasyprint` or `reportlab`
- [ ] Add DOCX export using `python-docx`
- [ ] Add plain text copy-to-clipboard on dashboard
- [ ] Serve exports as secure download URLs (not public)
- [ ] Commit: `docs: PDF and DOCX export`

---

## PHASE 4 — Dashboard
*Goal: Clean, functional user dashboard for full document lifecycle.*

### Sprint 4.1 — Dashboard Home
- [ ] Build dashboard home view — list all user's documents
- [ ] Show: document type, title, created date, status, actions (view/edit/delete/download)
- [ ] Add empty state for new users with CTA to create first document
- [ ] Add usage quota meter (X of Y documents used this month)
- [ ] Commit: `dashboard: home view`

### Sprint 4.2 — Document CRUD
- [ ] Create document — multi-step form (type → inputs → preview → save)
- [ ] Edit document — pre-populate form with saved inputs, regenerate on save
- [ ] Delete document — confirmation modal, soft delete
- [ ] Duplicate document — copy inputs to new document
- [ ] Commit: `dashboard: document CRUD`

### Sprint 4.3 — Document Preview
- [ ] Build rendered document preview page (clean, printable layout)
- [ ] Add regenerate button — re-run generator with updated inputs
- [ ] Add version history — save previous versions on edit
- [ ] Commit: `dashboard: document preview and versioning`

### Sprint 4.4 — Notifications & Activity
- [ ] Add in-app notification system (subscription renewals, failed payments, document expiry)
- [ ] Build activity log: document created/edited/downloaded with timestamps
- [ ] Add email notification on subscription events
- [ ] Commit: `dashboard: notifications and activity log`

---

## PHASE 5 — Frontend & SEO
*Goal: Fast, indexable marketing site that converts organic traffic.*

### Sprint 5.1 — Landing Page
- [ ] Build `/` homepage: hero, features, pricing, testimonials, CTA
- [ ] Write copy targeting: "privacy policy generator", "terms and conditions template"
- [ ] Add structured data (JSON-LD) for SoftwareApplication schema
- [ ] Ensure mobile-responsive layout
- [ ] Commit: `frontend: landing page`

### Sprint 5.2 — SEO Infrastructure
- [ ] Add `<title>`, `<meta description>`, `<canonical>` to all public pages
- [ ] Build dynamic `sitemap.xml` view
- [ ] Build `robots.txt` view
- [ ] Add Open Graph and Twitter Card meta tags
- [ ] Submit sitemap to Google Search Console (document steps in `research/seo.md`)
- [ ] Commit: `seo: meta tags, sitemap, robots`

### Sprint 5.3 — Document Landing Pages
- [ ] Create individual SEO pages for each document type:
  - `/privacy-policy-generator/`
  - `/terms-and-conditions-generator/`
  - `/cookie-policy-generator/`
  - `/nda-generator/`
  - `/service-agreement-generator/`
  - `/disclaimer-generator/`
- [ ] Each page: unique copy, feature list, CTA to signup
- [ ] Commit: `seo: document type landing pages`

### Sprint 5.4 — Pricing Page
- [ ] Build `/pricing/` page with plan comparison table
- [ ] Highlight Pro plan, show savings on annual
- [ ] Add FAQ section targeting billing questions
- [ ] Commit: `frontend: pricing page`

---

## PHASE 6 — Testing
*Goal: Full test coverage across all critical paths.*

### Sprint 6.1 — Unit Tests
- [ ] Set up `pytest` + `pytest-django`
- [ ] Test all model methods (`__str__`, `has_active_subscription`, `DocumentGenerator`)
- [ ] Test form validation for all document input forms
- [ ] Target: 80% coverage on models and forms
- [ ] Commit: `tests: unit tests for models and forms`

### Sprint 6.2 — Integration Tests
- [ ] Test full signup → verify email → login flow
- [ ] Test checkout → webhook → subscription activated flow
- [ ] Test document creation → PDF export flow
- [ ] Test quota enforcement (free user hitting 3 doc limit)
- [ ] Commit: `tests: integration tests for critical paths`

### Sprint 6.3 — Security Tests
- [ ] Test all auth-required views return 403/redirect when unauthenticated
- [ ] Test users cannot access other users' documents
- [ ] Test webhook endpoint rejects invalid Stripe signatures
- [ ] Test file upload validation (size, type)
- [ ] Commit: `tests: security and access control tests`

### Sprint 6.4 — Performance Tests
- [ ] Add `django-silk` or `django-debug-toolbar` for query profiling
- [ ] Identify and fix N+1 queries in dashboard document list
- [ ] Add `select_related` / `prefetch_related` where needed
- [ ] Test page load under simulated load with `locust`
- [ ] Commit: `perf: query optimisation and load testing`

---

## PHASE 7 — DevOps & Deployment
*Goal: Reliable, automated deployment pipeline.*

### Sprint 7.1 — CI/CD Pipeline
- [ ] Create `.github/workflows/ci.yml`:
  - Run `pytest` on every push
  - Run `pip audit` security check
  - Run `flake8` linting
  - Block merge if any check fails
- [ ] Commit: `ci: GitHub Actions pipeline`

### Sprint 7.2 — Production Deployment
- [ ] Confirm `railway.toml` and `nixpacks.toml` are correct
- [ ] Set all production env vars in Railway dashboard
- [ ] Configure PostgreSQL addon on Railway
- [ ] Configure custom domain and SSL
- [ ] Run `python manage.py collectstatic` in entrypoint
- [ ] Commit: `deploy: Railway production config`

### Sprint 7.3 — Monitoring & Logging
- [ ] Add `sentry-sdk` — capture exceptions in production
- [ ] Configure Sentry DSN in `.env`
- [ ] Add structured logging with request ID tracing
- [ ] Set up uptime monitoring (UptimeRobot — free tier)
- [ ] Commit: `ops: Sentry and logging`

### Sprint 7.4 — Backups
- [ ] Configure automated daily PostgreSQL backups on Railway
- [ ] Document restore procedure in `docs/disaster-recovery.md`
- [ ] Test restore from backup
- [ ] Commit: `ops: backup and recovery documentation`

---

## PHASE 8 — AI Integration (Enhancement Phase)
*Goal: AI-powered document customisation to differentiate from competitors.*

### Sprint 8.1 — AI Document Drafting
- [ ] Integrate Anthropic Claude API (or OpenAI)
- [ ] Add `AI_API_KEY` to `.env.example`
- [ ] Build `AIDocumentDrafter` class — takes user inputs → returns AI-drafted document
- [ ] Add "AI Draft" button on document creation flow (Pro feature only)
- [ ] Commit: `ai: AI-powered document drafting`

### Sprint 8.2 — Custom Clause Editor
- [ ] Allow users to edit individual clauses in generated documents
- [ ] Save custom clauses to user profile for reuse
- [ ] Add AI "improve this clause" button
- [ ] Commit: `ai: custom clause editor`

### Sprint 8.3 — Document Q&A
- [ ] Build chat interface on document view page
- [ ] User can ask questions about their document ("What does clause 4 mean?")
- [ ] Use RAG approach — feed document content as context to LLM
- [ ] Commit: `ai: document Q&A chat`

---

## PHASE 9 — Growth & Analytics
*Goal: Understand usage, reduce churn, grow revenue.*

### Sprint 9.1 — Analytics
- [ ] Add Plausible or Fathom analytics (privacy-friendly)
- [ ] Track: signups, document creations, plan upgrades, churn events
- [ ] Build internal admin dashboard showing key metrics
- [ ] Commit: `analytics: event tracking and admin dashboard`

### Sprint 9.2 — Referral System
- [ ] Add unique referral code per user
- [ ] Track referral signups
- [ ] Reward referrer with 1 free month on referred user's first payment
- [ ] Commit: `growth: referral system`

### Sprint 9.3 — Email Marketing
- [ ] Integrate Resend or Mailchimp for transactional + marketing emails
- [ ] Onboarding sequence: welcome → first document tip → upgrade nudge
- [ ] Churn recovery: email on subscription cancellation with discount offer
- [ ] Commit: `growth: email sequences`

---

## Backlog (Post-Launch)
- Team/organisation accounts with seat management
- API access for Enterprise plan (generate documents programmatically)
- White-label option for agencies
- Document expiry and renewal reminders
- E-signature integration (DocuSign / HelloSign)
- Multi-language document templates
- HIPAA-compliant document templates
- Mobile app (React Native)

---

## Definition of Done
Every task is only complete when:
1. Code is written and working
2. Tests cover the new code
3. Changes are committed with a conventional commit message
4. Changes are pushed to GitHub
5. No `TODO` or `FIXME` left in shipped code
6. SCRUM.md updated with sprint outcome
