# Nexus TA Dashboard

Live dashboard for the **Nexus API regression test automation** work (and the AI platform
engineering tasks alongside it). The **source of truth lives here, inside the module**, so data can
be regenerated straight from the specs as part of the normal workflow; a publish step pushes the
generated static site to a free public GitHub Pages repo.

## Live site

https://gimesi13.github.io/nexus-ta-dashboard/

## How it works

The live site is **static** (JSON + HTML/JS). “Always up to date” means a **scheduled job**
regenerates data from the latest specs / OpenAPI / TeamCity and pushes Pages — the browser never
calls TeamCity or the monorepo directly (keeps tokens off the public site).

```
TeamCity nightly finishes
        |
        v
automation/agent-jobs/dashboard-publish.sh   (cron / TC / Cursor Automation, weekdays ~06:30)
  1. git pull module checkout
  2. tc_fetch_nightly.py          ->  .last-tc-nightly.json
  3. generate_inventory.py        ->  data/inventory.json   (specs / steps / types)
  4. generate_coverage.py         ->  data/coverage.json    (OpenAPI × overlay; Mon: --fetch-openapi)
  5. generate_nightly.py          ->  data/nightly.json
  6. publish.sh                   ->  gimesi13/nexus-ta-dashboard  ->  GitHub Pages
```

| Signal | How it lands on the site |
|---|---|
| New / changed Spock feature or step | Morning job `git pull` + inventory regen |
| New nightly run | `tc_fetch_nightly.py` after TC finishes |
| New / changed API endpoint | Monday `FETCH_OPENAPI=1` (live QA); or any publish with `FETCH_OPENAPI=1` |
| “Is this endpoint tested?” overlay | Weekly `coverage-refresh` / `openapi-drift` jobs (PRs you merge) — next morning publish picks them up |

- **In-module source** — everything under `dashboard/` is versioned in the monorepo with the tests.
- **Static + generated** — Python generators emit JSON; a plain static site renders it (no backend,
  no build step). TeamCity credentials never live in `dashboard/`.
- **Public hosting stays free** — the monorepo is private, so the built site is published to the
  public `gimesi13/nexus-ta-dashboard` repo, which serves GitHub Pages.

## Hands-off refresh (recommended)

One trigger only (cron **or** TeamCity scheduled config **or** Cursor Automation §1b in
[docs/AUTOMATIONS.md](../docs/AUTOMATIONS.md) — do not double-run):

```bash
export TEAMCITY_URL='https://teamcity.dynata.com'
export TEAMCITY_TOKEN='…'                          # read-scoped TCV2 token
export TEAMCITY_NIGHTLY_BUILD_TYPE_ID='…'          # see docs/MCP_TEAMCITY.md
# Optional: PAGES_REPO_DIR, FETCH_OPENAPI=1 (force OpenAPI every run)

../automation/agent-jobs/dashboard-publish.sh
```

Cron example (weekday ~06:30 local, after the nightly):

```cron
30 6 * * 1-5  cd /path/to/NexusApiRegressionTests && automation/agent-jobs/dashboard-publish.sh >> /var/log/nexus-dashboard.log 2>&1
```

Until that cron/TC/Automation is installed on a machine that has the monorepo checkout, Pages clone,
and `TEAMCITY_TOKEN`, the site only updates when someone runs the job manually.

## Manual refresh

From the `dashboard/` folder:

```bash
python3 tools/generate_inventory.py
python3 tools/generate_coverage.py                 # uses committed OpenAPI snapshot
python3 tools/generate_coverage.py --fetch-openapi # refresh OpenAPI from live QA first
python3 ../automation/tc_fetch_nightly.py           # pull latest TC build summary
python3 tools/generate_nightly.py                  # shape into data/nightly.json
```

Or regenerate all three without pushing Pages:

```bash
SKIP_PUBLISH=1 tools/publish.sh
# with live OpenAPI:
FETCH_OPENAPI=1 SKIP_PUBLISH=1 tools/publish.sh
```

Publish (refresh data + deploy live):

```bash
tools/publish.sh
```

Overridable via env vars: `PAGES_REPO_DIR` (local checkout of the Pages repo, default
`~/IdeaProjects/nexus-ta-dashboard`), `PAGES_REPO_URL`, `FETCH_OPENAPI=1`.

See [docs/MCP_TEAMCITY.md](../docs/MCP_TEAMCITY.md) and [docs/AUTOMATIONS.md](../docs/AUTOMATIONS.md).

## Structure

- `index.html` + `overview.js` — overview / landing
- `nightly.html` + `nightly.js` — **Nightly Run** (latest TeamCity build)
- `inventory.html` + `inventory.js` — Test-Case Inventory (searchable/filterable)
- `coverage.html` + `coverage.js` — Endpoint Coverage (OpenAPI × tested overlay)
- `styles.css` — shared dark styling
- `data/inventory.json` / `coverage.json` / `nightly.json` — generated data
- `tools/generate_*.py` — regenerators (nightly only shapes automation outputs)
- `tools/publish.sh` — regenerates data and pushes the static site to the Pages repo
- `ROADMAP.md` — full plan (flaky tracker, AI platform work log, and more)
