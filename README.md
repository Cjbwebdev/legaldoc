# LegalDoc — Subscription SaaS for Auto-Generated Legal Documents

**LegalDoc** is a modern, production-ready **SaaS platform** designed to help individuals and businesses quickly generate essential legal documents through a clean, automated, and secure workflow. Built with a modular architecture and powered by a full authentication, billing, dashboard, and SEO-optimized frontend, LegalDoc provides a complete foundation for a scalable legal-tech product.

The project was scaffolded using **Qwentin Site Factory v2.0**, giving it a professional, enterprise-grade structure from day one.

---

## Core Value Proposition

LegalDoc solves a simple but painful problem:
**Legal documents take too long, cost too much, and require expertise most people don’t have.**

This platform turns that multi-hour process into a **90-second workflow** by combining:
- Automated document generation
- Secure user accounts
- Subscription-based access
- A clean dashboard for managing documents
- SEO-optimized public pages for organic acquisition

It is built to be extended with AI-powered document drafting, template customization, and integrations with payment processors or CRM systems.

---

## Key Features

### 1. Authentication & User Management
- Secure signup/login flow
- Password reset and email verification readiness
- User profiles stored in the dedicated `users` module
- Session-based auth today, ready for OAuth/SSO expansion
- Clean separation for future enterprise security

### 2. Subscription Billing
- Full billing module included in `billing/`
- Designed for Stripe or Paddle integration
- Supports:
  - Monthly/annual plans
  - Trials
  - Webhook-driven subscription state updates
- Automatic gating of premium features

### 3. Document Dashboard
- User-friendly dashboard for:
  - Creating new legal documents
  - Managing existing documents
  - Downloading or exporting generated files
- Template-driven generation system under `templates/`
- Extendable to AI-generated content and customization

### 4. Core Legal Document Templates
- Privacy Policy: data collection, cookies, retention, and user rights
- Terms and Conditions / Terms of Service: user obligations, billing, cancellation, liability
- Cookie Policy: cookie categories, consent, third-party tracking, opt-out
- Non-Disclosure Agreement (NDA): confidentiality terms, permitted disclosures, governing law
- Service Agreement / Engagement Letter: scope of services, fees, deliverables, termination
- Website Disclaimer: liability limitation and legal advice notice

### 5. SEO-Optimized Marketing Pages
- Clean, fast, indexable public pages
- Structured metadata for search engines
- Built-in sitemap and robots configuration readiness
- Ideal for ranking on terms like:
  - “privacy policy generator”
  - “terms and conditions template”
  - “legal document SaaS”

### 5. Production-Ready Deployment
- Includes `railway.toml`, `nixpacks.toml`, and `Procfile`
- `.env.example` for environment variable setup
- Docker-friendly `entrypoint.sh`
- Python backend with Django-style app design

---

## Technical Architecture

### Backend
- Python backend with modular apps:
  - `users/`
  - `billing/`
  - `dashboard/`
  - `templates/`
  - `config/`

### Frontend
- Server-rendered HTML templates in `templates/`
- SEO-optimized layout and metadata
- Clean, responsive UI with customization-ready structure

### DevOps
- Railway deployment pipeline
- Nixpacks for reproducible builds
- GitHub-friendly deployment configuration
- Environment-based application settings

---

## Use Cases

### For Entrepreneurs
Launch a legal-document generator SaaS with minimal setup.

### For Agencies
Offer automated legal document creation to clients.

### For Internal Teams
Generate consistent legal templates across departments.

### For AI Integrators
Plug in LLMs to generate custom contracts, policies, NDAs, and more.

---

## Why This Project Matters

LegalDoc gives you a **complete SaaS foundation**—auth, billing, dashboard, SEO, deployment—so you can focus on the differentiator:
**your legal templates, your AI logic, your business model.**

It is a perfect starting point for commercial apps like PolicyGen, Termly, or Iubenda competitors, but with full ownership and extensibility.

---

## Scrum-Style Hourly Sprint Roadmap

This project can be executed in focused hourly sprints with clear delivery checkpoints.

### Sprint 1 — 1 hour
- Audit repo structure and confirm current app wiring
- Update README with polished product description
- Verify environment files and deploy config exist

### Sprint 2 — 1 hour
- Validate authentication flows in `users/`
- Check signup/login and session handling
- Tab future work for OAuth/SSO and email verification

### Sprint 3 — 1 hour
- Review `billing/` for plan gating and webhook support
- Confirm subscription flows and premium access checks
- Document Stripe/Paddle integration points

### Sprint 4 — 1 hour
- Review dashboard flow in `dashboard/`
- Confirm document creation, management, and export UX
- Identify missing template CRUD or generation hooks

### Sprint 5 — 1 hour
- Audit frontend SEO and public landing pages
- Verify metadata, sitemap, and responsive layout
- Plan keyword-focused copy for organic acquisition

### Sprint 6 — 1 hour
- Validate deployment readiness using Railway and Nixpacks
- Run a local deployment smoke test
- Capture remaining enhancements for AI and integrations

---

## Deploy
1. Configure environment variables from `.env.example`
2. Deploy with Railway or your preferred Python host
3. Use `entrypoint.sh`, `railway.toml`, and `Procfile` for quick setup
