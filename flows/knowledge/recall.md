# Recall

Surface relevant knowledge as context for the current task. Read-only — recall never modifies the knowledge layer. Log every execution per `refs/admin/logging.md`.

## Scope

Retrieves knowledge content relevant to a query, topic, entity, or task context. Operates RAG-style: surfaces content into the current context for the agent to integrate naturally. References, links, and citations are not surfaced unless explicitly requested.

## Prerequisites

- Read `config.yaml` for knowledge layer paths and any defined external sources (`sources:`).
- See `refs/admin/safety.md` for operational rules (recall is read-only; external sources are pull-only).

## Input

- A query, topic, entity reference, or task context for which knowledge would help.
- May be implicit (the agent is starting a task and proactively recalls relevant context) or explicit (the user asks "what do I know about X").

## Output

- Relevant knowledge content surfaced as context for the current task. Empty result if no relevant knowledge exists.
- Execution log in `{admin}/knowledge/logs/` (mandatory).

## Instructions

### Step 1: Understand the query

**Objective:** Determine what context is needed.

**Produces:** A retrieval target — by entity, type, timeframe, topic, or free-form keywords.

1. Parse the explicit or implicit query.
2. Identify known attributes: entity name, class, datetime range, topic, related entities.
3. If the query is ambiguous and high-stakes (e.g., a fact answer that hinges on which "John" is meant), ask for clarification before retrieving.

### Step 2: Retrieve

**Objective:** Read matching nodes from the knowledge layer.

1. Determine likely subdirs to scan based on the query — `Episodic/`, `Semantic/`, `Procedural/`, or all.
2. If an entity is named, check semantic first (most direct hit); follow links from there to related episodic and procedural nodes. Wikilinks like `[[draft-youtube-storyboard]]` resolve to procedural via the `aliases` frontmatter field (the file itself is `SKILL.md` inside the matching directory).
3. If a timeframe is given, narrow episodic by date prefix.
4. If a how-to is needed, search procedural — each procedural is a `<skill-name>/SKILL.md` directory; the directory name is the skill identifier.
5. Use whatever capability is available to read and search the markdown vault — agent-native is usually sufficient; bundled vault tools are optional (see `tools/`).
6. If a matching node references an external source (`sources:` field or inline scheme-prefixed address) and the query suggests the source's content matters, attempt to resolve via the source's capability. If unable, surface the reference and continue.

### Step 3: Surface

**Objective:** Return the retrieved content as context for the current task.

1. Surface the relevant content directly — facts, decisions, observations, procedures — as context the agent integrates into its response.
2. Do NOT prefix or append references, citations, or wikilink lists by default. Knowledge informs; the agent answers naturally.
3. If sources or links are explicitly requested, surface the references then.
4. If retrieval found nothing relevant, return an empty result.

## Examples

### Example 1: Implicit recall before a task

Input: "draft a status update for the NorthStar project."

Actions:
1. **Understand** — entity reference: `NorthStar`. Implicit need: project context for the draft.
2. **Retrieve** — read `Semantic/NorthStar.md`; follow links to recent `Episodic/` entries about NorthStar; check `Procedural/` for any NorthStar-specific templates.
3. **Surface** — present scope, deadline, recent decisions, latest activity directly as context.

Result: agent has full project context without the user prompting for it explicitly.

### Example 2: Direct fact lookup

Input: "what's John Doe's passport number?"

Actions:
1. **Understand** — entity: `John Doe`; attribute: passport number.
2. **Retrieve** — read `Semantic/John Doe.md`; look for passport number in body or attributes.
3. **Surface** — if present, return the value. If not present, return an empty result.

Result: either a direct answer or a clear empty signal.

### Example 3: Topic browse

Input: "what have I been working on this month?"

Actions:
1. **Understand** — timeframe: current month; type: episodic; topic: open.
2. **Retrieve** — list episodic nodes with `datetime` in current month; cluster by referenced entities/projects.
3. **Surface** — summarize: projects touched, key decisions, notable events.

Result: topical summary built from recent episodic nodes.

## Troubleshooting

**Multiple matching nodes, unclear which is meant**
Cause: Ambiguous entity reference (two Johns; project vs concept of same name).
Solution: Surface all with disambiguating context, or ask for clarification.

**Retrieved content is stale**
Cause: Knowledge was encoded based on outdated information; reality has changed.
Solution: Surface what's there with a note on staleness; flag for reflect.

## References

| Document | When to consult |
|---|---|
| `refs/admin/safety.md` | All steps — operational safety rules |
| `refs/admin/logging.md` | All steps — logging |
| `refs/knowledge/types.md` | Steps 1, 2 — type definitions for retrieval scope |
| `refs/knowledge/nodes.md` | Step 2 — body and link conventions for traversal |
| `config.yaml` | Prerequisites — knowledge layer paths |
