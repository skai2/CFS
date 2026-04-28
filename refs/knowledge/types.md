# Types

What episodic, semantic, and procedural nodes are — definitions, what counts, what doesn't, and guiding questions for encoding.

---

## Episodic

Events, decisions, and the user's journal of activity.

**Counts:** any discrete unit of activity worth recording — a conversation that moved something forward, a decision made, an event attended, work done, an observation worth remembering.

**Doesn't count:** routine actions with no signal (a single trivial chat turn, a step within a larger task that's already captured by the parent episode).

**Quality bar:** conservative — err toward recording. Episodic is near-literal diary. Reflect can consolidate or prune later.

**Granularity:** one episode per coherent unit of activity (one task, one decision, one event). A session may produce zero, one, or several episodes. Encode segments before writing.

**Examples:**
- A conversation where you and the agent debugged a deploy issue.
- A decision to switch banks, with the reasoning.
- A meeting with a client.
- A trip's day-by-day log entries.

## Semantic

Nameable things — entities and concepts the user might want to know about later.

**Counts:** anything with an identity that can be named and re-referenced — people, organizations, places, projects, vehicles, properties, concepts, theories, products, methods.

**Doesn't count:** transient mentions with no plausible future relevance; common nouns used generically (the word "bank" in passing isn't a semantic node; "Acme Bank" is).

**Class field:** every semantic node carries a `class` (`person`, `organization`, `place`, `project`, `vehicle`, `property`, `concept`, `thing`, etc.). Open vocabulary; choose the most natural class. Reflect can suggest standardization across nodes if drift accumulates.

**Vs storage entities:** storage's *entity* concept (see `refs/storage/entities.md`) is narrower — only things with administrative ownership of records. Semantic nodes are broader: every storage entity has a semantic node (same canonical name, richer content), but semantic also covers concepts, theories, products, and places that own no records.

**Guiding questions when encoding:**

1. **Was a nameable thing introduced or referenced?** A person, organization, place, project, vehicle, property, concept, theory, or other identifiable thing.
2. **Does a node already exist for it?** Check by title and aliases.
   - Yes → does the new content add a fact, attribute, relationship, status change, or correction? If so, append. If purely a re-mention, no update needed.
   - No → create a new semantic node.
3. **Is there potential ambiguity with an existing node?** (Two Johns; same name in different contexts.) If unsure, create disambiguated and flag for reflect via todo.
4. **What `class` is it?** Influences body shape and which facts to capture.

**Examples:**
- `John Doe Smith` (person, colleague at Acme)
- `Acme Corp` (organization, employer)
- `Las Vegas` (place, frequent travel destination)
- `Theory of Evolution` (concept)
- `Riverside Apartment` (property, also a storage entity)

## Procedural

Reusable how-tos, processes, methods, templates, and preferences.

**Counts:** anything stable, concrete, and reusable beyond the immediate context — a how-to that worked, a template to use again, a method the user prefers, a process to repeat.

**Doesn't count:** one-off actions (those go in episodic); vague principles too abstract to act on.

**Open Skills format:** procedural nodes are stored as `<skill-name>/SKILL.md` directories so each is a complete, loadable skill. Frontmatter requires `name`, `description`, and `aliases` per `refs/knowledge/nodes.md`. Bootstrap (see `BOOTSTRAP.md`) symlinks procedural directories into harness skill paths for cross-environment loadability.

**Guiding questions when encoding:**

1. **Did a how-to, method, template, or reusable pattern get articulated, used, or discovered?** As distinct from a one-off action.
2. **Is it reusable beyond the immediate context?** A future agent or you, weeks later, would benefit.
3. **Is it stable and concrete enough to be actionable?** Vague principles don't qualify; concrete steps or templates do.
4. **Is the skill-format frontmatter right?** `name` matches the directory; `description` is concise and routing-friendly; `aliases` includes the skill name for Obsidian wikilink resolution.
5. **Does it overlap with an existing procedural node?** If a clear improvement, append. If a competing approach, create separate and flag for reflect.

**Examples (each is a `Memory/Procedural/<name>/SKILL.md` directory):**
- `draft-youtube-storyboard/SKILL.md` (template for creating storyboards)
- `scaffold-client-project/SKILL.md` (recurring project setup pattern)
- `file-quarterly-receipts/SKILL.md` (specific filing process for tax-time receipts)
- `weekly-review/SKILL.md` (personal weekly review process)

## General rules

- **When in doubt, encode** — episodic carries a conservative bias; reflect consolidates and prunes later.
- **Encode appends, never rewrites** — destructive changes (renames, merges, deletions) are reflect's job, consent-gated per `refs/admin/safety.md` § User consent.
- **Identity over relationship** — name semantic nodes by what the thing IS, not its relation to anyone (`John Doe Smith`, not `My Brother`).
