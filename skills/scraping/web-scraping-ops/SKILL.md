---
name: web-scraping-ops
description: "Use when a scraper already exists and the user wants a failing run diagnosed or a run audited before the data is trusted."
metadata:
  version: "1.1.0"
---
# Web Scraping Ops

Use when a scraper already exists: after a run, before trusting data, or when it is failing or producing bad data. Do not build a new scraper here.

## Choose Path

- Output quality or data trust is the question: audit the run first, then debug only if the audit points to a fix.
- The scraper is failing to fetch or parse: diagnose from the smallest saved evidence. Prefer replay before live refetching.
- Do not re-run large crawls unless the user asks.

## Audit a Run

1. Locate run outputs: manifest, parsed, curated, audit, stats, raw samples, failures, logs.
2. Read `../web-scraping-references/references/quality-gates.md` and `../web-scraping-references/references/analysis.md`.
3. Report run metadata: run ID, scraper version, schema version, start/end time, duration, source scope, output paths.
4. Check record counts, per-stage counts, status distribution, errors/failures, and approximate throughput.
5. Compute fill rate, unique count, duplicates, and the delta against a previous run with `python scripts/run_metrics.py`. Pass the parsed or curated JSONL, `--id-field` when records have a stable key, `--fields` for the required fields, and `--previous` when a prior good run exists. Report the script's JSON. Do not recompute those four numbers by hand.
6. Check type consistency, examples, suspicious constants, schema/Pydantic validation, and sample good/bad records.
7. When `--previous` was passed, report `delta.records`, each `delta.fill_rate` entry, and `delta.duplicate_extra`, plus new errors and schema drift.
8. State whether the run is trusted, suspicious, or blocked. Include the evidence and the next action.

## Diagnose and Fix

1. Reproduce on the smallest saved raw sample, failure payload, fixture, URL, or page that fails.
2. Compare expected vs actual: status, response body, rendered DOM, network calls, manifest row, parsed row, curated row, audit finding.
3. Classify the failure and load only the reference you need:
   - fetch failure: status, timeout, retry exhaustion, DNS, TLS, proxy, rate limit
   - selector/parser drift: `../web-scraping-scout/references/parsers.md`
   - API contract drift: `../web-scraping-scout/references/api-scraping.md`
   - pagination drift: `../web-scraping-scout/references/pagination.md`
   - validation/schema drift: compare model, parsed output, and curated output
   - storage failure: `../web-scraping-references/references/storage-policy.md`
   - auth/login failure: `../web-scraping-scout/references/auth.md`
   - anti-bot/browser/proxy failure: `../web-scraping-scout/references/browsers.md` or `../web-scraping-scout/references/proxy.md`
   - analysis/reporting: `../web-scraping-references/references/data-analysis.md`
4. Fix the narrow cause; avoid rewriting from scratch unless the current method is dead.
5. Add a regression check when practical: saved HTML/API fixture, replay test, sample output assertion, or smoke command.

## Verify

Run project lint/type/test commands if present, replay the saved failure, then run the smallest live sample needed. Re-audit the new output before treating data as trusted.

If the extraction method is dead, route back to `web-scraping-scout`. If the project needs a production redesign, route to `web-scraping-pipeline-design`.
