"""Paths + constants for the second-brain MCP server.

Override via env vars (SECOND_BRAIN_VAULT). Nothing here is secret — Notion /
Calendar credentials live in env (via mcp/.env, gitignored), never in the vault.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

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

# --- Notion push (sync_plans) -----------------------------------------------
# Secrets/ids come from env (never the repo). Set these to enable the live path;
# without them, sync_plans still runs in dry_run (builds the payload, no writes).
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")            # internal integration secret
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")  # the Task List database uuid
# Notion's 2025-09-03 API split a database's schema/rows into "data sources"
# (a database can have several); `databases.retrieve` no longer returns
# `properties` — schema reads + page-parents must target the data source.
NOTION_DATA_SOURCE_ID = os.environ.get("NOTION_DATA_SOURCE_ID")

# Value maps: vault value -> the live Task List's EXISTING option (labels, not
# secret). sync_plans writes ONLY these and preflights they exist — it never
# creates or renames an option (that would be a schema change).
NOTION_CATEGORY_MAP = {
    "Staff Track": "Staff Track",
    "🎓 Learning": "🎓 Learning",
    "💻 ML Building": "💻 ML Building",
    "💪 Fitness": "💪 Fitness",
    "Family": "❤️ Family/Friends",
    "Entertainment": "🔋Entertainment",
}
NOTION_PRIORITY_MAP = {
    "💎 Top Priority": "💎 Top Priority ",           # NB: trailing space in Notion
    "‼️ Important + Urgent": "‼️ Important + Urgent",
    "🌱 Important + Not Urgent": "🌱 Important + Not Urgent",
    "⚡️ Quick Task": "⚡️ Quick Task",
    "🧤 Errand": "🧤 Errand",
}
NOTION_STATUS_SET = {"Backlog", "Not started", "In progress", "Done"}  # never write "Removed"
