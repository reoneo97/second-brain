# second-brain MCP server

Mechanical data-access tools over the vault + Time Blocks plugin. **No workflow
logic** — the `plan-day` skill orchestrates these. Model-agnostic (MCP), so it
works with Claude Desktop/Code today and a local model later.

## Model: containers & steps

Two levels of granularity:

- **Container** = one `type: task` file (a phase/project). Frontmatter holds the
  shared classification (cycle, roadmap, category, quarter, priority) + a
  `status` rollup. Addressed by its uuid `id`.
- **Step** = a `- [ ]` checkbox in the body — the atomic, schedulable,
  completable unit. Addressed by `"<path>:<line>"`, the **same id the Time Blocks
  plugin uses**, so scheduling a step lights up native completion + click-through.
  Per-step metadata is inline: `[size:: S|M|L]`, `📅 YYYY-MM-DD` due, `[↗](url)`.
  A step inherits its container's classification.

Because steps are addressed by line number, **every write is in place** — no tool
reflows a file, so step ids (and existing blocks) stay valid.

## v1 tools (the time-blocking planner)

| tool | what it does |
|------|--------------|
| `list_tasks(status?, done?, cycle?, roadmap?, quarter?, project?, week?)` | list **steps** with inherited context; `week=N` → only containers live that cycle-week |
| `get_task(id)` | one step by `path:line` (a container uuid returns its first open step) |
| `update_task(id, fields)` | patch a step's checkbox: `done`/`size`/`due`/`title`/`resource`/`freq` (in place) |
| `list_projects(status?, cycle?, roadmap?, quarter?, week?)` | list **containers** + done/total step counts |
| `update_project(id, fields)` | patch a container's frontmatter (status/start_week/notion_id/…) in place |
| `add_step(id, title, size?, due?, resource?, freq?)` | append a step to a container (no existing id shifts) |
| `read_project_status(id?, memory_path?)` | read a linked project's Claude memory as a sync feed (dumb pipe) |
| `sync_plans(project_id?, dry_run=true)` | push containers → live Notion Task List (props + step checkboxes); `dry_run` needs no creds |
| `read_time_blocks(week_start?, date?)` | scheduled blocks; `source='gcal'` = calendar busy |
| `schedule_task(id, date, start_hour, start_minute, duration?)` | write a block for a step into `data.json` |

`sync_plans` is one-directional (vault → Notion) and **never changes Notion's
schema** — it maps to existing options (`config.NOTION_*`), preflights they exist,
and skips unmapped values. Live path needs `NOTION_TOKEN` + `NOTION_DATABASE_ID`
in env + the DB shared with the integration (see `notes/planning/notion-sync.md`);
`notion-client` is lazy-imported so the server runs without it.

`read_project_status` powers the `/sync-project` skill: a container may declare
`repo:` + `memory:` (absolute paths) in its frontmatter; the tool reads that
memory dir (`MEMORY.md` + files) and returns loose `{name, description, type,
modified, body}` blobs with **no interpretation** — the skill (an LLM) reads the
prose, so Claude Code memory-schema drift degrades to "just read it", not a break.

Calendar isn't a tool — the Time Blocks plugin does Google Calendar sync itself,
so busy-times arrive via `read_time_blocks` (gcal blocks).

## Layout

```
mcp/
├── config.py     paths (vault, data.json), size→duration, colors
├── vault.py      OKF frontmatter parse + atomic write (raw + note)
├── tasks.py      container/step parse; in-place step + frontmatter edits; add_step
├── schedule.py   Time Blocks data.json read/write (ScheduledBlock)
├── projects.py   read a linked project's Claude memory (sync feed; dumb pipe)
├── notion.py     push containers → live Notion Task List (sync_plans; dry-run capable)
└── server.py     registers the tools (MCPServer, stdio)
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

## Register with Claude Code

One command (uses the venv's python so the SDK is on the path):

```bash
claude mcp add second-brain \
  --env SECOND_BRAIN_VAULT=/abs/path/to/second-brain/notes \
  -- /abs/path/to/second-brain/mcp/.venv/bin/python \
     /abs/path/to/second-brain/mcp/server.py
```

Verify with `claude mcp list` (look for `second-brain: ✔ Connected`). For Claude
Desktop, add the equivalent `command`/`args`/`env` block to its JSON config.

Requires **mcp SDK 2.x** (`MCPServer`; FastMCP in v1). Server logic is otherwise
transport-agnostic.

## Notes / build TODOs

- **Task ↔ block link:** blocks reference a step via `taskId = "<path>:<line>"`
  anchored on the **checkbox line**, which matches the Time Blocks scanner's own
  id format — so in-canvas completion + click-to-source resolve natively. This is
  why writes never reflow a file (see `update_task`/`update_project`): a reflow
  would shift line numbers and orphan every existing block.
- **Refresh:** after `schedule_task`, the plugin re-renders when you run the
  `time-blocks:refresh` command in Obsidian (can't be triggered from outside).
- `schedule.py` only ever mutates the `blocks` array — never `settings`,
  `eventMappings`, or user-created blocks.
- Next tools (later): `search_notes`, `write_note`, `sync_plans` (Notion),
  EchoVault `reviews_due`/`generate_cards`/`grade_review`.
```
