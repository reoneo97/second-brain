"""Notion push — a purely tactical, per-day dashboard mirror of the vault.

One-directional (vault -> Notion). No container-level overview page: each row
is a single **occurrence** — a habit's scheduled slot this week, or a project
step's `due:` date — with its own real Date, Priority, and Category. This is
deliberately not a full mirror of a container's checklist; it's "what to do,
on which day," nothing more. See ADR-017 (docs/decisions.md) for why the
earlier container-page design was retired.

Credentials come from env (mcp/.env via python-dotenv); nothing secret lives
in the repo. **Never changes the Notion schema** — writes only mapped option
values and preflights that each already exists; anything unmapped is skipped,
never created.

`dry_run=True` (the default) builds and returns the payloads WITHOUT touching
Notion or needing creds.
"""
import datetime

import config
import schedule
import tasks


def _client():
    if not config.NOTION_TOKEN:
        raise RuntimeError("NOTION_TOKEN not set — see notes/planning/notion-sync.md")
    if not config.NOTION_DATABASE_ID:
        raise RuntimeError("NOTION_DATABASE_ID not set (the Task List database uuid)")
    if not config.NOTION_DATA_SOURCE_ID:
        raise RuntimeError("NOTION_DATA_SOURCE_ID not set (see notes/planning/notion-sync.md)")
    from notion_client import Client   # lazy: dep only needed for the live path
    return Client(auth=config.NOTION_TOKEN)


def _preflight(client) -> list[str]:
    """Return mapped option values NOT present in the live schema (must be empty
    before we write — otherwise writing would create an option = schema change)."""
    schema = client.data_sources.retrieve(config.NOTION_DATA_SOURCE_ID)["properties"]
    missing = []
    prio = {o["name"] for o in schema.get("Priority", {}).get("select", {}).get("options", [])}
    missing += [f"Priority:{v!r}" for v in config.NOTION_PRIORITY_MAP.values() if v not in prio]
    cat = {o["name"] for o in schema.get("Category", {}).get("multi_select", {}).get("options", [])}
    missing += [f"Category:{v!r}" for v in config.NOTION_CATEGORY_MAP.values() if v not in cat]
    st = {o["name"] for o in schema.get("Status", {}).get("status", {}).get("options", [])}
    missing += [f"Status:{v!r}" for v in config.NOTION_STATUS_SET if v not in st]
    return missing


def _find_existing(client, title: str, date: str) -> str | None:
    """Dedup/upsert key for occurrence rows: they have no vault-side id (a
    step's `path:line` isn't a stable Notion property), so look up by exact
    Title + Date instead. Returns the existing page id, or None."""
    resp = client.data_sources.query(
        data_source_id=config.NOTION_DATA_SOURCE_ID,
        filter={"and": [
            {"property": "Title", "title": {"equals": title}},
            {"property": "Date", "date": {"equals": date}},
        ]},
    )
    results = resp.get("results", [])
    return results[0]["id"] if results else None


def _occurrence_properties(step: dict, title: str, date: str, status: str) -> dict:
    props = {
        "Title": {"title": [{"text": {"content": title}}]},
        "Status": {"status": {"name": status}},
        "Date": {"date": {"start": date}},
    }
    prio = (step.get("priority") or "").strip()
    if prio in config.NOTION_PRIORITY_MAP:
        props["Priority"] = {"select": {"name": config.NOTION_PRIORITY_MAP[prio]}}
    cats = [config.NOTION_CATEGORY_MAP[x] for x in (step.get("category") or [])
            if x in config.NOTION_CATEGORY_MAP]
    if cats:
        props["Category"] = {"multi_select": [{"name": m} for m in cats]}
    return props


def _week_bounds(week_start: str) -> tuple[str, str]:
    start = datetime.date.fromisoformat(week_start)
    return start.isoformat(), (start + datetime.timedelta(days=6)).isoformat()


def _collect_occurrences(week_start: str) -> list[dict]:
    plans = []

    # Habit occurrences: one per scheduled Time Blocks slot this week (a habit
    # step has no due: date — it recurs — so its only date signal is the
    # calendar it's actually placed on).
    for b in schedule.read_time_blocks(week_start=week_start):
        if b.get("source") != "task" or not b.get("taskId"):
            continue
        step = tasks.get_task(b["taskId"])
        if not step or step.get("kind") != "habit":
            continue
        day = (datetime.date.fromisoformat(b["weekStart"])
               + datetime.timedelta(days=b["dayIndex"]))
        date_str = day.isoformat()
        # Habits are always "Important + Not Urgent" by definition — never
        # "Top Priority"/urgent (that's what makes them easy to skip under
        # pressure, so this is pinned rather than inherited from a container
        # field that may be unset or drift).
        plans.append({
            "step": {**step, "priority": "🌱 Important + Not Urgent"},
            "date": date_str, "status": "Not started",
            "title": f"{step['title']} — {day.strftime('%a %-m/%-d')}",
        })

    # Project-step occurrences: any non-habit step due this week. Status
    # mirrors the vault's done-state, so re-running after ticking a step
    # refreshes the Notion row instead of leaving it stale.
    week_end_start, week_end = _week_bounds(week_start)
    for step in tasks.list_tasks():
        if step.get("kind") == "habit":
            continue
        due = step.get("due")
        if not due or not (week_end_start <= str(due) <= week_end):
            continue
        day = datetime.date.fromisoformat(str(due))
        plans.append({
            "step": step, "date": str(due),
            "status": "Done" if step.get("done") else "Not started",
            "title": f"{step['title']} — {day.strftime('%a %-m/%-d')}",
        })

    return plans


def sync_occurrences(week_start: str, dry_run: bool = True) -> dict:
    """Push one standalone, tactical Notion row per schedulable item this week:
    a habit's scheduled Time-Blocks slot, or a regular step whose `due:` date
    falls in this week. Each row = Title, Date, Priority, Category, Status —
    purely "what to do, on which day," no container-level overview page.

    Upserted by (Title, Date) — a step has no stable Notion-side id, so this
    doubles as the dedup key: an existing row's Status/Priority/Category gets
    refreshed (so ticking a step done and re-syncing updates Notion) instead
    of creating a duplicate. Nothing is ever written back to the vault."""
    plans = _collect_occurrences(week_start)

    if dry_run:
        return {"dry_run": True, "count": len(plans), "plans": [
            {"title": p["title"], "date": p["date"], "status": p["status"]}
            for p in plans]}

    client = _client()
    if missing := _preflight(client):
        return {"dry_run": False, "aborted": True,
                "reason": "mapped options missing from the Notion schema — writing "
                          "them would create options (a schema change); aborted",
                "missing": missing}
    results = []
    for p in plans:
        props = _occurrence_properties(p["step"], p["title"], p["date"], p["status"])
        if existing := _find_existing(client, p["title"], p["date"]):
            client.pages.update(page_id=existing, properties=props)
            results.append({"title": p["title"], "action": "updated", "notion_id": existing})
            continue
        page = client.pages.create(
            parent={"type": "data_source_id", "data_source_id": config.NOTION_DATA_SOURCE_ID},
            properties=props)
        results.append({"title": p["title"], "action": "created", "notion_id": page["id"]})
    return {"dry_run": False, "count": len(results), "results": results}
