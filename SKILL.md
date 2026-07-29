---
name: cfs
description: "The agent's persistent personal memory and file system across sessions. Load on every turn — recall surfaces prior context, encode captures the turn's signal. Operations dispatch by trigger: file, find, keep, rule (storage); recall, encode, reflect, direct (knowledge); setup, test, update (admin)."
---

# CFS — Cognitive File System

The agent's persistent context across sessions — personal memory and file system. Load and consult on every turn. Log every execution per `refs/admin/logging.md`.

## Scope

The meta-flow that orchestrates memory and file operations across the user's life. The agent dispatches to a specific operation when its trigger matches; otherwise runs the default per-turn rhythm. Storage and knowledge layers each carry distinct operations; admin operations are out-of-band.

CFS is the agent's primary memory. Harnesses with internal memory systems need no special handling — CFS operates as the primary core memory alongside them; no coupling, mirroring, or migration is required.

## Prerequisites

- Read `config.yaml` for active layers (`storage.active`, `knowledge.active`) and addresses. If `config.yaml` does not exist or the environment is not set up, follow `flows/admin/setup.md`.
- See `refs/admin/safety.md` for operational rules — backend dispatch invariants, user consent, source protection, sensitive data handling.
- See `refs/admin/addressing.md` for the `<backend>:<path>` grammar used in `config.yaml`, admin files, and knowledge nodes.
- For any operation, use the best capability available in your environment — agent-native, MCP, installed CLI, or a CFS-bundled reference implementation under `tools/`. Bundled tools are optional and per-tool; install only what's needed.

## Execution

How operations run, regardless of which branch below dispatched them.

### Subagent delegation

Operations split by execution mode. The goal is to keep the main thread clean of CFS chatter so the user's conversation isn't diverted by routine memory or filing work.

- **Foreground** — `keep`, `reflect`, `rule`, `direct`, `setup`, `test`, `update`. User-driven or scheduled; the user wants to see the work. Use subagents only as internal parallelization within the flow when batching helps (e.g., `keep` fanning out across many todos), never as the outer execution shell.
- **Subagent** — `recall`, `find`, `encode`, `file`. Whenever the harness supports subagents, run these in one so the main thread stays clean. The parent integrates returns by operation:
  - `recall` / `find` return retrieved context — the parent weaves it into the response, no "found X" status line.
  - `encode` / `file` return brief summaries of what changed — the parent surfaces a one-liner so the user is aware something was recorded or filed.

Two chains run inline within their parent subagent rather than spawning siblings:

- `file` → `encode` (when knowledge layer is active) — one file subagent does the whole chain and returns a single outcome.
- `recall` → `find` fallback (fact-like miss in default rhythm) — one recall subagent returns consolidated context.

The engage check (default rhythm Step 1) runs in the main thread before any recall subagent spawns — don't pay subagent latency on trivial turns.

### Subagent contract

A subagent returns:

- `outcome_summary` — parent-surfacable content (retrieved context for recall/find; a brief one-liner for encode/file). Empty when nothing material happened.
- `todos_created` — deferred items written to the admin todo path.
- `consent_needed` — if the operation would cross a consent gate (per `refs/admin/safety.md`), the subagent halts at the gate and returns the prompt for the parent to surface. Subagents do not cross consent gates; the parent owns user-facing decisions.

### Narration

When operations run silently (subagent mode in default rhythm), surface only what the subagent returns as `outcome_summary`. Do not narrate routine recall, encode, or filing — status lines like "loading cfs", "recalling context", "encoding memory" are noise; silence is the target. Explicit operation invocations may report fully; the user asked and expects to see the work.

## Operations

Dispatch directly to an operation when its trigger matches. Recall and encode also fire implicitly per the default rhythm below — they are not gated on explicit phrasing.

### Storage

Active when `storage.active: true` in `config.yaml`.

| Operation | Trigger | Flow |
|---|---|---|
| **file** | New item entering storage; phrases like *"file this"*, *"process my Downloads"*, *"save this receipt"*, *"store this PDF"* | `flows/storage/file.md` |
| **find** | Retrieval — phrases like *"find my passport"*, *"show me my Acme receipts"*, *"where did I put X"*, *"what do I have filed for Y"* | `flows/storage/find.md` |
| **keep** | Maintenance — phrases like *"clean up storage"*, *"anything in unsorted?"*, *"review the todos"*, *"triage drift"*; periodic schedules | `flows/storage/keep.md` |
| **rule** | User establishes / changes / removes a source or target rule — phrases like *"from now on, X items go to Y"*, *"drop the Acme naming rule"* | `flows/storage/rule.md` |

### Knowledge

Active when `knowledge.active: true` in `config.yaml`.

| Operation | Trigger | Flow |
|---|---|---|
| **recall** | User-context queries — facts, decisions, history, references to people / places / projects (*"what's John Doe's email?"*, *"have we discussed X before?"*). Fires implicitly before responding whenever the turn references known entities. | `flows/knowledge/recall.md` |
| **encode** | Phrases like *"remember this"*, *"save that decision"*. Fires implicitly at end of turn whenever the turn produced something worth remembering. | `flows/knowledge/encode.md` |
| **reflect** | Maintenance — phrases like *"review the knowledge graph"*, *"consolidate duplicates"*, *"strengthen connections"*, *"any gaps?"*; periodic schedules | `flows/knowledge/reflect.md` |
| **direct** | User establishes a directive about what knowledge should track or maintain — phrases like *"always record meeting outcomes"*, *"track project status going forward"* | `flows/knowledge/direct.md` |

