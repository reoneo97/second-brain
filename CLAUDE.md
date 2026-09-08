# Second brain — umbrella

This is the **umbrella** of Reo's second brain — the planner + orchestration
root. It is **not** the knowledge vault; knowledge lives in `notes/` (its own
Obsidian vault, with its own `CLAUDE.md`). Read `docs/system-design.md` for the full
architecture — it's the authoritative map. New machine? `make setup` +
`docs/SETUP.md`.

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
.claude/skills/   PLANNER skills: plan-cycle, plan-week, plan-day, today,
                  track-project, sync-project
                  (plan-cycle & plan-week each do review→plan; plan-week is the only
                  regular calendar writer; plan-day is optional/on-demand day fine-tuning;
                  track-project is one-time opt-in setup, sync-project is the recurring pull)
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
- A container marked `kind: habit` (fitness, reading) **recurs** — its steps carry a
  `[freq:: 3x/week]` cadence, are tracked by adherence (not done/total), and
  `/plan-week` reserves their time *first*, off the top of capacity. Cycle
  placement uses `start_week`/`end_week`; `list_tasks(week=N)` returns only the
  containers live that week.

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

- `/plan-cycle` — the 12-week cycle ritual: **review** the cycle (goal pace, gaps,
  VISION adherence) → set up / adjust the next.
- `/plan-week` — the Sunday ritual: **review** last week (execution score, gaps) →
  plan this week's target set **and place a day-by-day guideline schedule** on
  the Time Blocks canvas. The only regular writer to the calendar.
- `/plan-day` — **optional, on-demand** single-day fine-tuning (not a nightly
  ritual) — re-optimizes one day's exact slots against what's actually on the
  calendar right now, when the guideline from `/plan-week` has drifted.
- `/track-project` — **one-time** opt-in setup for a repo: scaffolds its
  `.second-brain/status.md` contract, links it to a vault container (`repo:`
  frontmatter), and registers it in `planning-config.md`'s tracked-projects list.
- `/sync-project` — pull a local repo's progress into its vault task container
  (one-directional, repo → vault). Reads the repo's git-tracked
  `.second-brain/status.md` (not Claude Code's own memory dir — that's
  machine/harness-local; the status file survives regardless of which machine
  or agent harness wrote it). Only containers with a `repo:` link are touched.
`sync_plans` is an **MCP tool** (not a skill): pushes task containers into the live
Notion Task List (frontmatter → row properties, steps → page checkboxes).
One-directional (vault → Notion) for now; `dry_run=true` builds the payload with no
creds; the live path needs `NOTION_TOKEN` + `NOTION_DATABASE_ID` in env and never
changes Notion's schema (preflights + skips unmapped options). Value maps live in
`mcp/config.py`; the real ids/setup live in the private `notes/planning/notion-sync.md`.
