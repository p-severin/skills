---
name: web-scraping-pipeline-design
description: "Use when the user wants a production scraping pipeline designed after scouting and before implementation."
disable-model-invocation: true
metadata:
  version: "1.0.0"
---
# Web Scraping Pipeline Design

Use for production scraping architecture. Do not build scraper code here.

## Inputs

Start from scout notes when available: target, data goal, source strategy, endpoint/selector evidence, pagination, browser need, risk notes, sample records, and failure modes.

If the data goal is unclear, ask what records/fields the user needs before designing.

## Read References

Load only the references needed:

- `../web-scraping-references/references/lifecycle.md`
- `../web-scraping-references/references/framework-choice.md`
- `../web-scraping-references/references/storage-policy.md`
- `../web-scraping-references/references/quality-gates.md`
- `../web-scraping-references/references/legal-ethics.md`
- `../web-scraping-references/references/operator-runbook.md`
- `../web-scraping-references/references/downstream-ml-llm.md`
- `../web-scraping-references/references/checkpointing.md`
- `../web-scraping-references/references/toolbox.md`
- `../web-scraping-references/references/scrapy-integration.md`, `testing.md`, `docker.md` for implementation and deploy details

## Design Rules

- Scrapy is the default production recommendation, including API-only production, unless there is a stronger reason not to.
- Recommend Crawlee-python only when browser context, SPA interactions, scrolling/clicking, stateful UI, or adaptive browser/HTTP behavior are central.
- Standalone Python is for feasibility and rare production exceptions; justify it explicitly.
- Name the primary output format and why it fits.
- Surface legal/ethical/anti-bot risk as advisory notes and user decisions.
- Stop after the design brief and ask for approval before implementation handoff.

## Required Brief Format

Include every section; use `N/A` only when truly irrelevant.

### Target
Site/API, domain scope, seed URLs, and out-of-scope areas.

### Goal/Data Contract
Record types, fields, required fields, stable IDs, schema expectations.

### Source Strategy
HTML/API/XHR/GraphQL/embedded JSON/browser path, pagination, detail flow, evidence.

### Framework Decision
Recommended framework and why.

### Why Not Alternatives
Why not Scrapy/Crawlee/standalone/browser/direct API as applicable.

### Data Lifecycle
Raw, parsed, curated, manifest, audit, and run metadata expectations.

### Storage/Formats
Primary format, optional formats, append/versioning, latest-good, retention.

### Run Modes
Smoke/sample mode, full mode, limits, resume/checkpoint expectations.

### Quality Gates/Audit
Required fields, validation, duplicates, fill rates, suspicious constants, run deltas.

### Risk Notes
Login, captcha, anti-bot, robots/ToS signals, cost, rate limits, user decisions.

### Deploy/Operations
Docker/cron/systemd/env/secrets/alerts/logs/runbook expectations.

### Open Questions
Unknowns that affect implementation.

### Approval Request
Ask the user to approve before routing to implementation.

## Handoff

After approval:

- Scrapy default: implement the approved Scrapy project in the target repo.
- Browser-interaction-heavy: implement with Crawlee-python in the target repo.
- Rare standalone exception: route to `web-scraping-simple` with explicit rationale.
- Running scrapers that break or need a quality check: `web-scraping-ops`.
