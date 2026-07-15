#!/usr/bin/env python3
"""Generate data/inventory.json for the Nexus TA Dashboard.

Parses the Spock regression specs (*TestSteps.groovy) straight from source -- the
trustworthy source of truth for "what test cases exist" -- and emits one row per Spock
feature method, with area, spec class, name, inferred type, @TestTags, @Owner, and the
count of static `where:` rows (parameterized cases).

Regex approach mirrors the module's test-coverage-report/recount_spock_tests.py so the
numbers stay consistent with the existing counter.

Usage:
    python3 tools/generate_inventory.py [--module-root PATH]

The module root defaults to the sibling monorepo checkout; override with --module-root
or the NEXUS_MODULE_ROOT env var.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

DEFAULT_MODULE_ROOT = Path(
    os.environ.get(
        "NEXUS_MODULE_ROOT",
        Path.home() / "IdeaProjects/dk-microservices1/gateway/unifiedApi/NexusApiRegressionTests",
    )
)

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT = REPO_ROOT / "data" / "inventory.json"

FEATURE_RE = re.compile(r"(?:^ {4}|^\t)def\s+\"([^\"]+)\"\s*\(\)\s*\{", re.MULTILINE)
CLASS_RE = re.compile(r"\bclass\s+(\w+)\b")
FEATURE_ANNO_RE = re.compile(r'@Feature\(\s*"([^"]*)"\s*\)')
OWNER_ANNO_RE = re.compile(r'@Owner\(\s*"([^"]*)"\s*\)')
TESTTAGS_RE = re.compile(r"@TestTags\(\s*\[([^\]]*)\]\s*\)")


def infer_type(simple: str) -> str:
    if "RegrTests" in simple:
        return "API regression"
    if "Validation" in simple:
        return "Validation"
    if "CRUD" in simple:
        return "CRUD"
    if "Workflow" in simple:
        return "Workflow"
    if "E2E" in simple:
        return "E2E"
    return "Other"


def area_from_path(path: Path) -> str:
    s = str(path)
    m = re.search(r"/tests/steps/([^/]+)/", s)
    if m:
        return m.group(1)
    for marker in ("apitest", "workflow", "businessflow", "sources", "resetters", "regression", "testdata"):
        if f"/{marker}/" in s:
            return marker
    return "other"


def static_where_rows(block: str) -> int:
    pipe_lines = [ln for ln in block.splitlines() if "|" in ln.split("//")[0] and ln.strip()]
    if len(pipe_lines) >= 2:
        return len(pipe_lines) - 1  # header row excluded
    return 1


def tags_before(text: str, start: int) -> list[str]:
    window = text[max(0, start - 500):start]
    matches = TESTTAGS_RE.findall(window)
    if not matches:
        return []
    raw = matches[-1]
    return [t.strip() for t in raw.split(",") if t.strip()]


def parse_spec(path: Path, module_root: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    mcls = CLASS_RE.search(text)
    if not mcls or not FEATURE_RE.search(text):
        return []
    simple = mcls.group(1)
    area = area_from_path(path)
    ctype = infer_type(simple)
    feature_anno = FEATURE_ANNO_RE.search(text)
    owner_anno = OWNER_ANNO_RE.search(text)
    feature_label = feature_anno.group(1) if feature_anno else ""
    owner = owner_anno.group(1) if owner_anno else ""
    rel = path.relative_to(module_root).as_posix()

    rows = []
    starts = [(m.start(), m.group(1)) for m in FEATURE_RE.finditer(text)]
    for i, (start, name) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
        block = text[start:end]
        has_where = re.search(r"^\s*where:\s*$", block, re.MULTILINE)
        cases = static_where_rows(block) if has_where else 1
        rows.append({
            "area": area,
            "spec": simple,
            "name": name,
            "type": ctype,
            "tags": tags_before(text, start),
            "owner": owner,
            "feature": feature_label,
            "cases": cases,
            "file": rel,
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--module-root", type=Path, default=DEFAULT_MODULE_ROOT,
                    help="Path to the NexusApiRegressionTests module (read-only).")
    args = ap.parse_args()

    module_root = args.module_root.resolve()
    src_root = module_root / "src/test/groovy"
    if not src_root.is_dir():
        print(f"error: spec source not found at {src_root}", file=sys.stderr)
        return 1

    rows: list[dict] = []
    for path in sorted(src_root.rglob("*TestSteps.groovy")):
        rows.extend(parse_spec(path, module_root))

    rows.sort(key=lambda r: (r["area"], r["spec"], r["name"]))
    specs = len({(r["area"], r["spec"]) for r in rows})
    total_cases = sum(r["cases"] for r in rows)

    result = {
        "generatedAt": dt.date.today().isoformat(),
        "source": "source",
        "features": len(rows),
        "cases": total_cases,
        "specs": specs,
        "areas": len({r["area"] for r in rows}),
        "rows": rows,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}: {len(rows)} features / {total_cases} cases across {specs} specs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
