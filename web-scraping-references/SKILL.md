---
name: web-scraping-references
description: "Use when another scraping skill points at a shared reference, or when a scraping workflow needs one shared reference loaded."
metadata:
  version: "1.0.1"
---
# Web Scraping References

Shared vocabulary, decision rules, and implementation references for scraping skills. Load only the reference needed by the active workflow. Recon-specific references (API scraping, pagination, HTTP clients, browsers, auth, proxy, parsers) live in `../web-scraping-scout/references/`.

## References

- `references/lifecycle.md`: feasibility vs production, raw/parsed/curated/manifest/audit.
- `references/feasibility-poc.md`: structured feasibility PoC project and `FEASIBILITY.md`.
- `references/framework-choice.md`: Scrapy, Crawlee, standalone, and browser/API decisions.
- `references/storage-policy.md`: JSONL, Parquet, DuckDB, Postgres, retention, append-only runs, and implementation backends.
- `references/quality-gates.md`: audits, acceptance checks, run-to-run comparisons.
- `references/legal-ethics.md`: advisory risk notes and escalation boundaries.
- `references/operator-runbook.md`: production operator README expectations.
- `references/downstream-ml-llm.md`: stable IDs, metadata, hashes, clean text.
- `references/toolbox.md`: dependency/tool selection and health checks.
- `references/checkpointing.md`: resume, retries, dedupe, latest-good pointers.
- `references/standalone-template.md`: standalone Python scraper template.
- `references/testing.md`: fixtures, replay tests, and scraper test strategy.
- `references/docker.md`: containerizing and running scrapers.
- `references/utilities.md`: shared helper utilities.
- `references/analysis.md`: run analysis for audits.
- `references/data-analysis.md`: analyzing and reporting scraped data.
