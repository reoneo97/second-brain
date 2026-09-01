---
name: plan-week
description: The weekly ritual — review last week (execution score, gaps, reflection) then plan this week's target set within capacity. Run every Sunday. The bridge between /plan-cycle and /plan-day.
---

# /plan-week — the weekly ritual (review → plan)

Two phases in one Sunday sitting: **reflect on last week, then commit to this
week.** The review's output (what slipped, what got neglected) feeds the plan —
that's why they're one skill. Vault + MCP; no Notion. Writes the review + plan to
`notes/planning/weeks/<ISO-week>.md`.

Input: `$ARGUMENTS` — optional week / focus hint; pass `review` to stop after
Phase 1 (review only).

## Tools (second-brain MCP)

- `list_projects(cycle?, roadmap?)` / `list_tasks(done?, …)` — containers + steps
- `read_time_blocks(week_start?)` — what was scheduled last / this week (Monday ISO)
- `update_project(id, {start_week, end_week})` / `update_task(id, {due, done})` — placement

## Phase 1 — Review last week (collaborative — stop and discuss)

1. **Read** `planning/planning-config.md` (dials, capacity) + `notes/planning/VISION.md`
   (the goals to weigh against).
2. **Execution score:** `read_time_blocks(last Monday)` → for each block, is its step
   now `done`? Score = done / planned. **12WY target ≥ 85%.** State it plainly.
3. **Surface gaps** (reflect, don't just list):
   - **slipped** steps (scheduled, not done) — flag any slipped 3+ weeks;
   - **neglected arcs** — a container / roadmap that got *zero* time (esp. personal);
   - **roadmap balance** — actual professional/personal split vs the ~70/30 dial;
   - **priority inversion** — 🌱 done while 💎 sat idle.
4. **Reflect *with* the user** — ask what worked, what didn't, what to change. A
   dialogue, not a report. **Don't rush to planning.**
5. **Gate:** "ready to plan the week?" If input was `review`, write the review to
   `weeks/<week>.md` and stop here.

## Phase 2 — Plan this week

6. **Weekly capacity** = sum of the availability focus-hours (skip rest days). State it.
7. **Candidates:** `list_tasks(done=false)`, preferring the active cycle; **carryover
   (slipped) first**. Subtract already-booked (`read_time_blocks` this Monday).
8. **Fit a week's worth ≤ capacity**, honouring ~70/30 balance + priority order.
   Slack, not a wall — *finishable*.
9. **Present** the week plan (table: project · step · size · priority) + running total
   vs capacity + what didn't fit. **Wait for approval.**
10. **On approval:** set `start_week`/`end_week` on containers new to the week;
    `update_task(id, {due})` to flag the target set. Leave day-blocking to `/plan-day`.
11. **Write** review + plan to `notes/planning/weeks/<ISO-week>.md` (`type: note`).
    Point the user at `/plan-day` for the evening.

## Rules

- Reflection is **collaborative** — surface gaps and *ask*; never auto-conclude.
- **Weekly capacity is a hard cap** — a week must be finishable.
- Read all state from the MCP — never guess.
- Carryover first; flag 3+ week slips (split / re-prioritise / blocked).
- **Propose** config edits — never apply silently.
