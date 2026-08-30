# Setup & porting to a new machine

What `git clone` carries, what it doesn't, and how to close the gap. The durable
truth (framework, skills, tasks, knowledge) lives in the two repos; a few
per-machine things must be recreated locally.

## Prerequisites

- **Python 3.11+** (developed on 3.14) — for the MCP server.
- **Claude Code** CLI (`claude` on PATH) — the harness.
- **Obsidian** — the vault editor + Time Blocks plugin host.
- **git**.

## 1. Clone both repos

`notes/` is a **separate repo** nested inside the umbrella (the umbrella
gitignores it). Clone the umbrella, then clone the vault into `./notes`:

```bash
git clone <umbrella-repo-url> second-brain
cd second-brain
git clone <notes-repo-url> notes        # the private knowledge vault
```

> Portability note: the per-project Claude memory (below) is keyed by the repo's
> **absolute path**. If you want `/sync-project` memory + your own memory to carry
> over cleanly, clone to the **same absolute path** as the old machine (same
> username + folder layout).

## 2. `make setup` — MCP venv + registration

```bash
make setup
```

This derives all paths from the clone location and:
- creates `mcp/.venv` + installs `mcp/requirements.txt`,
- registers the `second-brain` MCP with Claude Code (idempotent).

Verify: `make check` (should print `tools: 9`) and `claude mcp list` (look for
`second-brain: ✔ Connected`).

## 3. Obsidian (manual — `.obsidian/` is gitignored)

The vault's `.obsidian/` — config **and all plugins** — is not tracked, so:

1. Open Obsidian → **Open folder as vault** → select `second-brain/notes`.
2. Install / enable the **Time Blocks** plugin (Community Plugins). `/plan-day`
   writes blocks to `notes/.obsidian/plugins/time-blocks/data.json`; the plugin
   creates that file on first use (the MCP also creates it when scheduling).
3. (Optional) enable the other plugins you use — echo-vault, calendar, pomodoro.
4. Set the Obsidian template folder to `_templates/` if you want the note template.
5. After scheduling, run the `Time Blocks: refresh` command to re-render.

## 4. Claude memory (machine-local under `~/.claude`)

Memory lives at `~/.claude/projects/<mangled-abs-path>/memory/` — **not in any
repo**, and the slug encodes the absolute repo path. Two options:

- **Accept fresh (simplest).** The durable truth is already in the vault; memory
  re-accrues as you work. `/sync-project` needs the *linked* project present
  locally — its own Claude sessions rebuild its memory over time.
- **Copy it over.** `rsync` the relevant `~/.claude/projects/<slug>/memory/`
  dirs. Only works if the new machine reproduces the **same absolute paths** (so
  the slugs match); otherwise Claude looks under a different slug and won't find
  them.

A container links its upstream via `repo:` + `memory:` frontmatter (absolute
paths) — update these if the new machine's layout differs. The portable
long-term fix is a repo-committed `.second-brain/status.md` per project (in git,
relative path) instead of reading `~/.claude` — see ADR-011.

## 5. Restart Claude Code

MCP tools load at session start, so **restart** (or `/mcp` reconnect) after
`make setup`. Then `/plan-day` and `/sync-project` are live.

## 6. (Optional) shell aliases

```bash
brain() { cd ~/path/to/second-brain && claude "$@"; }        # planner agent
notes() { cd ~/path/to/second-brain/notes && claude "$@"; }  # knowledge agent
```

Launch location picks the agent (planner vs knowledge skills) — see `CLAUDE.md`.

---

## What travels vs what's local

| | Carried by clone | Recreate on new machine |
|---|---|---|
| Framework (`mcp/*.py`, skills, docs, templates) | ✅ | |
| Tasks + knowledge (`notes/`) | ✅ (separate clone) | |
| `mcp/.venv` | | `make venv` |
| MCP registration (`~/.claude.json`) | | `make register` |
| Obsidian config + plugins (`.obsidian/`) | | reinstall (step 3) |
| Claude memory (`~/.claude/.../memory`) | | copy or re-accrue (step 4) |
| `EchoVault/` flashcard data | | machine-local |
