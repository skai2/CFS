# CFS — Cognitive File System

An AI-native system for organizing and unlocking your personal files and knowledge.

How should a person organize all their digital files and knowledge? Despite well-established work in library science, archival science, records management, and personal information management, no single system exists for personal mixed-media digital collections. Research across CLIR, institutional digital preservation programs, and the academic PIM literature confirms this gap — the component pieces are well-established, but nobody has assembled them into a unified personal-scale system.

CFS is our attempt at a principled approach. It combines two independent layers — a prescribed filesystem for stable storage, and an emergent knowledge layer for understanding and retrieval — drawing from established disciplines rather than starting from scratch.

The longer-term ambition is for CFS to grow into something closer to a personal digital twin — a structured mirror of the user's digital life that captures context, organizes it, and stays available to both the user and the agents acting on their behalf. Each interaction leaves a trace, and the accumulated trace compounds into a foundation. This is the design's direction, not its guarantee; the structural and operational substrate described below is what aims to make it possible.

---

## Overview

### The two-layer concept

CFS separates the problem of organizing digital life into two independent systems:

**Storage layer (filesystem)** — a stable, navigable folder structure for files. Optimized for findability through browsing. Prescribed and rarely changes. Answers: *where does this file go?*

**Knowledge layer (memory)** — an Obsidian vault of atomic, densely linked markdown notes. Optimized for understanding, connection, and retrieval. Flat and emergent — structure grows from links and metadata, not hierarchy. Answers: *what does this mean, and how does it connect to everything else?*

The two layers are **independently designed, independently valuable, and independently adoptable.** Someone could use only the filesystem and have a well-organized personal filing system. Someone could use only the knowledge layer and have a rich thinking environment. Together they complement each other — the filesystem provides stable storage, the graph provides multi-dimensional retrieval — but neither requires the other.

Both layers are designed for operation by humans and AI agents alike (see Part III: Operation).

### Design goals

1. **Complete** — every file and every piece of knowledge has a place.
2. **Simple** — minimal decisions at every routing point, minimal depth.
3. **Stable** — the structure rarely changes; refactoring is rare and cheap.
4. **Unambiguous** — any item has one defensible location, determined by clear routing rules with secondary connections handled by the knowledge layer.
5. **Navigable** — findable by browsing, not just search.
6. **AI-native** — readable and operable by AI agents as naturally as by humans.

---

## Principles

Three governing beliefs that constrain decisions across the entire system.

**Simplicity first — no speculative structure, but address friction immediately.** Premature complexity is as costly as missing complexity. No infrastructure built for hypothetical scale, no categories created for items that don't yet exist. But when friction is felt, address it immediately — deferring needed complexity is equally costly. Three prototype iterations validated this: each simplified what the previous had over-specified, while adding structure where real filing friction demanded it.

**Opinionated by design — embody decisions with reasoning, don't defer to users.** Most people want to organize files, not design taxonomies. CFS provides a complete structural schema that can be adopted as-is. The opinions are documented with their reasoning so they can be challenged, modified, or replaced — but the default is a system that works out of the box, not a toolkit for building one. This is informed by PIM research (Jones, 2007) finding that personal organization is idiosyncratic to the point of dysfunction; some prescription reduces chaos.

**Durability over features — bet on formats and patterns that outlast tools, services, and paradigms.** The system must outlast any individual application. This manifests as: plain text (markdown) for the knowledge layer, configurable paths for storage flexibility, no vendor lock-in (Obsidian-compatible but not dependent), and open protocols (MCP) for AI integration. Many AI memory projects (2025-2026) independently converged on plain-markdown-on-disk as a substrate for persistent, human-readable, AI-navigable knowledge — which we take as signal for the durability of this choice. This converges with Steph Ango's "file over app" philosophy: "if you want your writing to still be readable on a computer from the 2060s, it's important that your notes can be read on a computer from the 1960s."

---

## System properties

CFS is implemented as plain markdown files and folders — no database, no proprietary format. It works with any AI agent that supports the Agent Skills standard, runs silently as part of normal AI sessions rather than as a separate application, and stores content wherever the user points it. Together with the durability principle, these properties make CFS portable, inspectable, and forkable.

---

# Part I: Storage Layer

*Status: in active use; designed and tested across three prototype iterations.*

The storage layer organizes all personal files into a stable, navigable folder structure. It operates independently of the knowledge layer — no knowledge node is required for a file to be correctly filed and findable.

## Storage rules

**Stable locations.** Every item has a permanent location from the moment it's filed. Status changes (active, completed, paused) happen via metadata in the knowledge layer, not relocation. The only exception is the unsorted inbox — items move from unsorted to their permanent home during processing. This is grounded in the records continuum model (Upward, 1990s), which treats records as simultaneously active and archival. It addresses a friction point in systems like PARA where items migrate to an "archive" or "inactive" bucket — creating routing ambiguity, broken references, and maintenance burden.

**Corrections are allowed.** "Stable locations" does not mean "never re-route, even when wrong." Items filed incorrectly can and should be moved to their correct location. What stable locations prohibits is *status-driven relocation* — moving items because they're "done" or "inactive." Location reflects what the item IS, not what stage it's at.

**Versioning and updates.** When a document is superseded (new insurance policy, updated resume), both versions stay in the same location. The knowledge layer tracks which is current. When multiple versions of the same work exist in different formats (FLAC and MP3 of the same album), the knowledge layer links them — a pattern informed by FRBR's Work/Expression/Manifestation/Item model.

**CFS manages what the user manages.** System-installed software, platform-managed games, and package dependencies are outside CFS's scope. CFS covers what the user personally curates, preserves, and organizes.

**Minimum necessary hierarchy.** Each storage class has exactly the depth it needs for unambiguous routing — no more. Structural depth is driven by routing requirements, not forced symmetry. This is informed by PIM research (Bergman & Whittaker) showing users navigate faster with broader, shallower structures.

**Flat by default, structure when warranted.** Archive items within a domain are flat until collections form from accumulation (5 items minimum). Library items follow established media naming conventions that create natural folder hierarchies from the first item (e.g., `Artist/Album`, `Series/Season`). In both cases, structure emerges from need — archive collections from browsing friction, library hierarchy from domain conventions. This is grounded in archival science's MPLP (More Product, Less Process) philosophy: organize broadly first, add structure incrementally.

**Naming conventions are the primary navigation mechanism.** Folder structure gets you to the right container; file and folder names let you find the specific item within it.

