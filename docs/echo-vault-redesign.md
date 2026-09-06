# EchoVault redesign — agent-first card generation

Design proposal for the retention pillar. Supersedes two things in EchoVault's
original design: git-commits-as-change-detection, and single-shot LLM
extraction as the card-generation mechanism. **Status: design only — no code
changed.** See [ADR-014](decisions.md) for the short decision record.

## 1. Why the current pipeline falls short

Today: a file's git diff → one LLM call to the backend → cards, straight out.
That's **extraction** — summarize what's here — and it has a ceiling. Concrete
evidence from EchoVault's own logs (`backend/logs/requests.jsonl`):

- **Duplicate shallow cards.** Five different FastAPI-adjacent notes
  (`fastapi-auth.md`, `fastapi-body.md`, `fastapi-path.md`, `fastapi-query.md`,
  the `api/_index.md`) each independently produced a card asking essentially
  *"What is FastAPI?"* — because each file is summarized in isolation, with no
  memory of what's already been tested.
- **A degenerate card**: one generated MC question has `"correct_answer": null`
  — a real quality failure a self-critique pass would catch.
- **No depth calibration.** "What is FastAPI?" is beneath someone shipping ML
  systems professionally. Extraction has no notion of the learner's level.

Root cause: **stateless, one-shot generation.** No memory of existing coverage,
no cross-note context, no judgment about what's actually worth testing.

## 2. Design principles

1. **Curate, don't just extract.** An agent that reads existing coverage before
   writing a new card, not a function that summarizes one file in isolation.
2. **Depth relative to the learner.** Calibrate to current expertise (VISION,
   roadmap, topic performance) — don't test what's already obvious.
3. **Question type is a deliberate choice**, not a default. Recall is the
   lowest-value type and should be used sparingly.
4. **Cross-note synthesis is first-class.** A card can connect two notes; this
   is structurally impossible for single-file extraction and is exactly what a
   tool-using agent is for.
5. **Conservative bias.** Skip more than you card — a bad/redundant card costs
   real review time forever; a missed one costs nothing.
6. **Same split as the rest of the system:** mechanical fetch/write vs. the
   actual judgment. The reasoning gets deeper; it doesn't move to a different
   place model-agnostically at the cost of the existing surface.
7. **Preserve the Obsidian plugin's API contract.** The plugin is the existing
   UI (review session, grading, the generate command) — it is NOT being
   replaced. `POST /generate-flashcards-batch` (and `/feedback`, `/health`,
   `/config`) keep their current request/response shapes. What changes is
   what the backend does **inside** that same call — single-shot extraction
   becomes the multi-step reasoning pipeline below, but the plugin never knows
   the difference. This is "change the implementation behind a stable
   interface," not a new integration model.

## 3. Change detection (replaces git-diffing)

The original mechanism — `git add -A && git commit "EchoVault: <ts>"` as a
checkpoint to diff from — collides with the vault having other independent
committers (the planner, `/distill`, `/librarian`, you in Obsidian). See
ADR-014 for the full reasoning. **This fix is entirely internal to the
plugin's own change-detection logic — it never touches the backend API
contract.** The plugin already computes a diff client-side and sends
`diff_content` as plain text in the `/generate-flashcards-batch` request; the
backend has never known or cared whether that diff came from git. Swapping the
plugin's git-diff for a manifest-diff changes nothing about what it sends.

The replacement:

- A **content manifest** at `notes/EchoVault/manifest.json` — gitignored,
  the same pattern the Time Blocks plugin uses for `data.json`. No git
  involvement at all.
- Store each processed note's **previous full content**, not just a hash, so a
  local text diff (`difflib`) can still tell the model "here's what's new"
  rather than re-feeding the whole file every time.
- **Scope strictly to `knowledge/`** — never `_inbox/` or `planning/`. This
  respects the capture → distill → file pipeline: a raw jot isn't "true"
  knowledge yet, so it shouldn't be tested.
- Optional **maturity threshold** — skip a note edited in the last N hours, so
  a half-written draft doesn't get carded mid-thought.

