---
name: plan-cycle
description: Set up and run a 12-week plan in Reo's own format — Vision → Themes → brain-dump → Eisenhower tagging → Start/End Week assignment. Use to start a new 12-week cycle, or to plan/review a week within the active cycle.
---

# /plan-cycle — 12-week planning in Reo's native format

> ⚠️ **Pending rebuild.** Targets the Notion *sandbox* (old Notion-as-source-of-truth
> model). The planner is moving to vault-canonical `type: task` files in
> `notes/planning/`, with Notion as a mirror via `sync-plans`. Treat the mechanics
> below as reference until the rebuild lands. See `docs/system-design.md`.

Works with the **replica of Reo's own 12 Week Plan template** (not the relational Tasks DB — that's a separate experiment). Sandbox only; never touch live databases.

## Anchors (sandbox)

- **Cycle template** (duplicate this to start a cycle): page `<notion-id>` — "📋 12 Week Plan — Cycle Template (sandbox)"
- Cycle pages live under the sandbox container `<notion-id>`.
- Each cycle page has its **own inline task database** (Reo's structure). Don't hardcode its id — `fetch` the cycle page and read the inline `<database ... data-source-url="collection://...">` to get that cycle's task data source.
- Task fields (Reo's schema): `Name`, `Theme` (multi: Machine Learning, Fitness, Entertainment/Gaming, General Knowledge, Personal Effectiveness, Family), `Priority` (Eisenhower: ‼️ Important + Urgent / 🌱 Important + Not Urgent / 🤷 Urgent + Not Important / 🤔 Not Urgent + Not Important), `Date`, `Duration`, `Start Week` (1–12), `End Week` (1–12).
- Read `planning/planning-config.md` for availability + dials (capacity cap still applies).

## Mode A — start a new cycle

1. **Duplicate** the cycle template, move the copy under the sandbox container, rename `YYYY QN — <focus>`, and record the **Start Date** (Monday). Compute + note the end date (Start + 12 weeks − 1 day).
2. **Vision** — carry over the long-term goals; ask Reo what's changed. Keep it his voice; don't rewrite.
3. **Themes** — confirm which of his themes this cycle emphasises (aim for 1–3 focus goals, per 12 Week Year).
4. **To-Do brain-dump** — capture everything into the inline task DB, no filtering yet.
5. **Putting it together** — for each task set `Theme` + Eisenhower `Priority` + a rough `Duration`.
6. **Timeline** — assign `Start Week`/`End Week` to each task. **Respect weekly capacity** from the availability table — don't overload a week. Actionable + quantifiable tasks only.

## Mode B — plan / review a week

7. Compute the **current week**: `week = floor((today − Start Date) / 7) + 1`. State it and its date range.
8. Pull this cycle's tasks where `Start Week ≤ current week ≤ End Week`. Order by Eisenhower priority, then Theme balance.
9. Fit to the week's focus-hours (availability table). Present as a table; flag anything over capacity.
10. For the daily view, filter to `Date = today` (or set Dates within the week during this step). Keep the daily list to 2–3 items.

## Rules

- Never modify the live Task List DB or Reo's real 12 Week Plans DB.
- Config edits (availability, dials) are proposed, not silent.
- If a task spans too many weeks or keeps slipping, flag it to split or re-prioritise.
- This skill and the relational `/plan-week` + `/today` are two paradigms in the sandbox — Reo is choosing this native-format one. Once he commits, the relational Tasks DB can be retired.
