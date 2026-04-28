# Encode

Encode new knowledge into the CFS knowledge layer. Non-destructive — creates new nodes and appends to existing ones; renames, merges, restructures, and rewrites are reflect's job. Log every execution per `refs/admin/logging.md`.

## Scope

Captures understanding from a conversation, a filed item, an observation, or any source of knowledge. Walks the type hierarchy in order — episodic, semantic, procedural — creating or appending nodes as the input warrants. Cross-links bidirectionally as it goes.

## Prerequisites

- Read `config.yaml` for knowledge layer paths and any defined external sources (`sources:`).
- See `refs/admin/safety.md` § User consent for the rule on what encode may and may not do (encode appends and creates; renames, merges, restructures, and deletions are reflect's job). § Source protection — external sources are pull-only.

## Input

- A conversation context (the most common case — what just happened in this session).
- A filed item from the storage layer (when knowledge can be derived from a document).
- Content pulled from a defined external source (`config.yaml` `sources:`) — email thread, calendar event, web page, app-native content. Resolution via the source's capability.
- An observation, decision, or fact made explicit by the user.

## Output

- New or appended episodic, semantic, and/or procedural nodes in the knowledge layer.
- Bidirectional links between related nodes.
- Todos in `{admin}/knowledge/todo/` for ambiguities or proposed promotions/consolidations that reflect should handle.
- Execution log in `{admin}/knowledge/logs/` (mandatory).

## Instructions

### Step 1: Identify episodes

**Objective:** Segment the input into discrete episodes worth recording.

**Produces:** A list of episodes. Each episode is a coherent unit of activity — one task, one decision, one event. A single input may produce zero, one, or several episodes.

1. Apply the episodic quality bar and granularity rule from `refs/knowledge/types.md` — conservative; err toward recording. One episode per coherent unit of activity (one task, one decision, one event).
2. For each episode, identify: brief title, datetime, participants, source.
3. If the input contains no episode-worthy activity, skip to Step 3 (semantic) or stop. Not every input produces an episode.

### Step 2: Encode episodic

**Objective:** Write an episodic node for each identified episode.

1. Name per `refs/knowledge/naming.md` (date-prefixed, Title Case).
2. Frontmatter per `refs/knowledge/nodes.md` — `type`, `title`, `datetime`, `created`, `updated`, optional `tags`. If content was pulled from external sources, record them in the `sources:` field.
3. Body: brief narrative of what happened, decisions made, why. Keep it journal-like — record, don't editorialize.
4. Reference participant entities and external sources inline using `[[wikilinks]]` for knowledge nodes and scheme-prefixed addresses for external references (filesystem, email, calendar, web, app-native — see `refs/knowledge/nodes.md` § Links).

### Step 3: Encode semantic

**Objective:** Identify nameable things in the input and create or append semantic nodes.

1. Apply the semantic guiding questions from `refs/knowledge/types.md`.
2. For each identified thing:
   - Check whether a semantic node already exists (by title, then by aliases).
   - If exists: append a new fact, attribute, relationship, or dated observation. Don't rewrite existing content.
   - If new: create the node per naming and frontmatter conventions. Pick the most natural `class`.
   - If ambiguous (potential collision with existing node): create disambiguated and create a todo for reflect to consolidate or confirm.
3. Bidirectional linking: episodic nodes reference participants via `[[wikilinks]]`; semantic nodes can list episodes/relationships in their bodies.

### Step 4: Encode procedural

**Objective:** Identify reusable how-tos / processes / templates and create procedural nodes.

1. Apply the procedural guiding questions from `refs/knowledge/types.md`. Most inputs produce no procedural node — only those that articulate or discover a reusable pattern do.
2. If a procedural pattern is present:
   - Check whether an existing procedural node covers it.
   - If clear improvement: append to existing.
   - If competing approach: create separate and flag for reflect via todo.
   - If new: create the procedural as a `Memory/Procedural/<skill-name>/SKILL.md` directory (per `refs/knowledge/naming.md`). Frontmatter must include `name` (matches dir), `description`, `title` (display), and `aliases: [<skill-name>]` (for Obsidian wikilink resolution). See `refs/knowledge/nodes.md`.
3. If a new procedural was created and the user has run bootstrap on this environment, mention that re-running `BOOTSTRAP.md` will expose the new skill to other harnesses (Cursor, Codex, etc.) — encode does not perform symlinking itself.

### Step 5: Verify

**Objective:** Confirm nodes are well-formed and relationships are captured.

- Filenames respect uniqueness rules (per `refs/knowledge/naming.md`).
- Required frontmatter fields are present per type (per `refs/knowledge/nodes.md`).
- Cross-links exist where the content references other nodes.
- Any ambiguities, collisions, or proposed promotions/consolidations are captured as todos for reflect.

## Examples

### Example 1: Conversation about a new project

Input: User says "I'm starting a new project called 'NorthStar' for Acme Corp — quarterly metrics dashboard, due end of November."

Actions:
1. **Identify** — one episode: project kickoff conversation. Datetime: now.
2. **Episodic** — create `2026-04-26-1530 - NorthStar Project Kickoff for Acme Corp.md`. Body: project name, client, scope, deadline. Wikilinks to participants.
3. **Semantic** — `NorthStar` (class: project, new). `Acme Corp` (class: organization, may already exist — append project as relationship if so).
4. **Procedural** — none in this input.
5. **Verify** — wikilinks bidirectional; todo if `Acme Corp` already exists under a slightly different name.

Result: 1 episodic + 2 semantic nodes; reflect handles any disambiguation.

### Example 2: Filed receipt informs semantic node

Input: A receipt for a hotel in Las Vegas was just filed.

Actions:
1. **Identify** — no narrative episode (filing alone is captured by storage logs); skip episodic.
2. **Semantic** — `Las Vegas` (class: place) gets a new dated observation: "stayed at [hotel] on [date]". `[hotel name]` may become a new semantic node (class: organization).
3. **Procedural** — none.
4. **Verify** — links from the new dated observations point to relevant entities; storage source noted via address.

Result: semantic enrichment from a filing event without a corresponding episode.

### Example 3: User articulates a preferred process

Input: User says "From now on, when I ask you to draft a YouTube storyboard, follow this template: hook, problem, demo, callback. Each section ~30 seconds."

Actions:
1. **Identify** — one episode: defining a procedural template.
2. **Episodic** — `2026-04-26-1545 - Defined YouTube Storyboard Template.md`. Brief narrative + the context for why the template was defined.
3. **Semantic** — none (no nameable thing introduced beyond the procedural).
4. **Procedural** — create `Memory/Procedural/draft-youtube-storyboard/SKILL.md`. Skill-format frontmatter (`name`, `description`, `title`, `aliases: [draft-youtube-storyboard]`); body contains the template steps.
5. **Verify** — episodic links to the new procedural via `[[draft-youtube-storyboard]]` (resolves through the alias). If bootstrap is in use, mention re-running it to expose this new skill to other harnesses.

Result: episodic + procedural; future agents can load the procedural as a skill directly from any harness with the bootstrapped symlinks.

## Troubleshooting

**Ambiguity: which existing node does this match?**
Cause: Similar names; possibly same identity vs distinct.
Solution: Create disambiguated; create a todo for reflect to confirm or merge.

**No clear episode in the input**
Cause: The input is a fact or filing event without narrative.
Solution: Skip Step 2 (episodic). Encode semantic and procedural as warranted.

**Procedural conflict with existing node**
Cause: Two competing approaches for the same task.
Solution: Create the new procedural separately and flag for reflect to decide whether to merge, replace, or coexist.

**Encode is unsure if something is worth a node**
Cause: Borderline case (transient mention vs persistent thing).
Solution: For semantic, err toward creating with light content. Reflect can prune later. For procedural, err toward not creating until reuse is clear — procedural's bar is "stable and reusable".

## References

| Document | When to consult |
|---|---|
| `refs/admin/safety.md` | All steps — operational safety rules |
| `refs/admin/logging.md` | All steps — logging |
| `refs/knowledge/types.md` | Steps 1, 3, 4 — type definitions and guiding questions |
| `refs/knowledge/nodes.md` | Steps 2, 3, 4 — frontmatter, body, link conventions |
| `refs/knowledge/naming.md` | Steps 2, 3, 4 — naming conventions |
| `config.yaml` | Prerequisites — knowledge layer paths |
