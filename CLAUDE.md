# Second brain — umbrella

This is the **umbrella** of Reo's second brain — the planner + orchestration
root. It is **not** the knowledge vault; knowledge lives in `notes/` (its own
Obsidian vault, with its own `CLAUDE.md`). Read `docs/system-design.md` for the full
architecture — it's the authoritative map.

## Layers (see docs/system-design.md)

- **Stores:** `notes/` (Markdown + OKF frontmatter) is the **canonical source of
  truth** for almost everything. **Notion** is a *supplementary mirror* of the
  plan/task slice only — a human-friendly editing surface, not a second truth.
- **Intelligence:** a custom **MCP server** (`mcp/`, to build) exposes the vault
  + scheduling as mechanical tools; **skills** encode the workflows.
- **Conversational layer:** not built — Claude / a local model reads skills,
  calls MCP tools. Model-agnostic by design.

## Layout

```
notes/            the knowledge vault (canonical). Topic folders, _inbox/, planning/
mcp/              custom MCP server (to build)
planning/         planner config + roadmap docs (planning-config.md)
templates/        note/plan templates
docs/             system design + decision log (start: docs/system-design.md)
.claude/skills/   PLANNER skills: plan-cycle, today, weekly (+ plan-day, coming)
```

Knowledge skills (`capture`, `distill`, `librarian`, `pick`) live in
`notes/.claude/skills/`. **Two agents by launch location:** launch Claude here
for the planner; launch in `notes/` for knowledge.

## Task model: containers & steps

- A `type: task` file is a **container** — a phase/project. Its frontmatter holds
  the shared classification (cycle, roadmap, category, quarter, priority) + a
  `status` rollup. Its body is the idea + a checklist of **steps**.
- A **step** is a `- [ ]` checkbox — the atomic, schedulable, completable unit,
  addressed by `"<path>:<line>"` (the id the Time Blocks plugin uses). Per-step
  metadata is inline: `[size:: S|M|L]`, `📅` due, `[↗](url)`. Steps inherit the
  container's classification; cycle/roadmap planning tracks containers, daily
  time-blocking schedules steps.
- The MCP addresses steps by line, so **every write is in place** — never reflow
  a task file (it would orphan step ids and existing time blocks).

## Source of truth & sync (summary)

- Vault is canonical. Only files with OKF `type: task` or `type: plan` sync to
  Notion — the **whole file** (frontmatter → properties, body → page content
  incl. step checkboxes/descriptions). All other `type`s are vault-only.
- Reconciliation is **last-writer-wins by timestamp** (OKF `timestamp` vs
  Notion `last_edited_time`); a user edit in Notion flows back into the vault.
- An inline `- [ ]` checkbox inside a `type: note` is an ephemeral jot (never
  syncs); **promoting** it to a `type: task` container commits it (and syncs it).

## Notion (supplementary mirror)

Task List Database — `collection://<your-notion-datasource>`
(DB `<notion-id>`), under the Weekly Task Plan page
`<notion-id>`. A `🧪 Planning System (Sandbox)` exists
for prototyping; **never modify Reo's live Notion schemas** — clone/sandbox.

Known bug: the Notion MCP view DSL silently drops status-equality filters — use
`Date IS EMPTY` proxies or set status filters in the UI; don't retry via MCP.

## Planner skills

- `/plan-cycle` — set up / run a 12-week cycle in Reo's native format.
- `/today` — daily surfacing of what to do now.
- `/weekly` — weekly review vs goals.
- `/plan-day` — the time-blocking planner (first MCP deliverable; schedules
  steps into the Obsidian Time Blocks plugin via the second-brain MCP).
