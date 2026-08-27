---
name: plan-day
description: Plan today (or a given day) — pull outstanding tasks, see what's already scheduled, fit a realistic set into your working hours, and write time blocks into the Obsidian Time Blocks plugin. The daily "plan my day" command.
---

# /plan-day — the time-blocking planner

Turns your `type: task` backlog into a concrete, time-blocked day in the Time
Blocks plugin. **This skill does the reasoning; the second-brain MCP does the
I/O.** Never invent scheduling data — read it from the tools.

Input: `$ARGUMENTS` — optional date (default today) and/or focus hint
("just deep work", "light day").

## Tools (second-brain MCP)

- `list_tasks(status?, cycle?, week?, date?, roadmap?)` — the backlog
- `read_time_blocks(date?)` — what's already booked; `source:'gcal'` = calendar busy
- `schedule_task(task_id, date, start_hour, start_minute, duration_minutes?)` — write a block
- `update_task(task_id, fields)` — stamp `date` / `status` on the task

## Steps

1. **Read `planning/planning-config.md`** — working-hours window, the heuristics
   (deep-work-early, ≥90-min focus, ≤6h/day cap), sizing (S30/M60/L120). Obey it;
   don't hardcode preferences here.
2. **Determine the day** and its window from config (weeknight vs weekend). If
   it's a rest day / outside any window, say so and stop unless the user insists.
3. **Get the candidates:** `list_tasks(status='Not started')` (+ `In progress`).
   Prefer the current cycle's tasks; drop `Done`. Order by `priority`, then keep
   phase order within a series (Phase 0 before 1.1 before 1.2…).
4. **See what's taken:** `read_time_blocks(date)`. Treat every existing block
   (task, `gcal`, manual) as **busy** — never double-book a slot.
5. **Size the unsized:** many imported tasks have no `size`/`priority`. Estimate
   S/M/L (and rough priority) from the title, **show the user your estimates, and
   ask them to confirm** before scheduling. Write confirmed values back with
   `update_task` so it's not re-estimated next time.
6. **Fit to the window (the core):** place blocks into free time within today's
   window —
   - respect the **≤6h/day** cap and leave the day *finishable* (2–4 tasks is
     usually right, not a wall);
   - **deep-work/L earlier**, S/admin later; aim for **≥90-min** focus stretches;
   - snap starts to :00/:15/:30/:45; ≥15 min between blocks;
   - duration = the task's size (S30/M60/L120) unless the user overrides.
7. **Show the proposed day** as a table (time · task · size · why-this-slot) with
   running hours vs the cap, and note anything that didn't fit. **Wait for
   approval** — nothing is written before the user okays it.
8. **Write it:** for each approved block, `schedule_task(...)` then
   `update_task(id, {date, status:'In progress'})`. Report the blocks written.
9. **Tell the user to run `time-blocks:refresh`** in Obsidian to re-render (the
   plugin can't be triggered from outside).

## Rules

- Read all task/schedule state from the MCP — never guess what's scheduled.
- Never exceed the daily cap or overwrite existing/user-created blocks.
- Sizing/priority estimates are **proposed and confirmed**, then persisted.
- If a recurring pattern emerges (L tasks always slip on weeknights), **propose**
  an edit to `planning-config.md` — don't apply it silently.
- Carryover: unfinished tasks from earlier days are candidates too; surface them
  first. If one has slipped 3+ times, flag it (too big / mis-prioritised / blocked).
