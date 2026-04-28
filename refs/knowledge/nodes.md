# Nodes

Frontmatter, body structure, and linking conventions for knowledge nodes.

---

## Frontmatter

YAML frontmatter at the top of every node. Minimal required floor; type-specific additions; open-ended `tags` for everything else.

### Required (all types)

| Field | Type | Notes |
|---|---|---|
| `type` | `episodic` \| `semantic` \| `procedural` | Determines folder and required additions below |
| `title` | string | Human-readable display title — for procedural, this is what Obsidian shows in graph view (since the file itself is `SKILL.md`); typically the dehyphenated, capitalized form of the skill name |
| `created` | ISO 8601 datetime | When the node was first created |
| `updated` | ISO 8601 datetime | Last modification — bump on every change |

### Required by type

**Episodic:**

| Field | Type | Notes |
|---|---|---|
| `datetime` | ISO 8601 datetime | When the event itself occurred (may differ from `created`) |

**Semantic:**

| Field | Type | Notes |
|---|---|---|
| `class` | string | What kind of thing — `person`, `organization`, `place`, `project`, `vehicle`, `property`, `concept`, `thing`, etc. Open vocabulary; choose the most natural class. |

**Procedural:** stored as a directory `<skill-name>/SKILL.md`. The open Skills frontmatter applies — at minimum:

| Field | Type | Notes |
|---|---|---|
| `name` | string | Skill identifier; matches the directory name (lowercase, hyphenated) |
| `description` | string | Per agentskills.io — concise statement of what the skill does and when to use it |
| `aliases` | list of strings | Must include the skill's directory name (e.g., `[draft-youtube-storyboard]`) so Obsidian wikilinks resolve to the right `SKILL.md`. Required because the file is named `SKILL.md` for skill-loader compatibility, not the skill name. |

### Recommended (all types)

| Field | Type | Notes |
|---|---|---|
| `tags` | list of strings | Free-form. Use whatever helps retrieval and reflection. Suggested patterns below. |

#### Tag pattern suggestions

Tags are open-ended; these patterns help recall and reflect work:

- **Entity tags** — names of entities the node touches (`john-doe`, `acme-corp`, `riverside`)
- **Topic tags** — what the node is about (`finance`, `health`, `programming`, `2026-q4`)
- **Status tags** — for tracking state (`active`, `deferred`, `superseded`)
- **Decision tags** — for episodes containing decisions (`decision`)
- **Source tags** — origin (`conversation`, `email`, `from-file`)

No fixed vocabulary. Reflect can later identify recurring tags and suggest formalization.

### Example frontmatter

Episodic:

```yaml
---
type: episodic
title: Discussed File Organization with User
datetime: 2026-10-01T13:00
created: 2026-10-01T13:42
updated: 2026-10-01T13:42
tags: [john-doe, file-organization, decision]
---
```

Semantic:

```yaml
---
type: semantic
title: John Doe Smith
class: person
created: 2026-04-26T21:00
updated: 2026-10-01T13:00
tags: [colleague, acme-corp]
---
```

Procedural (stored as `Memory/Procedural/draft-youtube-storyboard/SKILL.md`):

```yaml
---
type: procedural
title: Draft YouTube Storyboard
name: draft-youtube-storyboard
description: Generate a storyboard for a YouTube video given topic, target length, and audience.
aliases: [draft-youtube-storyboard]
created: 2026-10-01T13:00
updated: 2026-10-01T13:00
tags: [content-creation, video]
---
```

## Body

Body is free-form Markdown — knowledge layer is fluid and emergent. Suggested shape per type:

**Episodic:**
- Brief narrative of what happened (the journal entry).
- Decisions made and their rationale, when applicable.
- References to participants, sources, related episodes.

**Semantic:**
- Description of the thing.
- Known facts and attributes (date of birth, address, identifiers, relationships).
- History — append new facts/observations as dated sections rather than rewriting.

**Procedural:**
- Skill instructions per the open Skills format — what to do, in what order.
- Inputs, outputs, constraints.
- Examples where helpful.

## Links

Two link types, used by audience:

### Knowledge ↔ knowledge

Obsidian wikilinks: `[[Title]]`. Resolution is by filename (without `.md`).

```markdown
Worked with [[John Doe Smith]] on the [[Acme Corp]] migration.
See [[draft-youtube-storyboard]] for the template used.
```

### Knowledge ↔ external sources

External references use scheme-prefixed addresses pointing at data wherever it lives — files, email, calendars, web, app-native content. Resolution is the agent's responsibility: use whatever capability the environment offers (MCP, native, installed CLI, bundled tool). If a reference cannot be resolved, surface the reference itself and continue.

Common schemes (extensible — adapt to your environment):

| Scheme | Example | Resolves via |
|---|---|---|
| `<backend>:<path>` | `gdrive:System/Archive/John Doe/Identity/2024-08-15 - Passport.pdf` | filesystem capability per `config.yaml` `backends:` (see `refs/admin/addressing.md`) |
| `url:<https://...>` | `url:https://example.com/announcement` | web fetch capability |
| `email:[<account>]` | `email:thread/abc123` | email MCP / IMAP / native capability |
| `calendar:[<calendar-id>]` | `calendar:event/xyz789` | calendar MCP / CalDAV capability |
| `<app>:<id>` | `notion:page/abc`, `slack:channel/T123/p456` | service-specific MCP or API |

Schemes are user/community-extensible; CFS does not enumerate exhaustively.

Inline (in body):

```markdown
Discussed deadline in email:thread/abc123. See also [[Acme Corp]].
```

Frontmatter (formal `sources:` field — recommended when content is derived from external sources):

```yaml
sources:
  - email:thread/abc123
  - calendar:event/xyz789
  - gdrive:System/Archive/John Doe/Identity/2024-08-15 - Passport.pdf
  - url:https://example.com/announcement
```

Named sources defined in `config.yaml` `sources:` may be referenced by name (e.g., `work-email:thread/abc123` where `work-email` is a defined source). Sources are read-only — see `refs/admin/safety.md` § Source protection.

Wikilinks are knowledge-internal; external references use scheme-prefixed addresses to stay protocol-agnostic.

## Updates

Nodes evolve. Update semantics:

- **Append** — adding a new dated section, a new tag, a new fact, a new link. Non-destructive. `encode` and `direct` can do this.
- **Rewrite, restructure, merge, rename, delete** — destructive. `reflect` only, with user consent per `refs/admin/safety.md` § User consent.

The `updated` frontmatter field is bumped on every change.
