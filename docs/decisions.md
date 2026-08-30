# Decision log (ADR)

Lightweight architecture decision records for the second-brain system — the
*why/history* behind the current design. `system-design.md` records the *what*;
this records why we chose it and what we rejected. Newest at the bottom. Format:
context → decision → why → rejected.

---

## ADR-001 — Two source-of-truth stores: Obsidian (knowledge) + Notion (tasks)
- **Context:** want one system for knowledge + task/project planning.
- **Decision:** knowledge lives in an Obsidian Markdown vault; task state in Notion.
- **Why:** one source of truth per concern; each store fits its data (files for
  durable knowledge, Notion UI for churny task state). Claude is the bridge.
- **Rejected:** tracking task status inside the vault; a single tool for both.

## ADR-002 — No spaced-repetition scheduling in the planner
- **Decision:** dropped SM-2/Anki-style scheduling from the core system.
- **Why:** Reo didn't want the bookkeeping. Retention lives in **EchoVault** (a
  separate service) via note-diff flashcards; `grill-me` is on-demand reasoning,
  not retention.

## ADR-003 — Reuse the existing `data-science-notes` vault as the knowledge store
- **Context:** a fresh vault was built first, then reconsidered.
- **Decision:** fold knowledge into Reo's existing established vault rather than a
  new one; the 12 distilled notes were migrated in.
- **Why:** build on the established, git-versioned, daily-driver vault instead of
  fragmenting knowledge across two places.

## ADR-004 — OKF frontmatter + Markdown relative links
- **Decision:** all notes follow Open Knowledge Format (`type` required, +
  `resource`/`timestamp`/`tags`); links are Markdown relative links, not
  `[[wikilinks]]` (placeholders to non-existent notes stay as wikilinks).
- **Why:** OKF is a vendor-neutral, human- + agent-readable standard (Google's
  "LLM-wiki pattern"). Markdown links are portable and can reach **across repos**
  (a stated goal); wikilinks can't leave the vault.
- **Rejected:** keeping wikilinks (not portable); a bespoke frontmatter schema.

## ADR-005 — Umbrella-rooted layout; two agents by launch location; two git repos
- **Decision:** `second-brain/` is the umbrella (planner + orchestration); the
  vault is nested at `notes/`. Launch Claude at the umbrella for the planner
  agent, at `notes/` for the knowledge agent. Umbrella and `notes/` are
  **separate git repos** (umbrella gitignores `notes/` + private `import/`).
- **Why:** physical realization of the two-agent split; keeps the shareable
  agentic framework separate from private knowledge content.
- **Rejected:** two fully-separate sibling repos (more churn); a git submodule
  (overkill, pins private notes).

## ADR-006 — Vault-canonical, Notion as supplementary mirror
- **Decision:** the vault is the canonical source of truth. Notion mirrors only
  the plan/task slice (`type: task`/`plan` files) — the **whole file**
  (frontmatter→properties, body→page content). Reconciliation is
  **last-writer-wins by timestamp** (OKF `timestamp` vs Notion `last_edited_time`);
  a user edit in Notion flows back to the vault.
- **Why:** vault is the better medium for agents (Markdown + git); Notion is the
  better medium for human actions (checkboxes, mobile). Explicit reconciliation
  avoids the two-editable-copies drift problem.
- **Rejected:** Notion as source of truth; periodic one-way exports as the primary.

## ADR-007 — Intelligence = custom MCP server + text skills; model-agnostic
- **Decision:** a custom MCP server exposes the vault + scheduling as mechanical
  tools; skills are editable text workflows with heuristics; the conversational
  layer is not built (Claude/local model). First deliverable = the time-blocking
  planner (`plan-day` + MCP tools).
- **Why:** MCP is model- and harness-agnostic (Claude today, Ollama later);
  keeping intelligence in tools + text keeps the model swappable.
- **Rejected:** hardcoding workflow logic into tools; a bespoke conversational UI.

## ADR-008 — Indexing: automatic `_index.md` + curated MOCs
- **Decision:** per-folder `_index.md` is auto-generated (exhaustive, script-run);
  curated Maps of Content (MOCs / Permanent Notes) are a separate, manual layer.
