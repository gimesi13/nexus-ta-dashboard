# Nexus TA Dashboard

A live dashboard for the **Nexus API regression test automation** work — built to give the team
(and anyone interested) visibility into test coverage, runs, and suite health.

> Status: **hello-world / bootstrap**. This is the seed of the dashboard; content and data wiring
> are being planned next.

## Live site

Hosted on GitHub Pages: https://gimesi13.github.io/nexus-ta-dashboard/

## Local preview

It's a static site — just open `index.html` in a browser, or serve the folder:

```bash
python3 -m http.server 8000
# then visit http://localhost:8000
```

## Structure

- `index.html` — landing page
- `styles.css` — styling

## Roadmap

Planning in progress. Candidate sections: test coverage overview, latest CI/regression run
results, flaky-test tracker, coverage gaps, and links to Jira/TeamCity.
