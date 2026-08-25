# Planning config

Policy dials for the planning skills (`/plan-week`, `/today`). **Skills read this file every run** — edit here to change behaviour, never hardcode preferences in the skills.

> Everything below is a starting default. Tune it and the planner adapts next run.

## Sandbox location (isolated — NOT the live Task List)

Container page: `<notion-id>` — 🧪 Planning System (Sandbox).

**Primary paradigm — Reo's native 12-week format** (used by `/plan-cycle`):
- Cycle template page: `<notion-id>` — 📋 12 Week Plan — Cycle Template (sandbox). A faithful copy of Reo's real template (Vision / Themes / Eisenhower / Start-End-Week timeline). Duplicate it to start a cycle.
- Each cycle page carries its own inline task DB — discover its data source by fetching the page.

**Secondary paradigm — relational experiment** (used by `/plan-week` + `/today`; retire once the native format is confirmed):
- Tasks DS: `collection://<your-notion-datasource>` — 🎯 Planning Tasks (Sandbox)
- 12-Week Plans DS: `collection://<your-notion-datasource>` — 🗓️ 12 Week Plans (Sandbox)

Live Task List (READ-ONLY source for seeding; never modify its schema): `collection://<your-notion-datasource>`

## Roadmaps (scope: Professional + Personal)

- **Professional** — Staff Track. Active. Tasks seeded from the live Task List (Category = Staff Track).
- **Personal** — ⚠️ not yet defined. Define 1–3 personal arcs (fitness / side-project / relationships) in a follow-up session, then seed with `Roadmap = Personal`.

## Availability (my working time is OUTSIDE 9–6)

Focus-hours per weekday — evenings + weekends. **These are placeholder defaults — edit to your real week.**

| Day | Focus-hrs | Note |
|-----|-----------|------|
| Mon | 1.0 | |
| Tue | 1.0 | |
| Wed | 1.0 | |
| Thu | 1.0 | |
| Fri | 0   | rest / social — protect it |
| Sat | 3.0 | |
| Sun | 2.0 | |

**Weekly capacity ≈ 9 focus-hours.** Date overrides (specific dates, win over the weekday default):

- _none yet — e.g. `2026-08-08: 0  # travel`_

## Task sizing

- `S` ≈ 30 min · `M` ≈ 60 min · `L` ≈ 120 min
- If a task has no `Size`, the planner estimates and asks you to confirm.

## Planning dials

- **Capacity cap (hard rule):** never commit more task-hours to a week than the availability table allows. A week must be *finishable*. "Doable but a stretch," not a pile.
- **Domain balance:** ~70% Professional / ~30% Personal (once Personal is defined).
- **Daily pop:** surface **2–3 tasks** for today, fitted to that day's focus-hours.
- **Carryover:** unfinished tasks roll to the next available day; if a task slips 3× the planner flags it (too big? wrong priority? blocked?).
- **Priority order:** 💎 Top Priority → ‼️ Important + Urgent → 🌱 Important + Not Urgent → ⚡️ Quick Task → 🧤 Errand. Within a topic, respect phase order (Phase 0 before Phase 1).
- **Rest days** (Fri here) get no tasks unless you explicitly ask.

## Learning loop

When `/today` or `/plan-week` notices a recurring pattern (e.g. you keep deferring `L` tasks on weeknights), it **proposes** an edit to this file. It never rewrites your policy silently — you approve the change.
