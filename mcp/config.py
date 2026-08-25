"""Paths + constants for the second-brain MCP server.

Override via env vars (SECOND_BRAIN_VAULT). Nothing here is secret — Notion /
Calendar credentials (added later) live in env, never in the vault.
"""
import os
from pathlib import Path

VAULT = Path(
    os.environ.get(
        "SECOND_BRAIN_VAULT",              # set this to your vault path
        Path.home() / "second-brain" / "notes",
    )
).expanduser()

TASKS_DIR = VAULT / "planning" / "tasks"          # type:task files (canonical)
TIMEBLOCKS_JSON = VAULT / ".obsidian" / "plugins" / "time-blocks" / "data.json"

# Time Blocks plugin conventions (from its AGENTS.md)
SIZE_MINUTES = {"S": 30, "M": 60, "L": 120}       # task size -> duration
TASK_BLOCK_COLOR = "#7B61FF"                        # plugin default for task blocks
