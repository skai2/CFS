# Naming

How to name knowledge nodes in the CFS knowledge layer.

---

## General rules

- **Knowledge nodes are user-facing content** — read in Obsidian, traversed via wikilinks. Names follow user-content conventions, not the system-internal convention used for admin files (logs, todos).
- **No unsafe characters** — avoid `/ : * ? " < > |` (cross-platform hazard).
- **Preserve accents and diacritics** in episodic and semantic — match the natural spelling of names and words. Procedural is the exception (ASCII-only per the Skills format).
- **Mandatory `.md` extension, lowercase.**
- Two sub-conventions apply by node type, defined below.

## Language

**Episodic** nodes use the language of the episode itself — a conversation in Portuguese produces a Portuguese-titled episodic node.

**Semantic** nodes use the entity's natural identity language — a Brazilian person's node uses their Portuguese name; an English concept uses English. Choose what the thing uses for itself.

**Procedural** is constrained to lowercase ASCII per the open Skills format, regardless of language. Express the action in whatever phrasing fits, transliterated where needed.

Same principle as storage filenames following the document's language — see `refs/storage/naming.md` § Language.

## Understand before naming

Never name a knowledge node from a query, mention, or surface impression alone. Read the source content (conversation, filed item, observation) first; the name reflects what the node is about, not what triggered its creation.

## Conventions by type

### Episodic

Date-prefixed descriptive names, Title Case, natural spaces.

| Pattern | Example |
|---|---|
| `YYYY-MM-DD-HHmm - [Descriptive Event Title].md` | `2026-10-01-1300 - Discussed File Organization with User.md` |
| `YYYY-MM-DD - [Descriptive Event Title].md` | `2026-04-26 - Refactored Knowledge Layer Naming.md` |

Use the most specific datetime available. The frontmatter `datetime` field carries the precise event time; the filename prefix is a coarse navigation aid. The time component disambiguates same-date episodes.

### Semantic

Identity-based names, Title Case, natural spaces, no relationship qualifiers.

| Pattern | Example |
|---|---|
| `[Identity name].md` | `John Doe Smith.md`, `Las Vegas.md`, `Theory of Evolution.md`, `Riverside Apartment.md` |

Use the shortest unambiguous form. Disambiguate via qualifying detail when collisions occur (`John Doe Smith.md` and `John Doe Brown.md`, not `John Doe.md` for both). Same identity-not-relationship principle as storage entities — see `refs/storage/entities.md` for the independence test. Aliases go in frontmatter (`aliases:`), not in the filename.

### Procedural

Open Skills format: a directory whose name is the skill identifier, containing a `SKILL.md` file with the skill content.

| Pattern | Example |
|---|---|
| `[action-shape]/SKILL.md` | `draft-youtube-storyboard/SKILL.md`, `scaffold-client-project/SKILL.md`, `file-quarterly-receipts/SKILL.md`, `weekly-review/SKILL.md` |

The directory name is the skill identifier (matches the `name` frontmatter field inside `SKILL.md`). It must satisfy the open Skills name pattern: lowercase ASCII letters, digits, and hyphens only. This shape makes each procedural node a complete, loadable skill — bootstrap (see `BOOTSTRAP.md`) can symlink procedural directories directly into harness skill paths without wrapping. See `refs/knowledge/nodes.md` for full skill-format frontmatter.

## Uniqueness

Filenames must be unique within their type's folder (Obsidian resolves wikilinks by filename, not path; aliases supplement). When a new node would collide with an existing one:

- **Episodic** — disambiguate via the time component (e.g., `1300` vs `1430` on the same date).
- **Semantic** — add the qualifying detail that distinguishes the entity; update the existing under-qualified node's name if needed.
- **Procedural** — refine the action to be more specific. Note: every procedural's file is `SKILL.md`; uniqueness is by directory name + the `aliases` frontmatter field, which Obsidian uses to resolve wikilinks like `[[draft-youtube-storyboard]]` to the right `SKILL.md`.

Renames of existing nodes are reflect's job — encode flags collisions via todo rather than overwriting.
