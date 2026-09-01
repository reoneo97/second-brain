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

- `list_projects(cycle?, week?)` / `list_tasks(done?, cycle?, week?, …)` — containers +
  steps; **`week=N` returns only containers live that cycle-week** (start_week ≤ N ≤
  end_week). Each carries `kind` — `kind: habit` containers recur (cadence in the
  step's `freq`; track adherence, not done/total).
- `read_time_blocks(week_start?)` — what was scheduled last / this week (Monday ISO)
- `update_project(id, {start_week, end_week})` / `update_task(id, {due, done})` — placement

**Compute the current week:** read the cycle file (`notes/planning/cycles/<cycle>.md`)
for its Monday start; `current_week = floor((today − start)/7) + 1`. Pass that as
`week` so you only ever plan containers that are live now.

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
   - **habit adherence** — for each `kind: habit` container, did last week hit the
     cadence? (e.g. "fitness 2/3 sessions, reading 4/7"). Report the streak, **not**
     done/total — a missed habit isn't a slipped step, it's a broken streak.
4. **Reflect *with* the user** — ask what worked, what didn't, what to change. A
   dialogue, not a report. **Don't rush to planning.**
5. **Gate:** "ready to plan the week?" If input was `review`, write the review to
   `weeks/<week>.md` and stop here.

## Phase 2 — Plan this week

6. **Weekly capacity** = sum of the availability focus-hours (skip rest days). State it.
7. **Reserve habits first (off the top).** `list_projects(cycle=…, week=N)` where
   `kind == 'habit'` → each habit step's `freq` × `size` is a **protected**
   commitment (2× weekly M-run = 2h, etc.). Reserve that time before anything else;
   **`remaining = capacity − habit hours`** is the project budget. Habits are a
   floor you protect, not a queue — they get scheduled regardless of project progress.
8. **Project candidates:** `list_tasks(done=false, cycle=…, week=N)` (the `week`
   filter keeps out containers not yet live — e.g. SFT before week 4), **excluding
   `kind: habit`** (already reserved). **Carryover (slipped) first.** Subtract
   already-booked (`read_time_blocks` this Monday).
9. **Fit project work into `remaining`**, honouring ~70/30 balance + priority +
   phase order. Slack, not a wall — *finishable*.
10. **Present** the week plan — habits (protected) then project steps (table: project ·
    step · size · priority) + running total vs capacity + what didn't fit. **Wait for
    approval.**
11. **On approval:** `update_task(id, {due})` to flag the target set. Leave day-blocking
    to `/plan-day`. (Don't re-window containers the cycle already placed.)
12. **Write** review + plan to `notes/planning/weeks/<ISO-week>.md` (`type: note`).
    Point the user at `/plan-day` for the evening.

## Rules

- Reflection is **collaborative** — surface gaps and *ask*; never auto-conclude.
- **Weekly capacity is a hard cap** — a week must be finishable.
- Read all state from the MCP — never guess.
- Carryover first; flag 3+ week slips (split / re-prioritise / blocked).
- **Propose** config edits — never apply silently.