**Relationships are metadata, not hierarchy.** An item lives in ONE location determined by what it is and who it belongs to. All other connections — related entities, topics, status, secondary categorizations — are handled by the knowledge layer, not by folder nesting. This is grounded in Ranganathan's faceted classification: a single hierarchy can only encode one organizational axis; the knowledge layer encodes all others.

## Routing rules

**Entity-first where ownership is clear.** Archive and projects are entity-subdivided because items have clear owners or beneficiaries. Library is type-subdivided because items are often shared or ownership-irrelevant. Entity-first routing is inspired by social cognition research (the brain prioritizes agents), grounded in archival science's principle of provenance (respect des fonds), and supported by data modeling (Kimball's star schema, Linstedt's Data Vault).

**Entity determines location, attributes determine metadata.** The entity and item type determine the folder. Domain, date, issuer, relationships, and all other dimensions are metadata in the knowledge layer.

**Each domain captures one kind of information.** Finance is strictly money moving. Health is strictly health information. Legal is strictly binding instruments about the entity itself. Career and Clients capture relationship histories — with employers/institutions and with those served, respectively.

**File by primary purpose.** When an item could route to multiple domains, its primary purpose at time of filing determines the location. The knowledge layer handles secondary connections.

**When in doubt, file it.** An item in an imperfect location is better than an unfiled item. Routing can be corrected; unfiled items get lost.

## Structure

```
Archive  / [owner]    / [domain]   / items & collections
Library  / [category]              / items & collections
Projects / [client]   / [project]
```

Each storage class has the minimum hierarchy needed for unambiguous routing:

| Storage class | Routing decisions | Depth |
|---|---|---|
| **Archive** | WHO or WHAT it belongs to → WHAT domain | entity / domain / items |
| **Library** | WHAT kind of content | category / items |
| **Projects** | WHO it serves → WHICH project | client / project |

### Archive

Settled files organized by **who or what they belong to** and **what domain they fall under.** These represent the ongoing responsibilities of an entity — identity, finances, health, career, client relationships, possessions, legal obligations, experiences.

**Owner entity:** The person, organization, family, or independent record-bearing thing this item belongs to. An entity is anything with an administrative life that persists independently — it can own records regardless of who currently manages it. A property has utility bills, tax records, and maintenance history that transfer with the property. A company has obligations that persist regardless of its owner. Entities are named by identity (shortest unambiguous name), not by relationship. The system owner is just another entity, structurally identical to any other.

**Independence test:** Does this thing have an administrative life that persists independently? Apply two questions: (1) Can this record exist without entity X? (2) Can entity X exist without entity Y? If the answers reveal the record is tied to a thing rather than a person, and that thing has independent administrative continuity, it qualifies as its own entity.

Examples that pass (independent entities):
- A property (an apartment) — utility bills, tax records, maintenance history transfer with the property, not the owner
- A company — tax obligations, contracts, expenses persist regardless of who owns the company
- A vehicle — registration, insurance, maintenance follow the vehicle across owners

