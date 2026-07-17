#!/usr/bin/env python3
"""Post a short Nexus API nightly status card to Microsoft Teams.

Reads ``dashboard/data/nightly.json`` and POSTs an Adaptive Card via a Power Automate
Workflows webhook. Primary CTA: Nightly dashboard. Secondary: TeamCity.

Webhook:
  NEXUS_TEAMS_NIGHTLY_WEBHOOK_URL   required for posting
  NEXUS_TEAMS_NIGHTLY_ALLOW_FALLBACK=1  — then allow NEXUS_TEAMS_WEBHOOK_URL

Styles (``--style``):
  A  airy metrics (current favorite candidate)
  B  compact digest
  C  hero pass-rate
  D  status ribbon
  E  two-by-two KPIs

  --style-gallery   post A–E labeled so you can pick one

Usage:
  python3 automation/post_nightly_teams.py
  python3 automation/post_nightly_teams.py --style C
  python3 automation/post_nightly_teams.py --style-gallery
  python3 automation/post_nightly_teams.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = MODULE_ROOT / "dashboard" / "data" / "nightly.json"
DASHBOARD_BASE = "https://gimesi13.github.io/nexus-ta-dashboard/"
DASHBOARD_NIGHTLY_URL = DASHBOARD_BASE + "nightly.html"
ENV_NIGHTLY = "NEXUS_TEAMS_NIGHTLY_WEBHOOK_URL"
ENV_FALLBACK = "NEXUS_TEAMS_WEBHOOK_URL"
ENV_ALLOW_FALLBACK = "NEXUS_TEAMS_NIGHTLY_ALLOW_FALLBACK"
# Hard cap — Teams cards must stay short even on a red night.
FAIL_CAP = 3
# Long enough for most feature titles; wrap instead of hard-cutting early.
NAME_LIMIT = 160
STYLES = ("A", "B", "C", "D", "E")
STYLE_LABELS = {
    "A": "Airy metrics (default)",
    "B": "Compact digest",
    "C": "Hero pass-rate",
    "D": "Status ribbon",
    "E": "Two-by-two KPIs",
}
DEFAULT_STYLE = "A"


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
    s = (status or "").upper()
    if s == "SUCCESS":
        return "Passed", "good", "good"
    if s == "FAILURE":
        return "Failed", "attention", "attention"
    return s or "Unknown", "emphasis", "default"


def _shorten(text: str, limit: int = 90) -> str:
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _actions(build: dict) -> list[dict]:
    actions = [
        {
            "type": "Action.OpenUrl",
            "title": "Open TA Dashboard",
            "url": DASHBOARD_NIGHTLY_URL,
            "style": "positive",
        }
    ]
    tc = build.get("webUrl")
    if tc:
        actions.append(
            {
                "type": "Action.OpenUrl",
                "title": "Open TeamCity Build",
                "url": tc,
            }
        )
    return actions


def _inventory_url(item: dict) -> str:
    href = (item.get("inventoryHref") or "").lstrip("/")
    if not href:
        return DASHBOARD_BASE + "inventory.html?run=failed"
    if href.startswith("http"):
        return href
    return DASHBOARD_BASE + href


def _failure_chips(c: dict) -> list[dict]:
    """Soft chips: Area · NEW (red) + wrapping test name.

    Whole chip is clickable via selectAction (plain text — no purple underline).
    """
    build_url = (c.get("build") or {}).get("webUrl") or ""
    items: list[dict] = []
    for item in c["failed"][:FAIL_CAP]:
        area = item.get("area") or "?"
        name = _shorten(item.get("name") or item.get("id") or "?", NAME_LIMIT)
        new = bool(item.get("newFailure"))
        tc_url = (item.get("teamcityUrl") or "").strip() or build_url
        # Keep NEW on its own TextBlock so Teams paints it attention/red.
        title_cols = [
            {
                "type": "Column",
                "width": "auto",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": f"**{area}**",
                        "size": "Small",
                        "spacing": "None",
                    }
                ],
            }
        ]
        if new:
            title_cols.append(
                {
                    "type": "Column",
                    "width": "auto",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": " · ",
                            "size": "Small",
                            "spacing": "None",
                        }
                    ],
                }
            )
            title_cols.append(
                {
                    "type": "Column",
                    "width": "auto",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "NEW",
                            "size": "Small",
                            "weight": "Bolder",
                            "color": "attention",
                            "spacing": "None",
                        }
                    ],
                }
            )
        chip: dict = {
            "type": "Container",
            "style": "emphasis",
            "spacing": "Small",
            "items": [
                {"type": "ColumnSet", "spacing": "None", "columns": title_cols},
                {
                    "type": "TextBlock",
                    "text": name,
                    "size": "Small",
                    "isSubtle": True,
                    "spacing": "None",
                    "wrap": True,
                },
            ],
        }
        # Whole chip opens TeamCity (plain text — no purple underline).
        if tc_url:
            chip["selectAction"] = {
                "type": "Action.OpenUrl",
                "title": "Open in TeamCity",
                "url": tc_url,
            }
        items.append(chip)

    shown = min(len(c["failed"]), FAIL_CAP)
    remaining = max(0, int(c["failed_n"] or 0) - shown)
    if c["more"]:
        remaining = max(remaining, c["more"])
    if remaining > 0:
        items.append(
            {
                "type": "TextBlock",
                "text": (
                    f"[+ {remaining} more on the dashboard →]"
                    f"({DASHBOARD_NIGHTLY_URL})"
                ),
                "size": "Small",
                "color": "accent",
                "spacing": "Small",
                "wrap": True,
            }
        )
    return items


def _wrap_card(body: list[dict], actions: list[dict]) -> dict:
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


def _style_banner(style: str) -> dict:
    return {
        "type": "TextBlock",
        "text": f"STYLE {style} — {STYLE_LABELS.get(style, style)}",
        "size": "Small",
        "weight": "Bolder",
        "color": "accent",
        "spacing": "None",
    }


def _ctx(data: dict) -> dict:
    build = data.get("build") or {}
    summary = data.get("summary") or {}
    status = (build.get("status") or "UNKNOWN").upper()
    label, style, accent = _status_tone(status)
    pr = summary.get("passRate")
    failed_n = summary.get("failures", 0) or 0
    failed = list(data.get("failed") or [])
    return {
        "build": build,
        "summary": summary,
        "generated_at": data.get("generatedAt") or "",
        "status": status,
        "label": label,
        "container_style": style,
        "accent": accent,
        "number": build.get("number") or "?",
        "branch": build.get("branchName") or "master",
        "rate": f"{pr}%" if pr is not None else "—",
        "failed_n": failed_n,
        "fail_color": "attention" if failed_n else "good",
        "duration": _fmt_duration(summary.get("timeSec")),
        "passed": summary.get("passed", "—"),
        "muted": summary.get("muted", "—"),
        "skipped": summary.get("skipped", "—"),
        "tests": summary.get("tests", "—"),
        "failed": failed,
        "more": max(0, len(failed) - FAIL_CAP + int(data.get("failedTruncated") or 0)),
    }


def _kpi(label: str, value: str, color: str = "default", size: str = "ExtraLarge") -> dict:
    return {
        "type": "Column",
        "width": "stretch",
        "items": [
            {
                "type": "TextBlock",
                "text": value,
                "size": size,
                "weight": "Bolder",
                "color": color,
                "spacing": "None",
                "horizontalAlignment": "Center",
                "wrap": True,
            },
            {
                "type": "TextBlock",
                "text": label,
                "size": "Small",
                "isSubtle": True,
                "spacing": "None",
                "horizontalAlignment": "Center",
            },
        ],
    }


def _fail_md(c: dict, numbered: bool = True) -> str:
    lines = []
    for i, item in enumerate(c["failed"][:FAIL_CAP], start=1):
        area = item.get("area") or "?"
        name = _shorten(item.get("name") or item.get("id") or "?")
        tag = " · **new**" if item.get("newFailure") else ""
        prefix = f"{i}. " if numbered else "• "
        lines.append(f"{prefix}**{area}** — {name}{tag}")
    if c["more"]:
        lines.append(f"_+ {c['more']} more on the dashboard_")
    return "\n".join(lines)


def _header_row(c: dict, status_text: str) -> dict:
    return {
        "type": "ColumnSet",
        "columns": [
            {
                "type": "Column",
                "width": "stretch",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": "Nexus API · Nightly",
                        "size": "Small",
                        "isSubtle": True,
                        "spacing": "None",
                    },
                    {
                        "type": "TextBlock",
                        "text": status_text,
                        "size": "Large",
                        "weight": "Bolder",
                        "color": c["accent"],
                        "spacing": "Small",
                    },
                ],
            },
            {
                "type": "Column",
                "width": "auto",
                "verticalContentAlignment": "Bottom",
                "items": [
                    {
                        "type": "TextBlock",
                        "text": f"#{c['number']}",
                        "weight": "Bolder",
                        "horizontalAlignment": "Right",
                        "spacing": "None",
                    },
                    {
                        "type": "TextBlock",
                        "text": c["branch"],
                        "size": "Small",
                        "isSubtle": True,
                        "horizontalAlignment": "Right",
                        "spacing": "None",
                    },
                ],
            },
        ],
    }


def style_a(c: dict) -> list[dict]:
    """Airy metrics — chosen look: passed up top, muted down below."""
    body: list[dict] = [
        _header_row(c, f"●  {c['label']}"),
        {
            "type": "ColumnSet",
            "spacing": "Large",
            "separator": True,
            "columns": [
                _kpi("pass rate", c["rate"]),  # white / default — not green
                _kpi("passed", str(c["passed"]), "good"),
                _kpi("failed", str(c["failed_n"]), c["fail_color"]),
                _kpi("duration", c["duration"]),
            ],
        },
        {
            "type": "TextBlock",
            "text": (
                f"{c['muted']} muted   ·   "
                f"{c['skipped']} ignored   ·   "
                f"{c['tests']} total"
            ),
            "isSubtle": True,
            "size": "Small",
            "horizontalAlignment": "Center",
            "spacing": "Small",
            "wrap": True,
        },
    ]

    if c["failed_n"] or c["failed"]:
        body.append(
            {
                "type": "TextBlock",
                "text": "Needs attention",
                "weight": "Bolder",
                "size": "Small",
                "spacing": "Large",
                "separator": True,
            }
        )
        if c["failed"]:
            body.extend(_failure_chips(c))
        else:
            body.append(
                {
                    "type": "TextBlock",
                    "text": (
                        f"[{c['failed_n']} failures — open the dashboard →]"
                        f"({DASHBOARD_NIGHTLY_URL})"
                    ),
                    "size": "Small",
                    "color": "accent",
                    "spacing": "Small",
                    "wrap": True,
                }
            )
    elif c["status"] == "SUCCESS":
        body.append(
            {
                "type": "TextBlock",
                "text": "Clean run — no open failures.",
                "color": "good",
                "spacing": "Large",
                "separator": True,
                "wrap": True,
            }
        )
    return body


def style_b(c: dict) -> list[dict]:
    """Compact digest — one tight card, minimal chrome."""
    line = (
        f"**{c['rate']}** pass · **{c['failed_n']}** failed · "
        f"{c['muted']} muted · {c['duration']}"
    )
    body = [
        {
            "type": "TextBlock",
            "text": f"Nexus nightly  ·  #{c['number']}  ·  {c['branch']}",
            "size": "Small",
            "isSubtle": True,
            "spacing": "None",
        },
        {
            "type": "TextBlock",
            "text": c["label"],
            "size": "ExtraLarge",
            "weight": "Bolder",
            "color": c["accent"],
            "spacing": "Small",
        },
        {"type": "TextBlock", "text": line, "wrap": True, "spacing": "Small"},
    ]
    if c["failed"]:
        body.append(
            {
                "type": "TextBlock",
                "text": _fail_md(c, numbered=False),
                "wrap": True,
                "spacing": "Medium",
                "separator": True,
            }
        )
    return body


def style_c(c: dict) -> list[dict]:
    """Hero pass-rate — big number first."""
    body = [
        {
            "type": "TextBlock",
            "text": "Nexus API · Nightly",
            "size": "Small",
            "isSubtle": True,
            "horizontalAlignment": "Center",
            "spacing": "None",
        },
        {
            "type": "TextBlock",
            "text": c["rate"],
            "size": "ExtraLarge",
            "weight": "Bolder",
            "color": "good",
            "horizontalAlignment": "Center",
            "spacing": "Medium",
        },
        {
            "type": "TextBlock",
            "text": f"pass rate  ·  {c['label'].lower()}  ·  #{c['number']}",
            "size": "Small",
            "isSubtle": True,
            "horizontalAlignment": "Center",
            "spacing": "None",
        },
        {
            "type": "ColumnSet",
            "spacing": "Large",
            "separator": True,
            "columns": [
                _kpi("failed", str(c["failed_n"]), c["fail_color"], "Large"),
                _kpi("muted", str(c["muted"]), "default", "Large"),
                _kpi("duration", c["duration"], "default", "Large"),
            ],
        },
    ]
    if c["failed"]:
        body.append(
            {
                "type": "TextBlock",
                "text": "**Failures**\n" + _fail_md(c, numbered=False),
                "wrap": True,
                "spacing": "Medium",
                "separator": True,
            }
        )
    return body


def style_d(c: dict) -> list[dict]:
    """Status ribbon — thin colored bar, then calm facts."""
    body = [
        {
            "type": "Container",
            "style": c["container_style"],
            "items": [
                {
                    "type": "ColumnSet",
                    "columns": [
                        {
                            "type": "Column",
                            "width": "stretch",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": f"Nexus API nightly  ·  {c['label']}",
                                    "weight": "Bolder",
                                    "wrap": True,
                                    "spacing": "None",
                                }
                            ],
                        },
                        {
                            "type": "Column",
                            "width": "auto",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": f"#{c['number']}",
                                    "weight": "Bolder",
                                    "spacing": "None",
                                }
                            ],
                        },
                    ],
                }
            ],
        },
        {
            "type": "FactSet",
            "spacing": "Medium",
            "facts": [
                {"title": "Pass rate", "value": c["rate"]},
                {"title": "Failed", "value": str(c["failed_n"])},
                {"title": "Muted", "value": str(c["muted"])},
                {"title": "Passed / total", "value": f"{c['passed']} / {c['tests']}"},
                {"title": "Duration", "value": c["duration"]},
                {"title": "Branch", "value": c["branch"]},
            ],
        },
    ]
    if c["failed"]:
        body.append(
            {
                "type": "TextBlock",
                "text": "**Needs attention**\n" + _fail_md(c),
                "wrap": True,
                "spacing": "Medium",
                "separator": True,
            }
        )
    return body


def style_e(c: dict) -> list[dict]:
    """Two-by-two KPI grid."""
    body = [
        _header_row(c, c["label"]),
        {
            "type": "ColumnSet",
            "spacing": "Medium",
            "separator": True,
            "columns": [
                _kpi("pass rate", c["rate"], "good", "Large"),
                _kpi("failed", str(c["failed_n"]), c["fail_color"], "Large"),
            ],
        },
        {
            "type": "ColumnSet",
            "spacing": "Small",
            "columns": [
                _kpi("muted", str(c["muted"]), "default", "Large"),
                _kpi("duration", c["duration"], "default", "Large"),
            ],
        },
        {
            "type": "TextBlock",
            "text": f"{c['passed']} passed · {c['skipped']} ignored · {c['tests']} total",
            "isSubtle": True,
            "size": "Small",
            "spacing": "Medium",
            "wrap": True,
        },
    ]
    if c["failed"]:
        # Soft chips instead of a wall of text
        for item in c["failed"][:FAIL_CAP]:
            area = item.get("area") or "?"
            name = _shorten(item.get("name") or "?", 70)
            new = "  ·  NEW" if item.get("newFailure") else ""
            body.append(
                {
                    "type": "Container",
                    "style": "emphasis",
                    "spacing": "Small",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": f"**{area}**{new}",
                            "size": "Small",
                            "spacing": "None",
                        },
                        {
                            "type": "TextBlock",
                            "text": name,
                            "size": "Small",
                            "isSubtle": True,
                            "wrap": True,
                            "spacing": "None",
                        },
                    ],
                }
            )
    return body


BUILDERS = {
    "A": style_a,
    "B": style_b,
    "C": style_c,
    "D": style_d,
    "E": style_e,
}


def build_adaptive_card(
    data: dict, style: str = DEFAULT_STYLE, *, label_style: bool = False
) -> dict:
    style = (style or DEFAULT_STYLE).upper()
    if style not in BUILDERS:
        style = DEFAULT_STYLE
    actions = _actions(data.get("build") or {})
    if not data.get("available"):
        reason = data.get("reason") or "no nightly summary"
        body: list[dict] = [
            {
                "type": "TextBlock",
                "text": "Nexus API · Nightly",
                "size": "Small",
                "isSubtle": True,
            },
            {
                "type": "TextBlock",
                "text": "No data yet",
                "size": "Large",
                "weight": "Bolder",
            },
            {"type": "TextBlock", "text": reason, "isSubtle": True, "wrap": True},
        ]
    else:
        body = BUILDERS[style](_ctx(data))
    if label_style:
        body = [_style_banner(style), *body]
    return _wrap_card(body, actions)


def build_markdown(data: dict) -> str:
    if not data.get("available"):
        reason = data.get("reason") or "no nightly summary"
        return (
            f"**Nexus API nightly** — no data ({reason})\n\n"
            f"[Open dashboard]({DASHBOARD_NIGHTLY_URL})"
        )
    c = _ctx(data)
    lines = [
        f"**Nexus API nightly** · {c['label']} · #{c['number']}",
        f"{c['rate']} pass · {c['failed_n']} failed · {c['muted']} muted · {c['duration']}",
    ]
    for item in c["failed"][:FAIL_CAP]:
        area = item.get("area") or "?"
        name = item.get("name") or "?"
        tag = " (new)" if item.get("newFailure") else ""
        lines.append(f"• {area} — {name}{tag}")
    lines.append(f"[Open dashboard]({DASHBOARD_NIGHTLY_URL})")
    if c["build"].get("webUrl"):
        lines.append(f"[TeamCity]({c['build']['webUrl']})")
    return "\n".join(lines)


def post_card(url: str, payload: dict) -> None:
    raw = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=raw, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        sys.stderr.write(f"[post_nightly_teams] posted to Teams (HTTP {resp.status}).\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", type=Path, default=DEFAULT_JSON)
    ap.add_argument("--url", default="")
    ap.add_argument(
        "--style",
        default=DEFAULT_STYLE,
        choices=[*STYLES, *[s.lower() for s in STYLES]],
    )
    ap.add_argument(
        "--style-gallery",
        action="store_true",
        help="Post styles A–E labeled for comparison",
    )
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    path: Path = args.json
    if not path.is_file():
        sys.stderr.write(f"[post_nightly_teams] missing {path}\n")
        return 1

    data = json.loads(path.read_text(encoding="utf-8"))
    styles = list(STYLES) if args.style_gallery else [args.style.upper()]

    if args.dry_run:
        for s in styles:
            card = build_adaptive_card(data, s, label_style=args.style_gallery)
            print(f"===== STYLE {s} ({STYLE_LABELS[s]}) =====")
            print(build_markdown(data))
            json.dump(card, sys.stderr, indent=2)
            sys.stderr.write("\n")
        return 0

    url = _webhook_url(args.url)
    if not url:
        sys.stderr.write(
            f"[post_nightly_teams] {ENV_NIGHTLY} unset — printing instead of posting.\n"
        )
        print(build_markdown(data))
        return 0

    for i, s in enumerate(styles):
        try:
            post_card(url, build_adaptive_card(data, s, label_style=len(styles) > 1))
        except (urllib.error.URLError, urllib.error.HTTPError) as exc:
            sys.stderr.write(f"[post_nightly_teams] FAILED style {s}: {exc}\n")
            return 1
        if i + 1 < len(styles):
            time.sleep(1.2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
