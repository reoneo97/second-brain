---
name: plan-cycle
description: The 12-week cycle ritual — review the current cycle (goal pace, gaps, VISION adherence, next steps) then set up or adjust the next one. Collaborative. Weekly planning within a cycle is /plan-week.
---

# /plan-cycle — the cycle ritual (review → plan)

Runs at a cycle boundary (or as a midpoint check): **reflect on the cycle against
your VISION, then set up / adjust the next.** Plans over `type: task` **containers**
in `notes/planning/tasks/` via the second-brain MCP. Writes to
`notes/planning/cycles/<cycle>.md`.

Input: `$ARGUMENTS` — optional cycle hint; `review` to stop after Phase 1; `new`
to skip the review (starting the very first cycle).

## Tools (second-brain MCP)

- `list_projects(cycle?, roadmap?)` / `list_tasks` — read containers + steps
- `update_project(id, {cycle, quarter, start_week, end_week, status, priority})` — classify + place
- `add_step(id, title, size)` — flesh out a container's steps
- new containers: create a file per phase/project from `templates/task.md`

## Concepts (aligned to the task schema)

- **Roadmap** = the spine: `professional | personal` (drives ~70/30 balance).
- **Category** ↔ Notion Category: Staff Track · 🎓 Learning · 💻 ML Building · 💪 Fitness · Family · Entertainment · …
- **Priority** ↔ 💎 Top · ‼️ Imp+Urgent · 🌱 Imp+NotUrgent · ⚡️ Quick · 🧤 Errand.
- **cycle** e.g. `2026-Q3-staff-track`; **start_week/end_week** = 1–12.

## Phase 1 — Review the cycle (collaborative — skip if `new`)

1. **Read** `planning/VISION.md` + `planning/planning-config.md`.
2. **Goal pace:** for each focus goal, its containers' done/total vs **weeks
   elapsed** (`current_week = floor((today − start)/7)+1`) — on pace, or behind?
3. **Surface gaps:**
   - off-track focus goal (barely moved at the midpoint);
   - **untouched containers** — assigned to the cycle, never scheduled;
   - **scope drift** — many containers added mid-cycle vs the original plan;
   - **burn-rate** — at this pace, will the goals finish by week 12?
4. **VISION adherence:** does the cycle's work still ladder up to the 1-year aims /
   vision? Surface drift; **suggest next steps.** Collaborative — ask, don't lecture.
5. **Carry-forward:** what should roll into the next cycle.
6. **Gate:** "ready to set up the next cycle?" If input was `review`, write the
   review to `cycles/<cycle>.md` and stop here.

## Phase 2 — Set up / adjust the cycle

7. **Anchor:** pick the `cycle:` id + Monday **start date**; end = start + 12 weeks
   − 1 day. Record it in the cycle file.
8. **Vision** — carry over the long-term goals (from `VISION.md`); ask what's
   changed. Keep Reo's voice.
9. **Themes** — pick **1–3 focus goals** for the cycle (12 Week Year: few, deep).
   Map each to a roadmap + category.
10. **Brain-dump** — capture the work as **containers** (one file per phase/project
    from `templates/task.md`), each with step checkboxes + `[size:: …]`.
11. **Classify** — set `category`, `priority`, `roadmap`, `cycle`, `quarter` per
    container (`update_project`).
12. **Timeline** — assign `start_week`/`end_week`. **Respect weekly capacity** — a
    week must be *finishable*.
13. **Write** the cycle setup (+ any review) to `notes/planning/cycles/<cycle>.md`.

## After setup — the cadence

- **`/plan-week`** — the Sunday ritual (review last week → plan this week).
- **`/plan-day`** — block tomorrow from the week's set.
- **`/today`** — the daily glance.

## Rules

- Reflection is **collaborative** — surface gaps and *ask*; never auto-conclude.
- Config edits (availability, dials) are **proposed, not silent**.
- **Capacity cap is a hard rule** — never commit more step-hours to a week than the
  availability table allows.
- Never invent progress — read done/total from the MCP.
