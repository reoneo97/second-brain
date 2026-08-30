"""Notion push — mirror task containers into the live Task List.

Mechanical, one-directional (vault -> Notion): maps a container's frontmatter to
row properties and its steps to page checkboxes, then creates/updates the row via
the Notion API. Credentials come from env (config.NOTION_TOKEN / NOTION_DATABASE_ID);
nothing secret lives in the repo.

**Never changes the Notion schema.** It writes only mapped option values and
preflights that each already exists; anything unmapped is skipped, never created.

`dry_run=True` (the default) builds and returns the payloads WITHOUT touching
Notion or needing creds — use it to inspect the mapping. The live path requires
the env creds + the DB shared with the integration.
"""
import datetime

import config
import tasks


def _properties(c: dict) -> dict:
    """Container frontmatter -> Notion property payload (existing options only)."""
    props = {"Title": {"title": [{"text": {"content": c.get("title", "")}}]}}
    if (st := c.get("status")) in config.NOTION_STATUS_SET:
        props["Status"] = {"status": {"name": st}}
    prio = (c.get("priority") or "").strip()
    if prio in config.NOTION_PRIORITY_MAP:
        props["Priority"] = {"select": {"name": config.NOTION_PRIORITY_MAP[prio]}}
    cats = [config.NOTION_CATEGORY_MAP[x] for x in (c.get("category") or [])
            if x in config.NOTION_CATEGORY_MAP]
    if cats:
        props["Category"] = {"multi_select": [{"name": m} for m in cats]}
    if q := c.get("quarter"):
        props["Quarter"] = {"rich_text": [{"text": {"content": str(q)}}]}
    if r := c.get("resource"):
        props["Resources"] = {"url": str(r)}
    if d := c.get("date"):
        props["Date"] = {"date": {"start": str(d)}}
    return props


def _body_blocks(project_id: str) -> list[dict]:
    """Container steps -> Notion to-do blocks (checked = done)."""
    blocks = []
    for s in tasks.list_tasks(project=project_id):
        txt = s["title"] + (f"  [size:: {s['size']}]" if s.get("size") else "")
        blocks.append({"object": "block", "type": "to_do", "to_do": {
            "rich_text": [{"type": "text", "text": {"content": txt}}],
            "checked": bool(s.get("done"))}})
    return blocks


def _plan_one(c: dict) -> dict:
    """The mapped payload + what got dropped/skipped, for one container."""
    return {
        "project": c.get("title"), "id": c.get("id"), "notion_id": c.get("notion_id"),
        "action": "update" if c.get("notion_id") else "create",
        "properties": _properties(c),
        "step_count": len(_body_blocks(c["id"])),
        "dropped_fields": [f for f in ("roadmap", "cycle", "start_week", "end_week")
                           if c.get(f) not in (None, "")],
        "skipped_categories": [x for x in (c.get("category") or [])
                               if x not in config.NOTION_CATEGORY_MAP],
    }


def _client():
    if not config.NOTION_TOKEN:
        raise RuntimeError("NOTION_TOKEN not set — see notes/planning/notion-sync.md")
    if not config.NOTION_DATABASE_ID:
        raise RuntimeError("NOTION_DATABASE_ID not set (the Task List database uuid)")
    from notion_client import Client   # lazy: dep only needed for the live path
    return Client(auth=config.NOTION_TOKEN)


def _preflight(client) -> list[str]:
    """Return mapped option values NOT present in the live schema (must be empty
    before we write — otherwise writing would create an option = schema change)."""
    schema = client.databases.retrieve(config.NOTION_DATABASE_ID)["properties"]
    missing = []
    prio = {o["name"] for o in schema.get("Priority", {}).get("select", {}).get("options", [])}
    missing += [f"Priority:{v!r}" for v in config.NOTION_PRIORITY_MAP.values() if v not in prio]
    cat = {o["name"] for o in schema.get("Category", {}).get("multi_select", {}).get("options", [])}
    missing += [f"Category:{v!r}" for v in config.NOTION_CATEGORY_MAP.values() if v not in cat]
    st = {o["name"] for o in schema.get("Status", {}).get("status", {}).get("options", [])}
    missing += [f"Status:{v!r}" for v in config.NOTION_STATUS_SET if v not in st]
    return missing


def sync_plans(project_id: str | None = None, dry_run: bool = True) -> dict:
    """Push containers to the live Task List. `dry_run=True` (default) returns the
    payloads without touching Notion (no creds needed). The live path preflights
    the schema, then creates new rows / updates existing ones (by `notion_id`) and
    writes the page id + `last_synced` back to the container.

    NOTE (MVP): on **create** it writes the step checkboxes into the page body; on
    **update** it syncs properties only (wholesale body replacement is a later
    step — the Notion API needs a delete-then-add of child blocks)."""
    containers = tasks.list_projects()
    if project_id:
        containers = [c for c in containers if c["id"] == project_id
                      or project_id.lower() in str(c.get("title", "")).lower()]
    plans = [_plan_one(c) for c in containers]

    if dry_run:
        return {"dry_run": True, "count": len(plans), "plans": plans}

    client = _client()
    if missing := _preflight(client):
        return {"dry_run": False, "aborted": True,
                "reason": "mapped options missing from the Notion schema — writing "
                          "them would create options (a schema change); aborted",
                "missing": missing}
    results = []
    for c in containers:
        props = _properties(c)
        if c.get("notion_id"):
            client.pages.update(page_id=c["notion_id"], properties=props)
            action, pid = "updated (properties)", c["notion_id"]
        else:
            page = client.pages.create(
                parent={"database_id": config.NOTION_DATABASE_ID},
                properties=props, children=_body_blocks(c["id"]))
            pid = page["id"]
            tasks.update_project(c["id"], {"notion_id": pid,
                                           "last_synced": datetime.date.today().isoformat()})
            action = "created"
        results.append({"project": c.get("title"), "action": action, "notion_id": pid})
    return {"dry_run": False, "count": len(results), "results": results}