Examples that fail (not independent — belong to a person's entity):
- A bank account — close it and its records cease. Belongs to the account holder's entity (Assets domain)
- A digital subscription — cancel it and it's gone. Belongs to the subscriber's entity
- A purchased item — a toothbrush receipt is the buyer's record, not the toothbrush's

**Domains (8):**

| Domain | Contains | Boundary — does NOT contain |
|---|---|---|
| **Identity** | IDs, passports, birth/marriage certificates, citizenship, registrations, memberships, academic diplomas/degrees | Professional certifications (→ Career) |
| **Finance** | Receipts, statements, tax filings, payments, investments, banking, loan payments, expense records | Loan agreements (→ Legal), insurance policies (→ Legal) |
| **Health** | Medical records, prescriptions, test results, diagnoses, dental, vision, wellness records | Health insurance policies (→ Legal) |
| **Career** | Resumes, employment records, employment contracts, transcripts, coursework, professional certifications, publications | Academic diplomas/degrees (→ Identity) |
| **Clients** | Client contracts, proposals, service agreements, invoices issued, work logs, timesheets, reports, deliverables, client correspondence | Entity's own tax filings (→ Finance), entity's own insurance (→ Legal) |
| **Assets** | Property docs, vehicle docs, warranties, equipment records, digital accounts, subscriptions, backups, data exports, software licenses | Purchase receipts (→ Finance), terms/agreements (→ Legal) |
| **Legal** | Insurance policies, leases, loan agreements, wills, POA, trusts, court orders, regulatory compliance, corporate governance | Payment records (→ Finance), health records (→ Health), employment contracts (→ Career), client contracts (→ Clients) |
| **Events** | Travel itineraries, booking confirmations, event programs, conference materials, loyalty programs, trip collections, settled experiential documentation | Event receipts (→ Finance), travel visas (→ Identity), event photos (→ Library) |

The first five domains each capture a distinct *kind of information*: who you are (identity), money moving (finance), health information (health), professional trajectory (career), things you own or manage (assets). Career and Clients are symmetric relationship domains: Career captures the entity's trajectory *through* other entities (as employee, student, or member), Clients captures the entity's trajectory *with* those it serves (as provider, consultant, or contractor). Both individuals and organizations may use either domain when the content fits. Legal captures binding instruments that are about the entity's own standing, not tied to a specific professional or client relationship. Events captures *experiential documentation* — records whose primary value is documenting an experience rather than serving an administrative function.

The domain set is grounded in functional classification (ISO 15489's recommended methodology for records management) and synthesized from estate planning frameworks, document vault services, personal recordkeeping guidance (Australian NSW, UK Citizens Advice), JD community implementations, and PIM research. The core five (identity, finance, health, career, assets) appear in virtually every framework surveyed. Clients was added to address the relationship-centric records that organizations (and freelancers) naturally organize by client rather than by administrative function.

**Cross-cutting routing rules:**
- Insurance distributes: policy → Legal, claims → Finance, medical records → Health
- Education distributes: diplomas → Identity, coursework → Career
- Employment distributes: contracts → Career/[Employer], pay stubs → Finance, recommendation letters → Career
- Client engagement distributes: contracts → Clients/[Client], invoices issued → Clients/[Client], proposals → Clients/[Client]
- Relationship test: is this about the entity itself, or about a relationship with an external entity? Relationship-centric items → Career (trajectory through others) or Clients (trajectory with those served). Entity-centric items → the domain matching their administrative function.
- Correspondence files by subject: letter from bank → Finance, from doctor → Health, from client → Clients
- Shared items file under primary entity; cross-reference in the knowledge layer
- Active event planning is a project; settled event documentation is Archive/Events

**Assets — the "things you own/manage" domain:**
- A bank account exists at an institution → Assets (you manage this account)
- The account's terms and conditions → Legal (binding agreement)
- Monthly statements showing transactions → Finance (money moving)

**Collections:** When items of the same kind accumulate within a domain, they group into collections. A collection is a folder containing related items — the final structural layer, with flat items inside.

Collections group items that share an **institutional source** (all statements from one bank), a **temporal cluster** (all tax documents for one year), or a **recurring administrative category** (all receipts for one ongoing expense). The test: would this grouping help someone browsing the domain find related items faster?

The filing process evaluates collection membership: does this item belong in an existing collection? Are there 4+ existing items that would form a natural collection with this one? If so, create the collection (5 items minimum). If not, file as an individual item. Library categories may use convention-driven groupings that form immediately — see `refs/storage/collections.md`.

### Library

Curated collections organized by **what kind of content it is.** Type-based rather than topic-based, because media collections are better served by content type than by subject — a finding consistent across datacurator-filetree, every media server (Plex, Jellyfin, Kodi), every OS default directory structure (XDG, macOS, Windows), and the Internet Archive's seven mediatype silos.

Topic-based retrieval isn't lost — it moves to the knowledge layer as faceted metadata. A song can be found by genre, artist, mood, or any other facet without the filesystem needing to encode those dimensions. This approach is grounded in Ranganathan's faceted classification — the dominant modern approach for digital collections.

**Categories (6):**

| Category | Contains |
|---|---|
| **Audio** | Music, podcasts, audiobooks, recordings, sound effects |
| **Video** | Movies, TV shows, personal recordings, clips, anime |
| **Images** | Photos, art, screenshots, wallpapers, diagrams |
| **Books** | Ebooks, comics, papers, articles, reference publications |
| **Games** | Video games, tabletop games, board games, mods, saves, game data |
| **Tools** | Portable applications, utilities, scripts, personal automations, AI skills |

Three categories are carrier-based (Audio, Video, Images — by sensory modality) and three are concept-based (Books, Games, Tools — by what the content is). This hybrid is consistent with every real-world mixed-media system surveyed. The categories were incorporated from datacurator-filetree's structure and cross-referenced against media server conventions, OS defaults, and Schema.org's CreativeWork type hierarchy.

Each category organizes items according to established media naming conventions — see `refs/storage/naming.md`. These conventions create natural folder hierarchies (e.g., `Artist/Album` for audio, `Title (Year)` for films) that form from the first item filed, unlike archive collections which require accumulation. Items may be single files or folder-units (an album, a game with its saves, a portable app).

Items in categories like games and tools may have complex internal structures (a game with saves, configs, and mods; a tool with binaries and documentation). CFS treats these as opaque units — their internal organization is dictated by their nature and is outside CFS's scope.

**Scope:** CFS manages what the user personally curates. Tools are portable apps, scripts, automations — not system-installed software or platform-managed applications. Games are curated files (ROMs, standalone games, tabletop PDFs, save archives) — not platform-managed installs.

### Projects

Active workspaces organized by **who the work serves** and **project name.**

**Client entity:** The person, organization, or self that this work serves — the beneficiary, not necessarily the person doing the work.

**Project:** Each project is a unit with internal structure dictated by its nature — a git repository, a design workspace, a data analysis environment, a game modding folder. CFS organizes to the project level; internal structure is entirely outside CFS's scope.

**Lifecycle:** Projects persist. Completed projects stay in Projects/. Status (active, completed, paused) is tracked in the knowledge layer, not by relocation. If a project produces a distributable artifact (a released tool, a published work), the artifact may also be filed in Library while the source workspace remains in Projects.

**Relationship to events:** Active event planning (a trip, a conference, a party) is a project. Settled event documentation (last year's itinerary) is Archive/Events. The specific event is time-bound work (project); managing experiences is an ongoing life responsibility (archive domain).

### Unsorted

Not a permanent storage class — a transient CFS-managed inbox. Items placed here await processing by the file flow. After filing, items are removed from unsorted — this is CFS-managed space, so the non-destructive source protection rule does not apply. External sources (folders, downloads, drives) are pointed at directly via flows and are never modified. Inspired by GTD's capture-then-process principle.

### Admin

Not a storage class — system state for CFS operations. A configurable path (see `config.yaml`) containing per-section operational state:

- `admin/` — `logs/`, `todo/` (admin-flow execution state: setup, test)
- `storage/` — `logs/`, `todo/`, `sources.md`, `targets.md` (storage-flow execution state and user-defined source/target rules; rule is a storage flow)
- `knowledge/` — `logs/`, `todo/` (knowledge-flow execution state)

See `refs/admin/logging.md` for format and conventions.

## Conventions

### Naming

**General rules:**
- **Natural, readable names** — capitalize and space as you naturally would
- **No unsafe characters** — avoid `/ : * ? " < > |` (cross-platform hazard)
- **Descriptive names** — what the item IS, not where it came from or its original filename
- **Category-specific conventions override** these defaults when applicable

**Date prefixes** for time-relevant items (primarily archive): use the most specific meaningful date available. `YYYY` when only year is known, `YYYY-MM-DD` when day is known, `YYYY-MM-DD-HHmm` when time disambiguates or is inherently significant. Prefer the creation date — when the document was issued, signed, recorded, or transacted. When only derivative dates are available (expiry, renewal), infer the creation date if possible or use the best available date and log the uncertainty.

**Entity names:** Identity names, not relationships (`John` not `My Brother`). Use the shortest unambiguous name. Add surname or detail only for disambiguation.

**Structural names:** Storage classes (`Archive`, `Library`, `Projects`), archive domains (`Identity`, `Finance`, `Health`, `Career`, `Clients`, `Assets`, `Legal`, `Events`), and library categories (`Audio`, `Video`, `Images`, `Books`, `Games`, `Tools`) are a fixed set. On-disk names render in the configured system language.

**Two-tier naming.** CFS uses two distinct naming conventions, reflecting the different purposes of user content and system internals. User-facing content in the filesystem (items, entities, structural folders) uses natural, readable names — capitalized and spaced as you naturally would. CFS project files and admin artifacts (logs, todos) use a system convention: lowercase, underscores bind words, hyphens separate components. The rationale: user content should be browsable and natural (the spec's primary navigation mechanism), while system internals should be consistent and machine-friendly. See `refs/storage/naming.md`.

**Language:** Structural hierarchy (storage classes, domains, categories) uses the configured system language (`language` in `config.yaml`). Item filenames use the document's own language — a Brazilian tax document is named in Portuguese regardless of the system language. This ensures filenames remain natural and findable to the user while the structure stays consistent. See `refs/storage/naming.md` for details.

**Item names:**
- Archive items: `[date] - [Descriptive Name].[ext]`
- Library items: follow established media conventions per category — see `refs/storage/naming.md` for specific patterns (MusicBrainz/Plex for Audio, Plex/Jellyfin for Video, Lightroom for Images, Calibre for Books, No-Intro for Games/ROMs)
- Tools: tool name — `rclone`, `Voicemeeter`
- Projects: project name — `My App`, `Client API`

### Units

A unit is a single file or a folder that constitutes one thing. Prefer flat files — don't create folder units unless the item naturally is a package (an album, a tool, a game with its saves, a course folder). CFS organizes to the unit, not inside it — internal structure of folder-units is opaque.

### Filing

- **File by primary purpose** — not by topic, origin, or secondary use
- **Each domain is strictly scoped** — see the boundary column in the domain table
- **Shared items** file under the primary entity; cross-reference in the knowledge layer
- **Cloud-native files** (Google Docs, Sheets, etc.) are referenced via typed links in the knowledge layer, not copied. Export to local format if a local copy is needed.
- **Content extraction is not optional** — read documents before filing. An earlier prototype demonstrated that filing by filename alone produces wrong results: a cryptically-abbreviated filename was misidentified as one document type when content extraction revealed it was something else entirely, with different routing, entity name, and metadata.

### Project lifecycle

Projects persist in Projects/ regardless of status. Status is tracked in the knowledge layer, not by relocation. Completed projects are not moved to Archive. Active event planning is a project; when the event concludes, settled documentation files to Archive/Events.

## Routing Examples

### Archive routing

| Item | Owner | Domain | Why |
|---|---|---|---|
| Passport | person | Identity | Government-issued ID |
| University degree | person | Identity | Academic credential |
| Company registration | company | Identity | Organizational credential |
| Monthly bank statements | person | Finance | Money moving (transactions) |
| Tax filings | person | Finance | Money moving (tax) |
| Purchase receipts | person | Finance | Money moving (purchase) |
| Vaccination card | family member | Health | Medical record |
| Medication information | family member | Health | Prescription record |
| Resume / CV | person | Career | Professional record |
| Course folder (e.g., Algorithms) | person | Career | Coursework unit |
| Chat app backup | family member | Assets | Digital data possessed |
| Hardware documentation | person | Assets | Equipment record |
| Digital account records | person | Assets | Account managed |
| Health insurance policy | person | Legal | Binding agreement |
| Employment contract | person | Legal | Binding agreement |
| Will / testament | person | Legal | Legal instrument |
| Power of attorney | family member | Legal | Legal instrument |
| Trip itinerary | person | Events | Experience logistics |
| Conference materials | person | Events | Event documentation |
| Loyalty program records | person | Events | Ongoing experience management |
| Apartment electricity bill | property | Finance | Money moving — independent entity (passes independence test) |
| Vehicle registration | vehicle | Identity | Formal identity — transfers with the vehicle |
| Property tax assessment | property | Finance | Money moving — tied to the property, not the owner |

### Library routing

| Item | Category | Notes |
|---|---|---|
| Music albums | Audio | Album folders as units |
| Podcast episodes | Audio | Individual files or show folders |
| Movie files | Video | Individual files |
| Home videos | Video | Individual files or event folders |
| Photo event albums | Images | Folder units |
| Ebooks | Books | Individual files |
| Game saves/configs | Games | Each game is a unit with opaque internals |
| Portable applications | Tools | Each tool is a unit with opaque internals |
| Personal scripts | Tools | Individual files or folders |
| AI skills | Tools | Skill folders as units |

### Decision examples

| Scenario | Decision | Principle |
|---|---|---|
| Health insurance policy | → Legal | Binding agreement, not health info |
| Health insurance claim payment | → Finance | Money moved |
| Medical test results | → Health | Health information |
| Textbook used for a course | → Career (inside course unit) | Part of the coursework unit |
| Textbook in personal collection | → Library/Books | Published work consumed independently |
| Family vacation photo | → Library/Images | Content value, not administrative |
| Planning a trip | → Projects | Active, time-bound work |
| Past trip itinerary | → Events | Settled experience documentation |
| Bank account credentials | → Assets | Account managed |
| Bank account terms | → Legal | Binding agreement |
| Bank account transactions | → Finance | Money moving |
| Completed project workspace | → stays in Projects | Status is metadata, not relocation |
| Released tool from a project | → Library/Tools + Projects | Artifact filed; workspace persists |
| Cloud-native document | → knowledge layer reference | Referenced via typed link, not copied |
| Misrouted item discovered | → move to correct location | Corrections are allowed; status-driven moves are not |
| Updated resume replacing old one | → same location, both versions | Knowledge layer tracks which is current |
| Apartment utility bill | → property entity / Finance | Independence test: bill persists with the property, not the owner |
| Car insurance policy | → vehicle entity / Legal | Independence test: policy transfers with the vehicle |
| Bank account statement | → person entity / Finance | Fails independence test: account ceases without the person |
| Subscription receipt | → person entity / Finance | Fails independence test: subscription ceases without the subscriber |

---

# Part II: Knowledge Layer

*Status: v1 in active use — refs and flows in place (`refs/knowledge/`, `flows/knowledge/`), functional and accumulating real content; broader validation still ahead and specifics will continue to mature.*

The knowledge layer captures understanding, connections, and meaning across all of the user's digital life. It operates independently of the filesystem — knowledge nodes can exist with no file counterpart, and they can reference sources beyond the filesystem (email, cloud services, conversations, online platforms).

## Philosophy

The knowledge layer is a **consolidating entity** that draws from many sources — the filesystem being one of them. It captures what things mean, how they relate, and why they matter, regardless of where the underlying files or data live.

This is informed by the Zettelkasten tradition (atomic notes, dense linking, emergent structure) and by Ranganathan's faceted classification (multiple retrieval dimensions without forcing a single hierarchy). Dublin Core provides the metadata vocabulary foundation.

**Plain text is canonical.** All knowledge is stored as markdown files on disk — readable by humans, parseable by machines, versionable by git, editable in any tool. Supplementary indices (vector databases, search indices) are derived and rebuildable. Markdown is always canonical. This is a direct expression of the durability principle applied to the knowledge layer.

**Encoding is everything.** Knowledge nodes contain real understanding, not metadata stubs. They connect to other nodes, capture why something matters, and grow richer over time through retrieval and review. Whether encoding is human-driven, AI-assisted, or AI-generated, the standard is the same: genuine understanding, not empty structure. This is informed by memory science: elaborative encoding produces durable traces, while passive storage produces a "graveyard" — the dominant PKM failure mode.

## Memory types

Inspired by Tulving's memory systems and Squire's declarative/nondeclarative taxonomy:

| Type | Contains | Inspiration |
|---|---|---|
| **Semantic** | Durable knowledge: entities, concepts, facts, relationships | Semantic memory — knowing that |
| **Episodic** | Temporal experiences: events, sessions, decisions, journal entries | Episodic memory — remembering when |
| **Procedural** | How-to knowledge: skills, processes, workflows | Procedural memory — knowing how |

Episodic and semantic notes are bare markdown files within their type folder. Procedural nodes follow the open Skills format — each is a `<skill-name>/SKILL.md` directory, so they can be loaded as standalone skills via bootstrap (see `BOOTSTRAP.md`). Structure emerges from links and metadata; no deeper hierarchy beyond this typology.

## Metadata and retrieval

Knowledge nodes use faceted metadata — enabling retrieval by entity, date, type, domain, source, relationship, or any combination — without the filesystem needing to encode those dimensions. The metadata vocabulary starts from Dublin Core (the established minimal standard for any digital object) and extends with domain-specific fields as needed.

**Source references** use scheme-prefixed addresses pointing at data wherever it lives — filesystem (`<backend>:<path>`), web (`url:`), email (`email:`), calendar (`calendar:`), or service-specific app schemes (`notion:`, `slack:`, `figma:`, etc.). Schemes are extensible; CFS does not enumerate exhaustively. Resolution is the agent's responsibility — use whatever capability the environment provides (MCP, native, installed CLI, bundled tool). See `refs/knowledge/nodes.md` for the convention and `refs/admin/addressing.md` for the filesystem grammar.

## Multi-source design

The knowledge layer intentionally draws from sources beyond the filesystem:

- **Filed items** — items in Archive, Library, or Projects can be referenced by knowledge nodes via filesystem addresses.
- **Cloud-native content** — Notion databases, Figma projects, Spotify playlists, bookmarked content. These have no local file; they exist only as knowledge nodes with service-scheme source references.
- **Communication** — email threads, chat conversations, meeting notes.
- **Observations** — thoughts, decisions, learnings with no external source.
- **External services** — calendar events, financial data from banking apps, health data from fitness trackers.

External sources are formalized in `config.yaml` `sources:` — read-only handles that both the file flow (consume into storage) and the encode flow (capture into knowledge) can pull from. CFS never mutates sources; the source-protection rule in `refs/admin/safety.md` applies. Resolution depends on the agent's available capabilities (MCP servers, installed CLIs, native support); sources fail gracefully when a capability is missing.

## Relationship to storage layer

The two layers complement each other but neither depends on the other:

| Capability | Filesystem alone | Knowledge layer alone | Both together |
|---|---|---|---|
| File a document | Yes — routing rules determine location | N/A | Yes |
| Find a specific file by browsing | Yes — navigate entity/domain/item | N/A | Yes |
| Find all documents related to a topic | Limited — only within one domain | Yes — faceted retrieval | Yes |
| Understand connections between items | No | Yes — links and metadata | Yes |
| Track status (active/completed) | No — stable locations only | Yes — metadata | Yes |
| Reference cloud-native content | No — filesystem only | Yes — typed source links | Yes |
| AI-assisted retrieval | Basic — filesystem search | Full — semantic search, graph traversal | Full |

The filesystem is designed to be **sufficient for storage and basic browsing** without the knowledge layer. The knowledge layer unlocks **multi-dimensional retrieval, connection-making, status tracking, and AI-powered discovery.** Full CFS power comes from both layers working together, but each layer delivers value independently.

---

# Part III: Operation

*Status: both layers operational and in active use; storage validated across prototype iterations, knowledge functional and accumulating real content. Broader validation still ahead.*

How CFS is operated — by humans and AI agents — across both layers.

## AI integration

CFS is designed for full AI integration throughout both layers — filing, encoding, connecting, maintaining, synthesizing, retrieving. This is not "AI-augmented" (a human system with AI helpers) but "AI-integrated" (designed for both humans and AI from the ground up). The knowledge layer is both a human thinking environment and an AI context layer.

This converges with several contemporary approaches: Karpathy's LLM Knowledge Base (April 2026) uses LLM-maintained markdown knowledge; Dubois's Agentic Knowledge Management (February 2026) describes AI proactively managing knowledge bases; and Forte's Personal Context Management (March 2026) frames the knowledge base as context for AI.

## Non-destructive operations

All CFS operations on source material are non-destructive — read or copy only. Source files are never moved, renamed, or deleted regardless of origin. This is a hard operational constraint, not a guideline. It ensures that CFS can safely operate on any input (downloads, cloud storage, external drives) without risk of data loss. Corrections within CFS-managed storage (re-routing a misrouted item, renaming an entity folder) are allowed — the non-destructive rule applies to sources, not to CFS's own structure.

## Instructions over automation

The system is expressed as natural language documents — specifications, routing rules, conventions, skill definitions — not scripts or rigid code. Purpose-and-outcome descriptions leverage AI intelligence better than step-by-step procedures. An AI agent reading CFS's skill definition understands the system's intent and can make judgment calls; an agent following a script can only execute predefined steps.

This is grounded in the Agent Skills standard (Anthropic, 2025; agentskills.io) for agent-readable procedural knowledge, and converges with the emerging agent skill pattern: Ango's obsidian-skills (January 2026) teaches AI agents to work with Obsidian formats; Eric Ma's AGENTS.md (March 2026) gives AI structural understanding of a vault. CFS's SKILL.md serves the same role — a single entry point that orients an agent to the entire system.

Progressive disclosure follows from this: the specification is layered so that an agent loads only what it needs for the current operation. Overview orients, principles guide, structure specifies, conventions operationalize. Nothing is front-loaded.

## Agent skills

CFS's specification, operational flows, and tools live in a project repository with a single skill entry point (SKILL.md) dispatching to specific flows. This pattern was established in the first prototype and refined through two iterations.

Flows are organized by layer:
- **Storage:** `file` (filing items), `find` (retrieval by browsing), `keep` (storage health), `rule` (record a user-directed source or target rule)
- **Knowledge:** `encode` (creating knowledge nodes), `recall` (retrieval by search and traversal), `reflect` (knowledge health and consolidation), `direct` (record a user-issued directive about what to track and maintain)
- **Admin:** `setup` (initialize/verify environment), `test` (validate flows against test cases), `update` (safely update the CFS project clone with preflight checks, impact review, and rollback option)

Project contributors use a separate flow at `dev/develop.md`, outside the runtime skill — git history is its audit trail.

These are specified as operational skill definitions in the CFS project repository. When the knowledge layer is active, they will also be represented as procedural knowledge nodes (Memory/Procedural).

## Operational logging and todos

In an AI-operated system, imperfect decisions are inevitable — entity names may be incomplete, routing may be uncertain, content extraction may fail. CFS treats uncertainty as a first-class operational concern rather than an error state. The system logs every operation and surfaces deferred judgments as explicit actionable items.

**Logs** record what happened during each flow execution — decisions, observations, warnings, and outcomes. One log file per execution, stored under the appropriate per-section admin path (`{admin}/admin/logs/`, `{admin}/storage/logs/`, or `{admin}/knowledge/logs/`). Logs serve as the operational audit trail: what was filed, where, why, and what was uncertain. See `refs/admin/logging.md` for format and section assignment.

**Todos** capture items that need attention beyond the current operation — entity names needing verification, possible misroutes, failed content extraction needing re-evaluation, or decisions requiring user input. Stored at the corresponding `{admin}/<section>/todo/` with pending/complete status tracking. All flows may create todos; the `keep` and `reflect` flows consume and resolve them.

This design is informed by the reality of AI-assisted filing: an agent making 50 routing decisions in a batch will get most right but should explicitly flag the ones it's uncertain about, rather than silently proceeding or blocking on every ambiguity. Unresolved todos represent system debt that affects health — the `keep` flow is expected to triage them.

## Operational targets

As the system operates, naming patterns and structural conventions emerge that are specific to individual locations — how receipts are named in a particular entity's Finance domain, what format a recurring document type follows, how items within a collection are structured. These are captured in `{admin}/storage/targets.md` as location-scoped targets.

Targets are a user-only artifact — only the user can create, modify, or remove them. The `keep` flow may suggest new targets via todos when it identifies patterns worth codifying, but it does not write targets directly. The `file` flow consults targets and conforms to them, but never creates them. This ensures targets remain a transparent, user-controlled policy layer rather than an opaque accumulation of agent decisions.

Refs define the universal conventions (routing, naming, domains, categories). Targets capture the instance-specific patterns that the user has decided to codify for their data.

## Ingestion sources

Different sources carry different context. A filename prefix, a folder structure, or a source-specific convention may encode information that content extraction alone cannot recover — such as which entity paid for an item when the payment came from a shared bank account.

Source-specific interpretation rules are captured in `{admin}/storage/sources.md`. The `file` flow consults sources during understanding (Step 1) to inform routing and naming decisions. Like targets, sources are a user-only artifact — established by the user directly or via AI assistance.

## Operating modes

The storage and knowledge layers are independently activatable via `config.yaml` flags (`storage.active`, `knowledge.active`). This creates distinct operating modes:

**Storage-only mode** (`storage.active: true`, `knowledge.active: false`) — items are filed, found, and maintained in the filesystem only. No knowledge nodes are created. The `file` flow completes at Step 6 (Verify) without chaining to `encode`. The `find` flow operates by filesystem browsing only. The simplest mode and the historical default during early validation.

**Dual-layer mode** (`storage.active: true`, `knowledge.active: true`) — full CFS operation. Filing chains to encoding. Retrieval spans both layers. Both `keep` and `reflect` maintain their respective layers. This is the target operating mode.

**Knowledge-only mode** (`storage.active: false`, `knowledge.active: true`) — knowledge nodes are created and managed without a CFS-managed filesystem. Useful for capturing understanding from sources that don't need filing (conversations, observations, cloud-native content). Not yet validated.

**Transition: enabling knowledge after storage-only use.** When the knowledge layer is activated after items have been filed without encoding, the system will have filed items with no corresponding knowledge nodes. This is expected — the `encode` flow can be run against existing filed items to create nodes retroactively. A full backfill is not required; nodes can be created on-demand as items are retrieved or reviewed.

**Private sessions.** Independent of the layer flags, a session the harness or the user marks as incognito, ephemeral, or not to be persisted keeps CFS dormant — no recall, encode, filing, logs, or todos — unless the user explicitly opts in within that session. See `refs/admin/safety.md` § Private sessions.

## Configurable locations

Each storage class has a default address in `config.yaml`. For classes where items have different physical requirements — such as projects that need local storage for git repos alongside projects that can live on cloud storage — additional named locations can be configured.

The default address is used unless a source directive (`{admin}/storage/sources.md`) specifies an alternative location. Sources interpret the nature of incoming items (e.g., "contains a git repo with remote origin") and direct them to the appropriate named location. Targets (`{admin}/storage/targets.md`) define conventions per location.

A location may resolve uniformly across machines (single `address:` field) or per-machine via a `mirrors:` map keyed by local backend — the same per-machine pattern remote backends use. Locations whose address (or matching mirror) belongs to an inactive backend in the current session are inert and soft-skipped. See `refs/admin/addressing.md` § Locations.

When any flow inspects the storage for a class (looking for existing entities, checking for duplicates, browsing), it must check all configured locations for that class — the default plus any additional locations active in the session.

### Address syntax

Every address in `config.yaml`, admin files, and knowledge nodes follows a uniform `<backend>:<path>` grammar — see `refs/admin/addressing.md` for the full specification. There is no bare-path form; every address carries an explicit backend prefix.

Backends fall into two classes. **Local** backends (`type: local`) represent a filesystem on a specific machine and declare a `match:` block of identifying signals (hostname, etc.) so the agent can determine which local backend, if any, is active in the current session. Local paths root at `$HOME` on the matched machine. **Remote** backends (`type: gdrive`, etc.) represent services reached via API/MCP/CLI capabilities; they may declare a `mirrors:` map of per-machine local sync paths used for reads only.

The uniform grammar means a single `config.yaml` is portable across all environments — laptops, desktops, cloud workers. Each environment activates whichever backends match its signals and capabilities; addresses with non-active backends remain valid as typed references but are inert (flows soft-skip rather than error).

Scheme prefixes are distinct from the brace placeholders used in docs and flows (`{admin}`, `{library}`): braces are template variables that resolve to addresses; the scheme is part of the address itself. Operational rules for dispatching on a backend live in `refs/admin/safety.md` § Backend dispatch.

## MCP and tool integration

CFS is designed to be operated through open protocols. MCP (Model Context Protocol, Anthropic 2024, Linux Foundation 2025) enables AI agents to access personal data sources through a standardized interface. CFS's plain-text, file-based architecture is naturally MCP-compatible — an MCP server can expose the filesystem and knowledge layer to any AI agent.

The agent reads most files directly using its own multimodal capabilities — images, PDFs, and text files require no external tools. For formats or backends beyond agent-native reach (complex binary formats, cloud-native files, server-side cloud storage operations), CFS draws on whatever capability the environment provides — agent-native, MCP, installed CLI, or a CFS-bundled reference implementation. These are operational conveniences, not architectural dependencies; see `refs/admin/safety.md` § Backend dispatch for the rule.

## Cognitive health

Full AI integration carries real risk. Research on cognitive offloading (Harvard/MIT, 2025) suggests heavy AI reliance can lead to reduced critical thinking and "belief offloading." The Zettelkasten community's concern — that automating knowledge work is like using a motorcycle in a marathon — is one we take seriously.

Our position: the motorcycle gets you farther. The question isn't whether to use it, but how to stay healthy while doing so. The history of human tools, from writing to calculators to search engines, is a history of cognitive offloading followed by adaptation. We believe AI integration in knowledge work follows the same pattern — and the design challenge is maintaining cognitive engagement alongside AI assistance, not avoiding AI integration.

CFS doesn't claim to have solved this. The specific practices for healthy AI-augmented knowledge work (active review, retrieval practice, deliberate encoding, knowing when to do the thinking yourself) are an open design concern to be explored through use. The plain-text, human-readable format of both layers ensures that human engagement is always possible — nothing is locked behind AI-only interfaces.

---

## Influences

CFS draws from multiple disciplines. Each influence is described with its specific relationship to the design — what was incorporated, what inspired a direction, and where independent work converges with CFS's approach.

### Organizational frameworks

- **PARA Method** (Forte, 2017) — CFS was informed by PARA's four-bucket model. The concepts of Projects (time-bound work), Areas (ongoing responsibilities), and Resources (reference collections) shaped CFS's storage classes. CFS diverges from PARA by removing the Archives bucket (stable locations instead), adding entity-first routing, restructuring Resources by type rather than topic, and adding a dedicated knowledge layer. Forte's 2026 pivot to "Personal Context Management" converges with CFS's knowledge layer as AI context layer.
- **Johnny Decimal** — Informed domain count and cognitive load considerations. JD Life Admin's 5-category personal system offered grounding for archive domain coverage, particularly the "Travel, events & entertainment" category.
- **datacurator-filetree** (~1,600 GitHub stars) — Library categories were incorporated from datacurator's media-type-first structure. The carrier/concept hybrid (audio, video, images alongside games, software, literature) was adopted as the library's organizational scheme.
- **Getting Things Done** (Allen, 2001) — Inspired input staging and the capture-then-process principle.

### Neuroscience and cognitive science

- **Social cognition research** (Quiroga et al., 2005; fusiform face area research) — Inspired the entity-first design intuition. The finding that the brain has dedicated machinery for processing agents (people, organizations) and that memory for "who did what" is stronger than for most other dimensions suggested entity-first organization might align with natural cognition. CFS extends the entity concept beyond agents to include independent record-bearing things (properties, vehicles) — grounded in the observation that administrative continuity, not just agency, determines record ownership.
- **Tulving (1972–2005)** — Memory systems taxonomy (semantic, episodic, procedural) inspired the knowledge layer's type structure. These are used as organizational metaphors, not claims about cognitive architecture.
- **Squire (1992)** — Declarative/nondeclarative taxonomy informed the separation of knowledge types.
- **Baddeley & Hitch (1974)** — Working memory model informed cognitive load limits at routing decision points (7±2 options at any choice).

### Data modeling

- **Kimball (1996)** — Star schema's "organize by dimensions, starting with WHO" offered grounding for entity-first routing in a data modeling context.
- **Linstedt (Data Vault 2.0)** — Hub-centric design (organize by identity, not domain) offered additional grounding for entity-first routing.

### Library and archival science

- **Ranganathan (1933)** — Faceted classification (PMEST) grounds the knowledge layer's multi-dimensional retrieval approach. The principle that items should be findable along multiple independent dimensions, not forced into a single hierarchy, is the organizing principle for the knowledge layer.
- **Dublin Core** — Incorporated as the metadata vocabulary starting point for knowledge layer notes.
- **FRBR/WEMI** — Informed handling of multiple versions/formats of the same work (e.g., FLAC and MP3 of the same album).
- **ISO 15489** — Functional classification methodology grounds the archive domain design. The domains represent functions of personal life, not document types.
- **MPLP** (Greene & Meissner, 2005) — Grounds the flat-by-default approach. Organize broadly first, add structure incrementally.
- **Records continuum model** (Upward, 1990s) — Grounds the stable locations principle. Records are simultaneously active and archival; the lifecycle model's sequential stages don't apply to digital materials.
- **Respect des fonds** — Principle of provenance grounds entity-first organization (organize by creator/owner).

### Media and digital collections

- **Plex, Jellyfin, Kodi** — Media server conventions confirmed library category separation by content type. Their naming standards for films (`Title (Year)/Title (Year).ext`), TV series (`Series/Season NN/Series - SNNENN - Episode Title.ext`), and music (`Artist/Album (Year)/Track - Title.ext`) were adopted as CFS's library video and audio naming conventions.
- **MusicBrainz Picard / beets** — The de facto standard for music file naming and tagging. Picard's `Artist/Album (Year)/Track - Title` convention, consistent across Plex, Jellyfin, and Kodi, was adopted for CFS's audio naming.
- **Calibre** — The dominant ebook manager. Calibre's `Author/Title (Year)` convention was adopted for CFS's books naming, extended with Mylar/ComicVine conventions for comics and academic paper conventions.
- **No-Intro** — The gold standard for ROM naming (`Title (Region).ext`), adopted for CFS's game ROM naming. Platform folder naming follows No-Intro DAT conventions. Cross-referenced with TOSEC and Redump.
- **Adobe Lightroom / photographer conventions** — Date-based photo organization (`YYYY/YYYY-MM-DD - Event/YYYYMMDD_HHMMSS.ext`) was adopted for CFS's image naming, consistent with digiKam and EXIF/DCF standards.
- **FileBot / Sonarr / Radarr** — Automated media renaming tools whose default expressions confirmed Plex/Jellyfin naming as the de facto video standard.
- **XDG Base Directory Specification** — OS-level user directories (Music, Pictures, Videos) confirmed carrier-based categories.
- **Internet Archive** — Seven mediatype silos with nested collections confirmed type-first organization at scale.
- **Schema.org CreativeWork** — Consensus type ontology cross-referenced for category completeness.

### Personal information management

- **Bergman & Whittaker (2016)** — *The Science of Managing Our Digital Stuff* (MIT Press). Finding that users navigate faster with broader, shallower structures informed minimum necessary hierarchy.
- **Jones (2007)** — *Keeping Found Things Found*. Finding that personal organization is activity-driven and idiosyncratic informed CFS's prescribed structure (reducing idiosyncrasy for findability).
- **McKemmish (1996)** — "Evidence of Me." Framework of personal records documenting identity, activities, relationships, and rights offered grounding for archive domain coverage.

### Personal records frameworks

- **Estate planning consensus** — Categories (Identity, Financial, Insurance, Property, Legal, Medical, Employment) cross-referenced and synthesized for archive domain validation.
- **Document vault services** (Everplans, Trustworthy, etc.) — Cross-referenced for domain coverage.
- **State Records Authority of NSW** — Personal recordkeeping guidance with 8 categories, cross-referenced for international validation.

### Contemporary convergent work (2025–2026)

Independent projects that arrived at patterns converging with CFS's approach — meaningful as signal that the design space pulls toward similar solutions, though not validation of any particular implementation:

- **Karpathy's "LLM Knowledge Base"** (April 2026) — Three-layer architecture (raw sources, LLM-maintained wiki, schema) converges with CFS's two-layer + skill definition approach.
- **Steph Ango / Obsidian** — "File over app" philosophy converges with CFS's plain text infrastructure. obsidian-skills (January 2026) converges with CFS's agent skill pattern.
- **Dubois, "Agentic Knowledge Management"** (February 2026) — AI proactively managing knowledge bases converges with CFS's agent skills approach.
- **Harper Reed, "Immaculate Knowledge Graph"** (March 2026) — AI-generated Obsidian vault converges with CFS's emergent knowledge structure.
- **Eric Ma, "Mastering PKM with Obsidian and AI"** (March 2026) — AGENTS.md pattern for AI vault access converges with CFS's SKILL.md approach.
- **A-MEM** (arXiv:2502.12110, February 2025) — LLM memory systems using Zettelkasten principles converges with CFS's knowledge layer design for AI agents.

### AI and cognition

- **Cognitive offloading research** (Harvard/MIT, 2025; Frontiers in Psychology, 2025) — Informs CFS's acknowledgment of cognitive health as an open design concern.
- **MCP (Model Context Protocol)** (Anthropic, 2024; Linux Foundation, 2025) — Enables CFS's AI-native operation through open protocol for agent access to personal data.
- **Agent Skills** (Anthropic, 2025; agentskills.io) — Open standard for agent-readable procedural knowledge. CFS's SKILL.md entry point, progressive disclosure pattern, and operational flow structure follow the Agent Skills specification. The guide's recommended format (Instructions, Examples, Troubleshooting sections with imperative voice) was adopted for CFS flows.

---

## Open Questions

These are acknowledged gaps and unresolved tensions in the current design. They're listed here to set expectations and guide future development.

1. **Events domain coherence.** Events is the broadest archive domain and the only one that doesn't cleanly pass the "one kind of information" test. Its contents (itineraries, conference materials, loyalty programs) share a temporal/experiential association rather than a strict information type. The other six domains are crisper. We've framed events as "experiential documentation," but this may need further refinement or redistribution through use.

2. **Collection decision framework.** The current criteria (5+ items sharing a meaningful grouping attribute) work for human judgment but may be underspecified for AI agents. Library categories use convention-driven grouping that forms immediately (see `refs/storage/collections.md`), but the archive threshold and grouping test — "would this grouping help someone browsing the domain find related items faster?" — remain intuitive rather than formally operationalized.

3. **Cognitive health practices.** CFS acknowledges the risk of cognitive atrophy from AI-integrated knowledge work but doesn't prescribe specific countermeasures. What review practices, encoding requirements, or deliberate friction points maintain cognitive engagement? This is the most important open design question.

4. **Knowledge layer encoding standards.** What constitutes "real understanding" in a knowledge node? What's the minimum quality bar for AI-generated encoding? When should a human engage directly vs. delegate to AI? These questions become concrete during implementation.

5. **Maturity asymmetry.** Part I (Storage) was developed and validated first across multiple prototype iterations. Part II (Knowledge) is now in active use but at an earlier stage of validation. This is intentional — development progressed storage-first — but readers should calibrate expectations accordingly.

---

## History

CFS is the third iteration of this system. Each prototype contributed specific insights:

**Prototype 1 (2026-04-02):** Established physical separation of concerns — notes, files, workspaces, and input staging as independent components with configurable paths. Introduced a single skill entry point dispatching to multiple operational flows. Key lesson: separating the knowledge layer from file storage is essential; they have fundamentally different requirements. Limitations discovered: flat entity structure with no domain-level organization, and heavy neuroscience-derived naming that created a learning curve.

**Prototype 2 (2026-04-04):** Established entity-first routing with 8 empirically derived domains, validated against 15 independent organizational systems and real-file migrations. Produced comprehensive specification documents covering routing, naming, and metadata. Built a content extraction pipeline for reading documents before filing. Key lesson through migration testing: unified storage (notes colocated with files) breaks when artifacts require different storage mechanisms — git repos and development environments cannot live on cloud-synced storage. This directly motivated the two-layer separation.

**v3 (2026-04-06 to present):** Separates filesystem and knowledge layer as independent layers. Simplifies hierarchy to minimum necessary depth per storage class. Introduces collections as the final structural layer. Adds events domain and reinforces assets for digital property. Positions CFS as drawing from multiple disciplines rather than enhancing any single framework. Subsequent development: adopted natural naming with established media conventions (MusicBrainz, Plex, Calibre, No-Intro, Lightroom), two-tier naming (natural for user content, lowercase for system internals), language support (structural hierarchy in system language, filenames in document language), flow restructuring by layer (storage/knowledge/admin), admin storage class with logging and todo systems, layer activation flags, and Agent Skills-aligned SKILL.md.

---

*CFS v3 — working draft, 2026-04-28. Both layers operational and in active use. The real test continues through sustained use.*
