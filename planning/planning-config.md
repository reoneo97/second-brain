# Planning config

Policy dials for the planner skills (`/plan-day`, `/plan-cycle`, `/today`).
**Skills read this file every run** — edit here to change behaviour, never
hardcode preferences in the skills.

> Everything below is a starting default. Tune it and the planner adapts next run.

## Data (canonical = the vault)

- **Tasks:** `type: task` files in `notes/planning/tasks/` are **containers**
  (a phase/project); the schedulable unit is a **step** — a `- [ ]` checkbox in
  the body, id `"<path>:<line>"`. Steps carry `[size:: S|M|L]` inline and inherit
  the container's cycle/roadmap/priority. Read via the second-brain MCP
  `list_tasks` (steps) / `list_projects` (containers) / `update_task`.
- **Schedule:** the Time Blocks plugin's `data.json` (via `read_time_blocks` /
  `schedule_task`). Calendar busy-times arrive as `source: gcal` blocks.
- **Notion** is a tactical per-day dashboard, pushed via `sync_occurrences`
  (`/plan-week` step 15) — one row per habit occurrence / due-dated step, no
  container-level page (ADR-017). It's also read back: `pull_from_notion`
  (`/today` step 2, `/plan-week` step 1) is the one write-back exception —
  habit completions and Notion-originated new items flow back into the vault
  (ADR-019).

## Roadmaps (scope: Professional + Personal)

- **Professional** — Staff Track + ML-building/learning. Active.
- **Personal** — active. Three arcs: Fitness & health, Relationships & family,
  Entertainment & lifestyle (`roadmap: personal` containers). The ~70/30
  professional/personal balance dial now applies.

## Availability (my working time is OUTSIDE 9–6)

Focus-hours per weekday — evenings + weekends. Updated 2026-09-06 from actual
routine (dinner ends ~8pm on weeknights; Sunday has a distinct 3-segment shape).

| Day | Focus-hrs | Note |
|-----|-----------|------|
| Mon | 2.5 | after dinner |
| Tue | 2.5 | after dinner |
| Wed | 2.5 | after dinner |
| Thu | 2.5 | after dinner |
| Fri | 0   | rest / social — protect it |
| Sat | 3.0 | |
| Sun | 5.0 | 1h workout + 2h + 2h — see working-hours below |

**Weekly capacity ≈ 18 focus-hours.** Some weeknights may run longer than 2.5h
in practice — that's upside, not the planning baseline. Date overrides (specific
dates, win over the weekday default):

- _none yet — e.g. `2026-08-08: 0  # travel`_

## Working hours (time-of-day, for /plan-day)

My work happens **outside 9–6** — evenings + weekends. Default schedulable window:
- **Weeknights (Mon–Thu):** 20:00–22:30 (post-dinner)
- **Saturday:** 09:00–12:00 and 14:00–18:00
- **Sunday** (distinct shape, not weeknight-style): 09:00–10:00 (workout —
  fitness habit slot), 14:00–16:00 (session), 19:00–21:00 (session). These
  default times are adjustable — flag it during planning if a given Sunday
  needs to move.

Heuristics for placing blocks within the window:
- **Deep work (L tasks / focus) earlier**, admin/short (S) later.
- **Focus blocks ≥ 90 min** where the task and window allow.
- **≤ 6 focus-hours of active work per day** (hard cap).
- Leave ≥ 15 min between blocks; snap starts to :00/:15/:30/:45.

## Task sizing (story points on each step)

- `S` ≈ 30 min · `M` ≈ 60 min · `L` ≈ 120 min (→ block duration)
- Size is a **quick T-shirt indicator** written on the checkbox as `[size:: M]`,
  not a time commitment — retune the minute mapping here and every block resizes.
- If a step has no `[size:: …]`, the planner estimates and asks you to confirm,
  then persists it to the checkbox.

## Planning dials

- **Capacity cap (hard rule):** never commit more task-hours to a week than the availability table allows. A week must be *finishable*. "Doable but a stretch," not a pile.
- **Domain balance:** ~70% Professional / ~30% Personal (once Personal is defined).
- **Daily pop:** surface **2–3 tasks** for today, fitted to that day's focus-hours.
- **Carryover:** unfinished tasks roll to the next available day; if a task slips 3× the planner flags it (too big? wrong priority? blocked?).
- **Priority order:** 💎 Top Priority → ‼️ Important + Urgent → 🌱 Important + Not Urgent → ⚡️ Quick Task → 🧤 Errand. Within a topic, respect phase order (Phase 0 before Phase 1).
- **Rest days** (Fri here) get no tasks unless you explicitly ask.

## Tracked projects (repo → vault sync)

`/sync-project` only touches containers below — tracking is **opt-in per
project** via `/track-project`, never an automatic scan of every repo on disk.
Each entry links a vault container to a repo's `.second-brain/status.md`
(default path; only listed if overridden). See ADR-015.

| Container | Repo |
|---|---|
| CS336 — Language Modeling from Scratch | `~/Documents/Reo/data-science/projects/cs336-assignment/assignment1-basics` |

## Inbox (Notion-originated items)

`notes/planning/tasks/inbox-quick-tasks.md` (`kind: inbox`) is where
`pull_from_notion` lands a Notion row that matches neither a pushed habit nor
step occurrence — a quick errand typed directly into Notion. Reviewed and
cleared during `/plan-week`'s Phase 1 (each item promoted or discarded, not
left to accumulate). See ADR-019.

## Learning loop

When `/today` or `/plan-week` notices a recurring pattern (e.g. you keep deferring `L` tasks on weeknights), it **proposes** an edit to this file. It never rewrites your policy silently — you approve the change.
