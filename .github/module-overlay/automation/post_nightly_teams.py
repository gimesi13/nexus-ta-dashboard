#!/usr/bin/env python3
"""Post a short Nexus API nightly status card to Microsoft Teams.

Reads ``dashboard/data/nightly.json`` (from ``generate_nightly.py`` / ``tc_fetch_nightly.py``)
and POSTs an Adaptive Card via a Power Automate Workflows webhook.

Primary CTA: public Nightly dashboard. Secondary: TeamCity build URL when present.

Webhook (group chat / shared channel — do **not** reuse the private morning-report URL):
  NEXUS_TEAMS_NIGHTLY_WEBHOOK_URL   required for posting
  NEXUS_TEAMS_NIGHTLY_ALLOW_FALLBACK=1  — only then fall back to NEXUS_TEAMS_WEBHOOK_URL

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
ENV_ALLOW_FALLBACK = "NEXUS_TEAMS_NIGHTLY_ALLOW_FALLBACK"
FAIL_CAP = 5


def _webhook_url(explicit: str = "") -> str:
    if explicit.strip():
        return explicit.strip()
    nightly = (os.environ.get(ENV_NIGHTLY) or "").strip()
    if nightly:
        return nightly
    if (os.environ.get(ENV_ALLOW_FALLBACK) or "").strip() in ("1", "true", "yes"):
        return (os.environ.get(ENV_FALLBACK) or "").strip()
    return ""


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


def _status_tone(status: str) -> tuple[str, str, str]:
    """Return (label, container_style, accent_color)."""
    s = (status or "").upper()
    if s == "SUCCESS":
        return "Passed", "good", "good"
    if s == "FAILURE":
        return "Failed", "attention", "attention"
    return s or "Unknown", "emphasis", "default"


def _kpi_column(label: str, value: str, color: str = "default") -> dict:
    return {
        "type": "Column",
        "width": "stretch",
        "items": [
            {
                "type": "TextBlock",
                "text": label.upper(),
                "size": "Small",
                "isSubtle": True,
                "spacing": "None",
            },
            {
                "type": "TextBlock",
                "text": value,
                "size": "Large",
                "weight": "Bolder",
                "color": color,
                "spacing": "None",
                "wrap": True,
            },
        ],
    }


def _failure_items(data: dict) -> list[dict]:
    failed = list(data.get("failed") or [])
    items: list[dict] = []
    for item in failed[:FAIL_CAP]:
        area = item.get("area") or "?"
        name = item.get("name") or item.get("id") or "?"
        new = bool(item.get("newFailure"))
        title = f"**{area}** · {name}"
        if new:
            title += "  ·  new"
        items.append(
            {
                "type": "Container",
                "spacing": "Small",
                "style": "emphasis",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": title,
                        "wrap": True,
                        "size": "Small",
                    }
                ],
            }
        )
    extra = len(failed) - FAIL_CAP
    trunc = int(data.get("failedTruncated") or 0)
    more = extra + trunc
    if more > 0:
        items.append(
            {
                "type": "TextBlock",
                "text": f"+ {more} more on the dashboard",
                "isSubtle": True,
                "size": "Small",
                "spacing": "Small",
            }
        )
    return items


def build_markdown(data: dict) -> str:
    """Plain Markdown for stdout / webhook-unset fallback."""
    if not data.get("available"):
        reason = data.get("reason") or "no nightly summary"
        return (
            f"**Nexus API nightly** — no data ({reason})\n\n"
            f"[Open dashboard]({DASHBOARD_NIGHTLY_URL})"
        )

    build = data.get("build") or {}
    summary = data.get("summary") or {}
    status = (build.get("status") or "UNKNOWN").upper()
    label, _, _ = _status_tone(status)
    number = build.get("number") or "?"
    pass_rate = summary.get("passRate")
    rate = f"{pass_rate}%" if pass_rate is not None else "—"
    failures = summary.get("failures", 0) or 0

    lines = [
        f"**Nexus API nightly** · {label} · #{number}",
        f"{rate} pass · {failures} failed · "
        f"{summary.get('muted', '—')} muted · {_fmt_duration(summary.get('timeSec'))}",
    ]
    failed = list(data.get("failed") or [])
    for item in failed[:FAIL_CAP]:
        area = item.get("area") or "?"
        name = item.get("name") or "?"
        tag = " (new)" if item.get("newFailure") else ""
        lines.append(f"• {area} — {name}{tag}")
    lines.append(f"[Open dashboard]({DASHBOARD_NIGHTLY_URL})")
    tc = build.get("webUrl")
    if tc:
        lines.append(f"[TeamCity]({tc})")
    return "\n".join(lines)


def build_adaptive_card(data: dict) -> dict:
    build = data.get("build") or {}
    summary = data.get("summary") or {}
    actions = [
        {
            "type": "Action.OpenUrl",
            "title": "Open nightly dashboard",
            "url": DASHBOARD_NIGHTLY_URL,
            "style": "positive",
        }
    ]
    tc = build.get("webUrl")
    if tc:
        actions.append(
            {"type": "Action.OpenUrl", "title": "TeamCity", "url": tc}
        )

    if not data.get("available"):
        reason = data.get("reason") or "no nightly summary"
        body: list[dict] = [
            {
                "type": "Container",
                "style": "emphasis",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": "NEXUS API REGRESSION",
                        "size": "Small",
                        "isSubtle": True,
                        "spacing": "None",
                    },
                    {
                        "type": "TextBlock",
                        "text": "No nightly data",
                        "size": "Large",
                        "weight": "Bolder",
                        "spacing": "Small",
                        "wrap": True,
                    },
                    {
                        "type": "TextBlock",
                        "text": reason,
                        "isSubtle": True,
                        "wrap": True,
                        "spacing": "Small",
                    },
                ],
            }
        ]
    else:
        status = (build.get("status") or "UNKNOWN").upper()
        label, style, accent = _status_tone(status)
        number = build.get("number") or "?"
        branch = build.get("branchName") or "master"
        pr = summary.get("passRate")
        rate = f"{pr}%" if pr is not None else "—"
        failed_n = summary.get("failures", 0) or 0
        fail_color = "attention" if failed_n else "good"

        body = [
            {
                "type": "Container",
                "style": style,
                "items": [
                    {
                        "type": "TextBlock",
                        "text": "NEXUS API REGRESSION",
                        "size": "Small",
                        "weight": "Bolder",
                        "spacing": "None",
                    },
                    {
                        "type": "ColumnSet",
                        "spacing": "Small",
                        "columns": [
                            {
                                "type": "Column",
                                "width": "stretch",
                                "items": [
                                    {
                                        "type": "TextBlock",
                                        "text": label,
                                        "size": "ExtraLarge",
                                        "weight": "Bolder",
                                        "color": accent,
                                        "spacing": "None",
                                    },
                                    {
                                        "type": "TextBlock",
                                        "text": f"Build #{number}  ·  {branch}",
                                        "isSubtle": True,
                                        "spacing": "None",
                                        "wrap": True,
                                    },
                                ],
                            },
                        ],
                    },
                ],
            },
            {
                "type": "ColumnSet",
                "spacing": "Medium",
                "separator": True,
                "columns": [
                    _kpi_column("Pass rate", rate, "good" if failed_n == 0 else "default"),
                    _kpi_column("Failed", str(failed_n), fail_color),
                    _kpi_column("Muted", str(summary.get("muted", "—"))),
                    _kpi_column("Duration", _fmt_duration(summary.get("timeSec"))),
                ],
            },
            {
                "type": "TextBlock",
                "text": (
                    f"{summary.get('passed', '—')} passed  ·  "
                    f"{summary.get('skipped', '—')} ignored  ·  "
                    f"{summary.get('tests', '—')} total"
                ),
                "isSubtle": True,
                "size": "Small",
                "spacing": "Small",
                "wrap": True,
            },
        ]

        fail_items = _failure_items(data)
        if fail_items:
            body.append(
                {
                    "type": "TextBlock",
                    "text": "Failures",
                    "weight": "Bolder",
                    "spacing": "Medium",
                    "separator": True,
                }
            )
            body.extend(fail_items)
        elif status == "SUCCESS":
            body.append(
                {
                    "type": "TextBlock",
                    "text": "No open failures — suite is clean.",
                    "color": "good",
                    "spacing": "Medium",
                    "separator": True,
                    "wrap": True,
                }
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
                    "msteams": {"width": "Full"},
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
        help=f"Webhook URL (default: ${ENV_NIGHTLY})",
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
            f"[post_nightly_teams] {ENV_NIGHTLY} unset — printing card instead of posting.\n"
            f"  Tip: create a Workflow aimed at the group chat and export that URL as "
            f"{ENV_NIGHTLY} (do not reuse the private {ENV_FALLBACK}).\n"
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
