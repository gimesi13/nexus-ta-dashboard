# Nexus TA Dashboard — Roadmap

Visibility into the Nexus API regression test-automation work (and the AI platform engineering
tasks alongside it). This document captures everything brainstormed so the plan lives with the
project. Sections are built incrementally; the first shipped feature is the **Test-Case Inventory**.

## Design principles

- **Trustworthy data, transparent provenance.** Every number is produced by a reproducible
  generator, shows how it was computed, and carries a "generated at / from source" stamp. No
  mystery figures.
- **Static + generated.** Python generators emit JSON; a plain static site renders it. No backend,
  no build step — deployable straight to GitHub Pages.
- **Self-contained.** Generators and committed data live in this repo so the site is independently
  deployable; they can later be wired into the module's `automation/agent-jobs/`.

## Tier 1 — Core

### Test-case inventory (shipped first)
Searchable/filterable table of every Spock feature: area, spec, test-case name, type, tags, owner,
and parameterized-case count. Generated directly from `*TestSteps.groovy` source — the trustworthy
source of truth for "what tests exist".

### Coverage (trustworthy pipeline)
Two lenses: **endpoint coverage** (OpenAPI spec vs. tests) and **feature/requirement coverage**.
Fix the existing "data I don't trust" problem by making coverage a transparent, reproducible
pipeline with inline methodology and links to raw generated JSON. Rank uncovered endpoints by real
QA traffic using the Honeycomb dataset `project-management.nexus-api-rest`.

### Nightly run report (TeamCity)
Latest nightly: pass/fail/skipped, duration, failed-test list with direct TeamCity links, plus a
short pass-rate trend. Sourced from `automation/tc-api.sh` + `tc-fetch-results.sh`.

### AI platform engineering work log
A separate portfolio/changelog of AI platform tasks delivered: title, date, description, impact,
links (PR/ticket/doc). Kept distinct from TA so the dashboard represents both work streams.

## Tier 2 — High-value additions

- **Flaky-test tracker** — surface `flaky_report.py` output ranked by flake rate + quarantine status.
- **Trends over time** — historical snapshots of test count, coverage %, and pass rate (append a
  small time-series JSON nightly).
- **Coverage gaps / OpenAPI drift** — new/changed endpoints lacking tests (`openapi_diff.py` ->
  `endpoint-drift.md`); the "what to write next" queue.
- **Activity feed** — in-progress NXS TA tickets + recently merged PRs (Jira + GitHub).
- **KPI strip** — headline numbers: total tests, coverage %, last-night pass rate, open flakes,
  AI tasks shipped this month.

## Tier 3 — Nice-to-have

- **Quick-links hub** — TeamCity, Honeycomb, Jira epic (NXS-11590), repo, key docs.
- **Suite health** — slowest tests, average duration, tag breakdown.
- **Requirement traceability** — ticket -> test mapping.

## Cross-cutting decisions

- **Single source of truth:** the module's Python generators emit versioned JSON artifacts; the
  site only renders them. This directly addresses the coverage-data trust problem.
- **Public vs. private:** the site is currently public. Nightly failures, endpoint names, and ticket
  detail may be sensitive. Options: keep public with aggregate/sanitized data; make the repo private
  (Pages needs GitHub Pro/org); or split public shell + private data. To be decided per section.

## Data flow

```
Spock specs (module, read-only)
        |
        v
tools/generate_*.py  ->  data/*.json (committed)  ->  static HTML + JS  ->  GitHub Pages (live)
```
