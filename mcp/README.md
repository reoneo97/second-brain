# second-brain MCP server

Mechanical data-access tools over the vault + Time Blocks plugin. **No workflow
logic** — the `plan-day` skill orchestrates these. Model-agnostic (MCP), so it
works with Claude Desktop/Code today and a local model later.

## v1 tools (the time-blocking planner)

| tool | what it does |
|------|--------------|
| `list_tasks(status?, cycle?, week?, date?, roadmap?)` | query `type:task` files |
| `get_task(id)` | one task by id |
| `update_task(id, fields)` | patch frontmatter (status/date/…), bump timestamp |
| `read_time_blocks(week_start?, date?)` | scheduled blocks; `source='gcal'` = calendar busy |
| `schedule_task(id, date, start_hour, start_minute, duration?)` | write a block into `data.json` |

Calendar isn't a tool — the Time Blocks plugin does Google Calendar sync itself,
so busy-times arrive via `read_time_blocks` (gcal blocks).

## Layout

```
mcp/
├── config.py     paths (vault, data.json), size→duration, colors
├── vault.py      OKF frontmatter parse/write (atomic)
├── tasks.py      type:task query + patch
├── schedule.py   Time Blocks data.json read/write (ScheduledBlock)
└── server.py     registers the tools (FastMCP, stdio)
```

## Run

```bash
cd mcp
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python server.py                 # stdio; run as a script (imports are top-level)
```

`SECOND_BRAIN_VAULT` env var overrides the vault path (default:
`~/second-brain/notes`).

## Register with Claude Desktop / Code

Add to the MCP config (`claude_desktop_config.json` or Claude Code `mcp` settings):

```json
{
  "mcpServers": {
    "second-brain": {
      "command": "python",
      "args": ["~/second-brain/mcp/server.py"],
      "env": { "SECOND_BRAIN_VAULT": "~/second-brain/notes" }
    }
  }
}
```

## Notes / build TODOs

- **Task ↔ block link:** blocks reference a task via `taskId = "<path>:<line>"`;
  we anchor on line 2 (`type: task`) since our tasks are whole files, not
  checkbox lines. Revisit if we also surface tasks as Obsidian-Tasks checkboxes.
- **Refresh:** after `schedule_task`, the plugin re-renders when you run the
  `time-blocks:refresh` command in Obsidian (can't be triggered from outside).
- `schedule.py` only ever mutates the `blocks` array — never `settings`,
  `eventMappings`, or user-created blocks.
- Next tools (later): `search_notes`, `write_note`, `sync_plans` (Notion),
  EchoVault `reviews_due`/`generate_cards`/`grade_review`.
```
