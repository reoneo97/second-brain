---
name: today
description: The daily glance — show today's scheduled time blocks, surface overdue/carryover steps, and check things off. Lighter than /plan-day (which does the scheduling); use /today during the day to see what's on and mark progress.
---

# /today — the daily pop

The quick "what's on right now?" view. `/plan-day` does the *planning* (fits steps
into your window, writes time blocks); `/today` just **reads the plan back**,
surfaces anything overdue, and lets you tick things off. Vault-canonical via the
second-brain MCP — no Notion.

Input: `$ARGUMENTS` — optional date (default today).

## Tools (second-brain MCP)

- `read_time_blocks(date?)` — today's blocks; `source:'gcal'` = calendar busy
- `list_tasks(done?, cycle?, roadmap?)` — open steps (for overdue/carryover)
- `update_task(id, {done:true} | {due:…})` — tick / defer a step

## Steps

1. **Read `planning/planning-config.md`** — working window, focus-hours, dials.
2. **Today's date + weekday → focus-hours.** Rest day (0h) → say so and stop unless
   the user insists.
3. **`read_time_blocks(today)`** → today's plan. Separate task blocks from `gcal`
   (busy). Show the day as a timeline: time · step · size.
4. **Overdue / carryover:** `list_tasks(done=false)` with a `due` before today (and
   any step whose block sat on an earlier day and is still unchecked). List these
   **first** — they slipped.
5. If today has **no task blocks** and there's open work, suggest running `/plan-day`.
6. **Present:** today's timeline + overdue, with total task-hours vs today's
   focus-hours. Keep it a glance, not a report.
7. **Quick actions** per step: **done** → `update_task(id,{done:true})`; **defer** →
   set `due` / reschedule to the next free day; **drop** → just leave it unscheduled.

## Rules

- Read all state from the MCP — never guess what's scheduled.
- A step is binary — *done* = its checkbox ticked; there's no per-day status.
- If a step has slipped 3+ times, flag it (too big → split into two checkboxes /
  mis-prioritised / blocked).
- Recurring pattern (L steps always slip on weeknights) → **propose** a
  `planning-config.md` edit, don't apply it silently.
