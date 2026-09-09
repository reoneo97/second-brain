#!/usr/bin/env python3
"""Read back mcp/logs/tool_calls.jsonl and summarize it — an on-demand audit,
not a live dashboard (see logging_utils.py for why). Run from mcp/:

    .venv/bin/python3 scripts/audit_log.py [--since YYYY-MM-DD] [--session-gap-min 20]

Sessions are inferred purely from time gaps between consecutive calls, since
MCP's protocol carries no skill/session id — a `/plan-week` run has a
distinctive shape (list_projects -> read_time_blocks -> schedule_task*N ->
sync_occurrences), so it's usually recognizable by eye even ungrouped.
"""
import argparse
import datetime
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

LOG_PATH = Path(__file__).parent.parent / "logs" / "tool_calls.jsonl"


def load(since: str | None) -> list[dict]:
    if not LOG_PATH.exists():
        print(f"no log yet at {LOG_PATH}")
        return []
    cutoff = datetime.date.fromisoformat(since) if since else None
    out = []
    for line in LOG_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)
        if cutoff and datetime.datetime.fromisoformat(entry["ts"]).date() < cutoff:
            continue
        out.append(entry)
    return out


def sessions(entries: list[dict], gap_min: int) -> list[list[dict]]:
    """Group calls into sessions by time gap -- a heuristic stand-in for the
    session id the MCP protocol doesn't give us."""
    out, cur = [], []
    prev_ts = None
    for e in entries:
        ts = datetime.datetime.fromisoformat(e["ts"])
        if prev_ts and (ts - prev_ts).total_seconds() > gap_min * 60:
            out.append(cur)
            cur = []
        cur.append(e)
        prev_ts = ts
    if cur:
        out.append(cur)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", help="only calls on/after this date (YYYY-MM-DD)")
    ap.add_argument("--session-gap-min", type=int, default=20,
                    help="minutes of silence that starts a new inferred session")
    args = ap.parse_args()

    entries = load(args.since)
    if not entries:
        return

    print(f"{len(entries)} calls, {entries[0]['ts']} -> {entries[-1]['ts']}\n")

    by_tool = Counter(e["tool"] for e in entries)
    errors_by_tool = Counter(e["tool"] for e in entries if not e["ok"])
    print("Calls per tool (errors in parens):")
    for tool, n in by_tool.most_common():
        err = errors_by_tool.get(tool, 0)
        print(f"  {tool:24s} {n:4d}" + (f"  ({err} errors)" if err else ""))

    total_errors = sum(errors_by_tool.values())
    if total_errors:
        print(f"\n{total_errors} errors total:")
        for e in entries:
            if not e["ok"]:
                print(f"  {e['ts']}  {e['tool']}({e['args']}) -> {e['error']}")

    # repeated identical failure = the exact bug pattern that bit sync_plans /
    # the stale-MCP-schema issue earlier this session: same tool+args+error
    # more than once means "this was broken, not a one-off fluke."
    dupes = Counter((e["tool"], json.dumps(e["args"], sort_keys=True, default=str), e["error"])
                    for e in entries if not e["ok"])
    repeats = {k: v for k, v in dupes.items() if v > 1}
    if repeats:
        print("\nRepeated identical failures (likely a real bug, not a fluke):")
        for (tool, args_json, error), n in repeats.items():
            print(f"  {n}x  {tool}({args_json}) -> {error}")

    slow = sorted(entries, key=lambda e: -e["duration_ms"])[:5]
    print("\nSlowest calls:")
    for e in slow:
        print(f"  {e['duration_ms']:7.1f}ms  {e['tool']}({e['args']})")

    sess = sessions(entries, args.session_gap_min)
    print(f"\n{len(sess)} inferred sessions (gap > {args.session_gap_min}min):")
    for s in sess:
        span = f"{s[0]['ts']} -> {s[-1]['ts']}"
        shape = " -> ".join(e["tool"] for e in s)
        errs = sum(1 for e in s if not e["ok"])
        print(f"  [{span}] {len(s)} calls" + (f", {errs} errors" if errs else "")
              + f"\n    {shape}")


if __name__ == "__main__":
    sys.exit(main())
