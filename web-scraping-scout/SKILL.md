---
name: web-scraping-scout
description: >-
  Use first before building or redesigning any scraper, or for an unclear scrape
  request: pick the cheapest complete extraction route, prove it on a 20–50
  record sample with curl_cffi, and estimate cost.
---
# Web Scraping Scout

Use this first for a new or unclear target, or before redesigning a scraper. Probe with small requests. Do not build the final crawler or structured PoC here.

## 1. Requirements

Get required fields, nice-to-haves, target volume (records/day), freshness, and markets. Without a field list, completeness cannot be judged — ask before deeper discovery.

## 2. Rules and legal

- Fetch `robots.txt`. Note `Disallow` for the paths you need and any `Crawl-delay`.
- Skim ToS for scraping/API clauses. Prefer logged-out public data. Flag personal data (GDPR) and anything that needs the user's decision.
- Load `../web-scraping-references/references/legal-ethics.md` when risk is unclear.

## 3. Discovery

- Fetch the URL and classify: status, redirects, login, bot-check, SPA shell, visible data.
- Enumerate URLs: sitemaps (`Sitemap:` in robots, `/sitemap.xml`, indexes, news/product sitemaps). Count URLs and check `lastmod` freshness.
- Map categories, filters, and search pagination. Find result caps and how to split queries under them. Note listing IDs and whether detail URLs can be built from them.
- Check embedded data: JSON-LD, `__NEXT_DATA__`, `__NUXT__`, `__PRELOADED_STATE__`, Apollo state, inline `<script>` JSON.
- Inspect XHR/fetch/GraphQL in a real browser or HAR on listing and detail pages; also check mobile app APIs. Read `references/api-scraping.md` and `references/pagination.md` when the path is unclear.

Temporary recon snippets are allowed. Do not create the final project.

## 4. Extraction route, cheapest first

1. Public or hidden JSON API (REST, XHR, GraphQL, mobile).
2. Data embedded in HTML.
3. Plain HTML parsing with selectors.
4. Browser rendering only if 1–3 fail. If needed, use the browser only to obtain cookies, then replay with a TLS-impersonating HTTP client.

For each candidate, record: endpoint, required headers/cookies/tokens, pagination, page size, and whether it works without login.

## 5. Access test

- Probe each route with `curl_cffi` from the intended IP type (datacenter vs residential, right country). Read `references/http-clients.md` if the client choice is unclear.
- Run a small, polite batch (tens of requests, with delays). Record status codes, block pages/challenges, latency, response size, and where blocking starts.
- Ask before login/session reuse, private cookies, captcha handling, proxy rotation, fingerprint/stealth escalation, paid APIs or paid proxies, high-rate crawling, or paywall access.

## 6. Completeness check

Take 20–50 records. Compare the cheap route field-by-field against the rendered detail page. Produce a table: field, % present per route, value mismatches. Fields missing from the cheap route decide whether you need a second request type (e.g. detail page) or a hybrid. Do this before optimizing cost.

## 7. Cost and load

For each route that passes completeness: requests per 1,000 records, average compressed bytes, expected GB per run via proxy, proxy cost, and run time at a safe concurrency. Compare only among complete routes.

## 8. Report and route

Write a short report as a testable experiment (hypothesis, test plan, metrics, success threshold). Include the recommended route plus fallback, field-coverage table, access-test results, cost estimate, open risks, and decisions needed from the user. Save probe scripts, sample responses, and HAR files next to the report so the investigation can be repeated. Check existing issues/PRs for duplicates before filing it in the project's tracker.

Handoff must include:

- working source path: HTML, embedded JSON, REST/XHR, GraphQL, browser render, or blocker
- endpoint URLs, payloads, required headers, selectors, pagination clues, sample records
- what was tried and failed
- risk notes and user decisions needed
- recommended next skill

Route after the report:

- One-off feasibility or small standalone proof: `web-scraping-simple`
- Recurring, production, or operational scraper: `web-scraping-pipeline-design`
- Existing scraper broken, output empty, or run quality review: `web-scraping-ops`

Load shared workflow references only as needed: `../web-scraping-references/references/lifecycle.md`, `framework-choice.md`, `toolbox.md`.

## Escalation

Proceed without extra approval for normal HTTP requests, browser/network inspection, embedded JSON, XHR/API/GraphQL discovery, sitemap and pagination probing, and small sample requests.
