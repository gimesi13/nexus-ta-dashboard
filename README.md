# Nexus TA Dashboard

Live dashboard for the **Nexus API regression test automation** work (and the AI platform
engineering tasks alongside it). The **source of truth lives here, inside the module**, so data can
be regenerated straight from the specs as part of the normal workflow; a publish step pushes the
generated static site to a free public GitHub Pages repo.

## Live site

https://gimesi13.github.io/nexus-ta-dashboard/

## How it works

```
src/test/groovy/**/*TestSteps.groovy   (specs, read in place)
docs/openapi-*.json + test-coverage-report/endpoints-data.js
        |
        v
dashboard/tools/generate_inventory.py  ->  dashboard/data/inventory.json
dashboard/tools/generate_coverage.py   ->  dashboard/data/coverage.json
        |
        v
dashboard/*.html + *.js  --(tools/publish.sh)-->  public Pages repo  ->  GitHub Pages (live)
```

- **In-module source** — everything under `dashboard/` is versioned in the monorepo with the tests.
- **Static + generated** — Python generators emit JSON; a plain static site renders it (no backend,
  no build step).
- **Public hosting stays free** — the monorepo is private, so the built site is published to the
  public `gimesi13/nexus-ta-dashboard` repo, which serves GitHub Pages.

## Refresh the data

Run from the `dashboard/` folder (self-locating: it finds the module automatically):

```bash
python3 tools/generate_inventory.py
python3 tools/generate_coverage.py                 # uses committed OpenAPI snapshot
python3 tools/generate_coverage.py --fetch-openapi # refresh OpenAPI from live QA first
```

## Publish (refresh data + deploy live)

```bash
tools/publish.sh
```

Overridable via env vars: `PAGES_REPO_DIR` (local checkout of the Pages repo, default
`~/IdeaProjects/nexus-ta-dashboard`) and `PAGES_REPO_URL`.

## Structure

- `index.html` — overview / landing page
- `inventory.html` + `inventory.js` — Test-Case Inventory (searchable/filterable)
- `coverage.html` + `coverage.js` — Endpoint Coverage (OpenAPI × tested overlay)
- `styles.css` — shared dark styling
- `data/inventory.json` / `data/coverage.json` — generated data (served by the site)
- `tools/generate_inventory.py` / `tools/generate_coverage.py` — regenerators
- `tools/publish.sh` — regenerates data and pushes the static site to the Pages repo
- `ROADMAP.md` — full plan (nightly run, flaky tracker, AI platform work log, and more)
