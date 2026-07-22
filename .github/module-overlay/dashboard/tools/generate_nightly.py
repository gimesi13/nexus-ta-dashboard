#!/usr/bin/env python3
"""Generate data/nightly.json for the Nexus TA Dashboard Nightly Run page.

Does **not** call TeamCity itself. Prefers the REST summary written by
``automation/tc_fetch_nightly.py``:

  automation/tc_fetch_nightly.py  ->  ta-runtime/.last-tc-nightly.json

Fallbacks (weaker): JUnit under build/test-results/test, then
ta-runtime/test-results.json from generate_digest.py.

Usage:
    python3 tools/generate_nightly.py [--module-root PATH]

Always writes nightly.json (available=true|false) so the site never 404s.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote

DASHBOARD_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODULE_ROOT = Path(
    os.environ.get("NEXUS_MODULE_ROOT", DASHBOARD_ROOT.parent)
)
OUT = DASHBOARD_ROOT / "data" / "nightly.json"
FAILED_CAP = 80
DEFAULT_BUILD_TYPE = (
    "Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_"
    "CompileUnitTestAndGeneratePactsAndSt"
)


def _iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def _load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _short_name(case_id: str) -> str:
    if "::" in case_id:
        return case_id.split("::", 1)[1]
    return case_id


def _parse_fqcn_dot_feature(raw: str) -> tuple[str, str]:
    raw = (raw or "").strip()
    m = re.match(
        r"^(?P<fqcn>.+\.(?P<short>\w+TestSteps))\.(?P<feat>.+)$",
        raw,
    )
    if m:
        return m.group("fqcn"), m.group("feat").strip()
    m = re.match(
        r"^(?P<fqcn>(?:[a-z]\w*\.)+[A-Z]\w*)\.(?P<feat>.+)$",
        raw,
    )
    if not m:
        return "", raw
    fqcn, feat = m.group("fqcn"), m.group("feat").strip()
    m2 = re.match(r"^(?P<short>\w+TestSteps)\.(?P<feat>.+)$", feat)
    if m2:
        return f"{fqcn}.{m2.group('short')}", m2.group("feat").strip()
    short = fqcn.rsplit(".", 1)[-1]
    if short.endswith("TestSteps") or " " in feat:
        return fqcn, feat
    return "", raw


def _normalize_occurrence(classname: str, name: str) -> tuple[str, str]:
    """Re-parse stored TC rows that still have FQCN / class jammed into name."""
    classname = classname or ""
    name = name or ""
    # Class peeled into package, feature still "FooTestSteps.…"
    m = re.match(r"^(?P<short>\w+TestSteps)\.(?P<feat>.+)$", name)
    if m and not classname.endswith("TestSteps"):
        short = m.group("short")
        classname = f"{classname}.{short}" if classname else short
        name = m.group("feat")
    if not classname.endswith("TestSteps") and (
        name.startswith("com.") or name.startswith("org.")
    ):
        classname, name = _parse_fqcn_dot_feature(name)
    elif not classname and (name.startswith("com.") or name.startswith("org.")):
        classname, name = _parse_fqcn_dot_feature(name)
    name = _clean_feature_name(name, classname)
    if name.startswith("com.") or name.startswith("org."):
        classname, name = _parse_fqcn_dot_feature(name)
        name = _clean_feature_name(name, classname)
    return classname, name


def _clean_feature_name(name: str, classname: str = "") -> str:
    name = (name or "").strip()
    name = re.sub(r"\s*\[[^\]]*\]\s*$", "", name).strip()
    if ": com." in name or ": org." in name:
        name = re.split(r":\s+(?:com|org)\.", name, maxsplit=1)[0].strip()
    short = classname.rsplit(".", 1)[-1] if classname else ""
    if short and name.startswith(short + "."):
        name = name[len(short) + 1 :].strip()
    if classname and name.startswith(classname + "."):
        name = name[len(classname) + 1 :].strip()
    # Still looks like package.Class.feature
    if name.startswith("com.") or name.startswith("org."):
        _, peeled = _parse_fqcn_dot_feature(name)
        if peeled and peeled != name:
            name = peeled
    return name


def _match_inventory(classname: str, name: str, rows: list) -> dict | None:
    classname, cleaned = _normalize_occurrence(classname, name)
    short = classname.rsplit(".", 1)[-1] if classname else ""
    if not short or not cleaned:
        return None
    same_spec = [r for r in rows if r.get("spec") == short]
    for r in same_spec:
        if r.get("name") == cleaned:
            return r
    for r in same_spec:
        rn = r.get("name") or ""
        if cleaned.startswith(rn) or rn.startswith(cleaned):
            return r
    # Loose: unique prefix match of first 40 chars within spec
    prefix = cleaned[:40]
    hits = [r for r in same_spec if (r.get("name") or "").startswith(prefix)]
    if len(hits) == 1:
        return hits[0]
    return None


_STATUS_RANK = {"failed": 0, "muted": 1, "ignored": 2, "passed": 3}


def _worse(a: str | None, b: str) -> str:
    if a is None:
        return b
    return a if _STATUS_RANK.get(a, 9) <= _STATUS_RANK.get(b, 9) else b


def _build_status_by_case(occurrences: list, rows: list) -> dict:
    """Map inventory caseKey -> worst status across parameterized TC runs."""
    by_case: dict[str, str] = {}
    by_spec_name: dict[str, str] = {}
    for o in occurrences or []:
        classname, name = _normalize_occurrence(
            o.get("classname") or "", o.get("name") or ""
        )
        status = o.get("status") or "passed"
        match = _match_inventory(classname, name, rows)
        if match:
            key = f"{match.get('area')}::{match.get('spec')}::{match.get('name')}"
            by_case[key] = _worse(by_case.get(key), status)
        short = classname.rsplit(".", 1)[-1] if classname else ""
        cleaned = _clean_feature_name(name, classname)
        if short and cleaned:
            sn = f"{short}::{cleaned}"
            by_spec_name[sn] = _worse(by_spec_name.get(sn), status)
    return {"byCase": by_case, "bySpecName": by_spec_name}


def _attach_inventory(failed: list, module_root: Path) -> list:
    inv = _load_json(DASHBOARD_ROOT / "data" / "inventory.json", {})
    rows = inv.get("rows") or []
    out = []
    for f in failed:
        classname = f.get("classname") or ""
        name = f.get("name") or ""
        cleaned = _clean_feature_name(name, classname)
        match = _match_inventory(classname, cleaned or name, rows)
        item = {
            "id": f.get("id") or "",
            "classname": classname,
            "name": (match.get("name") if match else cleaned) or name,
            "durationMs": f.get("durationMs"),
            "newFailure": bool(f.get("newFailure")),
        }
        if match:
            item["area"] = match.get("area")
            item["spec"] = match.get("spec")
            item["caseKey"] = (
                f"{match.get('area')}::{match.get('spec')}::{match.get('name')}"
            )
            item["inventoryHref"] = (
                "inventory.html?run=failed&case=" + quote(item["caseKey"])
            )
        else:
            short = classname.rsplit(".", 1)[-1] if classname else ""
            q = cleaned or name
            item["spec"] = short or None
            item["inventoryHref"] = (
                "inventory.html?run=failed&q=" + quote(q) if q
                else "inventory.html?run=failed"
            )
        out.append(item)
    return out


def _from_tc_nightly(module_root: Path):
    raw = _load_json(module_root / "ta-runtime" / ".last-tc-nightly.json", None)
    if not raw or not raw.get("buildId"):
        return None
    summary = raw.get("summary") or {}
    inv = _load_json(DASHBOARD_ROOT / "data" / "inventory.json", {})
    rows = inv.get("rows") or []
    failed = _attach_inventory(list(raw.get("failed") or [])[:FAILED_CAP], module_root)
    status_maps = _build_status_by_case(raw.get("occurrences") or [], rows)
    return {
        "source": "teamcity-rest",
        "build": {
            "buildTypeId": raw.get("buildTypeId") or DEFAULT_BUILD_TYPE,
            "buildId": raw.get("buildId"),
            "number": raw.get("number"),
            "status": raw.get("status"),
            "state": raw.get("state"),
            "statusText": raw.get("statusText"),
            "webUrl": raw.get("webUrl"),
            "buildsUrl": raw.get("buildsUrl"),
            "branchName": raw.get("branchName"),
            "startDate": raw.get("startDate"),
            "finishDate": raw.get("finishDate"),
        },
        "summary": {
            "tests": summary.get("tests", 0),
            "passed": summary.get("passed", 0),
            "failures": summary.get("failures", 0),
            "errors": summary.get("errors", 0),
            "skipped": summary.get("skipped", 0),
            "muted": summary.get("muted", 0),
            "newFailed": summary.get("newFailed", 0),
            "timeSec": summary.get("timeSec") or raw.get("durationSec"),
            "passRate": summary.get("passRate", 0),
        },
        "failed": failed,
        "failedTruncated": raw.get("failedTruncated", 0),
        "statusByCase": status_maps["byCase"],
        "statusBySpecName": status_maps["bySpecName"],
    }


def _from_junit(module_root: Path):
    sys.path.insert(0, str(module_root / "automation"))
    from _common import parse_junit_dir  # noqa: E402

    results_dir = module_root / "build" / "test-results" / "test"
    summary, files = parse_junit_dir(str(results_dir))
    if not files:
        return None

    failed_cases = [c for c in summary.cases if c.status in ("failed", "error")]
    failed_raw = []
    for c in failed_cases[:FAILED_CAP]:
        failed_raw.append({
            "id": c.id,
            "name": c.name,
            "classname": c.classname,
            "durationMs": int(c.time * 1000) if c.time else None,
        })
    failed = _attach_inventory(failed_raw, module_root)
    build = _load_json(module_root / "ta-runtime" / ".last-tc-build.json", {}) or {}
    tests = summary.tests or 0
    pass_rate = round((summary.passed / tests) * 100.0, 1) if tests else 0.0
    return {
        "source": "junit",
        "build": {
            "buildTypeId": build.get("buildTypeId") or DEFAULT_BUILD_TYPE,
            "buildId": build.get("buildId"),
            "number": build.get("number"),
            "status": build.get("status"),
            "state": build.get("state"),
            "webUrl": build.get("webUrl"),
            "buildsUrl": (
                "https://teamcity.dynata.com/buildConfiguration/"
                f"{build.get('buildTypeId') or DEFAULT_BUILD_TYPE}?mode=builds"
            ),
            "branchName": build.get("branchName"),
            "startDate": build.get("startDate"),
            "finishDate": build.get("finishDate"),
        } if build else None,
        "summary": {
            "tests": tests,
            "passed": summary.passed,
            "failures": summary.failures,
            "errors": summary.errors,
            "skipped": summary.skipped,
            "muted": 0,
            "newFailed": 0,
            "timeSec": round(summary.time, 1),
            "passRate": pass_rate,
        },
        "failed": failed,
        "failedTruncated": max(0, len(failed_cases) - len(failed)),
    }


def _from_digest(module_root: Path):
    digest = _load_json(module_root / "ta-runtime" / "test-results.json", None)
    if not digest or not digest.get("tests"):
        return None
    failed_ids = digest.get("failed") or []
    failed_raw = [
        {
            "id": cid,
            "name": _short_name(cid),
            "classname": cid.split("::", 1)[0],
        }
        for cid in failed_ids[:FAILED_CAP]
    ]
    failed = _attach_inventory(failed_raw, module_root)
    tests = digest.get("tests", 0) or 0
    pass_rate = round((digest.get("passed", 0) / tests) * 100.0, 1) if tests else 0.0
    build = _load_json(module_root / "ta-runtime" / ".last-tc-build.json", {}) or {}
    return {
        "source": "digest",
        "build": {
            "buildTypeId": build.get("buildTypeId") or DEFAULT_BUILD_TYPE,
            "buildId": build.get("buildId"),
            "number": build.get("number"),
            "status": build.get("status"),
            "state": build.get("state"),
            "webUrl": build.get("webUrl"),
            "buildsUrl": (
                "https://teamcity.dynata.com/buildConfiguration/"
                f"{build.get('buildTypeId') or DEFAULT_BUILD_TYPE}?mode=builds"
            ),
            "branchName": build.get("branchName"),
        } if build else None,
        "summary": {
            "tests": tests,
            "passed": digest.get("passed", 0),
            "failures": digest.get("failures", 0),
            "errors": digest.get("errors", 0),
            "skipped": digest.get("skipped", 0),
            "muted": 0,
            "newFailed": 0,
            "timeSec": digest.get("time", 0),
            "passRate": pass_rate,
        },
        "failed": failed,
        "failedTruncated": max(0, len(failed_ids) - len(failed)),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--module-root", default=str(DEFAULT_MODULE_ROOT))
    args = ap.parse_args()
    module_root = Path(args.module_root).resolve()

    stats = (
        _from_tc_nightly(module_root)
        or _from_junit(module_root)
        or _from_digest(module_root)
    )

    if not stats:
        payload = {
            "available": False,
            "generatedAt": _iso_now(),
            "message": (
                "No TeamCity nightly summary yet. "
                "Run: python3 automation/tc_fetch_nightly.py && "
                "python3 dashboard/tools/generate_nightly.py"
            ),
            "build": None,
            "summary": None,
            "failed": [],
        }
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {OUT}: available=false (no results)")
        return 0

    s = stats["summary"]
    build = stats.get("build") or {}
    fail_n = (s.get("failures") or 0) + (s.get("errors") or 0)

    payload = {
        "available": True,
        "generatedAt": _iso_now(),
        "source": stats["source"],
        "build": build or None,
        "summary": s,
        "failed": stats["failed"],
        "failedTruncated": stats.get("failedTruncated", 0),
        "statusByCase": stats.get("statusByCase") or {},
        "statusBySpecName": stats.get("statusBySpecName") or {},
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        f"Wrote {OUT}: available=true tests={s.get('tests')} "
        f"fail={fail_n} passRate={s.get('passRate')}% source={stats['source']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
