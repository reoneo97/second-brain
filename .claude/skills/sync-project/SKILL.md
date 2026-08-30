---
name: sync-project
description: Pull progress from a local project's Claude memory into its vault task container — tick done steps, add new deliverables, update phase status. One-directional (repo → vault); the repo is authoritative for what's actually done.
---

# /sync-project — repo → vault progress sync

A local repo is the **source of truth for its own execution** (what's done is
whatever the code/tests/commits say; its Claude memory is the curated summary).
The vault is the **planning layer** that mirrors it. This skill flows progress
**one way, repo → vault** — never the reverse.

Input: `$ARGUMENTS` — a project name/id (matches a container title), or `all`.

## Ownership (never clobber)

- **Repo owns** → step `done` state, *new* deliverables, phase `status`.
- **Vault owns** → step order, `priority`, sizing you've overridden, and ALL
  scheduling (`date`, `start_week`). Never touch these from a sync.

## Tools (second-brain MCP)

- `list_projects()` — find the container; check it has a `memory:` link
- `read_project_status(project_id)` — the raw memory feed (index + blobs). A
  **dumb pipe**: interpret the prose yourself; don't expect a fixed schema.
- `list_tasks(project=id)` — the container's current steps (done + open)
- `update_task(id, {done:true})` — tick a step
- `add_step(project_id, title, size)` — append a new deliverable
- `update_project(id, {status})` — roll up phase status

## Steps

1. **Resolve the container.** `list_projects()`, match `$ARGUMENTS` to a title/id.
   If it has **no `memory:` (or `repo:`) link**, stop and tell the user — offer to
   add the link (`update_project(id, {memory: <path>})`). You can't sync an
   unlinked project.
2. **Read the feed.** `read_project_status(project_id)`. Prefer `type: project`
   memories (status/bugs/progress) and the `MEMORY.md` index; `reference` memories
   are config, not progress. **Be schema-tolerant** — if fields are missing, read
   the `description` + `body` prose. The `modified` timestamp is your recency signal.
3. **Read the current plan.** `list_tasks(project=id)` — the existing steps and
   their done-state.
4. **Interpret + diff (the core, your judgment):** from the memory, work out —
   - which existing steps are now **done** (map memory statements → step titles,
     fuzzy is fine) → tick;
   - which reported deliverables have **no matching step** → propose as new steps
     (estimate `size`);
   - the **phase status** (all done → Done; some in flight → In progress);
   - any **dependency/order** notes (e.g. "fix X before Y") worth surfacing.
   Don't invent progress the memory doesn't state.
5. **Propose, don't apply.** Show a table: `tick` / `add` / `status→` with the
   memory line that justifies each. **Wait for approval.**
6. **Apply** the approved diff: `update_task(id,{done:true})`, `add_step(...)`,
   `update_project(id,{status})`. Report what changed.
7. **Flag learnings (don't act).** If the memory holds reusable *knowledge*
   (a gotcha, a design lesson) that isn't a task, note "worth promoting to a
   knowledge note later" — but **do not** create notes here (that's a separate,
   opt-in flow). Parking it is the whole job for now.

## Rules

- **One-directional.** Never write to the repo or its memory — read only.
- **Propose-then-confirm** every write, like `/plan-day`.
- **Never touch** order / priority / scheduling — those are vault-owned.
- Schema-tolerant: the memory format drifts as the harness evolves; key off
  frontmatter delimiters + `description` + body, not exact field names.
- If a step is done in the vault but the memory implies it regressed, **surface
  the conflict** — don't silently un-tick.
- `all`: iterate every container with a `memory:` link; summarise per project.
