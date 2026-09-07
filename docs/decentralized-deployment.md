# Decentralized deployment — home server sketch

**Status: design/sketch only — nothing here has been implemented.** Captures a
conversation about moving the second-brain stack (vault + MCP + Claude Code
orchestration) onto a home server, with Obsidian staying local.

## 1. The split

- **Obsidian** (GUI: Time Blocks canvas, Pomodoro, EchoVault UI) stays on this
  device — it's a desktop app tied to a local folder, no clean "headless"
  option.
- **Claude Code sessions + the second-brain MCP** run **on the home server** —
  both the planner (`brain`) and knowledge (`notes`) agents.
- The **vault** (`notes/`) is canonically stored on the server; the laptop
  keeps a synced replica so Obsidian has something local to read/write.

This is a meaningful simplification versus a "remote MCP, local Claude Code"
split: because Claude Code itself relocates to the server, the MCP can stay
exactly as it is today — a local `stdio` subprocess, just co-located with
Claude Code on the server instead of on the laptop. No remote-transport
(`streamable-http`/SSE) work needed. The reason this matters: skills read
`planning-config.md`, `VISION.md`, cycle files, etc. directly via Claude
Code's own `Read`/`Edit` tools, **not** through an MCP call — those tools
operate on whichever machine Claude Code itself runs on. Splitting "MCP here,
Claude Code there" would leave direct file reads pointing at nothing unless
the vault were *also* reachable from wherever Claude Code runs. Colocating
Claude Code with the vault on the server sidesteps that entirely.

```
┌─────────────────────────────┐              ┌───────────────────────────────────┐
│  Laptop (this device)       │              │  Home server                       │
│                              │              │                                     │
│  Obsidian (GUI only)         │              │  Claude Code sessions               │
│  ├─ Time Blocks canvas       │              │  ├─ `brain`  (planner)              │
│  ├─ Pomodoro / EchoVault UI  │              │  └─ `notes`  (librarian etc.)       │
│                              │              │                                     │
│  notes/  (local replica) ────┼──── git ─────┼──► notes/  (canonical copy)         │
│  ├─ knowledge/, planning/   │  push/pull    │      + second-brain MCP (stdio,     │
│  └─ .git history             │  (existing,  │        unchanged — colocated here)  │
│                              │   unchanged) │                                     │
│  .obsidian/plugins/          │              │  .obsidian/plugins/                 │
│  ├─ time-blocks/data.json ───┼─ Syncthing ──┼──►  time-blocks/data.json           │
│  └─ echo-vault/ (card store) │  or network  │      echo-vault/ (card store)       │
│                              │  mount (see  │                                     │
│                              │  §2)         │                                     │
└─────────────────────────────┘              └───────────────────────────────────┘
```

## 2. Sync: two categories of file, not one mechanism

