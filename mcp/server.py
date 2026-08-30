"""second-brain MCP server — v1: the time-blocking planner tools.

Mechanical data-access only. The plan-day skill orchestrates these; the server
holds no scheduling logic. Two levels: **containers** (`type: task` files, the
phases) and **steps** (their `- [ ]` checkbox lines, the schedulable units).
Run: `python server.py` (stdio transport).
"""
from mcp.server.mcpserver import MCPServer  # MCP SDK 2.x (was FastMCP in v1)

import tasks as _tasks       # local modules (run server.py as a script)
import schedule as _schedule

mcp = MCPServer("second-brain")


# ---- steps (the schedulable units) -----------------------------------------
@mcp.tool()
def list_tasks(status: str | None = None, done: bool | None = None,
               cycle: str | None = None, roadmap: str | None = None,
               quarter: str | None = None, project: str | None = None) -> list[dict]:
    """List step checkboxes across all container files, each with its inherited
    context (project, cycle, roadmap, priority, …). Filters: `status` (container
    rollup), `done` (step completion — pass False for the plannable backlog),
    `cycle`/`roadmap`/`quarter`, `project` (container id or title substring).
    Each step's `id` is "<path>:<line>" — pass it to schedule_task/update_task."""
    return _tasks.list_tasks(status=status, done=done, cycle=cycle,
                             roadmap=roadmap, quarter=quarter, project=project)


@mcp.tool()
def get_task(task_id: str) -> dict | None:
    """One step by its "<path>:<line>" id (a container uuid also works — returns
    its first unchecked step)."""
    return _tasks.get_task(task_id)


@mcp.tool()
def update_task(task_id: str, fields: dict) -> dict | None:
    """Patch a step's checkbox line. Fields: `done` (bool — checks the box),
    `size` (S/M/L), `due` (YYYY-MM-DD), `title`, `resource`. Bumps the
    container's timestamp."""
    return _tasks.update_task(task_id, fields)


# ---- containers (phases; cycle planning + sync) ----------------------------
@mcp.tool()
def list_projects(status: str | None = None, cycle: str | None = None,
                  roadmap: str | None = None, quarter: str | None = None) -> list[dict]:
    """List container files (the phases) with frontmatter + done/total step
    counts. Use for cycle-level planning; use list_tasks for daily scheduling."""
    return _tasks.list_projects(status=status, cycle=cycle,
                                roadmap=roadmap, quarter=quarter)


@mcp.tool()
def update_project(project_id: str, fields: dict) -> dict | None:
    """Patch a container's frontmatter (status, start_week, notion_id, …) by its
    uuid. Bumps timestamp."""
    return _tasks.update_project(project_id, fields)


# ---- scheduling (Time Blocks data.json) ------------------------------------
@mcp.tool()
def read_time_blocks(week_start: str | None = None, date: str | None = None) -> list[dict]:
    """Read scheduled blocks. Filter by `week_start` (Monday ISO) or `date`.
    Blocks with source='gcal' are your calendar busy-times."""
    return _schedule.read_time_blocks(week_start=week_start, date=date)


@mcp.tool()
def schedule_task(task_id: str, date: str, start_hour: int, start_minute: int,
                  duration_minutes: int | None = None) -> dict:
    """Write a time block for a step into the Time Blocks plugin. `task_id` is a
    step's "<path>:<line>" id. Duration defaults from the step's size. After
    scheduling, run `time-blocks:refresh` in Obsidian to re-render."""
    return _schedule.schedule_task(task_id, date, start_hour, start_minute, duration_minutes)


if __name__ == "__main__":
    mcp.run()
