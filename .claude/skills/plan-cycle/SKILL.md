---
name: plan-cycle
description: Set up or review a 12-week cycle in Reo's native format — Vision → Themes → brain-dump → prioritise → assign Start/End Week — over vault-canonical task containers. Use to start a cycle, or to plan/review a week within the active one.
---

# /plan-cycle — 12-week planning (vault-native)

Plans over `type: task` **containers** in `notes/planning/tasks/` via the
second-brain MCP — not Notion. A **cycle** = a set of containers sharing a `cycle:`
id, with `start_week`/`end_week` (1–12) assigned across the twelve weeks. Notion
mirroring is a later `sync_plans` concern.

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

## Mode A — start a new cycle

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

## Mode B — plan / review a week

7. `current_week = floor((today − start_date) / 7) + 1`. State it + its date range.
8. `list_projects(cycle=…)`; keep those with `start_week ≤ week ≤ end_week`. Order
   by priority, then roadmap balance.
9. Fit the week's **open steps** to the week's focus-hours; present a table; flag
   anything over capacity.
10. Hand off to **`/plan-day`** for day-level time-blocking.

## Rules

- Config edits (availability, dials) are **proposed, not silent**.
- A container spanning too many weeks, or slipping repeatedly → flag to split or
  re-prioritise.
- **Capacity cap is a hard rule** — never commit more step-hours to a week than the
  availability table allows.
- Never invent progress — read done/total from the MCP.