- **Why:** the two answer different questions ("what's here?" vs "what matters?").
  Keep curation human, assembly automatable (e.g. a `moc:`/`starred` frontmatter
  marker the agent assembles from).

## ADR-009 — `docs/` folder + this decision log
- **Decision:** `second-brain/docs/` holds all system documentation
  (`system-design.md`, this ADR log, future roadmap).
- **Why:** design rationale lived only in chat; `system-design.md` captured the
  "what" but not the "why". This log makes the reasoning durable so
  stateless-by-design sessions can re-read it.

## ADR-010 — Task model = containers (files) + steps (checkboxes)
- **Decision:** a `type: task` file is a **container** (phase/project) holding
  shared classification + a `status` rollup; the **step** — a `- [ ]` checkbox in
  its body — is the atomic schedulable/completable unit, addressed by
  `"<path>:<line>"`. Per-step metadata is inline (`[size:: S|M|L]`, `📅`, `[↗]`);
  steps inherit the container's classification. The MCP flips accordingly
  (`list_tasks` returns steps; `list_projects` returns containers) and **edits
  only in place** — no write reflows a file.
- **Why:** (1) the step id matches the Time Blocks plugin's own `path:line`
  scanner format, so scheduled steps get native completion + click-to-source
  (the earlier line-2 anchor was a dead link); (2) a time block is step-sized
  (30–120 min), not whole-task-sized; (3) shared frontmatter lives once, not
  copied across dozens of files; (4) the agent reads one coherent file per phase
  instead of many atomized ones. In-place-only writes are forced by line
  addressing — a reflow would orphan every step id and existing block.
- **Cost accepted:** steps can't hold YAML, so `size` (and any per-step field)
  goes inline as a Dataview field; the MCP gained a checklist parser.
- **Rejected:** one-file-per-task (frontmatter repetition, mis-sized blocks,
  dead Time Blocks link); a Notion row per step (steps stay page-body checkboxes,
  so Notion sync granularity is unchanged).
- **Migration:** the 41 atomized task files compacted to 10 containers
  (4 embedding phases, 4 learning tracks, CS336, planner-agent). Safe to drop the
  old per-task uuids — nothing had synced to Notion yet (`notion_id` all empty).

## ADR-011 — repo → vault sync via the project's Claude memory (one-directional)
- **Decision:** a local project repo is the **source of truth for its own
  execution**; the vault container mirrors it. Sync is **one-directional
  (repo → vault)** — the repo owns step `done`-state, new deliverables, and phase
  `status`; the vault owns order, priority, and all scheduling. The feed is the
  project's **Claude memory** (`~/.claude/projects/<slug>/memory/`, esp.
  `type: project` files); a container declares its upstream with `repo:` +
  `memory:` frontmatter. `/sync-project` reads → interprets → proposes → applies.
- **Why:** (1) one-directional avoids the two-writers-clobber problem (unlike
  Notion, which is bidirectional for the *human-editing* slice); (2) the memory is
  already a curated, *typed* summary — a far lower-noise interface than git diffs;
  (3) the mangled memory-dir slug isn't reliably reversible from the repo path
  (hyphens vs slashes are ambiguous), so the container stores `memory:` explicitly.
- **Fault tolerance:** Claude Code's memory schema drifts as the harness evolves,
  so the MCP tool (`read_project_status`) is a **dumb pipe** — it returns loose
  `{description, type, modified, body}` blobs keyed off stable anchors (frontmatter
  delimiters + prose), and the **skill's LLM does the interpretation**. Because the
  consumer is a language model, unknown fields degrade to "read the prose" instead
  of breaking a parser. Tolerance lives in the skill, not the pipe — the same
  mechanical-MCP / reasoning-skill split as everything else.
- **Deferred:** promoting reusable *learnings* (gotchas, design lessons) from
  memory into knowledge notes — interesting, `/librarian`-flavoured, opt-in later.
  A repo-committed `.second-brain/status.md` contract (portable, git-tracked) is
  the graduation target from reading `~/.claude` memory directly.
