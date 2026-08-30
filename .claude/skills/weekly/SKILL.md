---
name: weekly
description: Weekly review — what got done vs planned last week against your roadmap/cycle goals, and 2-3 suggested picks for the week ahead. Honest scorekeeper, not cheerleader.
---

# /weekly — weekly review

Vault-canonical review via the second-brain MCP. Notion is a future mirror
(`sync_plans`), not read here.

## Tools (second-brain MCP)

- `list_projects(cycle?, roadmap?)` — containers + done/total step counts
- `list_tasks(done?, cycle?, roadmap?)` — steps
- `read_time_blocks(week_start?)` — what was scheduled last / this week

## Steps

1. **Read `planning/planning-config.md`** — the roadmap dials (professional /
   personal spines, ~70/30 balance), capacity, priority order. Cycle goals live on
   the containers themselves (`cycle:` / `quarter:` frontmatter).
2. **Last week:**
   - Steps completed (`done`, container `timestamp` within the last 7 days) vs what
     was scheduled (`read_time_blocks` for last week's Monday).
   - Call out anything **scheduled-but-not-done**, and anything **repeatedly
     slipping** — repeated delay usually means wrongly scoped or not actually wanted.
3. **Goal progress:** map completions to `cycle` / `roadmap`. `list_projects` shows
   each phase's done/total. As evidence of learning-goal progress, check `notes/`
   (`knowledge/`) for notes created or updated in the last week.
4. **Suggested picks:** 2–3 open steps/containers that best advance the goals this
   week, one line of reasoning each. Prefer the active cycle; respect priority +
   phase order.
5. **Offer to place them:** `/plan-cycle` (assign `start_week`/`end_week`) for the
   week, or `/plan-day` to schedule today.
6. *(light)* Note any items sitting in `notes/_inbox/` worth filing — but leave the
   filing to the knowledge agent (`/librarian`, launched in `notes/`); don't do it
   here.

Tone: **honest scorekeeper, not cheerleader.** A thin week → say so plainly and
suggest a *smaller* commitment next week, not a bigger one.
