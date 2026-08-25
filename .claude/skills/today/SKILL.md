---
name: today
description: Surface today's 2-3 tasks from the active 12-week plan and handle carryover. Use each morning (or start of a work block) to get a clear, capacity-fitted list of what to do now. The daily habit layer on top of /plan-week.
---

# /today — the daily pop

> ⚠️ **Pending rebuild.** Targets the Notion *sandbox* (old model). Moving to
> vault-canonical `type: task` files in `notes/planning/`. Reference until the
> rebuild lands. See `docs/system-design.md`.

Turns this week's allocation into a clear "here's what to do now" list. Sandbox only — never the live Task List.

## Read first

1. Read `planning/planning-config.md` — sandbox IDs, availability table, dials.
2. Get today's date and weekday. Look up today's **focus-hours** in the availability table (apply date overrides). If today is a rest day (0h), say so and stop unless the user insists.

## Pull today's tasks

3. Query the sandbox Tasks data source (`collection://<your-notion-datasource>`) for tasks where `Date` = today and `Status` in ('Not started', 'In progress').
4. **Carryover:** also pull any task with `Date` < today that is still `Not started` / `In progress` (unfinished from earlier). List these first — they're overdue.
5. If the combined list exceeds today's focus-hours, present only what fits (priority + phase order) and note what's being pushed.

## Present

6. Show today's list: Task · Size · Topic · (carryover?). Give the total hours vs today's capacity. Keep it short — this is a glance, not a report.
7. Offer three quick actions per task: **done**, **defer** (roll to next available day), **drop**.

## Write back

8. On "done": set `Status = 'Done'`. On "defer": move `Date` to the next day with free capacity. On "drop": set `Status = 'Backlog'` and clear `Date`.
9. When the user starts a task, optionally set `Status = 'In progress'`.
10. Never touch the live Task List.

## Weekly hygiene

- If nothing is dated for today and the week looks empty, suggest running `/plan-week`.
- If a task has been carried over 3+ times, flag it (too big → split into S/M pieces? mis-prioritised? blocked?) and offer to re-size it.
- If you notice a recurring pattern (e.g. weeknight `L` tasks always slip), propose an edit to `planning/planning-config.md`; don't apply unasked.
