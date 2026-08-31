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

## Phase 1 — Review (collaborative — skip if `new`)

1. **Read the history.** `planning/VISION.md` (esp. the 1-year aims) +
   `planning/planning-config.md` + **all of `planning/cycles/*.md`** (every past
   cycle, not just the last) + current container done-state (`list_projects`).
   The vault IS the planner's memory: done-state is permanent and each cycle is a
   durable file — read across them.
2. **Per-aim progress ledger (the cross-cycle memory).** For each **1-year aim**
   in VISION, map what prior cycles + completed containers/steps have advanced it,
   and roughly how far. Infer the aim ↔ work mapping from content (no explicit
   link needed). This is the "have I already partially done this?" view. Surface:
   - aims **well-advanced** across cycles (don't re-do — build on them);
   - aims **untouched for 2+ cycles** (a neglected aim — deliberate, or drift?);
   - the **trajectory** toward each yearly aim.
3. **Current-cycle pace:** for the active cycle's focus goals, containers'
   done/total vs **weeks elapsed** (`current_week = floor((today − start)/7)+1`).
4. **Surface gaps:** off-track focus goal; **untouched containers** (assigned,
   never scheduled); **scope drift** (many added mid-cycle); **burn-rate** (will it
   finish by week 12?).
5. **VISION adherence + next steps:** does the work still ladder up to the aims?
   Use the ledger — e.g. "aim X hasn't moved in two cycles; make it this cycle's
   bet, or consciously defer it?" Collaborative — ask, don't lecture.
6. **Carry-forward:** what rolls into the next cycle.
7. **Gate:** "ready to set up the next cycle?" If input was `review`, write the
   review (incl. the per-aim ledger) to `cycles/<cycle>.md` and stop here.

## Phase 2 — Set up / adjust the cycle

8. **Anchor:** pick the `cycle:` id + Monday **start date**; end = start + 12 weeks
   − 1 day. Record it in the cycle file.
9. **Vision** — carry over the long-term goals (from `VISION.md`); ask what's
   changed. Keep Reo's voice.
10. **Themes** — pick **1–3 focus goals** for the cycle (12 Week Year: few, deep).
    Map each to a roadmap + category. Let the per-aim ledger inform which aims are
    due for a deep bet vs already advanced.
11. **Brain-dump** — capture the work as **containers** (one file per phase/project
    from `templates/task.md`), each with step checkboxes + `[size:: …]`.
12. **Classify** — set `category`, `priority`, `roadmap`, `cycle`, `quarter` per
    container (`update_project`).
13. **Timeline** — assign `start_week`/`end_week`. **Respect weekly capacity** — a
    week must be *finishable*.
14. **Write** the cycle setup (+ any review) to `notes/planning/cycles/<cycle>.md`.

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
