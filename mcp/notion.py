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


def _habit_occurrences(week_start: str) -> list[dict]:
    """One per `kind: habit` step's scheduled Time Blocks slot this week (a
    habit has no due: date — it recurs — so its only date signal is the
    calendar it's actually placed on)."""
    plans = []
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
    return plans


def _step_occurrences(week_start: str) -> list[dict]:
    """One per non-habit step whose `due:` falls in this week. Status mirrors
    the vault's done-state (the vault is authoritative for steps, unlike
    habits — see pull_from_notion)."""
    plans = []
    week_start_d, week_end = _week_bounds(week_start)
    for step in tasks.list_tasks():
        if step.get("kind") == "habit":
            continue
        due = step.get("due")
        if not due or not (week_start_d <= str(due) <= week_end):
            continue
        day = datetime.date.fromisoformat(str(due))
        plans.append({
            "step": step, "date": str(due),
            "status": "Done" if step.get("done") else "Not started",
            "title": f"{step['title']} — {day.strftime('%a %-m/%-d')}",
        })
    return plans


def _collect_occurrences(week_start: str) -> list[dict]:
    return _habit_occurrences(week_start) + _step_occurrences(week_start)


def sync_occurrences(week_start: str, dry_run: bool = True) -> dict:
    """Push one standalone, tactical Notion row per schedulable item this week:
    a habit's scheduled Time-Blocks slot, or a regular step whose `due:` date
    falls in this week. Each row = Title, Date, Priority, Category, Status —
    purely "what to do, on which day," no container-level overview page.

    Upserted by (Title, Date) — a step has no stable Notion-side id, so this
    doubles as the dedup key. On update, a **step**'s Status is refreshed from
    the vault (vault-authoritative); a **habit**'s Status is left untouched —
    Notion is where habit completion actually gets marked (see
    pull_from_notion), so re-pushing must never stomp it back to
    "Not started". Nothing else is ever written back to the vault here."""
    habit_plans = _habit_occurrences(week_start)
    step_plans = _step_occurrences(week_start)
    plans = habit_plans + step_plans

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
    habit_titles = {p["title"] for p in habit_plans}
    results = []
    for p in plans:
        props = _occurrence_properties(p["step"], p["title"], p["date"], p["status"])
        if existing := _find_existing(client, p["title"], p["date"]):
            if p["title"] in habit_titles:
                props.pop("Status", None)
            client.pages.update(page_id=existing, properties=props)
            results.append({"title": p["title"], "action": "updated", "notion_id": existing})
            continue
        page = client.pages.create(
            parent={"type": "data_source_id", "data_source_id": config.NOTION_DATA_SOURCE_ID},
            properties=props)
        results.append({"title": p["title"], "action": "created", "notion_id": page["id"]})
    return {"dry_run": False, "count": len(results), "results": results}


def _row_status(client, page_id: str) -> str | None:
    page = client.pages.retrieve(page_id)
    status = page.get("properties", {}).get("Status", {}).get("status")
    return status.get("name") if status else None


def _row_title(page: dict) -> str:
    rich = page.get("properties", {}).get("Title", {}).get("title", [])
    return "".join(r.get("plain_text", "") for r in rich)


def pull_from_notion(week_start: str, dry_run: bool = True) -> dict:
    """Reconcile this week's Notion rows back into the vault — the one
    exception to sync_occurrences' one-directional flow. Handles three cases:

    1. A habit occurrence marked "Done" in Notion -> tasks.log_habit(...)
       (habits are primarily marked done in Notion, not the vault — see
       ADR-019 for why this doesn't contradict ADR-017's one-directional
       framing: it's a per-field split, not symmetric bidirectional sync).
    2. A step occurrence marked "Done" in Notion, not yet done in the vault
       -> tasks.update_task(id, {done: True}). Only propagates Done; a
       reversion in Notion is never pulled back (avoids accidentally erasing
       vault-side progress from a stray edit).
    3. A Notion row in this week's date range matching NEITHER a pushed habit
       nor step occurrence -> a genuinely new item typed directly into
       Notion. Imported as a new step in the Inbox container
       (kind: inbox), and its Notion Title is immediately renamed to match
       the "<title> — <weekday date>" convention so the next sync_occurrences
       upserts it instead of duplicating it."""
    habit_plans = {(p["title"], p["date"]): p for p in _habit_occurrences(week_start)}
    step_plans = {(p["title"], p["date"]): p for p in _step_occurrences(week_start)}
    week_start_d, week_end = _week_bounds(week_start)

    client = _client()
    resp = client.data_sources.query(
        data_source_id=config.NOTION_DATA_SOURCE_ID,
        filter={"and": [
            {"property": "Date", "date": {"on_or_after": week_start_d}},
            {"property": "Date", "date": {"on_or_before": week_end}},
        ]},
    )
    actions = []
    for page in resp.get("results", []):
        title = _row_title(page)
        date_prop = page.get("properties", {}).get("Date", {}).get("date")
        date = date_prop.get("start") if date_prop else None
        status_prop = page.get("properties", {}).get("Status", {}).get("status")
        status = status_prop.get("name") if status_prop else None
        key = (title, date)

        if key in habit_plans and status == "Done":
            step = habit_plans[key]["step"]
            if not tasks.is_habit_logged(step["id"], date):
                actions.append({"kind": "habit_complete", "title": title, "date": date,
                                "step_id": step["id"]})
        elif key in step_plans and status == "Done" and not step_plans[key]["step"].get("done"):
            step = step_plans[key]["step"]
            actions.append({"kind": "step_complete", "title": title, "date": date,
                            "step_id": step["id"]})
        elif key not in habit_plans and key not in step_plans and title and date:
            actions.append({"kind": "new_item", "title": title, "date": date,
                            "notion_id": page["id"]})

    if dry_run:
        return {"dry_run": True, "count": len(actions), "actions": actions}

    inbox = next((c for c in tasks.list_projects() if c.get("kind") == "inbox"), None)
    results = []
    for a in actions:
        if a["kind"] == "habit_complete":
            r = tasks.log_habit(a["step_id"], a["date"])
            results.append({**a, "result": r})
        elif a["kind"] == "step_complete":
            r = tasks.update_task(a["step_id"], {"done": True})
            results.append({**a, "result": "done" if r else "step not found"})
        elif a["kind"] == "new_item":
            if not inbox:
                results.append({**a, "result": "no Inbox container found — skipped"})
                continue
            new_step = tasks.add_step(inbox["id"], a["title"], due=a["date"])
            day = datetime.date.fromisoformat(a["date"])
            renamed = f"{a['title']} — {day.strftime('%a %-m/%-d')}"
            client.pages.update(page_id=a["notion_id"],
                                properties={"Title": {"title": [{"text": {"content": renamed}}]}})
            results.append({**a, "result": "imported to Inbox", "step_id":
                            new_step["id"] if new_step else None, "renamed_to": renamed})
    return {"dry_run": False, "count": len(results), "results": results}