## 4. Architecture — where the reasoning actually lives

Two callers share **one card store and one generation contract**: the Obsidian
plugin (existing UI, unchanged) and the second-brain planner (the new
integration). Neither owns the reasoning exclusively — the backend does, behind
the stable API.

```
Obsidian plugin ──POST /generate-flashcards-batch──┐
                                                     ├─▶ backend (the agent, upgraded)
second-brain MCP (generate_cards) ──same request────┘         │
                                                                ▼
                                          notes/EchoVault/  (card store + manifest,
                                          shared, gitignored — both callers read it)
```

**Inside the backend**, `/generate-flashcards-batch` becomes a multi-step
pipeline instead of one extraction call — same request/response shape, deeper
implementation:

1. **Survey** — the request already carries `diff_content` per file (unchanged).
2. **Contextualize** — two different retrieval jobs, two different mechanisms
   (see §4a below): `similar_cards()` (embeddings) for dedup, `related_notes()`
   (the vault's existing link graph) for cross-note connections. Also pull
   ease/lapses/last-graded for the note's topic, for depth calibration.
3. **Decide** — worth testing at all (salience filter)? Overlaps existing
   coverage? What depth, what question type?
4. **Draft** — author the card(s), grounded in and citing the source sentence(s).
5. **Self-critique** — a second pass: ambiguity, duplication, factual
   grounding, degenerate distractors (exactly the `correct_answer: null` class
   of bug seen today).
6. **Return** — the same `BatchGenerateResponse` shape the plugin already
   parses; each card additionally carries a short rationale for its own
   records/debugging.

**The second-brain side is a thin client, not a rival pipeline:**

| second-brain MCP tool | What it does |
|---|---|
| `generate_cards(...)` | calls the **same** `/generate-flashcards-batch` endpoint the plugin uses |
| `reviews_due(date?)` | reads the shared card store for today's due count/list — sizes the daily review habit block |
| `grade_review(id, grade)` | writes an SM-2 update to the **same** store the plugin's review UI writes to |

Because both callers hit the identical contract and the identical store,
grading a card in the Obsidian UI and grading it via a second-brain `/review`
session update the same state — no drift, no second source of truth.

**One open backend-side question this creates:** today the backend is
stateless — it's handed `diff_content` and returns cards, with no read access
to the vault. Steps 2–3 need it to see existing cards/related notes, so it
needs either (a) read access to `notes/EchoVault/` (a mounted path/volume), or
(b) the plugin passes richer context in the request as an **additive, optional**
field. (a) keeps the plugin's request payload untouched entirely — probably
the cleaner choice, since the backend already runs as a local service
(`docker-compose`) that can simply be given the vault path.

### 4a. Dedup and "related" are two different retrieval problems

Don't reach for one mechanism to answer both. Neither "a knowledge graph" nor
"plain text indexing" alone is right — but a **knowledge graph already exists**
here, for free, and doesn't need to be built:

- **Dedup → embedding similarity, not text matching.** The FastAPI duplicates
  weren't identical strings ("What is FastAPI?" vs. "FastAPI is primarily used
  for..." vs. "...how does it relate to authentication?") — plain keyword/BM25
  indexing catches exact-phrase overlap but is blind to paraphrase, which is
  exactly how duplicates actually show up. `similar_cards(candidate_text,
  threshold?)` embeds the draft and compares (cosine similarity) against
  existing card embeddings. At this corpus size (hundreds–low-thousands of
  cards), this is a flat file of vectors + a brute-force numpy matmul — no
  vector DB needed. **The similarity score isn't just skip/keep**: a
  near-exact match → skip; a high-but-not-identical match → the signal to
  draft a *harder or different-angle* question about the same concept instead
  (feeds the depth-calibration in step 3), rather than a flat duplicate.
- **Cross-note connections → the vault's own link graph, not a new one.**
  Obsidian's markdown links + shared tags/folders **already are a knowledge
  graph** — nodes (notes) and edges (links/tags) that exist as a side effect of
  how the vault is written, not a structure that needs constructing or
  maintaining. `related_notes(note_path)` just traverses 1–2 hops of existing
  links or shared-tag membership. This gives graph-*reach* for connection-cards
  without graph-database weight — no entity/relation extraction pipeline, no
  separate index to keep in sync.
- These two tools solve different questions ("is this the same fact I already
  test" vs. "what's conceptually nearby") — keep them separate rather than
  building one general "similarity" tool that tries to do both.

## 5. Question-type taxonomy — the real lever over extraction

- **Recall** — "What is X?" Use sparingly; genuinely new terminology only.
- **Application** — "Given scenario X, would you use A or B, and why?"
- **Mechanism / why** — "Why does LoRA reduce trainable params without hurting
  quality?"
- **Contrast** — "TRL vs. Unsloth vs. Axolotl — what's the key tradeoff for a
  memory-constrained run?" (directly useful for the SFT-hands-on container)
- **Connection / synthesis** — links two notes/concepts; needs
  `related_notes()` cross-note context — impossible for single-file extraction.

## 6. Adaptive personalization loop

`topic_performance()` aggregates SM-2 ease/lapses by tag or topic. Feed that
into step 3 (Decide): strong, easy retention in a topic → fewer/harder cards
there, reallocate the new-card budget to weaker or newer topics. This is the
thing pure extraction can never do — it has no memory of how you've performed.

## 7. Gap-probing — testing what's missing, not just what changed

Everything above is **reactive**: a note changes → test it. A real tutor is
also **proactive** — it notices what isn't there, or isn't solid, without
waiting for an edit to trigger it. This is the actual difference between a
study aid and a tutor, and it needs a genuinely separate pass (§7c), not a
tweak to the reactive pipeline.

### 7a. Gap types

- **Shallow-coverage** — a note states *what* something is but not *why/how*
  it works (e.g. "LoRA reduces trainable params" with no mention of the
  low-rank mechanism). A probe here is a card that exposes the gap even if the
  note itself can't fully answer it — sometimes the "card" surfaces as a
  prompt to go deepen the note, not just a flashcard.
- **Prerequisite gaps** — note B links to / assumes concept A, but A's own note
  is thin or missing. Detectable cheaply via the same link graph as
  `related_notes()` (§4a): follow a note's outlinks and check whether the
  target exists and has real content.
- **Weak-performance gaps** — `topic_performance()` already flags a struggling
  topic (§6); a tutor doesn't just repeat the same failed card, it probes
  *adjacent and prerequisite* concepts to isolate exactly what's missing.
- **Silence gaps** — a VISION 1-year aim (e.g. GPU/infra) has near-zero notes
  or cards. There's no source content to ground a flashcard in, so the output
  here isn't a card at all — it's a **signal**: "you have ~0 coverage on a
  stated aim." This is the knowledge-side mirror of `/plan-week`'s existing
  "neglected arc" check for *tasks* — the same gap-detection idea, one level
  down, applied to *knowledge* instead of *scheduled work*.

### 7b. Mechanism per gap type

| Gap type | How it's detected |
|---|---|
| Shallow-coverage | Reasoning judgment — the model reads a note and assesses whether it stops at *what* without *why/how* (not mechanical; a genuine LLM judgment call) |
| Prerequisite | Mechanical — walk `related_notes()`'s existing link graph, flag thin/missing targets |
| Weak-performance | Mechanical — `topic_performance()`, already planned |
| Silence vs. VISION | Reasoning — compare topic/tag frequency in `knowledge/` + the card store against VISION's aims (reuses the same aim-mapping `/plan-cycle` already does in its per-aim ledger) |

### 7c. A third, separate cadence

Generation (§7d below) is per-diff and daily; review is daily. **Gap-probing
is neither** — it's a whole-corpus scan, not tied to any single note changing,
and doesn't need to run often. Weekly fits naturally, and pairs well with
`/plan-week` (which already does the task-side neglect check) — a natural
place to also surface knowledge-side gaps in the same sitting, even though the
mechanism (backend + card store) is separate from the planner's task data.

## 8. Generation and review are separate habits (ties to ADR-012)

- **Generation** — less frequent (daily/on-demand), authors new material. A
  background maintenance task, not necessarily a scheduled block.
- **Review** — the actual daily **dynamic-load habit**: `reviews_due` sizes
  the block, `/plan-day` reserves it, adherence is tracked.

Don't conflate authoring new cards with practicing existing ones — they have
different cadences and different risk profiles (a bad review costs a few
minutes; a bad card costs review time indefinitely until retired).

## 9. Where the FastAPI backend fits now

**It stays "the generator" — that's the whole point of preserving the
contract.** What changes is only what happens inside the handler (§4). Nothing
here requires touching the plugin.
- The backend gains **read access to the shared card store** (`notes/EchoVault/`)
  so it can do dedup/context lookups — likely a mounted volume in
  `docker-compose.yml`, since it already runs locally alongside the vault.
- It keeps its existing **observability** (cost tracking, logs), and —
  notably — the repo already has an `evals/` LLM-as-judge harness. That
  becomes the tool to **A/B the upgraded pipeline against today's extraction
  baseline** — a real quantitative before/after using an asset that already
  exists.
- **OpenRouter stays the model provider** for the backend's LLM calls,
  unchanged — this redesign is about the reasoning *steps*, not the model
  behind them. (The earlier local-model/OpenRouter harness discussion was
  about the *second-brain planner's* own model choice — a separate axis from
  what model the EchoVault backend itself uses.)

## 10. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Over-testing trivial content | Conservative salience bias — skip by default |
| Hallucinated/ungrounded cards | Require each draft to quote/cite the exact source sentence(s) |
| Cost/latency of multi-step reasoning per note | Batch + a per-run budget (cap new cards/day), not per-edit |
| Re-litigating the same "not card-worthy" note | Record the decision (even a skip) in the manifest so it isn't re-considered until content actually changes |
| Gap-probing surfaces a "gap" that isn't real (shallow-coverage is a judgment call, not mechanical) | Bias toward *surfacing as a question to you*, not asserting a gap exists — a probe card, not a verdict |

## 11. Open questions (resolve when building)

- Confirm-before-write for ambiguous calls, or fully background with a
  periodic digest? (Leaning: digest-only — treat like `/today`, not `/plan-day`.)
- Maturity threshold — skip notes edited in the last N hours? What's N?
- Should question-type mix be user-tunable, the way size/priority dials live in
  `planning-config.md`?
- Should silence-gap signals (§7a) surface inside `/plan-week` alongside the
  existing task-neglect check, or as their own separate report?

## 12. Status & next step

Design only. Builds on ADR-012 (dynamic-load habit) for the review side; this
document covers the generation side (§1–6, §8) and the gap-probing side (§7).
**The Obsidian plugin's API contract is unchanged throughout** — this is a
backend-internal upgrade plus a thin second-brain client, not a new
integration model.

When ready to build, roughly in order:
1. Plugin-side: swap the git-checkpoint diffing for the content manifest (§3)
   — internal to the plugin, no contract change.
2. Backend-side: give it read access to `notes/EchoVault/`, then upgrade
   `/generate-flashcards-batch`'s implementation to the multi-step pipeline
   (§4) — same request/response shape.
3. second-brain MCP: scaffold `mcp/echo.py` (mirroring `notion.py`'s dumb-pipe
   pattern) with `generate_cards` (thin proxy to the same endpoint),
   `reviews_due`, `grade_review` (both reading/writing the shared store).
4. Wire the daily review as a dynamic-load habit (ADR-012) via `/plan-day`.
5. Use the existing `evals/` harness to A/B the new pipeline against the old
   extraction baseline before trusting it fully.
6. **Gap-probing (§7) — build after the reactive pipeline is trusted, not
   alongside it.** It's a genuinely separate, proactive capability (whole-corpus
   scan, weekly cadence) layered on top of a working reactive base, not a
   day-one requirement.
