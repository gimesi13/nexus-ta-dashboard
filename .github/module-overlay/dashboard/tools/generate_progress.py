#!/usr/bin/env python3
"""Generate data/progress.json — tests & coverage added over time.

Answers "how many tests did we add last sprint?" by scanning git history of
*TestSteps.groovy for the first appearance of each Spock feature method, then
joining those additions to the current inventory (area / type / case count) and
an append-only snapshot series for inventory + coverage totals.

Usage:
    python3 tools/generate_progress.py [--since YYYY-MM-DD] [--repo-root PATH]
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

DASHBOARD_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODULE_ROOT = Path(os.environ.get("NEXUS_MODULE_ROOT", DASHBOARD_ROOT.parent))
OUT = DASHBOARD_ROOT / "data" / "progress.json"
INVENTORY = DASHBOARD_ROOT / "data" / "inventory.json"
COVERAGE = DASHBOARD_ROOT / "data" / "coverage.json"

ADD_RE = re.compile(r'^\+\s*def\s+"([^"]+)"\s*\(', re.MULTILINE)
TICKET_RE = re.compile(r"NXS-\d+", re.IGNORECASE)
WINDOWS = (("7d", 7), ("14d", 14), ("30d", 30), ("90d", 90))
TYPE_ORDER = ("CRUD", "Validation", "Workflow", "Query", "E2E", "Other")


def run(cmd: list[str], cwd: Path) -> str:
    return subprocess.check_output(cmd, cwd=cwd, text=True, errors="replace")


def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(8):
        if (cur / ".git").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    raise RuntimeError(f"git repo root not found above {start}")


def iso_today() -> dt.date:
    return dt.date.today()


def parse_date(s: str) -> dt.date:
    return dt.date.fromisoformat(s[:10])


def norm_file(path: str | None, module_rel: str) -> str | None:
    """Map monorepo path → inventory-relative src/test/... path."""
    if not path:
        return None
    p = path.replace("\\", "/")
    marker = "/src/test/"
    if marker in p:
        return "src/test/" + p.split(marker, 1)[1]
    if p.startswith("src/test/"):
        return p
    # commit path sometimes relative to module
    mod = module_rel.rstrip("/") + "/"
    if p.startswith(mod):
        rest = p[len(mod) :]
        if rest.startswith("src/test/"):
            return rest
    return None


def area_from_file(file: str | None) -> str:
    if not file:
        return "unknown"
    parts = file.split("/")
    try:
        i = parts.index("steps")
        if i + 1 < len(parts):
            return parts[i + 1]
    except ValueError:
        pass
    return "unknown"


def week_start(d: dt.date) -> dt.date:
    return d - dt.timedelta(days=d.weekday())  # Monday


def load_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def inventory_index(inv: dict | None) -> dict[tuple[str, str], dict]:
    out: dict[tuple[str, str], dict] = {}
    if not inv:
        return out
    for row in inv.get("rows") or []:
        key = (row.get("file") or "", row.get("name") or "")
        if key[0] and key[1]:
            out[key] = row
    return out


def scan_first_seen(
    repo: Path,
    module_rel: str,
    since: dt.date,
) -> list[dict]:
    """Walk commits oldest→newest; record first appearance of each feature def."""
    src_path = f"{module_rel}/src/test"
    log = run(
        [
            "git",
            "log",
            f"--since={since.isoformat()}",
            "--pretty=format:%H\t%ad\t%an\t%s",
            "--date=short",
            "--",
            src_path,
        ],
        repo,
    )
    commits: list[tuple[str, str, str, str]] = []
    for line in log.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t", 3)
        if len(parts) < 4:
            continue
        commits.append((parts[0], parts[1], parts[2], parts[3]))

    first: dict[tuple[str, str], dict] = {}
    # oldest first so first_seen is true introduction
    for sha, day, author, subject in reversed(commits):
        tickets = sorted({t.upper() for t in TICKET_RE.findall(subject)})
        try:
            diff = run(
                ["git", "show", sha, "-U0", "--", src_path],
                repo,
            )
        except subprocess.CalledProcessError:
            continue
        cur_file: str | None = None
        for line in diff.splitlines():
            if line.startswith("+++ b/"):
                cur_file = norm_file(line[6:], module_rel)
                continue
            m = ADD_RE.match(line)
            if not m:
                continue
            name = m.group(1)
            file = cur_file or ""
            key = (file, name)
            if key in first:
                continue
            first[key] = {
                "name": name,
                "file": file or None,
                "date": day,
                "author": author,
                "subject": subject,
                "commit": sha[:10],
                "tickets": tickets,
                "area": area_from_file(file),
            }
    return sorted(first.values(), key=lambda x: (x["date"], x["area"], x["name"]), reverse=True)


def enrich(additions: list[dict], idx: dict[tuple[str, str], dict]) -> list[dict]:
    out = []
    for a in additions:
        row = idx.get((a.get("file") or "", a["name"]))
        # fallback: name-only if unique
        if not row:
            matches = [r for (f, n), r in idx.items() if n == a["name"]]
            if len(matches) == 1:
                row = matches[0]
        item = dict(a)
        if row:
            item["area"] = row.get("area") or item["area"]
            item["spec"] = row.get("spec")
            item["type"] = row.get("type") or "Other"
            item["cases"] = int(row.get("cases") or 1)
            item["tags"] = row.get("tags") or []
            item["ignored"] = bool(row.get("ignored"))
            item["inventoryHref"] = (
                "inventory.html?q=" + _urlquote(row.get("name") or a["name"])
            )
        else:
            item["type"] = item.get("type") or "Other"
            item["cases"] = 1
            item["tags"] = []
            item["ignored"] = False
            item["inventoryHref"] = "inventory.html?q=" + _urlquote(a["name"])
            item["gone"] = True  # added then removed / renamed
        out.append(item)
    return out


def _urlquote(s: str) -> str:
    from urllib.parse import quote

    return quote(s, safe="")


def window_payload(additions: list[dict], start: dt.date, end: dt.date) -> dict:
    rows = [a for a in additions if start <= parse_date(a["date"]) <= end]
    by_type = collections.Counter(a.get("type") or "Other" for a in rows)
    by_area = collections.Counter(a.get("area") or "unknown" for a in rows)
    tickets: dict[str, dict] = {}
    for a in rows:
        for t in a.get("tickets") or []:
            slot = tickets.setdefault(
                t, {"key": t, "featuresAdded": 0, "casesAdded": 0, "latestDate": a["date"]}
            )
            slot["featuresAdded"] += 1
            slot["casesAdded"] += int(a.get("cases") or 1)
            if a["date"] > slot["latestDate"]:
                slot["latestDate"] = a["date"]
    ticket_list = sorted(
        tickets.values(),
        key=lambda x: (-x["featuresAdded"], x["key"]),
    )
    return {
        "from": start.isoformat(),
        "to": end.isoformat(),
        "featuresAdded": len(rows),
        "casesAdded": sum(int(a.get("cases") or 1) for a in rows),
        "areasTouched": len(by_area),
        "ticketsTouched": len(ticket_list),
        "byType": {t: by_type.get(t, 0) for t in TYPE_ORDER if by_type.get(t)},
        "byArea": [
            {"area": k, "featuresAdded": v}
            for k, v in sorted(by_area.items(), key=lambda kv: (-kv[1], kv[0]))
        ],
        "tickets": ticket_list,
        "additions": rows,
    }


def week_series(additions: list[dict], end: dt.date, weeks: int = 12) -> list[dict]:
    start = week_start(end) - dt.timedelta(weeks=weeks - 1)
    buckets: dict[str, dict] = {}
    cur = start
    while cur <= week_start(end):
        key = cur.isoformat()
        buckets[key] = {
            "weekStart": key,
            "featuresAdded": 0,
            "casesAdded": 0,
        }
        cur += dt.timedelta(days=7)
    for a in additions:
        d = parse_date(a["date"])
        if d < start or d > end:
            continue
        key = week_start(d).isoformat()
        if key not in buckets:
            continue
        buckets[key]["featuresAdded"] += 1
        buckets[key]["casesAdded"] += int(a.get("cases") or 1)
    return [buckets[k] for k in sorted(buckets)]


def merge_snapshot(prev: dict | None, inv: dict | None, cov: dict | None, today: dt.date) -> list[dict]:
    snaps = list((prev or {}).get("snapshots") or [])
    # keep last ~180 days
    cut = (today - dt.timedelta(days=180)).isoformat()
    snaps = [s for s in snaps if (s.get("date") or "") >= cut]

    point = {
        "date": today.isoformat(),
        "features": (inv or {}).get("features"),
        "cases": (inv or {}).get("cases"),
        "specs": (inv or {}).get("specs"),
        "areas": (inv or {}).get("areas"),
    }
    if cov and isinstance(cov.get("summary"), dict):
        s = cov["summary"]
        point["coveragePercent"] = s.get("coveragePercent")
        point["tested"] = s.get("tested")
        point["untested"] = s.get("untested")
        point["nonDeprecated"] = s.get("nonDeprecated")

    # replace same-day snapshot
    snaps = [s for s in snaps if s.get("date") != today.isoformat()]
    if any(point.get(k) is not None for k in ("features", "cases", "coveragePercent")):
        snaps.append(point)
    snaps.sort(key=lambda s: s.get("date") or "")
    return snaps


def coverage_delta(snaps: list[dict], days: int, today: dt.date) -> dict | None:
    if not snaps:
        return None
    current = next((s for s in reversed(snaps) if s.get("coveragePercent") is not None), None)
    if not current:
        return None
    target = (today - dt.timedelta(days=days)).isoformat()
    prior = None
    for s in snaps:
        if s.get("date", "") <= target and s.get("coveragePercent") is not None:
            prior = s
    if not prior or prior["date"] == current["date"]:
        # nearest older with coverage
        older = [
            s
            for s in snaps
            if s.get("date", "") < current["date"] and s.get("coveragePercent") is not None
        ]
        prior = older[-1] if older else None
    if not prior:
        return {
            "currentPercent": current.get("coveragePercent"),
            "priorPercent": None,
            "deltaPoints": None,
            "priorDate": None,
            "currentDate": current.get("date"),
            "note": "Need another publish day before coverage delta is available.",
        }
    cur_p = float(current["coveragePercent"])
    pri_p = float(prior["coveragePercent"])
    return {
        "currentPercent": cur_p,
        "priorPercent": pri_p,
        "deltaPoints": round(cur_p - pri_p, 1),
        "priorDate": prior.get("date"),
        "currentDate": current.get("date"),
        "testedDelta": _safe_sub(current.get("tested"), prior.get("tested")),
        "untestedDelta": _safe_sub(current.get("untested"), prior.get("untested")),
    }


def _safe_sub(a, b):
    if a is None or b is None:
        return None
    return int(a) - int(b)


def build(repo: Path, module_root: Path, since: dt.date) -> dict:
    today = iso_today()
    try:
        module_rel = module_root.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        module_rel = "gateway/unifiedApi/NexusApiRegressionTests"

    inv = load_json(INVENTORY)
    cov = load_json(COVERAGE)
    prev = load_json(OUT)
    idx = inventory_index(inv)

    raw = scan_first_seen(repo, module_rel, since)
    additions = enrich(raw, idx)

    windows = {}
    for key, days in WINDOWS:
        start = today - dt.timedelta(days=days - 1)
        windows[key] = window_payload(additions, start, today)

    snaps = merge_snapshot(prev, inv, cov, today)
    cov14 = coverage_delta(snaps, 14, today)

    return {
        "generatedAt": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "methodology": (
            "Feature additions are first appearances of Spock `def \"…\"()` methods in "
            "git history under src/test (*TestSteps.groovy). Case counts and types come "
            "from the current inventory join. Coverage deltas use an append-only snapshot "
            "series written each time this generator runs."
        ),
        "since": since.isoformat(),
        "defaultWindow": "90d",
        "windows": windows,
        "weeks": week_series(additions, today, weeks=12),
        "snapshots": snaps,
        "coverage": {
            "currentPercent": (cov or {}).get("summary", {}).get("coveragePercent"),
            "tested": (cov or {}).get("summary", {}).get("tested"),
            "untested": (cov or {}).get("summary", {}).get("untested"),
            "delta14d": cov14,
        },
        "inventory": {
            "features": (inv or {}).get("features"),
            "cases": (inv or {}).get("cases"),
            "specs": (inv or {}).get("specs"),
            "areas": (inv or {}).get("areas"),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--since",
        default="2026-01-01",
        help="Earliest commit date to scan (YYYY-MM-DD)",
    )
    ap.add_argument(
        "--module-root",
        type=Path,
        default=DEFAULT_MODULE_ROOT,
        help="NexusApiRegressionTests module root",
    )
    ap.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Git repo root (auto-detected)",
    )
    args = ap.parse_args()
    module_root = args.module_root.resolve()
    repo = (args.repo_root or find_repo_root(module_root)).resolve()
    since = parse_date(args.since)

    print(f"Scanning git history in {repo} since {since} …", file=sys.stderr)
    data = build(repo, module_root, since)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    w = data["windows"]["14d"]
    print(
        f"Wrote {OUT.relative_to(DASHBOARD_ROOT)} — "
        f"14d: +{w['featuresAdded']} features / +{w['casesAdded']} cases "
        f"across {w['areasTouched']} areas, {w['ticketsTouched']} tickets",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
