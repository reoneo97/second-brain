"""second-brain MCP server — v1: the time-blocking planner tools.

Mechanical data-access only. The plan-day skill orchestrates these; the server
holds no scheduling logic. Run: `python -m mcp.server` (stdio transport).
"""
from mcp.server.fastmcp import FastMCP  # the installed MCP SDK, not this dir

import tasks as _tasks       # local modules (run server.py as a script)
import schedule as _schedule

mcp = FastMCP("second-brain")


# ---- tasks -----------------------------------------------------------------
@mcp.tool()
def list_tasks(status: str | None = None, cycle: str | None = None,
               week: int | None = None, date: str | None = None,
               roadmap: str | None = None) -> list[dict]:
    """List type:task files, optionally filtered. `week` matches
    start_week<=week<=end_week; `date` matches the scheduled day (YYYY-MM-DD)."""
    return _tasks.list_tasks(status=status, cycle=cycle, week=week, date=date, roadmap=roadmap)


@mcp.tool()
def get_task(task_id: str) -> dict | None:
    """Fetch a single task by its `id`."""
    return _tasks.get_task(task_id)


@mcp.tool()
def update_task(task_id: str, fields: dict) -> dict | None:
    """Patch frontmatter fields on a task (e.g. status, date). Bumps timestamp."""
    return _tasks.update_task(task_id, fields)


# ---- scheduling (Time Blocks data.json) ------------------------------------
@mcp.tool()
def read_time_blocks(week_start: str | None = None, date: str | None = None) -> list[dict]:
    """Read scheduled blocks. Filter by `week_start` (Monday ISO) or `date`.
    Blocks with source='gcal' are your calendar busy-times."""
    return _schedule.read_time_blocks(week_start=week_start, date=date)


@mcp.tool()
def schedule_task(task_id: str, date: str, start_hour: int, start_minute: int,
                  duration_minutes: int | None = None) -> dict:
    """Write a time block for a task into the Time Blocks plugin. Duration
    defaults from the task's size. After scheduling, run `time-blocks:refresh`
    in Obsidian to re-render."""
    return _schedule.schedule_task(task_id, date, start_hour, start_minute, duration_minutes)


if __name__ == "__main__":
    mcp.run()
