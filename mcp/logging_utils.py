"""Durable, append-only playback log for every MCP tool call.

Deliberately not a metrics/dashboard stack (Prometheus/Grafana were cut from
EchoVault this same session for being too heavy for a personal-scale project)
-- one JSONL line per call, read back on demand with audit_log.py. Mirrors
EchoVault's own backend/logs/requests.jsonl + build_historical_fixtures.py
pattern: log everything cheaply, analyze after the fact, not live.

No skill/session id is captured -- MCP's protocol doesn't tell the server
which skill made a call. audit_log.py clusters by time-gap instead; if that
turns out not to be good enough, skills passing an explicit session tag is
the fallback (touches every tool signature, so deferred until proven needed).
"""
import datetime
import functools
import inspect
import json
import time
from pathlib import Path

LOG_PATH = Path(__file__).parent / "logs" / "tool_calls.jsonl"


def _append(entry: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=str) + "\n")


def logged(fn):
    """Wrap an MCP tool function: log its args, outcome, and duration. Apply
    UNDER @mcp.tool() (i.e. `@mcp.tool()` then `@logged`, decorators read
    bottom-up) so the logged name/signature is what the tool actually is."""
    sig = inspect.signature(fn)

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        try:
            bound = sig.bind_partial(*args, **kwargs)
            all_args = dict(bound.arguments)
        except TypeError:
            all_args = kwargs  # fall back rather than fail the call over logging
        entry = {"ts": datetime.datetime.now().isoformat(timespec="seconds"),
                 "tool": fn.__name__, "args": all_args}
        try:
            result = fn(*args, **kwargs)
            entry["ok"] = True
            return result
        except Exception as e:
            entry["ok"] = False
            entry["error"] = f"{type(e).__name__}: {e}"
            raise
        finally:
            entry["duration_ms"] = round((time.monotonic() - start) * 1000, 1)
            _append(entry)
    return wrapper
