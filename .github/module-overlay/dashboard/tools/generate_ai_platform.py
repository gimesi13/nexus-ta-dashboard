#!/usr/bin/env python3
"""Refresh dashboard/data/ai-platform.json headline stats from the live tree.

Portfolio categories/items stay curated (edit the JSON when you ship a capability).
Countable headline stats (rules, commands, hooks, jobs, KB docs, …) are recomputed
here so the AI Platform tab does not rot between narrative updates.

Usage:
    python3 tools/generate_ai_platform.py
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

DASHBOARD_ROOT = Path(__file__).resolve().parents[1]
MODULE_ROOT = Path(os.environ.get("NEXUS_MODULE_ROOT", DASHBOARD_ROOT.parent))
OUT = DASHBOARD_ROOT / "data" / "ai-platform.json"

# MCP servers we document as part of the platform (not auto-discovered — mcp.json
# is machine-local). Update this list when a server is added/removed for real.
MCP_SERVERS = ("Atlassian", "GitHub", "Honeycomb", "Lucid", "Playwright")


def repo_root(module: Path) -> Path:
    """Monorepo root (parent of gateway/)."""
    cur = module.resolve()
    for _ in range(6):
        if (cur / "gateway").is_dir() and (cur / "project").is_dir():
            return cur
        if (cur / ".git").exists() and (cur / "gateway").is_dir():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return module.parent.parent.parent  # best-effort


def count_glob(root: Path, pattern: str) -> int:
    if not root.is_dir():
        return 0
    return sum(1 for _ in root.glob(pattern) if _.is_file())


def count_files(root: Path, suffixes: tuple[str, ...]) -> int:
    if not root.is_dir():
        return 0
    n = 0
    for p in root.rglob("*"):
        if p.is_file() and p.suffix in suffixes and "node_modules" not in p.parts:
            n += 1
    return n


def count_analyzed_readmes(repo: Path) -> int:
    """Service READMEs with the reverse-engineer Analyzed stamp."""
    n = 0
    marker = re.compile(r"<!--\s*Analyzed:", re.I)
    for base in (repo / "project", repo / "gateway"):
        if not base.is_dir():
            continue
        for readme in base.rglob("README.md"):
            # skip deep noise / regression test trees
            parts = set(readme.parts)
            if "NexusApiRegressionTests" in parts or "node_modules" in parts:
                continue
            try:
                head = readme.read_text(encoding="utf-8", errors="replace")[:4000]
            except OSError:
                continue
            if marker.search(head):
                n += 1
    return n


def count_agentic_workflows(repo: Path, module: Path) -> int:
    """GHA workflows that look agentic (cursor-agent / ta-* bot flows)."""
    keys = ("cursor-agent", "cursor_agent", "repository_dispatch", "ta-author", "ta-merge", "ta-open")
    n = 0
    for wf_dir in (repo / ".github" / "workflows", module / ".github" / "workflows"):
        if not wf_dir.is_dir():
            continue
        for wf in wf_dir.glob("*.yml"):
            try:
                text = wf.read_text(encoding="utf-8", errors="replace").lower()
            except OSError:
                continue
            if any(k in text for k in keys) or wf.name.startswith("ta-"):
                n += 1
    return n


def prior_stat(data: dict, label: str) -> str | None:
    for s in data.get("stats") or []:
        if s.get("label") == label and s.get("value") is not None:
            return str(s["value"])
    return None


def build_stats(repo: Path, module: Path, prior: dict | None = None) -> list[dict]:
    prior = prior or {}
    dev_rules = count_glob(repo / ".cursor" / "rules", "*.mdc")
    ta_rules = count_glob(module / ".cursor" / "rules", "*.mdc")
    dev_cmds = count_glob(repo / ".cursor" / "commands", "*.md")
    ta_cmds = count_glob(module / ".cursor" / "commands", "*.md")
    dev_hooks = count_files(repo / ".cursor" / "hooks", (".py", ".sh"))
    ta_hooks = count_files(module / ".cursor" / "hooks", (".py", ".sh"))
    jobs = count_glob(module / "automation" / "agent-jobs", "*.sh")
    dev_kb = count_glob(repo / "docs" / "backend", "*.md")
    ta_docs = count_glob(module / "docs", "*.md")
    agentic = count_agentic_workflows(repo, module)
    readmes = count_analyzed_readmes(repo)
    # Sparse/shallow checkouts may miss project/** READMEs — keep last good count.
    if readmes == 0:
        kept = prior_stat(prior, "AI-generated docs")
        if kept and kept.isdigit() and int(kept) > 0:
            readmes = int(kept)

    return [
        {
            "label": "Roles served",
            "value": "2",
            "hint": "backend dev + test automation",
        },
        {
            "label": "Cursor rules",
            "value": str(dev_rules + ta_rules),
            "hint": f"{dev_rules} Dev + {ta_rules} TA (.mdc)",
        },
        {
            "label": "Slash commands",
            "value": str(dev_cmds + ta_cmds),
            "hint": f"{dev_cmds} Dev + {ta_cmds} TA workflows",
        },
        {
            "label": "Guardrail hooks",
            "value": str(dev_hooks + ta_hooks),
            "hint": f"{dev_hooks} Dev + {ta_hooks} TA deterministic guards",
        },
        {
            "label": "Autonomous jobs",
            "value": str(jobs),
            "hint": "headless agent -p schedules",
        },
        {
            "label": "Agentic CI flows",
            "value": str(agentic),
            "hint": "cursor-agent / bot GHA workflows",
        },
        {
            "label": "MCP integrations",
            "value": str(len(MCP_SERVERS)),
            "hint": ", ".join(MCP_SERVERS),
        },
        {
            "label": "Knowledge-base docs",
            "value": str(dev_kb + ta_docs),
            "hint": f"{dev_kb} Dev (docs/backend) + {ta_docs} TA grounding docs",
        },
        {
            "label": "AI-generated docs",
            "value": str(readmes),
            "hint": "reverse-engineered service READMEs",
        },
    ]


def main() -> int:
    repo = repo_root(MODULE_ROOT)
    if not OUT.is_file():
        print(f"error: {OUT} missing — create the curated portfolio first", file=sys.stderr)
        return 1

    data = json.loads(OUT.read_text(encoding="utf-8"))
    data["stats"] = build_stats(repo, MODULE_ROOT.resolve(), prior=data)
    data["generatedAt"] = dt.date.today().isoformat()
    data["statsSource"] = (
        "Headline stats recomputed from the monorepo tree on each publish. "
        "Category items stay curated — edit this JSON when you ship a new AI-platform capability. "
        f"MCP list is maintained in generate_ai_platform.py ({', '.join(MCP_SERVERS)})."
    )

    # Lightweight rollup for Overview
    cats = data.get("categories") or []
    items = sum(len(c.get("items") or []) for c in cats)
    live = sum(
        1
        for c in cats
        for it in (c.get("items") or [])
        if str(it.get("status") or "").lower() == "live"
    )
    active = sum(
        1
        for c in cats
        for it in (c.get("items") or [])
        if str(it.get("status") or "").lower() == "active"
    )
    data["overview"] = {
        "categories": len(cats),
        "capabilities": items,
        "live": live,
        "active": active,
    }

    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"Wrote {OUT.relative_to(DASHBOARD_ROOT)} — "
        f"{items} capabilities across {len(cats)} categories; "
        f"stats refreshed from {repo}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
