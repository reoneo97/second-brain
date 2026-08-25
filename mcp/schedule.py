"""Time Blocks plugin bridge — read/write .obsidian/plugins/time-blocks/data.json.

Schema (from the plugin's AGENTS.md):
  data.json = {version, settings, blocks:[ScheduledBlock], eventMappings:[]}
  ScheduledBlock = {id, taskId?, gcalEventId?, title, weekStart, dayIndex,
                    startHour, startMinute, duration, color, source}
  taskId = "<relative/path.md>:<1-based line>"; source in {task, gcal, manual}

Mechanical only: builds/reads blocks. Deciding WHICH slot a task goes in is the
plan-day skill's job — this just writes where told. gcal blocks (source='gcal')
are calendar busy-times, so read_time_blocks doubles as "show me busy slots".
"""
import datetime
import json
import time
from pathlib import Path

import config
from tasks import get_task


def _load() -> dict:
    if not config.TIMEBLOCKS_JSON.exists():
        return {"version": 1, "settings": {}, "blocks": [], "eventMappings": []}
    return json.loads(config.TIMEBLOCKS_JSON.read_text(encoding="utf-8"))


def _atomic_write(data: dict) -> None:
    p = config.TIMEBLOCKS_JSON
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(p)


def _week_start(d: datetime.date) -> str:
    return (d - datetime.timedelta(days=d.weekday())).isoformat()


def read_time_blocks(week_start: str | None = None, date: str | None = None) -> list[dict]:
    """All scheduled blocks (task + gcal + manual). Filter by weekStart or a
    specific date. gcal blocks are your calendar busy-times."""
    blocks = _load().get("blocks", [])
    if date:
        d = datetime.date.fromisoformat(date)
        ws, di = _week_start(d), d.weekday()
        blocks = [b for b in blocks if b.get("weekStart") == ws and b.get("dayIndex") == di]
    elif week_start:
        blocks = [b for b in blocks if b.get("weekStart") == week_start]
    return blocks


def schedule_task(task_id: str, date: str, start_hour: int, start_minute: int,
                  duration_minutes: int | None = None) -> dict:
    """Write a ScheduledBlock for a task into data.json. The plan-day skill
    decides date/time; this validates + persists. Duration defaults from the
    task's size. Returns the created block.

    NOTE: after writing, the user runs the `time-blocks:refresh` command in
    Obsidian to re-render (the plugin can't be triggered from outside)."""
    task = get_task(task_id)
    if not task:
        raise ValueError(f"no task with id {task_id}")

    if start_minute not in (0, 15, 30, 45):
        raise ValueError("startMinute must be 0/15/30/45 (15-min snap grid)")
    duration = duration_minutes or config.SIZE_MINUTES.get(task.get("size", "M"), 60)
    if duration < 15:
        raise ValueError("duration must be >= 15 minutes")

    d = datetime.date.fromisoformat(date)
    day_index = d.weekday()  # 0=Mon..6=Sun, matches the plugin
    block = {
        "id": f"block-{day_index}-{int(time.time() * 1000)}",
        "taskId": f"{task['path']}:{task['line']}",
        "title": task.get("title", ""),
        "weekStart": _week_start(d),
        "dayIndex": day_index,
        "startHour": start_hour,
        "startMinute": start_minute,
        "duration": duration,
        "color": config.TASK_BLOCK_COLOR,
        "source": "task",
    }
    data = _load()
    if any(b.get("taskId") == block["taskId"] and b.get("weekStart") == block["weekStart"]
           for b in data.get("blocks", [])):
        raise ValueError("that task is already scheduled this week")
    data.setdefault("blocks", []).append(block)
    _atomic_write(data)                     # never touches settings / eventMappings
    return block
