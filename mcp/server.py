"""second-brain MCP server — v1: the time-blocking planner tools.

Mechanical data-access only. The plan-day skill orchestrates these; the server
holds no scheduling logic. Two levels: **containers** (`type: task` files, the
phases) and **steps** (their `- [ ]` checkbox lines, the schedulable units).
Run: `python server.py` (stdio transport).
"""
from mcp.server.mcpserver import MCPServer  # MCP SDK 2.x (was FastMCP in v1)

import tasks as _tasks       # local modules (run server.py as a script)
import schedule as _schedule
import projects as _projects
import notion as _notion

mcp = MCPServer("second-brain")


# ---- steps (the schedulable units) -----------------------------------------
@mcp.tool()
def list_tasks(status: str | None = None, done: bool | None = None,
               cycle: str | None = None, roadmap: str | None = None,
               quarter: str | None = None, project: str | None = None,
               week: int | None = None) -> list[dict]:
    """List step checkboxes across all container files, each with its inherited
    context (project, cycle, roadmap, priority, `kind`, and per-step `size`/`freq`).
    Filters: `status` (container rollup), `done` (step completion — pass False for
    the plannable backlog), `cycle`/`roadmap`/`quarter`, `project` (container id or
    title substring), `week` (only containers live that cycle-week). A step whose
    container is `kind: habit` recurs (cadence in `freq`) — track adherence, not
    done/total. Each step's `id` is "<path>:<line>"."""
    return _tasks.list_tasks(status=status, done=done, cycle=cycle, roadmap=roadmap,
                             quarter=quarter, project=project, week=week)


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
                  roadmap: str | None = None, quarter: str | None = None,
                  week: int | None = None) -> list[dict]:
    """List container files (the phases) with frontmatter + done/total step
    counts. `week` filters to containers live that cycle-week. `kind: habit`
    containers are recurring (adherence, not done/total). Use for cycle-level
    planning; use list_tasks for daily scheduling."""
    return _tasks.list_projects(status=status, cycle=cycle, roadmap=roadmap,
                                quarter=quarter, week=week)


@mcp.tool()
def update_project(project_id: str, fields: dict) -> dict | None:
    """Patch a container's frontmatter (status, start_week, notion_id, …) by its
    uuid. Bumps timestamp."""
    return _tasks.update_project(project_id, fields)


@mcp.tool()
def add_step(project_id: str, title: str, size: str | None = None,
             due: str | None = None, resource: str | None = None,
             freq: str | None = None) -> dict | None:
    """Append a new step to a container (after its last step, so existing step
    ids / blocks don't shift). `size` is S/M/L; `freq` sets a habit cadence
    (e.g. '3x/week'). Returns the created step."""
    return _tasks.add_step(project_id, title, size=size, due=due,
                           resource=resource, freq=freq)


# ---- project sync (read an external repo's git-tracked status file) --------
@mcp.tool()
def read_project_status(project_id: str | None = None,
                        repo_path: str | None = None,
                        status_file: str | None = None) -> dict:
    """Read a linked project's status contract as a sync feed — the raw
    frontmatter + body of its `.second-brain/status.md` (or a container's
    `status_file:` override), with NO interpretation. Pass a container
    `project_id` (uses its `repo:` + optional `status_file:` fields) or an
    explicit `repo_path`. The skill interprets the prose (schema-tolerant)."""
    return _projects.read_project_status(project_id=project_id, repo_path=repo_path,
                                          status_file=status_file)


# ---- Notion push (tactical per-day dashboard, no container-level page) -----
@mcp.tool()
def sync_occurrences(week_start: str, dry_run: bool = True) -> dict:
    """Push one standalone Notion row per schedulable item this week: a
    `kind: habit` step's scheduled Time-Blocks slot, or a regular step whose
    `due:` date falls in this week. Each row = Title, Date, Priority, Category,
    Status — a purely tactical "what to do, which day" dashboard; no
    container-level overview page. Upserted by (Title, Date) — refreshes an
    existing row's Status (so ticking a step done and re-syncing updates
    Notion) instead of duplicating. Nothing is written back to the vault.
    `dry_run=True` (default) returns the planned rows without touching Notion."""
    return _notion.sync_occurrences(week_start=week_start, dry_run=dry_run)


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
