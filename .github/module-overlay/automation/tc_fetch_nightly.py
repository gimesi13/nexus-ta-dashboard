#!/usr/bin/env python3
"""Fetch the latest TeamCity nightly build summary for the TA dashboard.

Writes ``test-coverage-report/.last-tc-nightly.json`` (and refreshes
``.last-tc-build.json``) from the TeamCity REST API — counts + non-muted
failures. Does not rely on JUnit artifacts (those are often incomplete).

Default build type (latest finished build on this config):
  Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_CompileUnitTestAndGeneratePactsAndSt

Env:
  TEAMCITY_URL, TEAMCITY_TOKEN
  TEAMCITY_NIGHTLY_BUILD_TYPE_ID  (optional override)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BUILD_TYPE = (
    "Dk_Microservices_UnifiedApi_NexusApiRegressionGeriTestsJ16_"
    "CompileUnitTestAndGeneratePactsAndSt"
)
OUT = MODULE_ROOT / "test-coverage-report" / ".last-tc-nightly.json"
META = MODULE_ROOT / "test-coverage-report" / ".last-tc-build.json"
FAILED_CAP = 80
OCC_PAGE = 200


def _tc_get(base: str, token: str, path: str, params: dict | None = None) -> dict:
    qs = urllib.parse.urlencode(params or {})
    url = f"{base.rstrip('/')}{path}"
    if qs:
        url = f"{url}?{qs}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.load(resp)


def _tc_get_href(base: str, token: str, href: str) -> dict:
    """Follow a TeamCity nextHref (absolute path + query)."""
    if href.startswith("http"):
        url = href
    else:
        url = f"{base.rstrip('/')}{href}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.load(resp)


def _classify(item: dict) -> str:
    if item.get("ignored"):
        return "ignored"
    status = (item.get("status") or "").upper()
    if status == "FAILURE" and item.get("muted"):
        return "muted"
    if status == "FAILURE":
        return "failed"
    if status == "SUCCESS":
        return "passed"
    if status == "UNKNOWN":
        return "ignored"
    return "passed"


def _fetch_all_occurrences(base: str, token: str, build_id: str) -> list[dict]:
    """Paginate every test occurrence for the build (compact fields)."""
    data = _tc_get(
        base,
        token,
        "/app/rest/testOccurrences",
        {
            "locator": f"build:(id:{build_id}),count:{OCC_PAGE}",
            "fields": (
                "count,nextHref,"
                "testOccurrence(id,name,status,muted,ignored,duration,newFailure,"
                "test(id))"
            ),
        },
    )
    out: list[dict] = []
    while True:
        batch = data.get("testOccurrence") or []
        if isinstance(batch, dict):
            batch = [batch]
        for item in batch:
            classname, name = _parse_name(item.get("name") or "")
            test_meta = item.get("test") or {}
            out.append({
                "classname": classname,
                "name": name,
                "status": _classify(item),
                "durationMs": item.get("duration"),
                "newFailure": bool(item.get("newFailure")),
                "occurrenceId": item.get("id") or "",
                "testId": str(test_meta.get("id") or ""),
            })
        nxt = data.get("nextHref")
        if not nxt or not batch:
            break
        data = _tc_get_href(base, token, nxt)
    return out


def _parse_fqcn_dot_feature(raw: str) -> tuple[str, str]:
    """Parse ``com…ClassName.feature title`` (no colon) — common for ignored/SUCCESS.

    Prefer a ``*TestSteps`` class segment so package folders like ``.QuotaGroup.``
    are not mistaken for the class name.
    """
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
    # Name still starts with XxxTestSteps. — class was left in the feature part
    m2 = re.match(r"^(?P<short>\w+TestSteps)\.(?P<feat>.+)$", feat)
    if m2:
        return f"{fqcn}.{m2.group('short')}", m2.group("feat").strip()
    short = fqcn.rsplit(".", 1)[-1]
    if short.endswith("TestSteps") or " " in feat:
        return fqcn, feat
    return "", raw


def _parse_name(raw: str) -> tuple[str, str]:
    """Split TeamCity occurrence name into (fqcn, feature title).

    TC often emits:
      Feature: com…Class.Feature [phase: QUOTE, #0]
      com…Class: Feature
      com…Class.Feature title   (no colon)
    """
    raw = (raw or "").strip()
    # "com.foo.Bar: feature title…"
    if re.match(r"^[\w.$]+:\s+", raw):
        cls, name = raw.split(":", 1)
        name = name.strip()
    elif ": " in raw:
        # "Feature title: com.foo.Bar.Feature title [where]"
        left, right = raw.split(": ", 1)
        if right.startswith("com.") or right.startswith("org."):
            m = re.match(r"^([\w.$]+)\.(.+)$", right)
            if m and m.group(1).split(".")[-1][:1].isupper():
                cls = m.group(1)
                name = left.strip()
            else:
                cls, name = "", left.strip()
        else:
            cls, name = left.strip(), right.strip()
    else:
        cls, name = _parse_fqcn_dot_feature(raw)
        if not cls:
            cls, name = "", raw

    short = cls.rsplit(".", 1)[-1] if cls else ""
    # Drop trailing where-block / iteration markers
    name = re.sub(r"\s*\[[^\]]*\]\s*$", "", name).strip()
    if short and name.startswith(short + "."):
        name = name[len(short) + 1 :].strip()
    if cls and name.startswith(cls + "."):
        name = name[len(cls) + 1 :].strip()
    # Name still looks like fqcn.feature — peel again
    if not cls or (name.startswith("com.") or name.startswith("org.")):
        cls2, name2 = _parse_fqcn_dot_feature(name if name.startswith("com.") else raw)
        if cls2:
            return cls2, re.sub(r"\s*\[[^\]]*\]\s*$", "", name2).strip()
    return cls, name


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--build-type-id",
        default=os.environ.get("TEAMCITY_NIGHTLY_BUILD_TYPE_ID") or DEFAULT_BUILD_TYPE,
    )
    args = ap.parse_args()

    base = os.environ.get("TEAMCITY_URL", "https://teamcity.dynata.com")
    token = os.environ.get("TEAMCITY_TOKEN", "")
    if not token:
        print("TEAMCITY_TOKEN unset; cannot fetch nightly summary.", file=sys.stderr)
        return 1

    try:
        # Always the latest finished build on this config (pass or fail).
        latest = _tc_get(
            base,
            token,
            f"/app/rest/buildTypes/id:{args.build_type_id}/builds",
            {
                "locator": "count:1,state:finished",
                "fields": (
                    "build(id,number,status,state,webUrl,branchName,"
                    "startDate,finishDate,statusText,"
                    "testOccurrences(count,passed,failed,muted,ignored,newFailed))"
                ),
            },
        )
    except urllib.error.HTTPError as e:
        print(f"TeamCity HTTP {e.code}: {e.reason}", file=sys.stderr)
        return 1

    builds = latest.get("build") or []
    if not builds:
        print(f"No finished builds for {args.build_type_id}", file=sys.stderr)
        return 1
    build = builds[0] if isinstance(builds, list) else builds
    build_id = str(build["id"])
    occ = build.get("testOccurrences") or {}

    try:
        occurrences = _fetch_all_occurrences(base, token, build_id)
    except urllib.error.HTTPError as e:
        print(f"TeamCity occurrences HTTP {e.code}: {e.reason}", file=sys.stderr)
        occurrences = []

    failed = []
    for item in occurrences:
        if item.get("status") != "failed":
            continue
        if len(failed) >= FAILED_CAP:
            break
        test_id = item.get("testId") or ""
        teamcity_url = ""
        if test_id:
            teamcity_url = (
                f"{base.rstrip('/')}/viewLog.html?buildId={build_id}"
                f"&tab=buildResultsDiv&testNameId={urllib.parse.quote(str(test_id), safe='')}"
            )
        failed.append({
            "id": (
                f"{item['classname']}::{item['name']}"
                if item.get("classname") else item.get("name")
            ),
            "classname": item.get("classname") or "",
            "name": item.get("name") or "",
            "durationMs": item.get("durationMs"),
            "newFailure": bool(item.get("newFailure")),
            "testId": test_id,
            "teamcityUrl": teamcity_url,
        })

    passed = int(occ.get("passed") or 0)
    failures = int(occ.get("failed") or 0)
    muted = int(occ.get("muted") or 0)
    ignored = int(occ.get("ignored") or 0)
    total = int(occ.get("count") or (passed + failures + muted + ignored))
    # TeamCity "count" includes muted/ignored; pass rate over executed non-muted
    executed = passed + failures
    pass_rate = round((passed / executed) * 100.0, 1) if executed else 0.0

    # Duration from start/finish if present (TeamCity format YYYYMMDDTHHMMSS+ZZZZ)
    duration_sec = None
    start, finish = build.get("startDate"), build.get("finishDate")
    if start and finish and len(start) >= 15 and len(finish) >= 15:
        try:
            from datetime import datetime

            def parse_tc(s: str):
                # 20260717T053004+0000
                return datetime.strptime(s[:15], "%Y%m%dT%H%M%S")

            duration_sec = (parse_tc(finish) - parse_tc(start)).total_seconds()
        except ValueError:
            duration_sec = None

    payload = {
        "buildTypeId": args.build_type_id,
        "buildId": build_id,
        "number": build.get("number"),
        "status": build.get("status"),
        "state": build.get("state"),
        "statusText": build.get("statusText"),
        "webUrl": build.get("webUrl"),
        "buildsUrl": (
            f"{base.rstrip('/')}/buildConfiguration/{args.build_type_id}?mode=builds"
        ),
        "branchName": build.get("branchName"),
        "startDate": start,
        "finishDate": finish,
        "durationSec": duration_sec,
        "summary": {
            "tests": total,
            "passed": passed,
            "failures": failures,
            "errors": 0,
            "skipped": ignored,
            "muted": muted,
            "newFailed": int(occ.get("newFailed") or 0),
            "passRate": pass_rate,
            "timeSec": duration_sec,
        },
        "failed": failed,
        "failedTruncated": max(
            0, sum(1 for o in occurrences if o.get("status") == "failed") - len(failed)
        ),
        "occurrences": occurrences,
        "source": "teamcity-rest",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    META.write_text(
        json.dumps(
            {
                "buildTypeId": args.build_type_id,
                "buildId": build_id,
                "number": build.get("number"),
                "status": build.get("status"),
                "state": build.get("state"),
                "webUrl": build.get("webUrl"),
                "branchName": build.get("branchName"),
                "startDate": start,
                "finishDate": finish,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        f"Wrote {OUT}: build #{payload['number']} status={payload['status']} "
        f"passed={passed} failed={failures} muted={muted} ignored={ignored} "
        f"occurrences={len(occurrences)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
