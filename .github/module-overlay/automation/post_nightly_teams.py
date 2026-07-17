#!/usr/bin/env python3
"""Post a short Nexus API nightly status card to Microsoft Teams.

Reads ``dashboard/data/nightly.json`` (from ``generate_nightly.py`` / ``tc_fetch_nightly.py``)
and POSTs an Adaptive Card via a Power Automate Workflows webhook.

Primary CTA: public Nightly dashboard. Secondary: TeamCity build URL when present.

Webhook env (first match wins):
  NEXUS_TEAMS_NIGHTLY_WEBHOOK_URL  — group-chat / nightly channel (preferred)
  NEXUS_TEAMS_WEBHOOK_URL          — fallback (same as morning-report)

If no webhook is set, prints the card Markdown and exits 0 (safe for local runs).

Usage:
  python3 automation/post_nightly_teams.py
  python3 automation/post_nightly_teams.py --dry-run
  python3 automation/post_nightly_teams.py --json path/to/nightly.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = MODULE_ROOT / "dashboard" / "data" / "nightly.json"
DASHBOARD_NIGHTLY_URL = "https://gimesi13.github.io/nexus-ta-dashboard/nightly.html"
ENV_NIGHTLY = "NEXUS_TEAMS_NIGHTLY_WEBHOOK_URL"
ENV_FALLBACK = "NEXUS_TEAMS_WEBHOOK_URL"
FAIL_CAP = 5


def _webhook_url(explicit: str = "") -> str:
    return (explicit or os.environ.get(ENV_NIGHTLY) or os.environ.get(ENV_FALLBACK) or "").strip()


def _fmt_duration(sec: float | int | None) -> str:
    if sec is None:
        return "—"
    try:
        s = int(round(float(sec)))
    except (TypeError, ValueError):
        return "—"
    if s < 60:
        return f"{s}s"
    m, rem = divmod(s, 60)
    if m < 60:
        return f"{m}m {rem}s" if rem else f"{m}m"
    h, m = divmod(m, 60)
    return f"{h}h {m}m"


def _status_emoji(status: str) -> str:
    s = (status or "").upper()
    if s == "SUCCESS":
        return "✅"
    if s == "FAILURE":
        return "🔴"
    return "⚪"


def _failure_lines(data: dict) -> list[str]:
    failed = list(data.get("failed") or [])
    if not failed:
        return []
    lines = ["**Failures:**"]
    for item in failed[:FAIL_CAP]:
        area = item.get("area") or "?"
        name = item.get("name") or item.get("id") or "?"
        tag = " _(new)_" if item.get("newFailure") else ""
        lines.append(f"- {area} — {name}{tag}")
    extra = len(failed) - FAIL_CAP
    if extra > 0:
        lines.append(f"- …and {extra} more")
    trunc = data.get("failedTruncated") or 0
    if trunc:
        lines.append(f"- _(plus {trunc} not listed in feed)_")
    return lines


def build_markdown(data: dict) -> str:
    """Plain Markdown for stdout / webhook-unset fallback."""
    if not data.get("available"):
        reason = data.get("reason") or "no nightly summary"
        return (
            f"**Nexus API nightly** — no data ({reason})\n\n"
            f"[Nightly dashboard]({DASHBOARD_NIGHTLY_URL})"
        )

    build = data.get("build") or {}
    summary = data.get("summary") or {}
    status = (build.get("status") or "UNKNOWN").upper()
    number = build.get("number") or "?"
    emoji = _status_emoji(status)

    tests = summary.get("tests", "—")
    passed = summary.get("passed", "—")
    failures = summary.get("failures", 0) or 0
    muted = summary.get("muted", "—")
    skipped = summary.get("skipped", "—")
    pass_rate = summary.get("passRate")
    rate = f"{pass_rate}%" if pass_rate is not None else "—"
    duration = _fmt_duration(summary.get("timeSec"))

    lines = [
        f"{emoji} **Nexus API nightly** — {status} · #{number}",
        "",
        f"{rate} · {passed} passed · **{failures} failed** · {muted} muted · "
        f"{skipped} ignored · {tests} total · {duration}",
    ]
    fail_block = _failure_lines(data)
    if fail_block:
        lines.append("")
        lines.extend(fail_block)

    lines.append("")
    dash = f"[Nightly dashboard]({DASHBOARD_NIGHTLY_URL})"
    tc = build.get("webUrl")
    if tc:
        lines.append(f"{dash} · [TeamCity]({tc})")
    else:
        lines.append(dash)
    return "\n".join(lines)


def build_adaptive_card(data: dict) -> dict:
    build = data.get("build") or {}
    summary = data.get("summary") or {}

    if not data.get("available"):
        reason = data.get("reason") or "no nightly summary"
        title = "⚪ Nexus API nightly — no data"
        body: list[dict] = [
            {
                "type": "TextBlock",
                "text": title,
                "weight": "Bolder",
                "size": "Large",
                "wrap": True,
            },
            {
                "type": "TextBlock",
                "text": reason,
                "wrap": True,
                "isSubtle": True,
            },
        ]
    else:
        status = (build.get("status") or "UNKNOWN").upper()
        number = build.get("number") or "?"
        title = f"{_status_emoji(status)} Nexus API nightly — {status} · #{number}"
        pr = summary.get("passRate")
        facts = [
            {"title": "Pass rate", "value": f"{pr}%" if pr is not None else "—"},
            {"title": "Passed", "value": str(summary.get("passed", "—"))},
            {"title": "Failed", "value": str(summary.get("failures", "—"))},
            {"title": "Muted", "value": str(summary.get("muted", "—"))},
            {"title": "Ignored", "value": str(summary.get("skipped", "—"))},
            {"title": "Total", "value": str(summary.get("tests", "—"))},
            {"title": "Duration", "value": _fmt_duration(summary.get("timeSec"))},
        ]
        body = [
            {
                "type": "TextBlock",
                "text": title,
                "weight": "Bolder",
                "size": "Large",
                "wrap": True,
            },
            {"type": "FactSet", "facts": facts},
        ]
        fail_md = "\n".join(_failure_lines(data))
        if fail_md:
            body.append({"type": "TextBlock", "text": fail_md, "wrap": True})

    actions = [
        {
            "type": "Action.OpenUrl",
            "title": "Nightly dashboard",
            "url": DASHBOARD_NIGHTLY_URL,
        }
    ]
    tc = build.get("webUrl")
    if tc:
        actions.append(
            {"type": "Action.OpenUrl", "title": "TeamCity build", "url": tc}
        )

    return {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": body,
                    "actions": actions,
                },
            }
        ],
    }


def post_card(url: str, payload: dict) -> None:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        sys.stderr.write(f"[post_nightly_teams] posted to Teams (HTTP {resp.status}).\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--json",
        type=Path,
        default=DEFAULT_JSON,
        help=f"Path to nightly.json (default: {DEFAULT_JSON})",
    )
    ap.add_argument(
        "--url",
        default="",
        help=f"Webhook URL (default: ${ENV_NIGHTLY} or ${ENV_FALLBACK})",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Print Markdown (and card JSON) without posting",
    )
    args = ap.parse_args()

    path: Path = args.json
    if not path.is_file():
        sys.stderr.write(f"[post_nightly_teams] missing {path}\n")
        return 1

    data = json.loads(path.read_text(encoding="utf-8"))
    markdown = build_markdown(data)
    card = build_adaptive_card(data)

    if args.dry_run:
        print(markdown)
        print("\n--- adaptive card ---", file=sys.stderr)
        json.dump(card, sys.stderr, indent=2)
        sys.stderr.write("\n")
        return 0

    url = _webhook_url(args.url)
    if not url:
        sys.stderr.write(
            f"[post_nightly_teams] {ENV_NIGHTLY}/{ENV_FALLBACK} unset — "
            "printing card instead of posting.\n"
        )
        print(markdown)
        return 0

    try:
        post_card(url, card)
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        sys.stderr.write(f"[post_nightly_teams] FAILED to post: {exc}\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
