#!/usr/bin/env python3
"""Investigate the latest nightly and write a shared nutshell review.

Focus: **new** unmuted failures — what type, which areas, and which build
changes likely explain them (path ↔ failing package correlation). Never invent
authors or root causes.

Writes:
  dashboard/data/nightly.json          → merges ``nutshell`` (short + detail)
  dashboard/data/nightly-evidence.json → compact pack for the GHA LLM rewrite
  test-coverage-report/nightly-nutshell.md   → short (Teams / overview)
  test-coverage-report/nightly-nutshell.json

Surfaces:
  - Overview + Teams → short (headline, investigation, ≤4 cause bullets)
  - Nightly page → detail (longer investigation + area / cause breakdown)

No redundant KPIs (pass %, duration, build #) — those live in the dashboard cards.

Usage:
  python3 automation/generate_nutshell.py
  python3 automation/generate_nutshell.py --merge-nightly
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from collections import Counter
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
TC_NIGHTLY = MODULE_ROOT / "test-coverage-report" / ".last-tc-nightly.json"
FAILURE_DETAILS = MODULE_ROOT / "test-coverage-report" / ".last-tc-failure-details.json"
NIGHTLY_JSON = MODULE_ROOT / "dashboard" / "data" / "nightly.json"
EVIDENCE_JSON = MODULE_ROOT / "dashboard" / "data" / "nightly-evidence.json"
OUT_MD = MODULE_ROOT / "test-coverage-report" / "nightly-nutshell.md"
OUT_JSON = MODULE_ROOT / "test-coverage-report" / "nightly-nutshell.json"

_MAX_FAILURES = 50
_MAX_DETAIL_CHARS = 400
_MAX_CHANGES = 10


def _iso_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")


def _load(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _classify_message(msg: str, details: str) -> str:
    blob = f"{msg or ''}\n{details or ''}"
    if "502" in blob or "Bad Gateway" in blob:
        return "infra_502"
    if "504" in blob or "Gateway Time-out" in blob or "Gateway Timeout" in blob:
        return "infra_504"
    if (
        "SocketTimeoutException" in blob
        or "RetryableException:timeout" in blob
        or "feign.RetryableException" in blob and "timeout" in blob.lower()
    ):
        return "infra_timeout"
    if "Unsupported country-language" in blob:
        return "product_data_country_lang"
    if "defaultCountries" in blob:
        return "flaky_settings"
    if "soft launch quota" in blob.lower() and "tally" in blob.lower():
        return "test_setup_soft_launch"
    if "Expected exception" in blob and "no exception was thrown" in blob:
        return "stale_validation"
    if "NOT_FOUND" in blob or "NotFoundInDb" in blob:
        return "product_data_not_found"
    if "EmptyResultDataAccessException" in blob:
        return "product_data_not_found"
    if "ValidationException" in blob or "jakarta.validation" in blob:
        return "validation_exception"
    if (
        "NestedServletException" in blob
        or "Handler dispatch failed" in blob
        or "NullPointerException" in blob
        or "IndexOutOfBoundsException" in blob
    ):
        return "server_exception"
    if "Condition not satisfied" in blob or "Condition failed" in blob:
        return "assert_fail"
    return "other"


_CLUSTER_LABELS = {
    "infra_502": "QA 502 Bad Gateway",
    "infra_504": "QA 504 timeout",
    "infra_timeout": "client/Feign socket timeout",
    "product_data_country_lang": "GB + fr unsupported",
    "flaky_settings": "Settings defaultCountries lag",
    "test_setup_soft_launch": "PES soft-launch vs tally",
    "stale_validation": "stale negative validation",
    "product_data_not_found": "NOT_FOUND / missing data",
    "validation_exception": "API ValidationException",
    "server_exception": "server NestedServletException / NPE",
    "assert_fail": "assertion Condition not satisfied",
    "other": "other",
}

_CLUSTER_WHY = {
    "infra_502": "QA gateway returned HTML 502 — infra during the run, not a product regression",
    "infra_504": "QA gateway timed out (504) — infra / overloaded dependency",
    "infra_timeout": "Feign/client socket timeout talking to a QA service",
    "product_data_country_lang": "unsupported country-language combo (often GB+[en,fr]; use CA for multi-lang)",
    "flaky_settings": "Settings defaultCountries read-after-write lag",
    "test_setup_soft_launch": "PES soft-launch total vs tally on a shared fixture",
    "stale_validation": "negative test expected an exception that was not thrown",
    "product_data_not_found": "missing DB row / EmptyResult / NOT_FOUND",
    "validation_exception": "API rejected the request (business validation)",
    "server_exception": "QA threw NestedServletException/NPE/IOOB — product/server bug in that path",
    "assert_fail": "Spock assertion failed (fixture or response shape)",
    "other": "no dominant signature yet — open TeamCity details",
}


def _svc_hits(details: str) -> list[str]:
    return re.findall(
        r"([a-z0-9.-]+\.nexus-ms-qa\.dynata\.com)", details or "", flags=re.I
    )


def _clean_sample(msg: str) -> str:
    s = (msg or "").strip()
    if not s:
        return ""
    if "<html" in s.lower() or "<head>" in s.lower():
        if "502" in s:
            return "502 Bad Gateway"
        if "504" in s:
            return "504 Gateway Timeout"
        return "HTML gateway error"
    if "Condition not satisfied" in s or s.startswith("Condition failed"):
        return ""
    # Prefer the first meaningful exception line
    for line in s.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("at ") or line.startswith("Caused by:"):
            continue
        s = line
        break
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"https?://\S+", "<url>", s)
    s = re.sub(r"\b\d{6,}\b", "<id>", s)
    return s[:110]


def _area_from_classname(classname: str) -> str:
    cn = classname or ""
    m = re.search(r"\.steps\.([A-Za-z0-9_]+)\.", cn)
    if m:
        return m.group(1)
    parts = [p for p in cn.split(".") if p]
    if len(parts) >= 2:
        return parts[-2]
    return parts[-1] if parts else "unknown"


def _areas_from_files(files: list[str]) -> set[str]:
    areas: set[str] = set()
    for path in files or []:
        m = re.search(r"/steps/([A-Za-z0-9_]+)/", path)
        if m:
            areas.add(m.group(1))
            continue
        # helpers often sit next to the domain they support
        m = re.search(
            r"/helpers/(?:coredomainhelpers/)?([A-Za-z0-9_]+?)(?:Helper)?\.groovy$",
            path,
        )
        if m:
            # SegmentDetailsHelper → Segment; SourcesHelper → Sources — weak signal
            name = m.group(1)
            if name.endswith("Helper"):
                name = name[: -len("Helper")]
            if name and name not in ("Base", "Common", "Test"):
                areas.add(name)
    return areas


def _ticket_from_comment(comment: str) -> str:
    m = re.search(r"\b(NXS-\d+)\b", comment or "", flags=re.I)
    return m.group(1).upper() if m else ""


def _root_exception(msg: str, details: str) -> str:
    blob = f"{msg or ''}\n{details or ''}"
    for pat in (
        r"(java\.lang\.[A-Za-z]+Exception)[^\n:]*",
        r"(jakarta\.validation\.[A-Za-z]+Exception)[^\n:]*",
        r"(org\.springframework\.[A-Za-z.]+Exception)[^\n:]*",
        r"(org\.springframework\.dao\.[A-Za-z]+Exception)[^\n:]*",
    ):
        m = re.search(pat, blob)
        if m:
            return m.group(1).split(".")[-1]
    return _clean_sample(msg or details)[:80]


def investigate(raw: dict) -> dict:
    summary = raw.get("summary") or {}
    prior = raw.get("prior") or {}
    failures = list(raw.get("failureDetails") or [])
    if not failures:
        failures = [
            {
                "name": f.get("name"),
                "classname": f.get("classname"),
                "newFailure": f.get("newFailure"),
                "message": "",
                "details": "",
            }
            for f in (raw.get("failed") or [])
        ]

    enriched = []
    for f in failures:
        label = _classify_message(f.get("message") or "", f.get("details") or "")
        area = _area_from_classname(f.get("classname") or "")
        enriched.append({
            **f,
            "cluster": label,
            "area": area,
            "rootException": _root_exception(
                f.get("message") or "", f.get("details") or ""
            ),
        })

    new_fails = [f for f in enriched if f.get("newFailure")]
    focus = new_fails if new_fails else enriched

    fail_n = int(summary.get("failures") or len(enriched) or 0)
    new_failed = int(summary.get("newFailed") or len(new_fails) or 0)
    status = (raw.get("status") or "").upper()
    prior_fail = prior.get("failed")

    cluster_all: Counter = Counter(f["cluster"] for f in enriched)
    cluster_new: Counter = Counter(f["cluster"] for f in focus)
    area_new: Counter = Counter(f["area"] for f in focus if f.get("area"))
    svc_counts: Counter = Counter()
    for f in focus:
        for svc in _svc_hits(f.get("details") or ""):
            svc_counts[svc] += 1

    cluster_samples: dict[str, str] = {}
    for f in focus:
        cluster_samples.setdefault(
            f["cluster"],
            _clean_sample(f.get("message") or f.get("rootException") or f.get("name") or ""),
        )

    def _infra_count(counter: Counter) -> int:
        return (
            counter.get("infra_502", 0)
            + counter.get("infra_504", 0)
            + counter.get("infra_timeout", 0)
        )

    infra_n = _infra_count(cluster_all)
    infra_new = _infra_count(cluster_new)
    focus_n = len(focus) or 1
    infra_dominates_new = infra_new >= max(3, focus_n // 2)

    # --- headline (new-failure first; no pass%/duration) ---
    tone = "ok"
    if fail_n == 0 and status == "SUCCESS":
        tone = "ok"
        headline = "Nightly was healthy — no new unmuted failures"
    elif infra_dominates_new:
        tone = "bad" if new_failed >= 10 else "warn"
        headline = (
            f"{new_failed or fail_n} new failures — mostly QA infra timeouts/502s"
        )
    elif new_failed == 0 and fail_n:
        tone = "warn"
        headline = f"{fail_n} continuing failure(s) — no new unmuted fails"
    elif new_failed <= 3:
        tone = "warn"
        top_area = area_new.most_common(1)[0][0] if area_new else ""
        headline = (
            f"{new_failed} new failure{'s' if new_failed != 1 else ''}"
            + (f" in {top_area}" if top_area else "")
        )
    else:
        tone = "bad"
        top_areas = ", ".join(a for a, _ in area_new.most_common(2))
        headline = f"{new_failed} new failures" + (
            f" — mainly {top_areas}" if top_areas else ""
        )

    # --- change ↔ area correlation ---
    changes = raw.get("changes") or []
    likely_causes: list[dict] = []
    suspect: list[dict] = []
    new_areas = set(area_new)
    for ch in changes[:_MAX_CHANGES]:
        files = ch.get("files") or []
        ch_areas = _areas_from_files(files)
        overlap = sorted(ch_areas & new_areas) if new_areas else sorted(ch_areas)
        # If no file areas, still keep change for display when non-infra
        hit_counts = sum(area_new.get(a, 0) for a in overlap)
        entry = {
            "version": ch.get("version"),
            "username": ch.get("username"),
            "comment": ch.get("comment"),
            "ticket": _ticket_from_comment(ch.get("comment") or ""),
            "areas": overlap,
            "hitNewFailures": hit_counts,
            "files": [
                p.split("/")[-1] for p in files[:6]
            ],
        }
        suspect.append({
            "version": entry["version"],
            "username": entry["username"],
            "comment": entry["comment"],
            "ticket": entry["ticket"],
            "areas": entry["areas"],
        })
        if overlap and (hit_counts or not infra_new):
            likely_causes.append(entry)

    likely_causes.sort(key=lambda c: (-c["hitNewFailures"], c.get("version") or ""))

    # --- short investigation (overview + Teams) ---
    short_parts: list[str] = []
    if focus:
        top_clusters = cluster_new.most_common(2)
        bits = []
        for label, count in top_clusters:
            why = _CLUSTER_WHY.get(label, "")
            bits.append(
                f"{count}× {_CLUSTER_LABELS.get(label, label)}"
                + (f" ({why.split('—')[0].strip()})" if why and "—" in why else "")
            )
        if bits:
            scope = "New fails" if new_fails else "Failures"
            short_parts.append(f"{scope}: " + "; ".join(bits) + ".")
        if likely_causes and not infra_dominates_new:
            top = likely_causes[0]
            ticket = top.get("ticket") or ""
            areas = ", ".join(top["areas"][:3]) or "touched specs"
            who = top.get("username") or "?"
            ver = top.get("version") or "?"
            short_parts.append(
                f"Likely related to {ticket + ' ' if ticket else ''}"
                f"{who} `{ver}` ({areas}"
                + (
                    f", {top['hitNewFailures']} new fails in overlap"
                    if top["hitNewFailures"]
                    else ""
                )
                + ")."
            )
        elif infra_new and svc_counts:
            svcs = ", ".join(s.split(".")[0] for s, _ in svc_counts.most_common(2))
            short_parts.append(f"Gateway hits: {svcs}.")
        elif prior_fail is not None and new_failed:
            delta = fail_n - int(prior_fail)
            if delta:
                short_parts.append(
                    f"Vs prior #{prior.get('number')}: "
                    f"{'up' if delta > 0 else 'down'} {abs(delta)} total fails."
                )
    else:
        short_parts.append("No unmuted failures.")

    # Short bullets: types + top cause — never pass%/duration/build#
    bullets: list[str] = []
    for label, count in cluster_new.most_common(3):
        sample = cluster_samples.get(label) or ""
        line = f"{count}× {_CLUSTER_LABELS.get(label, label)}"
        if sample and sample.lower() not in line.lower():
            line += f" — {sample}"
        bullets.append(line)
    for cause in likely_causes[:2]:
        ticket = cause.get("ticket") or ""
        areas = ", ".join(cause["areas"][:3]) or "changed files"
        bullets.append(
            f"Change {ticket or cause.get('version')}: "
            f"{cause.get('username') or '?'} · {areas}"
            + (
                f" · {cause['hitNewFailures']} overlapping new fails"
                if cause["hitNewFailures"]
                else ""
            )
        )

    # --- long detail (Nightly page) ---
    detail_paras: list[str] = []
    if new_fails:
        detail_paras.append(
            f"{new_failed} of {fail_n} unmuted failures are new since the prior build"
            + (
                f" (#{prior.get('number')}, {prior_fail} fails)."
                if prior.get("number") is not None
                else "."
            )
        )
    elif fail_n:
        detail_paras.append(
            f"No new unmuted failures; {fail_n} continuing from prior runs."
        )

    if focus:
        type_lines = []
        for label, count in cluster_new.most_common(5):
            why = _CLUSTER_WHY.get(label, "")
            sample = cluster_samples.get(label) or ""
            line = f"{count}× {_CLUSTER_LABELS.get(label, label)}"
            if why:
                line += f" — {why}"
            elif sample:
                line += f" — {sample}"
            type_lines.append(line)
        detail_paras.append("Failure types (new-first): " + " ".join(
            f"({i+1}) {t}." for i, t in enumerate(type_lines[:4])
        ))

    if area_new:
        area_bits = [
            f"{a} ({n})" for a, n in area_new.most_common(6)
        ]
        detail_paras.append("Hot areas among new fails: " + ", ".join(area_bits) + ".")

    detail_bullets: list[str] = list(bullets)
    if likely_causes and not infra_dominates_new:
        detail_paras.append(
            "Build changes that touch the same packages as new fails "
            "(best-effort path match — not proof of blame):"
        )
        for cause in likely_causes[:4]:
            ticket = cause.get("ticket") or "commit"
            files = ", ".join(cause.get("files") or []) or "files n/a"
            detail_bullets.append(
                f"{ticket} {cause.get('version')} by {cause.get('username') or '?'} "
                f"→ areas {', '.join(cause['areas']) or '?'} "
                f"({cause['hitNewFailures']} new fails) · {files}"
            )
    elif changes and not infra_dominates_new:
        detail_paras.append(
            "Build has VCS changes but none mapped cleanly onto failing step packages "
            "— correlate manually in TeamCity Changes."
        )
        for ch in changes[:3]:
            detail_bullets.append(
                f"{_ticket_from_comment(ch.get('comment') or '') or ch.get('version')}: "
                f"{ch.get('username') or '?'} — {(ch.get('comment') or '')[:100]}"
            )
    elif infra_dominates_new:
        detail_paras.append(
            "Infra-dominant among new fails: VCS changes are unlikely to explain "
            "502/504/timeouts."
        )

    # Example new failures (names only)
    examples = []
    for f in focus[:5]:
        name = (f.get("name") or "").strip()
        if not name:
            continue
        examples.append(
            f"{f.get('area') or '?'}: {name[:90]} "
            f"[{_CLUSTER_LABELS.get(f['cluster'], f['cluster'])}]"
        )
    if examples:
        detail_paras.append("Example new failures: " + "; ".join(examples[:4]) + ".")

    clusters = [
        {
            "label": label,
            "display": _CLUSTER_LABELS.get(label, label),
            "count": count,
            "newCount": cluster_new.get(label, 0),
            "sample": _clean_sample(cluster_samples.get(label, "")),
            "why": _CLUSTER_WHY.get(label, ""),
        }
        for label, count in cluster_all.most_common()
    ]

    area_breakdown = [
        {"area": a, "newCount": n}
        for a, n in area_new.most_common(10)
    ]

    # --- likely cause classification (fallback; AI overrides) ---
    if fail_n == 0:
        cause, cause_text = "none", "No unmuted failures."
    elif infra_dominates_new:
        svcs = ", ".join(s.split(".")[0] for s, _ in svc_counts.most_common(2))
        cause = "infra"
        cause_text = (
            "QA infrastructure (502/504/read timeouts"
            + (f"; {svcs}" if svcs else "")
            + ") — not a code regression."
        )
    elif likely_causes:
        top = likely_causes[0]
        cause = "code_change"
        cause_text = (
            f"Possibly {top.get('ticket') or top.get('version')} by "
            f"{top.get('username') or '?'} — touches "
            f"{', '.join(top['areas'][:3]) or 'the failing areas'} "
            f"({top['hitNewFailures']} overlapping new fails). Correlation only."
        )
    elif changes:
        cause = "mixed"
        cause_text = (
            "VCS changes present but none map onto the failing packages — "
            "likely test/data, correlate manually."
        )
    else:
        cause = "test"
        cause_text = "No build changes — likely test/data or environment flakiness."

    return {
        "headline": headline,
        "tone": tone,
        "cause": cause,
        "causeText": cause_text,
        "investigation": " ".join(short_parts[:2]),
        "bullets": bullets[:4],
        "detail": {
            "investigation": " ".join(detail_paras),
            "bullets": detail_bullets[:10],
            "newFailureAreas": area_breakdown,
            "likelyCauses": [
                {
                    "version": c.get("version"),
                    "username": c.get("username"),
                    "ticket": c.get("ticket"),
                    "comment": c.get("comment"),
                    "areas": c.get("areas"),
                    "hitNewFailures": c.get("hitNewFailures"),
                    "files": c.get("files"),
                }
                for c in likely_causes[:6]
            ],
        },
        "clusters": clusters,
        "suspectCommits": suspect[:6],
        "source": "investigator",
        "generatedAt": _iso_now(),
        "buildNumber": raw.get("number"),
        "buildId": raw.get("buildId"),
        "webUrl": raw.get("webUrl"),
        "focus": "new_failures" if new_fails else "all_failures",
        "newFailed": new_failed,
        "failed": fail_n,
    }


def to_markdown(nutshell: dict) -> str:
    """Minimal artifact for Teams / morning post — headline, one-line cause, ≤2 bullets."""
    lines = [f"**{nutshell.get('headline', 'Nightly review')}**", ""]
    cause = nutshell.get("causeText") or ""
    if cause:
        # keep it to a single sentence for Teams
        first = cause.split(". ")[0].rstrip(".")
        lines.append(f"_Likely cause: {first}._")
        lines.append("")
    for b in (nutshell.get("bullets") or [])[:2]:
        lines.append(f"- {b}")
    lines.append("")
    link = nutshell.get("webUrl")
    tail = "[Full investigation](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html)"
    if link:
        tail += f" · [TeamCity]({link})"
    lines.append(tail)
    return "\n".join(lines).strip() + "\n"


def _excerpt(text: str, n: int = _MAX_DETAIL_CHARS) -> str:
    s = re.sub(r"\s+", " ", (text or "").strip())
    if len(s) <= n:
        return s
    return s[: n - 1] + "…"


def build_evidence(raw: dict, nutshell: dict) -> dict:
    """Compact pack for GHA cursor-agent (no live TeamCity required)."""
    failures = raw.get("failureDetails") or []
    compact_failures = []
    for f in failures[:_MAX_FAILURES]:
        compact_failures.append(
            {
                "name": f.get("name"),
                "classname": f.get("classname"),
                "newFailure": bool(f.get("newFailure")),
                "area": _area_from_classname(f.get("classname") or ""),
                "cluster": _classify_message(
                    f.get("message") or "", f.get("details") or ""
                ),
                "message": _excerpt(f.get("message") or "", 160),
                "detailsExcerpt": _excerpt(f.get("details") or ""),
            }
        )
    changes = []
    for ch in (raw.get("changes") or [])[:_MAX_CHANGES]:
        changes.append(
            {
                "version": ch.get("version"),
                "username": ch.get("username"),
                "comment": _excerpt(ch.get("comment") or "", 120),
                "files": (ch.get("files") or [])[:20],
                "areas": sorted(_areas_from_files(ch.get("files") or [])),
            }
        )
    return {
        "schemaVersion": 2,
        "generatedAt": _iso_now(),
        "build": {
            "number": raw.get("number"),
            "buildId": raw.get("buildId"),
            "status": raw.get("status"),
            "webUrl": raw.get("webUrl"),
            "durationSec": raw.get("durationSec")
            or (raw.get("summary") or {}).get("timeSec"),
        },
        "summary": raw.get("summary") or {},
        "prior": raw.get("prior") or {},
        "changes": changes,
        "clusters": nutshell.get("clusters") or [],
        "failures": compact_failures,
        "rulesNutshell": {
            "headline": nutshell.get("headline"),
            "tone": nutshell.get("tone"),
            "bullets": nutshell.get("bullets"),
            "investigation": nutshell.get("investigation"),
            "detail": nutshell.get("detail"),
            "suspectCommits": nutshell.get("suspectCommits") or [],
        },
        "instructions": (
            "Rewrite short + detail nutshell for humans. Focus on NEW failures: "
            "types, areas, and which changes touch the same packages. Never invent "
            "authors or root causes. Short = overview/Teams (no pass%/duration/build#). "
            "Detail = Nightly page (longer). Set source=llm when you rewrite."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--merge-nightly",
        action="store_true",
        help="Merge nutshell into dashboard/data/nightly.json",
    )
    args = ap.parse_args()

    raw = _load(TC_NIGHTLY)
    if not raw or not raw.get("buildId"):
        print(
            f"Missing {TC_NIGHTLY} — run automation/tc_fetch_nightly.py first",
            file=sys.stderr,
        )
        return 1

    details_pack = _load(FAILURE_DETAILS) or {}
    if details_pack.get("failures") and not raw.get("failureDetails"):
        raw = dict(raw)
        raw["failureDetails"] = details_pack["failures"]
        raw.setdefault("changes", details_pack.get("changes"))
        raw.setdefault("prior", details_pack.get("prior"))

    nutshell = investigate(raw)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(nutshell, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(to_markdown(nutshell), encoding="utf-8")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"headline: {nutshell['headline']}")

    evidence = build_evidence(raw, nutshell)
    EVIDENCE_JSON.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_JSON.write_text(
        json.dumps(evidence, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {EVIDENCE_JSON}")

    if args.merge_nightly:
        nightly = _load(NIGHTLY_JSON, {}) or {}
        if not nightly.get("available"):
            print(
                f"warn: {NIGHTLY_JSON} not available yet — "
                "run generate_nightly.py before merge",
                file=sys.stderr,
            )
        nightly["nutshell"] = nutshell
        NIGHTLY_JSON.parent.mkdir(parents=True, exist_ok=True)
        NIGHTLY_JSON.write_text(json.dumps(nightly, indent=2) + "\n", encoding="utf-8")
        print(f"Merged nutshell into {NIGHTLY_JSON}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
