# Nexus TA Dashboard

A live dashboard for the **Nexus API regression test automation** work — built to give the team
(and anyone interested) visibility into test coverage, runs, and suite health.

> Status: **first feature shipped** — a searchable Test-Case Inventory. See [ROADMAP.md](ROADMAP.md)
> for the full plan.

## Live site

Hosted on GitHub Pages: https://gimesi13.github.io/nexus-ta-dashboard/

## Local preview

It's a static site — just open `index.html` in a browser, or serve the folder:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Structure

- `index.html` — overview / landing page
- `inventory.html` + `inventory.js` — Test-Case Inventory (searchable/filterable table)
- `styles.css` — GitHub dark-mode styling
- `data/inventory.json` — generated inventory data (served by the site)
- `tools/generate_inventory.py` — parses the module's `*TestSteps.groovy` into `data/inventory.json`

## Regenerating the inventory

```bash
python3 tools/generate_inventory.py            # uses the default local module checkout
python3 tools/generate_inventory.py --module-root /path/to/NexusApiRegressionTests
```

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the full plan (coverage, nightly run, flaky tracker,
AI platform work log, and more).
