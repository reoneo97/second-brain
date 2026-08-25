"""type:task file access — query and patch the canonical task files.

A "task" dict = its frontmatter + {"path": relative_path, "line": <task-line>}.
No scheduling logic here (that's the plan-day skill); these are mechanical.
"""
import datetime
import uuid
from pathlib import Path

import config
from vault import parse_note, write_note


def _rel(p: Path) -> str:
    return str(p.relative_to(config.VAULT))


def _load_all() -> list[dict]:
    tasks = []
    if not config.TASKS_DIR.exists():
        return tasks
    for p in sorted(config.TASKS_DIR.glob("*.md")):
        if p.name == "_index.md":
            continue
        fm, _ = parse_note(p)
        if fm.get("type") != "task":
            continue
        # taskId for the Time Blocks plugin is "<path>:<line>"; the frontmatter
        # `type: task` sits on line 2, a stable anchor for the whole-file task.
        tasks.append({**fm, "path": _rel(p), "line": 2})
    return tasks


def list_tasks(status=None, cycle=None, week=None, date=None, roadmap=None) -> list[dict]:
    """Query tasks. week matches start_week<=week<=end_week; date matches the
    scheduled day. Any arg left None is ignored."""
    out = []
    for t in _load_all():
        if status and t.get("status") != status:
            continue
        if cycle and t.get("cycle") != cycle:
            continue
        if roadmap and t.get("roadmap") != roadmap:
            continue
        if date and str(t.get("date")) != str(date):
            continue
        if week is not None:
            sw, ew = t.get("start_week"), t.get("end_week")
            if sw is None or ew is None or not (sw <= week <= ew):
                continue
        out.append(t)
    return out


def get_task(task_id: str) -> dict | None:
    for t in _load_all():
        if t.get("id") == task_id:
            return t
    return None


def update_task(task_id: str, fields: dict) -> dict | None:
    """Patch frontmatter fields on a task, bump timestamp, write back."""
    for p in config.TASKS_DIR.glob("*.md"):
        fm, body = parse_note(p)
        if fm.get("id") == task_id:
            fm.update(fields)
            fm["timestamp"] = datetime.date.today().isoformat()
            write_note(p, fm, body)
            return {**fm, "path": _rel(p), "line": 2}
    return None


def create_task(fields: dict, body: str = "") -> dict:
    """Create a new type:task file. Mints id + timestamp; slug from title."""
    fm = {"type": "task", "id": str(uuid.uuid4()), **fields}
    fm.setdefault("status", "Backlog")
    fm["timestamp"] = datetime.date.today().isoformat()
    slug = fm.get("title", fm["id"]).lower().replace(" ", "-")[:60]
    config.TASKS_DIR.mkdir(parents=True, exist_ok=True)
    p = config.TASKS_DIR / f"{slug}.md"
    write_note(p, fm, body or fm.get("title", ""))
    return {**fm, "path": _rel(p), "line": 2}
