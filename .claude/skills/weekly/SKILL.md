---
name: weekly
description: Weekly review — summarize last week's completed and delayed tasks against quarterly goals, and suggest this week's picks from the backlog. Use when the user asks for a weekly review or planning session.
---

# Weekly review

> ⚠️ **Pending rebuild.** Reads the live Notion Task List (old Notion-as-SoT
> model). Moving to vault-canonical `type: task` files in `notes/planning/`, with
> Notion as a mirror. Reference until the rebuild lands. See `docs/system-design.md`.

See CLAUDE.md for database IDs and conventions.

## Steps

1. Query the Task List data source (`collection://<your-notion-datasource>`):
   - Tasks with `Date` in the last 7 days → group by Status (Done / In progress / not touched).
   - Tasks with `Status = Backlog` → the queue.
2. Fetch the Weekly Task Plan page (https://app.notion.com/p/<notion-id>) for the current quarterly goals.
3. Report, concisely:
   - **Last week**: completed vs planned, anything repeatedly delayed (call it out — repeatedly delayed usually means wrongly scoped or not actually wanted).
   - **Goal progress**: how the week's completions map to the quarterly goals (papers read, project sessions, fitness, etc.). Check vault `papers/` and `projects/` for notes created/updated last week as evidence.
   - **Suggested picks**: 2–3 backlog items for this week that best advance the goals, with one-line reasons.
4. If the user agrees with picks, run the /pick promotion steps for each (status, date, note creation).
5. List any notes sitting in `inbox/` (from /capture or /distill) and ask which to promote to `ideas/` (set `status: evergreen`, move the file) and which to delete. Keep this quick — batch, don't deliberate per note.

Tone: honest scorekeeper, not cheerleader. If the week was thin, say so plainly and suggest a smaller commitment, not a bigger one.