### Admin

Out-of-band — not part of the per-turn rhythm.

| Operation | Trigger | Flow |
|---|---|---|
| **setup** | First-time environment setup or verification — phrases like *"set up CFS"*, *"verify the environment"* | `flows/admin/setup.md` |
| **test** | Validate CFS flows and routing against test cases — phrases like *"run the tests"* | `flows/admin/test.md` |
| **update** | Update this CFS project clone from upstream — phrases like *"update CFS"*, *"pull latest CFS changes"*, *"check what's new before updating"* | `flows/admin/update.md` |
| **todo** | Explicit todo lifecycle outside another running flow — phrases like *"create a todo"*, *"add a follow-up"*, *"close that todo"*, *"cancel todo X"*, *"update the todo about Y"* | `flows/admin/todo.md` |

## Default behavior

When the user's turn does not match a specific operation trigger, run the per-turn rhythm.

### Step 1: Engage check

Skip the rhythm entirely for trivial standalone exchanges with no user context — greeting, generic factual lookup, isolated code question, math question. If the user mentions any specific entity, project, decision, file, preference, or asks about themselves directly — not trivial.

When in doubt, engage. False positives (a routine episode encoded) cost a note that reflect prunes; false negatives cost permanent memory loss.

### Step 2: Recall

Skip if knowledge layer is inactive.

Follow `flows/knowledge/recall.md`. Integrate retrieved content as context for the response — do not surface citations or wikilinks unless the user explicitly asks.

If recall returned nothing for a fact-like query and storage is active, fall back to `find` on storage; encode what's learned in Step 4.

### Step 3: Work

Respond to the user, perform the task, hold the conversation. Storage and knowledge ops above may dispatch from within the work step when conditions arise mid-task.

### Step 4: Encode

Skip if knowledge layer is inactive.

If the turn produced something worth remembering — a decision, an event, new information about an entity, a process the user articulated — follow `flows/knowledge/encode.md`. Episodic is the conservative default; semantic and procedural fire conditionally per the encode flow's guidance.

## Examples

### Example 1: Explicit operation dispatch

Input: "File this PDF I just dragged in."

Actions:
1. Trigger matches **file** in the Storage menu. Dispatch to `flows/storage/file.md` directly.

Result: the file flow runs; encode chains at the end if knowledge is active.

### Example 2: Implicit fact lookup (default rhythm)

Input: "What's John Doe's passport number?"

Actions:
1. **Engage** — entity reference, fact about user's domain. Engage.
2. **Recall** — read `Memory/Semantic/John Doe.md`; look for passport number.
3. **Work** — recall returned nothing; storage is active, so fall back: `find` in `Archive/John Doe/Identity` for the passport document; extract the number.
4. **Encode** — append the passport number to John Doe's semantic node; encode a brief episodic noting the lookup.

Result: answer surfaced, knowledge enriched for next time.

### Example 3: Project work (default rhythm)

Input: "I'm starting NorthStar for Acme — quarterly metrics dashboard, due end of November."

Actions:
1. **Engage** — specific project, client, decision. Engage.
2. **Recall** — surface any prior context on `Acme` or related projects.
3. **Work** — conversational; no file operation needed.
4. **Encode** — episodic for the kickoff; semantic nodes for `NorthStar` (new) and `Acme` (append project as relationship if exists).

Result: project captured into knowledge for future recall.

### Example 4: Trivial standalone (rhythm skipped)

Input: "hi"

Actions:
1. **Engage check** — greeting, no user context. Skip rhythm.

Result: no operations executed.

### Example 5: Explicit knowledge maintenance

Input: "Sweep the knowledge graph and surface anything worth attention."

Actions:
1. Trigger matches **reflect** in the Knowledge menu. Dispatch to `flows/knowledge/reflect.md` directly.

Result: reflect runs Steps 1–6; produces todos for consent-gated mutations and writes its log.

## Storage structure

```
Admin    / admin     / logs, todo
         / storage   / logs, todo, sources, targets
         / knowledge / logs, todo
Archive  / [entity]   / [domain]   / items & collections
Projects / [entity]   / [project]
Library  / [category]              / items & collections
Unsorted /                           items awaiting processing
```

## Knowledge structure

```
Memory / Episodic   / events, decisions, journal of activity              (date-prefixed .md files)
       / Semantic   / entities (people, orgs, places, projects, things)   (Title Case .md files)
       / Procedural / how-tos, processes, templates as loadable skills    (<skill-name>/SKILL.md dirs)
```

## References

| Directory | Contents |
|---|---|
| `refs/admin/` | Safety, addressing, logging — apply across all layers |
| `refs/knowledge/` | Naming, nodes (frontmatter, body, links), types (episodic, semantic, procedural) |
| `refs/storage/` | Routing, entities, naming, domains, categories, collections |
| `docs/` | Design specification and history |
| `flows/` | Complete operational procedures |
| `tools/` | Optional CFS-bundled reference implementations (gdrive backend, content extraction, OCR). See `tools/README.md` for the catalog and per-tool setup. |
