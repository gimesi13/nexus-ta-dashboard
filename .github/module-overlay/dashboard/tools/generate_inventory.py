#!/usr/bin/env python3
"""Generate data/inventory.json for the Nexus TA Dashboard.

Parses the Spock regression specs (*TestSteps.groovy) straight from source -- the
trustworthy source of truth for "what test cases exist" -- and emits one row per Spock
feature method, with area, spec class, name, inferred type, @TestTags, @Owner, and the
count of static `where:` rows (parameterized cases).

Type taxonomy (per feature, not per class) — priority first-match:
  Validation → E2E → Workflow → Query → CRUD → Other

Signals come from the feature title + Spock step labels. The Spec class name is only a
weak hint when the feature text is ambiguous. Optional overrides live in
type_overrides.json keyed as "SpecName::exact feature title".

Note: legacy test-coverage-report/recount_spock_tests.py still uses class-name substring
typing; dashboard inventory.json is the source of truth for types.

Usage:
    python3 tools/generate_inventory.py [--module-root PATH] [--audit]

This script lives at <module>/dashboard/tools/, so by default it locates the module
automatically (two directories up) and reads the specs in place -- no external path
needed. Override with --module-root or the NEXUS_MODULE_ROOT env var if needed.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

DASHBOARD_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODULE_ROOT = Path(
    os.environ.get("NEXUS_MODULE_ROOT", DASHBOARD_ROOT.parent)
)

OUT = DASHBOARD_ROOT / "data" / "inventory.json"
OVERRIDES_PATH = Path(__file__).resolve().parent / "type_overrides.json"

FEATURE_RE = re.compile(r"(?:^ {4}|^\t)def\s+\"([^\"]+)\"\s*\(\)\s*\{", re.MULTILINE)
CLASS_RE = re.compile(r"\bclass\s+(\w+)\b")
FEATURE_ANNO_RE = re.compile(r'@Feature\(\s*"([^"]*)"\s*\)')
OWNER_ANNO_RE = re.compile(r'@Owner\(\s*"([^"]*)"\s*\)')
TESTTAGS_RE = re.compile(r"@TestTags\(\s*\[([^\]]*)\]\s*\)")

CANONICAL_TYPES = ("Validation", "E2E", "Workflow", "Query", "CRUD", "Other")

# --- per-feature type signals -------------------------------------------------

# Strong signals — safe on feature title + step labels
VALIDATION_STRONG_RE = re.compile(
    r"(?i)("
    r"\binvalid\b|\breject(?:ed|s)?\b|\brejection\b|should\s+fail|fails?\s+validation|"
    r"validation\s+exception|appropriate\s+error|"
    r"\bcannot\s+(?:save|hide|take|create|update|delete|deactivate|send|set|be\s+deleted)\b|"
    r"\ba\s+user\s+cannot\b|\bmust\s+not\b|\bmust\s+send\b|"
    r"\bnon-existent\b|\bnonexistent\b|\bunsupported\b|"
    r"\bunimplemented\b|\bunauthorized\b|\bforbidden\b|missing\s+required|"
    r"\bexceeding\b|over\s+100|do\s+not\s+sum|negative\s+(?:quota|percentage)|"
    r"\b422\b|\b400\b|\b401\b|\b403\b|\b404\b|"
    r"wrong\s+ordering|case\s+sensitivity\s+test|"
    r"is\s+rejected|returns?\s+500|returns?\s+4\d\d|"
    r"date\s+in\s+the\s+past|\bpast\s+date\b|"
    r"after\s+(?:the\s+)?(?:proposed\s+)?end|before\s+(?:the\s+)?(?:proposed\s+)?start"
    r")"
)
# Weaker title-only signals (step labels often mention empty/duplicate coincidentally)
VALIDATION_TITLE_RE = re.compile(
    r"(?i)("
    r"empty\s+(?:body|name|string|list)|very\s+long\s+name|"
    r"same\s+content\s+as\s+existing|with\s+same\s+content|partial\s+id\s+list|"
    r"\bduplicate\b"
    r")"
)
E2E_RE = re.compile(
    r"(?i)\b(e2e|end-to-end|end\s+to\s+end)\b|complete\s+.+\s+end-to-end"
)
WORKFLOW_RE = re.compile(
    r"(?i)\b("
    r"workflow|change\s+order\s+flow|flow:|"
    r"phase\s+management|sold\s*quota|"
    r"request,\s*evaluation|"
    r"block\s+traffic|"
    r"price\s*control|over[- ]threshold|approve\s+threshold|"
    r"hasRightToApprove|exceedsApproveThreshold|"
    r"allowReopenProject|reopens?\s+to|publishes\s+.+notification|"
    r"fullprojectsetup\s+(?:derives|fills|persists)"
    r")\b"
)
# Prefer matching these on the feature *title* so setup steps do not steal the type.
QUERY_RE = re.compile(
    r"\b("
    r"search|lookup|filter|catalog|assemble\s+options|"
    r"get\s+all\b|list\s+"
    r")\b|"
    r"\bget\s+(?:\w+\s+){0,4}(?:ids?|labels?|cores?)\b|"
    r"\bsearch\s+(?:\w+\s+){0,4}(?:ids?|labels?)\b",
    re.IGNORECASE,
)
QUERY_GET_RE = re.compile(
    r"(?i)\b("
    r"get\s+all\b|"
    r"get\s+available\b|get\s+managers?\b|get\s+exclusion\s+configuration\b|"
    r"get\s+quota\s+group\s+(?:delivery\s+settings|sources|project\s+exclusions|"
    r"respondent\s+exclusions|inclusion\s+settings)\b|"
    r"get\s+latest\s+feasibility\b|"
    r"get\s+project\s+(?:core|overview|notes|managers?|dates|ids?)\b|"
    r"get\s+(?:audience|quota)\s+group\s+ids?\b|"
    r"get\s+partner\s+event\s+defaults\b|"
    r"get\s+deprecated\b|download\b|view\s+project\s+exclusion|"
    r"compare\s+template|validate\s+audience\s+template|"
    r"get\s+sales\s+order|get\s+audience\s+template|"
    r"get\s+project\s+note\b|get\s+respondent\s+exclusions\b|"
    r"GET\s+sales\s+order|GET\s+active\s+partner|"
    r"view\s+(?:system|user)\s+settings|get\s+user\s+settings|"
    r"get\s+tracker\s+details|get\s+apply\s+sources|"
    r"soft\s+launch\s+(?:reached|state)|across\s+subsequent\s+reads"
    r")"
)
CRUD_RE = re.compile(
    r"(?i)\b("
    r"create|clone|delete|undelete|rename|update|updating|updates\b|configure|"
    r"toggle|enable|disable|hide|restore|reorder|switching|switch(?:ing)?|"
    r"lifecycle|add\s+|remove\s+|patch\b|change\s+(?:delivery|tally)|"
    r"changing\s+tally|connect\s+quota|put\s+|post\s+|accept\b|"
    r"set\s+default|copy\s+channel|clears\s+all|"
    r"get\s+.+\s+by\s+(?:id|guid)\b|get\s+project\s+by\s+id\b|"
    r"get\s+exclusion\s+rule\s+by\s+id\b|get\s+partner\s+event\b(?!\s+defaults)|"
    r"fullprojectsetup|halting\s+a\s+segment"
    r")\b"
)


def class_type_hint(simple: str) -> str:
    """Weak class-name hint (legacy substring rules). Dashboard types are per-feature."""
    if "Validation" in simple:
        return "Validation"
    if "E2E" in simple or "EndToEnd" in simple:
        return "E2E"
    if "Workflow" in simple:
        return "Workflow"
    if "Lookup" in simple or "Search" in simple or "Catalog" in simple:
        return "Query"
    if "CRUD" in simple:
        return "CRUD"
    return "Other"


def load_overrides(path: Path = OVERRIDES_PATH) -> dict[str, str]:
    if not path.is_file():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"warning: could not read overrides {path}: {exc}", file=sys.stderr)
        return {}
    if not isinstance(raw, dict):
        return {}
    out: dict[str, str] = {}
    for key, value in raw.items():
        if key.startswith("_"):
            continue
        if isinstance(value, str) and value in CANONICAL_TYPES:
            out[key] = value
    return out


def override_key(spec: str, name: str) -> str:
    return f"{spec}::{name}"


def feature_corpus(name: str, steps: list[dict] | None) -> str:
    parts = [name or ""]
    for step in steps or []:
        label = step.get("label") or ""
        if label:
            parts.append(label)
    return "\n".join(parts)


def infer_feature_type(
    name: str,
    steps: list[dict] | None,
    spec: str,
    overrides: dict[str, str] | None = None,
) -> str:
    """Classify one Spock feature. Overrides win; else Validation→E2E→Workflow→Query→CRUD→Other.

    Query/CRUD prefer the feature *title* so setup/assert step labels (e.g. \"Get all IDs\")
    do not re-type a rename/reorder/update scenario as Query.
    """
    key = override_key(spec, name)
    if overrides and key in overrides:
        return overrides[key]

    name_text = name or ""
    full = feature_corpus(name, steps)
    hint = class_type_hint(spec)

    # Titles that start with "Cannot …" are validation; avoid "cannot be retrieved" in asserts.
    if (
        VALIDATION_STRONG_RE.search(name_text)
        or VALIDATION_TITLE_RE.search(name_text)
        or VALIDATION_STRONG_RE.search(full)
        or re.match(r"(?i)^cannot\b", name_text.strip())
    ):
        return "Validation"
    if E2E_RE.search(full) or (hint == "E2E" and re.search(r"(?i)\bcomplete\b", full)):
        return "E2E"
    if WORKFLOW_RE.search(full) or (
        hint == "Workflow"
        and re.search(r"(?i)\b(complete|phase|sold|lock|draft|cpi|threshold|approval)\b", full)
    ):
        return "Workflow"

    # Title-first for Query vs CRUD
    name_is_crud = bool(CRUD_RE.search(name_text))
    name_is_query = bool(QUERY_RE.search(name_text) or QUERY_GET_RE.search(name_text))
    if name_is_query and not name_is_crud:
        return "Query"
    if name_is_crud and not name_is_query:
        return "CRUD"
    if name_is_crud and name_is_query:
        # e.g. "Get project by ID" matches both get-by-id (CRUD) and get… — prefer CRUD for by-id
        if re.search(r"(?i)\bby\s+(?:id|guid)\b", name_text):
            return "CRUD"
        return "Query"

    if QUERY_RE.search(full) or QUERY_GET_RE.search(full):
        return "Query"
    if CRUD_RE.search(full):
        return "CRUD"

    if hint in ("Validation", "Query", "CRUD", "Workflow", "E2E"):
        return hint
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


STEP_RE = re.compile(
    r"^\s*(given|when|then|and):\s*(?:\"([^\"]*)\"|'([^']*)')",
    re.MULTILINE | re.IGNORECASE,
)
IGNORE_RE = re.compile(r"@Ignore\b")


def parse_steps(block: str) -> list[dict]:
    steps = []
    for m in STEP_RE.finditer(block):
        label = m.group(2) if m.group(2) is not None else m.group(3)
        steps.append({"phase": m.group(1).lower(), "label": label or ""})
    return steps


def param_note(block: str, cases: int) -> str:
    if re.search(r"<<\s*testContext\.phases", block):
        return "Unrolled across project phases (2 runs at execution)"
    if cases <= 1:
        return ""
    if re.search(r"^\s*where:\s*$", block, re.MULTILINE):
        pipe_lines = [ln for ln in block.splitlines() if "|" in ln.split("//")[0] and ln.strip()]
        if len(pipe_lines) >= 2:
            header = pipe_lines[0].split("|")[0].strip()
            if header:
                return f"{cases} runs across {header}"
    return f"{cases} parameterized runs"


def tags_before(text: str, start: int) -> list[str]:
    window = text[max(0, start - 500):start]
    matches = TESTTAGS_RE.findall(window)
    if not matches:
        return []
    raw = matches[-1]
    return [t.strip() for t in raw.split(",") if t.strip()]


def parse_spec(
    path: Path,
    module_root: Path,
    overrides: dict[str, str] | None = None,
) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace")
    mcls = CLASS_RE.search(text)
    if not mcls or not FEATURE_RE.search(text):
        return []
    simple = mcls.group(1)
    area = area_from_path(path)
    feature_anno = FEATURE_ANNO_RE.search(text)
    owner_anno = OWNER_ANNO_RE.search(text)
    feature_label = feature_anno.group(1) if feature_anno else ""
    owner = owner_anno.group(1) if owner_anno else ""
    rel = path.relative_to(module_root).as_posix()
    hint = class_type_hint(simple)

    rows = []
    starts = [(m.start(), m.group(1)) for m in FEATURE_RE.finditer(text)]
    for i, (start, name) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
        block = text[start:end]
        has_where = re.search(r"^\s*where:\s*$", block, re.MULTILINE)
        cases = static_where_rows(block) if has_where else 1
        ignored = bool(IGNORE_RE.search(text[max(0, start - 300):start]))
        steps = parse_steps(block)
        ctype = infer_feature_type(name, steps, simple, overrides)
        row = {
            "area": area,
            "spec": simple,
            "name": name,
            "type": ctype,
            "tags": tags_before(text, start),
            "owner": owner,
            "feature": feature_label,
            "cases": cases,
            "file": rel,
            "ignored": ignored,
            "steps": steps,
        }
        note = param_note(block, cases)
        if note:
            row["paramNote"] = note
        # Audit helpers (stripped before write unless --audit keeps them in memory only)
        row["_classHint"] = hint
        rows.append(row)
    return rows


def print_audit(rows: list[dict]) -> None:
    by_type = collections.Counter(r["type"] for r in rows)
    print("Type distribution (features):")
    for t in CANONICAL_TYPES:
        print(f"  {t}: {by_type.get(t, 0)}")
    extras = sorted(k for k in by_type if k not in CANONICAL_TYPES)
    for t in extras:
        print(f"  {t}: {by_type[t]}")

    disagree = [r for r in rows if r.get("_classHint") and r["_classHint"] != r["type"]]
    print(f"\nClass-hint vs feature-type disagreements: {len(disagree)}")
    # High-risk buckets first
    risk_specs = (
        "CRUD", "Lookup", "Management", "Exclusion", "Delivery", "EndToEnd",
        "ChangeOrder", "Validation", "Workflow", "E2E",
    )
    shown = 0
    for r in sorted(disagree, key=lambda x: (x["spec"], x["name"])):
        if not any(s in r["spec"] for s in risk_specs) and shown > 40:
            continue
        print(
            f"  [{r['_classHint']} → {r['type']}] {r['spec']} :: {r['name'][:90]}"
        )
        shown += 1
        if shown >= 80:
            print(f"  … truncated ({len(disagree)} total)")
            break

    other = [r for r in rows if r["type"] == "Other"]
    print(f"\nOther residual: {len(other)}")
    for r in other[:40]:
        print(f"  {r['spec']} :: {r['name'][:90]}")
    if len(other) > 40:
        print(f"  … +{len(other) - 40} more")


def collect_rows(module_root: Path, overrides: dict[str, str]) -> list[dict]:
    src_root = module_root / "src/test/groovy"
    if not src_root.is_dir():
        raise FileNotFoundError(f"spec source not found at {src_root}")
    rows: list[dict] = []
    for path in sorted(src_root.rglob("*TestSteps.groovy")):
        rows.extend(parse_spec(path, module_root, overrides))
    rows.sort(key=lambda r: (r["area"], r["spec"], r["name"]))
    return rows


def strip_audit_fields(rows: list[dict]) -> list[dict]:
    cleaned = []
    for r in rows:
        row = {k: v for k, v in r.items() if not k.startswith("_")}
        cleaned.append(row)
    return cleaned


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--module-root", type=Path, default=DEFAULT_MODULE_ROOT,
                    help="Path to the NexusApiRegressionTests module (read-only).")
    ap.add_argument(
        "--audit",
        action="store_true",
        help="Print type distribution and class-hint disagreements; do not write inventory.json.",
    )
    args = ap.parse_args()

    module_root = args.module_root.resolve()
    overrides = load_overrides()

    try:
        rows = collect_rows(module_root, overrides)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.audit:
        print_audit(rows)
        return 0

    rows = strip_audit_fields(rows)
    specs = len({(r["area"], r["spec"]) for r in rows})
    total_cases = sum(r["cases"] for r in rows)
    with_steps = sum(1 for r in rows if r.get("steps"))
    step_count = sum(len(r.get("steps") or []) for r in rows)
    by_type = collections.Counter(r["type"] for r in rows)

    result = {
        "generatedAt": dt.date.today().isoformat(),
        "source": "source",
        "features": len(rows),
        "cases": total_cases,
        "specs": specs,
        "areas": len({r["area"] for r in rows}),
        "featuresWithSteps": with_steps,
        "steps": step_count,
        "byType": dict(sorted(by_type.items(), key=lambda kv: (-kv[1], kv[0]))),
        "rows": rows,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        f"Wrote {OUT}: {len(rows)} features / {total_cases} cases across {specs} specs "
        f"({with_steps} with steps, {step_count} step labels)"
    )
    print("byType:", ", ".join(f"{k}={v}" for k, v in result["byType"].items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