`.obsidian/` is **entirely gitignored** today (including `data.json` and
EchoVault's card store) — a real prerequisite gap, not just a config
afterthought. Git alone won't move the one thing this whole model most needs
synced: the server writing a schedule and the laptop's Obsidian seeing it.

**Git (unchanged, existing infra)** — for genuine *content*: `knowledge/`,
`planning/` (tasks, cycles, weeks, `VISION.md`), skills, docs. Already works
this way; needs no new tooling, just the normal discipline of pulling before
starting work on either side.

**For the currently-gitignored live app state** (`data.json`, EchoVault's
store) — two options, and which one's better depends heavily on one fact
about actual usage: **both devices are on the same LAN ~95% of the time.**

### Option A — Syncthing
Free, open-source, peer-to-peer file sync (no cloud, no account). Each device
runs a background agent; a shared folder is paired by device ID; changes
propagate continuously. A genuine simultaneous edit on both sides doesn't
silently overwrite — it's kept as a `file.sync-conflict-<date>` copy, never
destructive. On the same LAN it uses local discovery and connects
device-to-device directly (fast, no internet dependency); off-LAN it falls
back to relay/NAT traversal (works, just slower). Each side always has a
**local** copy, so reads never depend on the network.

Deliberately **scoped to only the gitignored live-state files**, not the whole
vault — syncing a folder that's *also* an actively-committed git repo from two
independent writers risks corrupting `.git` internals (a known anti-pattern:
don't run continuous background file-sync over `.git`). Git and Syncthing stay
non-overlapping: git owns tracked content, Syncthing owns exactly what git
ignores.

### Option B — a plain network share (SMB/NFS) + Tailscale for the 5%
Given the LAN is the common case: mount the server's vault folder directly
onto the laptop over the network; Obsidian reads/writes the **one true copy**
directly — no second copy, so no sync lag and no possibility of a conflict
file, ever. Simpler mental model than Syncthing for the 95% case. The gap is
entirely the remaining 5%: off the home network, the mount doesn't work unless
bridged — **Tailscale** (a near-zero-config personal VPN) would make the
laptop and server behave as if always on the same LAN, keeping the same mount
working from anywhere.

**Tradeoff:** Option A is more resilient (each side has a real local copy;
survives the laptop being offline entirely) at the cost of occasional
non-destructive conflict files and one more background service. Option B is
simpler and has zero conflict risk *for the 95% case*, but Obsidian pointed at
a network drive can occasionally be twitchy (file-locking/latency quirks some
plugins notice over SMB), and needs Tailscale wired in for the 5% case to work
at all. Given the actual usage pattern described, **Option B is the leaner
fit** — but this is a judgment call, not a settled decision.

The rest of `.obsidian/` (installed plugin binaries, workspace layout) stays
purely machine-local either way, reinstalled per-machine via `make install` as
today — genuinely shouldn't sync.

## 3. Resource profiling: three orchestration shapes

Three different ways the "reasoning" layer of this stack could run, profiled
by what each actually requires. (1) and (2) are what's live today; (3) is a
hypothetical self-hosted alternative raised by the local-model discussion
earlier — assumed here to mean **Nous Research's Hermes model family**
(flag if a different "Hermes" was meant).

### 3.1 — MCP server (`mcp/server.py`)

The mechanical layer, regardless of which orchestrator drives it.

| Resource | Requirement |
|---|---|
| Compute | Trivial — a single Python process, negligible CPU except brief spikes during embedding calls (network I/O, not local compute) |
| Memory | Tens of MB |
| GPU | None — no local model inference happens here at all |
| Storage | The vault itself (a personal knowledge base + task containers is realistically low tens of MB) + `data.json` (KB-scale) |
| Network | Outbound HTTPS only, to OpenRouter (`similar_cards`, `sync_plans`'s Notion calls) — no inbound port needed while `stdio` |
| Software | Python 3.11+, the packages in `mcp/requirements.txt` |

Comfortably runs on hardware far below "home server" tier — a Raspberry
Pi-class device would handle this alone without strain.

### 3.2 — Claude Code orchestration

The agent loop as it runs today: Claude Code (the CLI) drives skills, calls
MCP tools, and reasons via Anthropic's hosted models over the API.

| Resource | Requirement |
|---|---|
| Compute | Modest — the CLI itself, no local model inference (reasoning happens in Anthropic's cloud) |
| Memory | Low hundreds of MB per active session |
| GPU | None |
| Network | **Reliable outbound HTTPS to Anthropic's API is now load-bearing** — if the server's home internet drops, the whole reasoning loop stops (the MCP and vault would still be locally intact, just nothing can drive them) |
| Cost | Ongoing — a Claude subscription/API usage cost, not a one-time hardware spend |
| Always-on jobs | Interactive sessions need a live terminal (SSH+`tmux`, or Claude Code's own remote-session support, worth checking); truly unattended/scheduled jobs (e.g. a cron-triggered `/plan-day`-style pass) would want the Agent SDK / headless invocation rather than a left-open interactive session |

The home server's job here is almost entirely "stay on and stay connected" —
the heavy lifting is elsewhere.

### 3.3 — Hermes agent orchestration (self-hosted, hypothetical)

Replaces Anthropic's cloud inference with a **locally-run** open model,
requiring an actual inference stack on the server, not just a CLI.

| Resource | Requirement |
|---|---|
| Model choice | Hermes ships at multiple sizes (8B up to 70B+, Llama/Mistral-based). Per the earlier local-model discussion in this project: **tool-use reliability in a multi-step agentic loop is the real bottleneck**, not raw fluency — an 8B model is a real risk for the kind of multi-tool orchestration this system does; 70B-class is far more likely to hold up, but costs much more hardware. |
| GPU / VRAM | The dominant cost. Rough quantized (GGUF, 4-bit) footprints: **8B ≈ 5–8GB VRAM** (or slow CPU-only inference on ~16GB RAM); **70B ≈ 40–48GB VRAM** — doesn't fit on a single consumer 24GB card, realistically needs two, or a professional-tier card. This is a genuine hardware purchase, not something a typical home server already has. |
| Serving stack | A model alone isn't an agent — needs **Ollama** (or similar) to serve it with an OpenAI-compatible API, *plus* an actual orchestration harness on top to drive MCP tool-calling (Goose, `mcp-use`, `fast-agent`, or Pydantic AI, per the earlier harness discussion) |
| Network | **None required for inference** — a genuine advantage, fully offline-capable for the reasoning loop itself. (MCP tools that call external services — OpenRouter embeddings, Notion sync — still need internet regardless of which orchestrator drives them.) |
| Cost | No per-token API cost once running, but real upfront GPU cost + ongoing electricity for a GPU kept warm for scheduled/always-on use |
| Reliability caveat | The most important line in this table: **capability risk, not just resource cost.** A smaller local model can look fully configured and still silently mishandle multi-step tool orchestration in ways that are hard to notice until something's already gone wrong — this was flagged in the earlier harness conversation and applies here directly. |

**Net comparison:** (1) and (2) together are what's running today and need
zero new hardware — the home server's role is just "always-on host." (3) is a
substantial, separate hardware+ops investment (a GPU, a serving stack, a
harness) traded for no API cost and full offline capability, with a real
capability tax unless a large-enough Hermes variant is used.

## 4. Open decisions

- Sync mechanism: Syncthing vs. network-mount + Tailscale (§2) — leaning
  network-mount given the LAN-majority usage pattern, not yet decided.
- Remote-session mechanism for launching Claude Code on the server: bare
  SSH+`tmux` vs. Claude Code's own remote/session support — needs a closer
  look at the docs before deciding.
- Whether (3) (self-hosted Hermes) is worth pursuing at all, given (1)+(2)
  already work and need no new hardware — likely only worth it for the
  offline-capability or no-API-cost properties specifically, not as a general
  replacement.
- The precise `.gitignore` carve-out for `data.json`/EchoVault's store, if
  Syncthing (rather than network-mount) is chosen — un-ignoring a file nested
  inside an already-ignored directory has a known gitignore-negation gotcha,
  worth getting right rather than guessing.

## 5. What doesn't change either way

- MCP code (`tasks.py`, `schedule.py`, `server.py`) — untouched, still `stdio`.
- Skills — untouched; they already just `Read`/`Edit` files + call MCP tools.
- The two-repo structure (umbrella + nested `notes/`) — unchanged; `make
  setup` (see `docs/SETUP.md`) already covers cloning + provisioning a fresh
  machine, home server included.
