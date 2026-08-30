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

## Model: containers & steps

A task file is a **container** (a phase/project); the schedulable unit is a
**step** — a `- [ ]` checkbox in its body, id `"<path>:<line>"`. You schedule
*steps*, not whole files. A step carries `[size:: S|M|L]` inline and inherits
its container's cycle/roadmap/priority. `size` → block duration (S30/M60/L120).

## Tools (second-brain MCP)

- `list_tasks(status?, done?, cycle?, roadmap?, quarter?, project?)` — open steps;
  pass `done=false` for the plannable backlog. Each has an `id` = `path:line`.
- `list_projects(...)` — the phase containers (context / carryover, done/total)
- `read_time_blocks(date?)` — what's already booked; `source:'gcal'` = calendar busy
- `schedule_task(task_id, date, start_hour, start_minute, duration_minutes?)` — write a
  block for a step (`task_id` = its `path:line`)
- `update_task(task_id, fields)` — set `size`/`due`/`done` on a step's checkbox

## Steps

1. **Read `planning/planning-config.md`** — working-hours window, the heuristics
   (deep-work-early, ≥90-min focus, ≤6h/day cap), sizing (S30/M60/L120). Obey it;
   don't hardcode preferences here.
2. **Determine the day** and its window from config (weeknight vs weekend). If
   it's a rest day / outside any window, say so and stop unless the user insists.
3. **Get the candidates:** `list_tasks(done=false)` — open steps. Prefer the
   current cycle's containers; order by the container's `priority`, then keep
   step order within a phase (Phase 0 before 1.1 before 1.2…).
4. **See what's taken:** `read_time_blocks(date)`. Treat every existing block
   (task, `gcal`, manual) as **busy** — never double-book a slot.
5. **Size the unsized:** some steps have no `[size:: …]`. Estimate S/M/L from the
   title, **show the user your estimates, and ask them to confirm** before
   scheduling. Write confirmed values back with `update_task(id, {size})` so
   they're not re-estimated next time.
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
8. **Write it:** for each approved block, `schedule_task(...)`. Optionally
   `update_task(id, {due: date})` to stamp the step. Don't set a per-step status
   — a step is binary; it's *done* when its box is ticked (in Obsidian, or
   `update_task(id, {done:true})`). Report the blocks written.
9. **Tell the user to run `time-blocks:refresh`** in Obsidian to re-render (the
   plugin can't be triggered from outside).

## Rules

- Read all task/schedule state from the MCP — never guess what's scheduled.
- Never exceed the daily cap or overwrite existing/user-created blocks.
- Size estimates are **proposed and confirmed**, then persisted to the checkbox.
- If a recurring pattern emerges (L steps always slip on weeknights), **propose**
  an edit to `planning-config.md` — don't apply it silently.
- Carryover: unfinished (unchecked) steps from earlier days are candidates too;
  surface them first. If a step has slipped 3+ times, flag it (too big — split it
  into two checkboxes / mis-prioritised / blocked).
