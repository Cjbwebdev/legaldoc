# LegalDoc Sprint Plan

This sprint plan is organized as hourly Scrum-style increments for rapid execution and clear delivery around the LegalDoc repository.

## Sprint 1 — 1 hour
- Audit repository structure and verify app modules
- Confirm `config/`, `users/`, `billing/`, `dashboard/`, and `templates/` folders are wired correctly
- Update README with the polished LegalDoc project description

## Sprint 2 — 1 hour
- Validate authentication flows in `users/`
- Review signup, login, and user profile handling
- Note gaps for email verification, password reset, and OAuth/SSO expansion

## Sprint 3 — 1 hour
- Review billing module in `billing/`
- Confirm support for subscription gating, trials, and webhook state updates
- Document Stripe/Paddle integration points and billing plan logic

## Sprint 4 — 1 hour
- Review dashboard experience in `dashboard/`
- Confirm document creation, management, download/export flows
- Identify template-driven generation points and extension hooks
- Define the initial downloadable document templates and their fields

## Sprint 5 — 1 hour
- Seed the platform with core legal document templates and sample content
- Confirm each document is available for download in PDF/Word-friendly format
- Audit public pages and SEO readiness in `templates/`
- Verify metadata, sitemap/robots readiness, and landing page copy
- Align keyword strategy for legal document search terms

## Sprint 6 — 1 hour
- Validate deployment configuration for Railway and Nixpacks
- Smoke test `entrypoint.sh`, `Procfile`, and environment setup
- Capture remaining high-value enhancements for AI and integrations

## Core Document Templates

The following legal documents should be defined, templated, and made available for download in the dashboard:

- Privacy Policy
  - Purpose: Captures data collection, use, storage, and user rights.
  - Download output: downloadable policy page and exportable legal document.
  - Key fields: company name, contact email, types of personal data, data sharing, cookies, retention, user rights.

- Terms and Conditions / Terms of Service
  - Purpose: Defines site/service rules, user obligations, payment terms, cancellations, and liability.
  - Download output: downloadable contract-style terms document.
  - Key fields: service description, account requirements, subscription billing, refunds, dispute resolution.

- Cookie Policy
  - Purpose: Explains cookie usage, categories, and consent management.
  - Download output: standalone cookie policy document.
  - Key fields: cookie types, purpose, third-party cookies, consent management, opt-out links.

- Non-Disclosure Agreement (NDA)
  - Purpose: Provides a template for confidential information protection between parties.
  - Download output: downloadable agreement template.
  - Key fields: parties, confidential information, permitted disclosures, term, governing law.

- Service Agreement / Engagement Letter
  - Purpose: Formalizes service terms if the user wants to offer contract services.
  - Download output: downloadable service agreement template.
  - Key fields: scope of work, deliverables, fees, payment terms, termination, warranties.

- Website Disclaimer
  - Purpose: Limits liability and clarifies the scope of online information.
  - Download output: downloadable disclaimer statement.
  - Key fields: accuracy of information, external links, no legal advice disclaimer.

## Notes
- Each sprint is designed to deliver a small, testable outcome in one hour.
- Use this plan as a baseline for implementation, review, and prioritization.
