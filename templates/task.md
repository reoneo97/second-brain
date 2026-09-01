---
type: task
id: {{uuid}}                # mint one; identifies the container for Notion sync
title: "{{title}}"          # quote it — colons break YAML
status: Not started         # phase rollup: Backlog | Not started | In progress | Done
# kind: habit              # optional — this container RECURS (fitness, reading).
#                          # Steps carry a [freq:: …] cadence; tracked by adherence,
#                          # not done/total; the planner reserves their time first.
timestamp: {{date}}         # OKF last-updated; vs Notion last_edited_time for sync
category: [Staff Track]     # ↔ Notion Category (multi): Staff Track | 🎓 Learning | 💻 ML Building | …
priority:                   # ↔ Notion Priority: 💎 | ‼️ | 🌱 | ⚡️ | 🧤  (phase-level)
roadmap: professional       # professional | personal (the spine; drives domain balance)
cycle:                      # e.g. 2026-Q3-staff-track; may be empty
quarter:                    # ↔ Notion Quarter, e.g. 2026 Q3
start_week:                 # 1–12 within the cycle (set by /plan-cycle)
end_week:
notion_id:                  # mirrored Notion page (managed by sync_plans)
last_synced:
# repo:   ~/path/to/project           # optional — link to a local repo…
# memory: ~/.claude/projects/<slug>/memory   # …and its Claude memory, so
#                                     /sync-project can pull progress → steps
tags: []
---

<One or two lines: the idea / scope of this phase.>

## Steps
<!-- Each step is a schedulable unit. Inline metadata (no YAML on a checkbox):
     [size:: S|M|L]  →  block duration (S30/M60/L120, a story-point estimate)
     📅 YYYY-MM-DD    →  due (Obsidian Tasks)
     [↗](url)         →  resource link
     [freq:: 3x/week] →  cadence — ONLY on a `kind: habit` container's steps
     Classification (cycle/roadmap/category/quarter/priority) is inherited from
     the frontmatter above — don't repeat it per step. -->
- [ ] First step [size:: M]
- [ ] Second step [size:: S] [↗](https://example.com)
<!-- habit container example:  - [ ] Strength session [size:: M] [freq:: 3x/week] -->

