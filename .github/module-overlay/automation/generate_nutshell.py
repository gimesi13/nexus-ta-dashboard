#!/usr/bin/env python3
"""Investigate the latest nightly and write a shared nutshell review.

Reads TeamCity REST artifacts from ``tc_fetch_nightly.py``, clusters unmuted
failures, compares to the prior run, and writes:

  dashboard/data/nightly.json          → merges ``nutshell`` (after generate_nightly)
  dashboard/data/nightly-evidence.json → compact pack for the GHA LLM rewrite
  test-coverage-report/nightly-nutshell.md
  test-coverage-report/nightly-nutshell.json

TeamCity (or any host that can reach TC) runs this **before** Pages publish so
the site always has a rules-based nutshell + evidence. GitHub Actions then
optionally rewrites the prose with ``cursor-agent`` from the evidence pack
(public runners cannot reach private TeamCity).

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

# Keep the evidence pack small enough for git + agent context.
_MAX_FAILURES = 50
_MAX_DETAIL_CHARS = 400
_MAX_CHANGES = 8


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
    return "other"


def _svc_hits(details: str) -> list[str]:
    return re.findall(
        r"([a-z0-9.-]+\.nexus-ms-qa\.dynata\.com)", details or "", flags=re.I
    )


def _fmt_duration(sec) -> str:
    if sec is None:
        return "—"
    try:
        sec = int(round(float(sec)))
    except (TypeError, ValueError):
        return "—"
    if sec < 90:
        return f"{sec}s"
    m, s = divmod(sec, 60)
    if m < 90:
        return f"{m}m {s}s"
    h, m = divmod(m, 60)
    return f"{h}h {m}m"


_CLUSTER_LABELS = {
    "infra_502": "QA 502 Bad Gateway",
    "infra_504": "QA 504 timeout",
    "product_data_country_lang": "GB + fr unsupported",
    "flaky_settings": "Settings defaultCountries lag",
    "test_setup_soft_launch": "PES soft-launch vs tally",
    "stale_validation": "stale negative validation",
    "product_data_not_found": "NOT_FOUND / missing data",
    "other": "other",
}


def _clean_sample(msg: str) -> str:
    """Strip HTML / noise so nutshell bullets stay short and readable."""
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
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"https?://\S+", "<url>", s)
    s = re.sub(r"\b\d{6,}\b", "<id>", s)
    return s[:90]


def investigate(raw: dict) -> dict:
    summary = raw.get("summary") or {}
    prior = raw.get("prior") or {}
    failures = raw.get("failureDetails") or []
    if not failures:
        # fall back to names-only failed list
        failures = [
            {"name": f.get("name"), "classname": f.get("classname"),
             "newFailure": f.get("newFailure"), "message": "", "details": ""}
            for f in (raw.get("failed") or [])
        ]

    cluster_counts: Counter = Counter()
    cluster_samples: dict[str, str] = {}
    svc_counts: Counter = Counter()
    new_n = 0
    for f in failures:
        label = _classify_message(f.get("message") or "", f.get("details") or "")
        cluster_counts[label] += 1
        cluster_samples.setdefault(
            label, _clean_sample(f.get("message") or f.get("name") or "")
        )
        if f.get("newFailure"):
            new_n += 1
        for svc in _svc_hits(f.get("details") or ""):
            svc_counts[svc] += 1

    fail_n = int(summary.get("failures") or len(failures) or 0)
    new_failed = int(summary.get("newFailed") or new_n or 0)
    pass_rate = summary.get("passRate")
    status = (raw.get("status") or "").upper()
    dur = summary.get("timeSec") or raw.get("durationSec")
    prior_dur = prior.get("durationSec")
    prior_fail = prior.get("failed")

    infra_n = cluster_counts.get("infra_502", 0) + cluster_counts.get("infra_504", 0)
    tone = "ok"
    if fail_n == 0 and status == "SUCCESS":
        tone = "ok"
        headline = "Nightly was healthy"
    elif infra_n >= max(3, fail_n // 2):
        tone = "bad" if new_failed >= 10 else "warn"
        headline = (
            f"QA infra issues — {fail_n} failures"
            + (f" ({new_failed} new)" if new_failed else "")
        )
    elif fail_n <= 3:
        tone = "warn"
        headline = (
            f"Mostly healthy — {fail_n} failure"
            f"{'s' if fail_n != 1 else ''}"
            + (f", {new_failed} new" if new_failed else "")
        )
    else:
        tone = "bad"
        headline = (
            f"Nightly degraded — {fail_n} failures"
            + (f" ({new_failed} new)" if new_failed else "")
        )

    bullets: list[str] = []
    meta_bits = []
    if pass_rate is not None:
        meta_bits.append(f"{pass_rate}% pass")
    if raw.get("number"):
        meta_bits.append(f"#{raw['number']}")
    if dur is not None:
        dur_bit = _fmt_duration(dur)
        if prior_dur:
            delta = float(dur) - float(prior_dur)
            if abs(delta) >= 120:
                dur_bit += f", {'slower' if delta > 0 else 'faster'} than #{prior.get('number')}"
        meta_bits.append(dur_bit)
    if prior_fail is not None:
        meta_bits.append(f"was {prior_fail} fails prior")
    if meta_bits:
        bullets.append(" · ".join(meta_bits))

    # Keep causes short: at most 2 sentences, dominant cluster first
    investigation_parts: list[str] = []
    if infra_n:
        top_svcs = ", ".join(
            s.split(".")[0] for s, _ in svc_counts.most_common(2)
        ) or "QA gateways"
        investigation_parts.append(
            f"{infra_n}/{fail_n} look like QA 502/504 ({top_svcs}) — "
            "likely infra during the run, not a broad product regression."
        )
    if cluster_counts.get("product_data_country_lang"):
        investigation_parts.append(
            "Also: GB+[en,fr] still rejected (QuotaGroup E2E) — use CA for multi-lang."
        )
    if cluster_counts.get("flaky_settings") and len(investigation_parts) < 2:
        investigation_parts.append(
            "Settings defaultCountries read-after-write lag (await helper)."
        )
    if cluster_counts.get("test_setup_soft_launch") and len(investigation_parts) < 2:
        investigation_parts.append(
            "PES tally blocked: soft launch grew above total on shared fixture."
        )
    if cluster_counts.get("stale_validation") and len(investigation_parts) < 2:
        investigation_parts.append(
            f"{cluster_counts['stale_validation']} stale negative validations "
            "(expected exception not thrown)."
        )
    other_n = cluster_counts.get("other", 0)
    if other_n and not investigation_parts:
        investigation_parts.append(
            f"{other_n} failure(s) with no dominant signature — needs triage."
        )
    elif other_n and infra_n and len(investigation_parts) < 2:
        investigation_parts.append(f"{other_n} more outside the infra cluster.")

    changes = raw.get("changes") or []
    suspect: list[dict] = []
    # Commit blame is best-effort only: TC changes list, never invent authors.
    # Skip when infra dominates (commits rarely explain gateway HTML 502s).
    if changes and fail_n and infra_n < max(3, fail_n // 2):
        for ch in changes[:3]:
            suspect.append({
                "version": ch.get("version"),
                "username": ch.get("username"),
                "comment": ch.get("comment"),
            })
        if suspect:
            who = ", ".join(
                f"{c.get('username') or '?'} ({c.get('version') or '?'})"
                for c in suspect[:2]
            )
            investigation_parts.append(
                f"Build changes present ({who}) — correlate manually; "
                "no path→failure mapping yet."
            )

    if not investigation_parts:
        if fail_n == 0:
            investigation_parts.append("No unmuted failures.")
        else:
            investigation_parts.append("See failure list below / TeamCity.")

    clusters = [
        {
            "label": label,
            "display": _CLUSTER_LABELS.get(label, label),
            "count": count,
            "sample": _clean_sample(cluster_samples.get(label, "")),
        }
        for label, count in cluster_counts.most_common()
    ]

    # Top clusters only (short) — many failures collapse into a few lines
    for c in clusters[:3]:
        line = f"{c['count']}× {c['display']}"
        if c["sample"] and c["sample"].lower() not in c["display"].lower():
            line += f" — {c['sample']}"
        bullets.append(line)

    return {
        "headline": headline,
        "tone": tone,
        "bullets": bullets[:4],
        "investigation": " ".join(investigation_parts[:2]),
        "clusters": clusters,
        "suspectCommits": suspect,
        "source": "investigator",
        "generatedAt": _iso_now(),
        "buildNumber": raw.get("number"),
        "buildId": raw.get("buildId"),
        "webUrl": raw.get("webUrl"),
    }


def to_markdown(nutshell: dict) -> str:
    lines = [
        f"**{nutshell.get('headline', 'Nightly review')}**",
        "",
        nutshell.get("investigation") or "",
        "",
    ]
    for b in nutshell.get("bullets") or []:
        lines.append(f"- {b}")
    if nutshell.get("webUrl"):
        lines.append("")
        lines.append(f"[Open TeamCity build]({nutshell['webUrl']})")
    lines.append("")
    lines.append(
        f"[TA Dashboard — Nightly](https://gimesi13.github.io/nexus-ta-dashboard/nightly.html)"
    )
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
            }
        )
    return {
        "schemaVersion": 1,
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
            "suspectCommits": nutshell.get("suspectCommits") or [],
        },
        "instructions": (
            "Rewrite the shared nightly nutshell for humans. Prefer novel/"
            "non-infra failures in the investigation. Never invent authors or "
            "root causes. Keep headline + ≤2 investigation sentences + ≤4 bullets. "
            "Set source to llm when you rewrite."
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

    # Prefer dedicated details file when present (keeps investigation inputs clear)
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
