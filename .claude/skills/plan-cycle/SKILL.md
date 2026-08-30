---
name: plan-cycle
description: Set up a 12-week cycle in Reo's native format — Vision → Themes → brain-dump → prioritise → assign Start/End Week — over vault-canonical task containers. Use to start (or re-scope) a cycle. Weekly planning within the cycle is /plan-week.
---

# /plan-cycle — 12-week cycle setup (vault-native)

Sets up a **cycle** over `type: task` **containers** in `notes/planning/tasks/` via
the second-brain MCP — not Notion. A cycle = a set of containers sharing a `cycle:`
id, with `start_week`/`end_week` (1–12) assigned across the twelve weeks.

**Scope:** this skill *sets up* the cycle. Planning/reviewing a single week within
it is **`/plan-week`**; scheduling a day is **`/plan-day`**. Notion mirroring is a
later `sync_plans` concern.

## Tools (second-brain MCP)

- `list_projects(cycle?, roadmap?)` / `list_tasks` — read containers + steps
- `update_project(id, {cycle, quarter, start_week, end_week, status, priority})` — classify + place
- `add_step(id, title, size)` — flesh out a container's steps
- new containers: create a file per phase/project from `templates/task.md`

## Concepts (aligned to the task schema)

- **Roadmap** = the spine: `professional | personal` (drives ~70/30 balance).
- **Category** ↔ Notion Category: Staff Track · 🎓 Learning · 💻 ML Building · 💪 Fitness · …
- **Priority** ↔ 💎 Top · ‼️ Imp+Urgent · 🌱 Imp+NotUrgent · ⚡️ Quick · 🧤 Errand.
- **cycle** e.g. `2026-Q3-staff-track`; **start_week/end_week** = 1–12.

## Setting up a cycle

1. **Anchor:** pick the `cycle:` id + the Monday **start date**; end = start + 12
   weeks − 1 day. Note it (in `planning-config.md` or a short cycle doc).
2. **Vision** — carry over the long-term goals; ask what's changed. Keep Reo's
   voice; don't rewrite.
3. **Themes** — pick **1–3 focus goals** for the cycle (12 Week Year: few, deep).
   Map each to a roadmap + category.
4. **Brain-dump** — capture the work as **containers** (one file per phase/project,
   from `templates/task.md`), each with step checkboxes + `[size:: …]`. No
   filtering yet.
5. **Classify** — set `category`, `priority`, `roadmap`, `cycle`, `quarter` on each
   container (`update_project`).
6. **Timeline** — assign `start_week`/`end_week` per container. **Respect weekly
   capacity** (the availability table) — don't overload a week; a week must be
   *finishable*.

## After setup — the planning cadence

- **`/plan-week`** — pick this week's target set from the cycle (weekly capacity).
- **`/plan-day`** — block tomorrow from that week's set.
- **`/today`** — the glance; **`/weekly`** — the review.

## Rules

- Config edits (availability, dials) are **proposed, not silent**.
- A container spanning too many weeks, or slipping repeatedly → flag to split or
  re-prioritise.
- **Capacity cap is a hard rule** — never commit more step-hours to a week than the
  availability table allows.
- Never invent progress — read done/total from the MCP.
