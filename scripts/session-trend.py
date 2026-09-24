#!/usr/bin/env python3
"""Aggregate timing across all session files in a project to spot regressions.

Usage:
    session-trend.py                             # current project
    session-trend.py --project /path/to/repo
    session-trend.py --last 30                   # only last 30 sessions
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def parse_ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def project_slug(cwd: Path) -> str:
    """Convert /Users/jon/g/foo/bar.wt1 → -Users-jon-g-foo-bar-wt1 (Claude Code's scheme).

    Both ``/`` and ``.`` are replaced with ``-``.
    """
    return "-" + str(cwd).strip("/").replace("/", "-").replace(".", "-")


def analyze_file(path: Path) -> dict:
    tool_uses: dict[str, dict] = {}
    tool_results: dict[str, datetime] = {}
    has_taskoutput = False
    bg_count = 0

    with path.open() as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts_str = rec.get("timestamp")
            ts_dt = parse_ts(ts_str) if ts_str else None
            if rec.get("type") == "assistant":
                content = rec.get("message", {}).get("content", [])
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "tool_use":
                            name = block.get("name", "")
                            tool_uses[block["id"]] = {"name": name, "ts": ts_dt}
                            if name == "TaskOutput":
                                has_taskoutput = True
            elif rec.get("type") == "user":
                content = rec.get("message", {}).get("content", [])
                if isinstance(content, list):
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "tool_result":
                            tool_results[block["tool_use_id"]] = ts_dt
                            c = block.get("content", "")
                            txt = (
                                " ".join(str(x.get("text", "")) for x in c if isinstance(x, dict))
                                if isinstance(c, list)
                                else str(c)
                            )
                            if "running in background" in txt.lower():
                                bg_count += 1

    durs: list[tuple[float, str]] = []
    for tid, use in tool_uses.items():
        end = tool_results.get(tid)
        if end and use["ts"]:
            durs.append(((end - use["ts"]).total_seconds(), use["name"]))

    bash_durs = sorted(d for d, n in durs if n == "Bash")
    return {
        "calls": len(tool_uses),
        "wall_min": sum(d for d, _ in durs) / 60 if durs else 0,
        "bash_avg": sum(bash_durs) / len(bash_durs) if bash_durs else 0,
        "bash_p95": bash_durs[int(0.95 * len(bash_durs))] if bash_durs else 0,
        "bash_max": bash_durs[-1] if bash_durs else 0,
        "bg_count": bg_count,
        "task_output": has_taskoutput,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--project", help="Project directory (defaults to $PWD)")
    p.add_argument(
        "--project-slug",
        help="Project slug (e.g. -Users-jon-g-foo-bar-wt1). Use this when the slug-to-path "
        "inversion is ambiguous (dots vs. dashes). Bypasses --project entirely.",
    )
    p.add_argument("--last", type=int, default=30, help="Number of recent sessions to show")
    args = p.parse_args()

    if args.project_slug:
        proj = Path.home() / ".claude" / "projects" / args.project_slug
    else:
        cwd = Path(args.project) if args.project else Path.cwd()
        proj = Path.home() / ".claude" / "projects" / project_slug(cwd)

    if not proj.exists():
        print(f"No session directory: {proj}", file=sys.stderr)
        return 1

    files = sorted(proj.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    files = files[-args.last:]

    print(
        f"{'date':19s}  {'calls':>6s}  {'wall_m':>7s}  "
        f"{'bash_avg':>9s}  {'bash_p95':>9s}  {'bg':>3s}  {'task_out':>9s}"
    )
    print("-" * 80)
    for f in files:
        s = analyze_file(f)
        if s["calls"] == 0:
            continue
        mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        marker = "YES" if s["task_output"] else "."
        print(
            f"{mtime}  {s['calls']:>6d}  {s['wall_min']:>6.1f}m  "
            f"{s['bash_avg']:>8.2f}s  {s['bash_p95']:>8.1f}s  {s['bg_count']:>3d}  {marker:>9s}"
        )

    print("\nLook for: rows where bash_avg or bash_p95 jumps relative to neighbors,")
    print("or where bg_count > 0 / task_out=YES (the regression markers).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
