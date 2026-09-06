---
name: plan-week
description: The weekly ritual — review last week (execution score, gaps, reflection) then plan this week's target set AND place it on the Time Blocks canvas as a day-by-day guideline. Run every Sunday. /plan-day is now optional, on-demand fine-tuning for a single day, not a nightly requirement.
---

# /plan-week — the weekly ritual (review → plan → block)

Three things in one Sunday sitting: **reflect on last week, pick this week's
target set, and place it on the calendar** — day + rough time, for every
selected step, in one pass. The review's output (what slipped, what got
neglected) feeds the plan — that's why they're one skill. Vault + MCP; no
Notion. Writes the review + plan to `notes/planning/weeks/<ISO-week>.md`.

**This is a guideline schedule, not a fine-tuned one.** It picks a reasonable
day and a reasonable time per step, checking for gross conflicts (existing
blocks, `gcal` busy) — it does not re-optimize against a specific day's live
calendar the way a nightly re-plan would. If a day's calendar shifts mid-week
(a meeting gets added), the guideline block may drift — that's an accepted
tradeoff for planning once a week instead of every night. `/plan-day` still
exists for exactly that case: run it **on-demand**, only when you want to
re-optimize one specific day against what's actually on the calendar *today*.

Input: `$ARGUMENTS` — optional week / focus hint; pass `review` to stop after
Phase 1 (review only).

## Tools (second-brain MCP)

- `list_projects(cycle?, week?)` / `list_tasks(done?, cycle?, week?, …)` — containers +
  steps; **`week=N` returns only containers live that cycle-week** (start_week ≤ N ≤
  end_week). Each carries `kind` — `kind: habit` containers recur (cadence in the
  step's `freq`; track adherence, not done/total).
- `read_time_blocks(week_start?)` — what's already booked this week (Monday ISO);
  `source:'gcal'` = calendar busy. Used to dodge gross conflicts only, not fine-tune.
- `schedule_task(task_id, date, start_hour, start_minute, duration_minutes?)` — write
  the guideline block for a step.
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

## Phase 2 — Plan this week, day by day

6. **Per-day budget.** Read the availability table (focus-hours per weekday,
   e.g. Mon–Thu 1h, Fri 0/rest, Sat 3h, Sun 2h) and the working-hours windows
   (weeknight 19:00–22:00 for Mon–Thu/Sun; weekend 09:00–12:00 + 14:00–18:00 for
   Sat). State the week total and each live day's budget. Skip 0-capacity
   (rest) days entirely.
7. **Reserve habits first — placed on specific days, off the top.**
   `list_projects(cycle=…, week=N)` where `kind == 'habit'` → each habit step's
   `freq` decides how many days it needs this week (`weekly`→1 day,
   `3x/week`→3 days, `daily`→every live day). Spread them across the week
   rather than clumping; place a guideline block for each
   (`schedule_task`, at that day's window start or the next free slot — see
   step 9). **`remaining[day] = day budget − habit hours placed that day`** is
   what's left for project work. Habits are a protected floor, scheduled
   regardless of project progress.
8. **Project candidates:** `list_tasks(done=false, cycle=…, week=N)` (the `week`
   filter keeps out containers not yet live — e.g. SFT before week 4), **excluding
   `kind: habit`** (already reserved). **Carryover (slipped) first.**
9. **Assign each approved step a day + a rough start time:**
   - Walk live days Mon→Sun; place higher-priority and larger (L) steps on
     earlier days where they fit, respecting each day's `remaining` budget —
     don't exceed it.
   - **Start time** = that day's window start, or the next free slot after
     whatever's already there that day (existing blocks from
     `read_time_blocks(week_start)`, `gcal` busy, and habit blocks just placed)
     — snapped to :00/:15/:30/:45, ≥15 min gaps. This is a **reasonable
     placement, not a fine-tuned one** — it only dodges gross conflicts, it
     doesn't deep-optimize a day's exact sequencing the way `/plan-day` would.
   - Duration = the step's size (S30/M60/L120) unless overridden.
10. **Present** the week plan as a table — **day · time · project · step · size ·
    priority** — with running hours per day and for the week vs. capacity, and
    what didn't fit. **Wait for approval** before writing anything.
11. **On approval, for each step:** `schedule_task(task_id, date, start_hour,
    start_minute, duration)` to write its guideline block, **and**
    `update_task(id, {due: date})` to stamp the step itself. (Don't re-window
    containers the cycle already placed.)
12. **Write** review + plan (including the day-by-day schedule) to
    `notes/planning/weeks/<ISO-week>.md` (`type: note`). Tell the user to run
    `Time Blocks: refresh` in Obsidian to see the week. Mention `/plan-day` is
    available **on-demand** if a specific day's plan needs re-optimizing
    against that day's actual calendar later in the week.

**Known limitation (not fixed here):** if `/plan-day` is later run to refine a
day this skill already scheduled, `schedule_task`'s existing dedup-guard
(one block per taskId per week) will reject re-scheduling the same step —
resolving that (e.g. an explicit "replace" path) is a follow-up for when
`/plan-day`'s on-demand role is actually built out, not before.

## Rules

- Reflection is **collaborative** — surface gaps and *ask*; never auto-conclude.
- **Weekly capacity is a hard cap** — a week must be finishable. Per-day budgets
  are soft guidance for placement, not a second hard cap on top.
- Read all state from the MCP — never guess.
- Carryover first; flag 3+ week slips (split / re-prioritise / blocked).
- **Propose** config edits — never apply silently.
- Guideline placement dodges **gross** conflicts only (existing blocks, `gcal`
  busy) — it is not a fine-tuned day-of schedule. Don't over-optimize sequencing
  within a day; that's `/plan-day`'s job, on-demand, if the user wants it.
- Never write a block without showing the full week table and getting approval
  first.
