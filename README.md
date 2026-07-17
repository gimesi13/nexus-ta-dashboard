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
automation/tc-fetch-results.sh + generate_digest.py   (morning TC pull)
        |
        v
dashboard/tools/generate_inventory.py  ->  dashboard/data/inventory.json
dashboard/tools/generate_coverage.py   ->  dashboard/data/coverage.json
dashboard/tools/generate_nightly.py    ->  dashboard/data/nightly.json
        |
        v
dashboard/*.html + *.js  --(tools/publish.sh)-->  public Pages repo  ->  GitHub Pages (live)
```

- **In-module source** — everything under `dashboard/` is versioned in the monorepo with the tests.
- **Static + generated** — Python generators emit JSON; a plain static site renders it (no backend,
  no build step). TeamCity credentials never live in `dashboard/`.
- **Public hosting stays free** — the monorepo is private, so the built site is published to the
  public `gimesi13/nexus-ta-dashboard` repo, which serves GitHub Pages.

## Refresh the data

Run from the `dashboard/` folder (self-locating: it finds the module automatically):

```bash
python3 tools/generate_inventory.py
python3 tools/generate_coverage.py                 # uses committed OpenAPI snapshot
python3 tools/generate_coverage.py --fetch-openapi # refresh OpenAPI from live QA first
python3 tools/generate_nightly.py                  # needs JUnit/digest from automation/
```

Or regenerate all three without pushing Pages:

```bash
SKIP_PUBLISH=1 tools/publish.sh
```

## Publish (refresh data + deploy live)

```bash
tools/publish.sh
```

Overridable via env vars: `PAGES_REPO_DIR` (local checkout of the Pages repo, default
`~/IdeaProjects/nexus-ta-dashboard`) and `PAGES_REPO_URL`.

### When to republish

| Trigger | What to run |
|---|---|
| Specs / tags / owners changed | `tools/publish.sh` (or `SKIP_PUBLISH=1` then push later) |
| OpenAPI / coverage overlay changed | same — coverage generator runs inside publish |
| Morning after TeamCity nightly | `../automation/agent-jobs/dashboard-publish.sh` (pulls TC, then publish) |

Inventory and coverage do **not** auto-update in the browser — publish is the update mechanism.

## Morning TeamCity job

Pull latest nightly results and publish (maintainer machine / cron / Cursor Automation):

```bash
export TEAMCITY_URL='https://teamcity.dynata.com'
export TEAMCITY_TOKEN='…'                          # read-scoped TCV2 token
export TEAMCITY_NIGHTLY_BUILD_TYPE_ID='…'          # see docs/MCP_TEAMCITY.md

../automation/agent-jobs/dashboard-publish.sh
```

Cron example (weekday ~06:30 local):

```cron
30 6 * * 1-5  cd /path/to/NexusApiRegressionTests && automation/agent-jobs/dashboard-publish.sh >> /var/log/nexus-dashboard.log 2>&1
```

See [docs/MCP_TEAMCITY.md](../docs/MCP_TEAMCITY.md) and [docs/AUTOMATIONS.md](../docs/AUTOMATIONS.md).

## Structure

- `index.html` + `overview.js` — overview / landing (includes **Last nightly run**)
- `inventory.html` + `inventory.js` — Test-Case Inventory (searchable/filterable)
- `coverage.html` + `coverage.js` — Endpoint Coverage (OpenAPI × tested overlay)
- `styles.css` — shared dark styling
- `data/inventory.json` / `coverage.json` / `nightly.json` — generated data
- `tools/generate_*.py` — regenerators (nightly only shapes automation outputs)
- `tools/publish.sh` — regenerates data and pushes the static site to the Pages repo
- `ROADMAP.md` — full plan (flaky tracker, AI platform work log, and more)
