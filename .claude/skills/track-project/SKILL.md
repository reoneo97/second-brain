---
name: track-project
description: Wire a local repo up to the vault so /sync-project can pull its progress — scaffold the repo's status-file contract, link a vault container, and register it as tracked. Run this once, when a project starts being worth tracking (not automatically for every repo).
---

# /track-project — opt a repo into progress sync

`/sync-project` only ever touches containers with an explicit `repo:` link —
tracking is **opt-in per project**, never a scan of every repo on disk. This
skill is the one-time setup that turns a plain repo into a tracked one: it
scaffolds the git-tracked status contract the repo will keep updated, links it
to a vault container, and adds it to the visible tracked-projects list. See
ADR-015 (`docs/decisions.md`) for why the contract is a committed file, not
Claude Code's own memory dir — it has to survive being read by whichever
machine/harness (Claude Code today, a future Hermes harness, ...) runs
`/sync-project`, not just the one that did the coding.

Input: `$ARGUMENTS` — a local repo path, plus optionally an existing container
title/id to link instead of creating a new one.

## Tools (second-brain MCP)

- `list_projects()` — check whether a matching container already exists
- `add_step` / vault `Write` — only if a new container needs creating (rare;
  usually you're linking a container that already exists in the vault)
- `update_project(id, {repo, status_file?})` — write the link

## Steps

1. **Resolve the repo.** Confirm the path in `$ARGUMENTS` exists and is a git
   repo (`git -C <path> rev-parse --is-inside-work-tree`). Stop and ask if not.
2. **Resolve the container.** If `$ARGUMENTS` names an existing container,
   confirm it via `list_projects()`. Otherwise ask whether to link an existing
   one or scaffold a new `type: task` container (title, roadmap, priority —
   same as any new container; see `planning-config.md`'s conventions).
3. **Scaffold the status file** at `<repo>/.second-brain/status.md` (skip if it
   already exists — don't clobber real progress):
   ```markdown
   ---
   type: progress
   repo: <repo-relative-or-short-name>
   updated: <today>
   ---

   ## Completed
   - (nothing yet)

   ## In progress
   - (nothing yet)

   ## Blocked
   - (none)
   ```
   Tell the user the file was created — **don't `git add`/commit it yourself**;
   that repo's commit history isn't this skill's to touch. Suggest they commit
   it themselves whenever convenient.
4. **Wire the instruction to keep it updated.** Check the repo's own
   `CLAUDE.md` (or `AGENTS.md`). If it looks like the user's own project
   instructions (not third-party/course-provided content — read it first, ask
   if unsure), append a short section:
   ```markdown
   ## Progress tracking

   Keep `.second-brain/status.md` current — update its Completed / In progress
   / Blocked sections (and `updated:` date) at the end of any session with
   real progress. This file is how the second-brain planner's `/sync-project`
   pulls status; nothing else reads it automatically.
   ```
   If the file looks third-party-owned (e.g. course-provided guidelines
   shared across students), don't edit it — tell the user instead, so they can
   add the instruction themselves if they want it.
5. **Link the container:** `update_project(container_id, {repo: <path>})`
   (add `status_file: <path>` only if it's not the default
   `.second-brain/status.md`).
6. **Register it.** Add a line for this project under "Tracked projects" in
   `planning/planning-config.md` (create the section if it doesn't exist) —
   this is the human-visible index of what `/sync-project all` will touch.
7. **Report** what was created/linked/registered, and mention `/sync-project
   <project>` is now available.

## Rules

- **Opt-in only** — never auto-track a repo just because it was mentioned or
  worked in; this skill runs when the user explicitly asks to start tracking.
- **Never overwrite** an existing `.second-brain/status.md` — scaffold only if
  absent.
- **Never commit inside the target repo** — creating/editing files there is
  fine (reversible, visible in `git status`), committing on the user's behalf
  is not.
- Don't edit a repo's `CLAUDE.md`/`AGENTS.md` if it reads as third-party
  content (e.g. a course's shared guidelines) — ask instead.
