---
type: task
id: {{uuid}}                # mint one; identifies the container for Notion sync
title: "{{title}}"          # quote it — colons break YAML
status: Not started         # phase rollup: Backlog | Not started | In progress | Done
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
tags: []
---

<One or two lines: the idea / scope of this phase.>

## Steps
<!-- Each step is a schedulable unit. Inline metadata (no YAML on a checkbox):
     [size:: S|M|L]  →  block duration (S30/M60/L120, a story-point estimate)
     📅 YYYY-MM-DD    →  due (Obsidian Tasks)
     [↗](url)         →  resource link
     Classification (cycle/roadmap/category/quarter/priority) is inherited from
     the frontmatter above — don't repeat it per step. -->
- [ ] First step [size:: M]
- [ ] Second step [size:: S] [↗](https://example.com)
