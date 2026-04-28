# Reflect

Keep the CFS knowledge layer healthy — strengthen connections, consolidate duplicates, promote patterns, surface gaps. Destructive operations on existing nodes (renames, merges, restructures, deletions) require user consent per `refs/admin/safety.md` § User consent. Log every execution per `refs/admin/logging.md`.

## Scope

Four goals:

1. **Resolve** — pending knowledge todos are triaged and addressed or escalated.
2. **Consolidate** — duplicate semantic nodes merged; competing procedural nodes reconciled.
3. **Promote** — recurring patterns in episodic content surfaced as procedural templates; entities mentioned across episodes but lacking semantic depth get nodes.
4. **Strengthen** — weak or missing links repaired; orphan nodes connected; gaps surfaced.

## Prerequisites

- Read `config.yaml` for knowledge layer paths.
- See `refs/admin/safety.md` § User consent for the rule on what reflect may and may not do — reflect performs many mutations (renames, merges, restructures, deletions); each is consent-gated.
- Read `{admin}/knowledge/todo/` for pending items.

## Input

- A specific area to reflect on (a tag, an entity, a timeframe, a type).
- Or no target — orient from recent encode logs and pending todos.

## Output

- Strengthened knowledge graph: consolidated nodes, repaired links, new procedural templates promoted from observed patterns.
- Resolved todos in `{admin}/knowledge/todo/` (marked complete with notes).
- New todos for issues requiring user input or further consideration.
- Execution log in `{admin}/knowledge/logs/` (mandatory).

## Instructions

### Step 1: Triage knowledge todos

**Objective:** Process pending items in `{admin}/knowledge/todo/`.

For each todo:

- **No mutation needed** — todos resolvable by re-reading nodes, updating notes, or closing as obsolete. Resolve, mark complete, log.
- **Mutation needed on existing nodes** — renames, merges, restructures, deletions. Present the proposed action with what/why/risk per `refs/admin/safety.md` § User consent. If approved in-session, execute and mark complete. If not, update the todo with the fully specified proposal and leave it pending.
- **Requires user decision beyond consent** — entity disambiguation, classification questions, promotion judgment calls. Present context and options; update the todo.
- **No longer relevant** — already addressed by subsequent encoding. Mark complete with note.

### Step 2: Review recent additions

**Objective:** Surface nodes added since the last reflect run that may need review.

The watermark is the timestamp of the most recent prior reflect log in `{admin}/knowledge/logs/`. On the first-ever reflect run there is no prior log — skip this step with a notice; the current run establishes the baseline for next time.

For each section (Episodic, Semantic, Procedural):

1. List nodes added or modified since the watermark.
2. For each, check:
   - Required frontmatter present per `refs/knowledge/nodes.md`?
   - Cross-links bidirectional where relationships exist?
   - Tags consistent with established patterns?
3. Record observations. Remediations that touch existing content require approval — create a todo.

### Step 3: Consolidate

**Objective:** Identify duplicates and competing nodes; propose consolidation. Any consolidation moves or rewrites existing user content — requires user approval (see `refs/admin/safety.md` § User consent).

- **Semantic duplicates** — multiple nodes for the same identity (e.g., `John Doe.md` and `John Doe Smith.md` referring to the same person). Create a todo proposing the canonical name and the merge plan (which node absorbs the other; how content combines; which links update).
- **Procedural overlap** — multiple procedural nodes for the same task. Propose merge, replacement, or explicit coexistence (with a tag indicating they're variants).
- **Episodic overlap** — rarer; usually only when two encodes captured the same event from different inputs. Propose merging into one canonical episodic.

### Step 4: Promote

**Objective:** Surface patterns from accumulated content that warrant promotion.

1. **Episodic → procedural** — if a how-to or method appears across multiple episodic nodes (e.g., the user has filed quarterly receipts the same way three times), propose creating a procedural node that captures it. Promotion is non-destructive — creates a new procedural; episodic stays. User confirmation recommended for the procedural's framing.
2. **Implicit → explicit semantic** — if an entity is referenced across multiple episodic nodes but has no semantic node, propose creating one.

### Step 5: Strengthen

**Objective:** Repair weak structure and surface gaps.

1. **Orphan nodes** — nodes with no incoming or outgoing links. Read and identify what they should link to; propose link additions.
2. **Broken wikilinks** — `[[Title]]` references that don't resolve to a node. Propose either creating the missing node or correcting the link. For procedural targets, verify the `aliases` frontmatter field is present (procedural files are `SKILL.md` and resolve via alias).
3. **Stale nodes** — nodes not updated in a long time but referenced in recent episodic content. Surface for review.
4. **Gaps** — entities mentioned across multiple episodes but never given semantic depth. Propose enrichment.
5. **Procedural symlink currency** — if bootstrap (per `BOOTSTRAP.md`) is in use on this environment, verify each `Memory/Procedural/<name>/` directory has corresponding symlinks in the configured harness skill paths. New procedurals since last bootstrap run, or removed/renamed procedurals, may have stale or missing symlinks. Surface what needs a re-run; do not run bootstrap from inside reflect.

### Step 6: Verify

**Objective:** Confirm changes are correct and complete.

- **Consistency** — does the graph look right after changes? No broken links introduced.
- **Completeness** — were all pending todos addressed?
- **Log** — write a complete log of all actions taken, decisions made, and items requiring user input.

## Troubleshooting

**Two nodes look like duplicates but might be distinct**
Cause: Similar names, ambiguous identity (two Johns).
Solution: Don't merge without confirmation. Create a disambiguation todo with both nodes' content for user review.

**A procedural pattern is observed in episodic but the user doesn't want it formalized**
Cause: User does the pattern but doesn't consider it a reusable template.
Solution: Mark the suggestion todo as rejected; don't auto-promote. Reflect surfaces; user decides.

**Many orphan nodes**
Cause: Encode wasn't aggressive enough about cross-linking, or earlier nodes pre-date current entities.
Solution: Don't auto-link en masse. Surface in batches with proposals for user review.

**Watermark missing (first-ever reflect run)**
Cause: No prior reflect log exists.
Solution: Skip Step 2; the current run establishes the baseline for next time. Continue with todos, consolidation, promotion, and strengthening as discoverable.

## References

| Document | When to consult |
|---|---|
| `refs/admin/safety.md` | All steps — operational safety rules; Steps 3, 4, 5 — consent rules for mutations |
| `refs/admin/logging.md` | All steps — logging; Step 2 — prior reflect logs provide the watermark |
| `refs/knowledge/types.md` | Step 4 — promotion rules and type definitions |
| `refs/knowledge/nodes.md` | Steps 2, 5 — frontmatter and link conventions |
| `refs/knowledge/naming.md` | Step 3 — collision and naming conventions |
| `{admin}/knowledge/todo/` | Step 1 — pending items |
| `config.yaml` | Prerequisites — knowledge layer paths |
