---
name: sync-project
description: Pull progress from a local project's git-tracked status file into its vault task container — tick done steps, add new deliverables, update phase status. One-directional (repo → vault); the repo is authoritative for what's actually done.
---

# /sync-project — repo → vault progress sync

A local repo is the **source of truth for its own execution** (what's done is
whatever the code/tests/commits say; `.second-brain/status.md` is the curated
summary). The vault is the **planning layer** that mirrors it. This skill flows
progress **one way, repo → vault** — never the reverse.

Only containers with an explicit `repo:` link are ever touched — this is
opt-in per project, never a scan of everything in `notes/planning/tasks/`. See
the "Tracked projects" list in `planning/planning-config.md` for what's live.

Input: `$ARGUMENTS` — a project name/id (matches a container title), or `all`
(iterates every *tracked* container, not every container).

## Ownership (never clobber)

- **Repo owns** → step `done` state, *new* deliverables, phase `status`.
- **Vault owns** → step order, `priority`, sizing you've overridden, and ALL
  scheduling (`date`, `start_week`). Never touch these from a sync.

## Tools (second-brain MCP)

- `list_projects()` — find the container; check it has a `repo:` link
- `read_project_status(project_id)` — the raw status-file feed
  (`.second-brain/status.md`'s frontmatter + body, from the container's
  `repo:` + optional `status_file:` override). A **dumb pipe**: interpret the
  prose yourself; don't expect a rigid schema beyond the Completed/In
  progress/Blocked convention `/track-project` scaffolds.
- `list_tasks(project=id)` — the container's current steps (done + open)
- `update_task(id, {done:true})` — tick a step
- `add_step(project_id, title, size)` — append a new deliverable
- `update_project(id, {status})` — roll up phase status

## Steps

1. **Resolve the container.** `list_projects()`, match `$ARGUMENTS` to a title/id.
   If it has **no `repo:` link**, stop and tell the user — this project isn't
   tracked; offer to run `/track-project` to wire it up. Don't guess a repo path.
2. **Read the feed.** `read_project_status(project_id)`. If `found: false` (the
   status file doesn't exist yet — e.g. `repo:` was added by hand, not via
   `/track-project`), say so and stop; don't fabricate progress. Otherwise read
   the body's Completed / In progress / Blocked sections as prose — **be
   schema-tolerant**, headings and phrasing will drift, the `updated` frontmatter
   field is your recency signal.
3. **Read the current plan.** `list_tasks(project=id)` — the existing steps and
   their done-state.
4. **Interpret + diff (the core, your judgment):** from the status file, work out —
   - which existing steps are now **done** (map "Completed"/"In progress"
     statements → step titles, fuzzy is fine) → tick;
   - which reported deliverables have **no matching step** → propose as new steps
     (estimate `size`);
   - the **phase status** (all done → Done; some in flight → In progress);
   - anything in **Blocked** worth surfacing as a dependency/order note.
   Don't invent progress the status file doesn't state.
5. **Propose, don't apply.** Show a table: `tick` / `add` / `status→` with the
   status-file line that justifies each. **Wait for approval.**
6. **Apply** the approved diff: `update_task(id,{done:true})`, `add_step(...)`,
   `update_project(id,{status})`. Report what changed.
7. **Flag learnings (don't act).** If the status file's body holds reusable
   *knowledge* (a gotcha, a design lesson) beyond Completed/In progress/Blocked,
   note "worth promoting to a knowledge note later" — but **do not** create
   notes here (that's a separate, opt-in flow). Parking it is the whole job.

## Rules

- **One-directional.** Never write to the repo or its status file — read only.
- **Propose-then-confirm** every write, like `/plan-day`.
- **Never touch** order / priority / scheduling — those are vault-owned.
- Schema-tolerant: phrasing under Completed/In progress/Blocked will drift
  project to project; key off those headings loosely, not exact text.
- If a step is done in the vault but the status file implies it regressed,
  **surface the conflict** — don't silently un-tick.
- `all`: iterate every container with a `repo:` link; summarise per project.
