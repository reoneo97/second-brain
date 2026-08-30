---
name: plan-week
description: Plan or review the current week — pull the active cycle's steps and fit a week's worth of work (to your weekly focus-hours) into a realistic target set. The bridge between /plan-cycle (the 12-week map) and /plan-day (tomorrow's blocks).
---

# /plan-week — the weekly plan

Sits between `/plan-cycle` (the 12-week map) and `/plan-day` (tomorrow's blocks).
Picks **this week's realistic target set** — a week's worth of steps within your
weekly focus-hours — so each `/plan-day` just draws from it. Vault + MCP; no Notion.

Input: `$ARGUMENTS` — optional week hint ("next week", a date in the week) and/or
focus hint. **Default = the coming week** on a weekend, else the current week.

## Tools (second-brain MCP)

- `list_projects(cycle?, roadmap?)` — containers active this cycle (done/total)
- `list_tasks(done?, cycle?, roadmap?)` — open steps
- `read_time_blocks(week_start?)` — what's already booked this week (Monday ISO)
- `update_project(id, {start_week, end_week})` — place a container in the timeline
- `update_task(id, {due})` — optionally flag a step as this week's target

## Steps

1. **Read `planning/planning-config.md`** — availability table, dials, priority order.
2. **Determine the week:** Monday–Sunday containing the target date. If a cycle has
   a start date, compute `current_week = floor((today − start)/7)+1` and state it;
   else use the plain calendar week.
3. **Weekly capacity** = sum of the availability table's focus-hours across the
   week's days (skip rest days). State it (e.g. "≈ 9.0h this week").
4. **Candidates:** `list_tasks(done=false)`, preferring the active cycle's
   containers (`list_projects(cycle=…)`); order by priority then phase order.
   **Carryover first** — overdue/unchecked steps from earlier.
5. **Subtract what's booked:** `read_time_blocks(week_start=Monday)` — don't
   double-count time already blocked.
6. **Fit a week's worth:** select steps whose sizes sum to **≤ weekly capacity**,
   honouring ~70/30 professional/personal balance and priority order. Leave slack —
   *finishable*, not a wall.
7. **Present the week plan:** a table grouped by project (step · size · priority),
   running total vs weekly capacity, and what didn't make the cut. **Wait for
   approval** before writing anything.
8. **On approval (optional writes):** set `start_week`/`end_week` on containers new
   to this week, and/or `update_task(id, {due})` to flag the target set. Leave the
   day-level time-blocking to `/plan-day`.
9. **Hand off:** tell the user to run `/plan-day` each evening to block the next
   day from this week's set.

## Rules

- **Weekly capacity is a hard cap** — a week must be finishable.
- Read all state from the MCP — never guess what's scheduled.
- Balance professional/personal ~70/30 once personal is defined.
- Carryover first; flag any step slipped 3+ weeks (split / re-prioritise / blocked).
- **Propose** config edits (availability, dials) — never apply silently.
