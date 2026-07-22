#!/usr/bin/env python3
"""Generate data/coverage.json for the Nexus TA Dashboard endpoint-coverage page.

Merges:
  1. OpenAPI snapshot (existence + OpenAPI deprecated flag) — source of truth for
     which endpoints exist.
  2. Curated tested/deprecated overlay from dashboard/data/endpoints-overlay.json
     — the shrinking hand-maintained bit for "is it tested?".

Also emits a risk-ranked work queue (heuristic: HTTP method weight × domain
criticality × brand-new bump) and optional inventory hygiene stats when
data/inventory.json is present.

Usage:
    python3 tools/generate_coverage.py [--module-root PATH] [--fetch-openapi]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

DASHBOARD_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODULE_ROOT = Path(os.environ.get("NEXUS_MODULE_ROOT", DASHBOARD_ROOT.parent))
OUT = DASHBOARD_ROOT / "data" / "coverage.json"
INVENTORY = DASHBOARD_ROOT / "data" / "inventory.json"

SERVER_PREFIX = "/NexusApi"
HTTP_METHODS = {"get", "put", "post", "delete", "patch", "head", "options"}
OPENAPI_URL = "https://microservices-qa.dynata.com/NexusApi/swagger.json/Unified%20Api"

# Crude criticality: mutating > read; core product domains > edge.
METHOD_WEIGHT = {
    "DELETE": 4.0,
    "PUT": 3.5,
    "POST": 3.0,
    "PATCH": 3.0,
    "GET": 1.5,
    "HEAD": 1.0,
    "OPTIONS": 1.0,
}
CORE_PATH_FRAGMENTS = (
    "/projects/",
    "/quotaGroups/",
    "/quotas",
    "/audience",
    "/segments",
    "/feasibility",
    "/urlPools/",
    "/fieldwork",
)


def load_openapi(path: Path) -> tuple[list[dict], dict]:
    spec = json.loads(path.read_text(encoding="utf-8"))
    endpoints = []
    for raw_path, item in spec.get("paths", {}).items():
        if not isinstance(item, dict):
            continue
        full = SERVER_PREFIX + raw_path
        for method, op in item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(op, dict):
                continue
            tags = op.get("tags") or ["(untagged)"]
            endpoints.append({
                "m": method.upper(),
                "p": full,
                "tag": tags[0],
                "dOpenApi": bool(op.get("deprecated", False)),
                "operationId": op.get("operationId"),
            })
    info = spec.get("info") or {}
    return endpoints, {"title": info.get("title"), "version": info.get("version")}


def load_curated_overlay(path: Path) -> dict:
    if not path.exists():
        return {}
    by_cat = json.loads(path.read_text(encoding="utf-8"))
    overlay = {}
    for entries in by_cat.values():
        for e in entries:
            overlay[(e["m"].upper(), e["p"])] = {
                "t": bool(e.get("t")),
                "d": bool(e.get("d")),
            }
    return overlay


def fetch_openapi(dest: Path) -> None:
    print(f"Fetching {OPENAPI_URL} …")
    with urllib.request.urlopen(OPENAPI_URL, timeout=60) as resp:
        body = resp.read()
    json.loads(body)
    dest.write_bytes(body)
    print(f"Wrote {dest} ({len(body)} bytes)")


def domain_weight(path: str) -> float:
    pl = path.lower()
    if any(frag.lower() in pl for frag in CORE_PATH_FRAGMENTS):
        return 1.6
    return 1.0


def risk_score(method: str, path: str, gap: str | None) -> float:
    base = METHOD_WEIGHT.get(method.upper(), 1.0) * domain_weight(path)
    if gap == "new":
        base *= 1.25  # brand-new = surprise drift, prioritize slightly
    return round(base, 2)


def risk_band(score: float) -> str:
    if score >= 5.0:
        return "high"
    if score >= 3.0:
        return "medium"
    return "low"


def inventory_hygiene(path: Path) -> dict | None:
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("rows") or []
    if not rows:
        return None
    untagged = sum(1 for r in rows if not r.get("tags"))
    ignored = sum(1 for r in rows if r.get("ignored"))
    by_type: dict[str, int] = {}
    for r in rows:
        by_type[r.get("type") or "Other"] = by_type.get(r.get("type") or "Other", 0) + 1
    return {
        "features": len(rows),
        "cases": data.get("cases"),
        "untagged": untagged,
        "untaggedPercent": round(untagged / len(rows) * 100.0, 1),
        "ignored": ignored,
        "byType": dict(sorted(by_type.items(), key=lambda kv: (-kv[1], kv[0]))),
        "source": "dashboard/data/inventory.json",
        "generatedAt": data.get("generatedAt"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--module-root", type=Path, default=DEFAULT_MODULE_ROOT)
    ap.add_argument("--fetch-openapi", action="store_true",
                    help="Refresh docs/openapi-nexus-unified-api-qa.json from live QA.")
    args = ap.parse_args()

    module_root = args.module_root.resolve()
    openapi_path = module_root / "docs/openapi-nexus-unified-api-qa.json"
    overlay_path = module_root / "dashboard/data/endpoints-overlay.json"

    if args.fetch_openapi:
        try:
            fetch_openapi(openapi_path)
        except Exception as exc:  # noqa: BLE001
            print(f"error: failed to fetch OpenAPI: {exc}", file=sys.stderr)
            return 1

    if not openapi_path.is_file():
        print(f"error: OpenAPI snapshot missing at {openapi_path}", file=sys.stderr)
        return 1

    api, openapi_info = load_openapi(openapi_path)
    overlay = load_curated_overlay(overlay_path)
    api_keys = {(e["m"], e["p"]) for e in api}

    categories: dict[str, list] = {}
    tested = non_dep = deprecated = 0
    d_openapi = d_overlay_only = 0
    brand_new: list[dict] = []
    known_untested: list[dict] = []
    queue: list[dict] = []
    mutating_gaps = 0

    for e in sorted(api, key=lambda x: (x["tag"], x["p"], x["m"])):
        key = (e["m"], e["p"])
        curated = overlay.get(key)
        t = bool(curated["t"]) if curated else False
        d_oa = e["dOpenApi"]
        d_ov = bool(curated["d"]) if curated else False
        d = d_oa or d_ov
        if d_oa:
            d_openapi += 1
        elif d_ov:
            d_overlay_only += 1

        if curated is None and not d:
            gap = "new"
        elif curated is not None and not t and not d:
            gap = "known"
        else:
            gap = None

        score = risk_score(e["m"], e["p"], gap) if not d and not t else 0.0
        band = risk_band(score) if score else None

        if d:
            status = "deprecated"
            deprecated += 1
        elif t:
            status = "tested"
            non_dep += 1
            tested += 1
        else:
            status = "untested"
            non_dep += 1
            if e["m"] in {"POST", "PUT", "PATCH", "DELETE"}:
                mutating_gaps += 1
            item = {
                "m": e["m"],
                "p": e["p"],
                "category": e["tag"],
                "gap": gap,
                "risk": score,
                "riskBand": band,
                "operationId": e.get("operationId"),
            }
            queue.append(item)
            if gap == "new":
                brand_new.append(item)
            else:
                known_untested.append(item)

        categories.setdefault(e["tag"], []).append({
            "m": e["m"],
            "p": e["p"],
            "t": t,
            "d": d,
            "status": status,
            "gap": gap,
            "risk": score if status == "untested" else None,
            "riskBand": band if status == "untested" else None,
            "deprecatedSource": (
                "openapi" if d_oa else ("overlay" if d_ov else None)
            ),
        })

    stale = [
        {"m": m, "p": p}
        for (m, p) in sorted(k for k in overlay if k not in api_keys)
    ]
    coverage = (tested / non_dep * 100.0) if non_dep else 0.0

    # Work queue: highest risk first, brand-new before known on ties
    queue.sort(key=lambda x: (-x["risk"], 0 if x["gap"] == "new" else 1, x["p"], x["m"]))
    brand_new.sort(key=lambda x: (-x["risk"], x["p"], x["m"]))
    known_untested.sort(key=lambda x: (-x["risk"], x["p"], x["m"]))

    cat_rows = []
    for name, endpoints in categories.items():
        t_n = sum(1 for ep in endpoints if ep["status"] == "tested")
        u_n = sum(1 for ep in endpoints if ep["status"] == "untested")
        d_n = sum(1 for ep in endpoints if ep["status"] == "deprecated")
        denom = t_n + u_n
        max_risk = max((ep.get("risk") or 0) for ep in endpoints) if u_n else 0
        cat_rows.append({
            "name": name,
            "tested": t_n,
            "untested": u_n,
            "deprecated": d_n,
            "coveragePercent": round((t_n / denom * 100.0), 1) if denom else 100.0,
            "maxGapRisk": max_risk or None,
            "endpoints": endpoints,
        })
    cat_rows.sort(key=lambda c: (
        0 if c["untested"] else 1,
        -(c["maxGapRisk"] or 0),
        c["coveragePercent"],
        c["name"].lower(),
    ))

    hygiene = inventory_hygiene(INVENTORY)
    mtime = dt.datetime.fromtimestamp(openapi_path.stat().st_mtime, tz=dt.timezone.utc)

    result = {
        "generatedAt": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "source": {
            "openapi": "docs/openapi-nexus-unified-api-qa.json",
            "openapiUrl": OPENAPI_URL,
            "openapiInfo": openapi_info,
            "openapiFileMtimeUtc": mtime.strftime("%Y-%m-%dT%H:%MZ"),
            "overlay": "dashboard/data/endpoints-overlay.json",
            "methodology": (
                "Existence from OpenAPI paths×methods. Tested flag from curated overlay "
                "(t). Deprecated = OpenAPI deprecated OR overlay d. Coverage % = "
                "tested / non-deprecated only. Brand-new = in OpenAPI, not in overlay; "
                "known-untested = overlay t:false. Risk = method weight × domain weight "
                "× brand-new bump (heuristic until Honeycomb traffic is wired)."
            ),
            "riskNote": (
                "Heuristic only — DELETE/PUT/POST on core Project/QuotaGroup paths rank "
                "higher. Not traffic-weighted yet."
            ),
        },
        "summary": {
            "operations": len(api),
            "nonDeprecated": non_dep,
            "deprecated": deprecated,
            "deprecatedFromOpenApi": d_openapi,
            "deprecatedFromOverlayOnly": d_overlay_only,
            "tested": tested,
            "untested": len(queue),
            "coveragePercent": round(coverage, 1),
            "brandNew": len(brand_new),
            "knownUntested": len(known_untested),
            "stale": len(stale),
            "mutatingGaps": mutating_gaps,
            "highRiskGaps": sum(1 for g in queue if g["riskBand"] == "high"),
        },
        "queue": queue,
        "categories": cat_rows,
        "gaps": {
            "brandNew": brand_new,
            "knownUntested": known_untested,
            "stale": stale,
        },
        "dataQuality": {
            "overlayOnlyDeprecated": d_overlay_only,
            "openapiDeprecated": d_openapi,
            "staleOverlayEntries": len(stale),
            "handTrackedUntested": len(known_untested),
            "untrackedNew": len(brand_new),
            "inventory": hygiene,
        },
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    s = result["summary"]
    print(
        f"Wrote {OUT}: {s['coveragePercent']}% "
        f"({s['tested']}/{s['nonDeprecated']}) "
        f"gap={s['untested']} (new={s['brandNew']}, known={s['knownUntested']}) "
        f"highRisk={s['highRiskGaps']} mutating={s['mutatingGaps']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
