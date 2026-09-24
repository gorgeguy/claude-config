#!/usr/bin/env python3
"""Analyze tool-call durations in a Claude Code session log.

Usage:
    session-timing.py <session.jsonl>             # one file
    session-timing.py --latest                    # latest session in $PWD's project
    session-timing.py --latest --top 30           # show 30 slowest calls
    session-timing.py --latest --watch            # tail -f mode (re-runs every 5s)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def parse_ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def project_slug(cwd: Path) -> str:
    """Convert /Users/jon/g/foo/bar.wt1 → -Users-jon-g-foo-bar-wt1 (Claude Code's scheme).

    Both ``/`` and ``.`` are replaced with ``-``.
    """
    return "-" + str(cwd).strip("/").replace("/", "-").replace(".", "-")


def latest_session_log(cwd: Path) -> Path | None:
    project_dir = Path.home() / ".claude" / "projects" / project_slug(cwd)
    if not project_dir.exists():
        return None
    candidates = sorted(project_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    return candidates[-1] if candidates else None


def analyze(log_path: Path, top: int) -> None:
    tool_uses: dict[str, dict] = {}
    tool_results: dict[str, datetime] = {}
    first_ts = last_ts = None

    with log_path.open() as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue

            ts_str = rec.get("timestamp")
            if ts_str:
                ts_dt = parse_ts(ts_str)
                if first_ts is None:
                    first_ts = ts_dt
                last_ts = ts_dt
            else:
                ts_dt = None

            if rec.get("type") == "assistant":
                content = rec.get("message", {}).get("content", [])
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "tool_use":
                            tool_uses[block["id"]] = {
                                "name": block.get("name"),
                                "input": block.get("input", {}),
                                "ts": ts_dt,
                            }
            elif rec.get("type") == "user":
                content = rec.get("message", {}).get("content", [])
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "tool_result":
                            tool_results[block["tool_use_id"]] = ts_dt

    durations: list[tuple[float, str, dict]] = []
    for tid, use in tool_uses.items():
        end = tool_results.get(tid)
        if end and use["ts"]:
            durations.append(((end - use["ts"]).total_seconds(), use["name"], use["input"]))
    durations.sort(key=lambda d: d[0], reverse=True)

    print(f"\nSession: {log_path.name}")
    if first_ts and last_ts:
        span = (last_ts - first_ts).total_seconds()
        print(f"Wall:    {first_ts.isoformat()}  →  {last_ts.isoformat()}")
        print(f"Span:    {span / 60:.1f} min")
    print(f"Calls:   {len(tool_uses)} (matched {len(durations)})")
    print()

    by_name: dict[str, dict] = defaultdict(lambda: {"count": 0, "total": 0.0})
    for d, name, _ in durations:
        by_name[name]["count"] += 1
        by_name[name]["total"] += d

    print("=== Time by tool ===")
    for name, stats in sorted(by_name.items(), key=lambda x: -x[1]["total"]):
        avg = stats["total"] / stats["count"]
        print(
            f"  {name:20s} n={stats['count']:4d}  "
            f"total={stats['total'] / 60:6.1f}m  avg={avg:7.2f}s"
        )

    print(f"\n=== Top {top} slowest individual calls ===")
    for d, name, inp in durations[:top]:
        desc = inp.get("command") or inp.get("file_path") or inp.get("pattern") or str(inp)
        if len(desc) > 90:
            desc = desc[:87] + "..."
        print(f"  {d / 60:5.1f}m  {name:14s}  {desc}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("log", nargs="?", help="Path to session JSONL")
    p.add_argument("--latest", action="store_true", help="Use latest session for $PWD's project")
    p.add_argument("--top", type=int, default=15, help="Slowest N calls to show (default 15)")
    p.add_argument("--watch", action="store_true", help="Re-run every 5 seconds")
    args = p.parse_args()

    if args.latest:
        log = latest_session_log(Path.cwd())
        if log is None:
            print("No session log found for current project.", file=sys.stderr)
            return 1
    elif args.log:
        log = Path(args.log)
    else:
        p.print_help()
        return 1

    while True:
        analyze(log, args.top)
        if not args.watch:
            return 0
        print("\n--- (refreshing in 5s, ctrl-c to exit) ---")
        time.sleep(5)


if __name__ == "__main__":
    sys.exit(main())
