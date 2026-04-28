# Using CFS

Practical guide to using CFS day-to-day: what to say to your agent, what happens silently in the background, how to ingest your existing files, and how to keep the system healthy over time.

If you haven't set up CFS yet, see [Getting started](../README.md#getting-started) first.

## Talking to CFS

CFS operates through natural-language phrasing, not strict commands. Any AI agent with the skill loaded recognizes intent from how you ask. The example phrases below are illustrative — equivalent wording works.

## Operations at a glance

CFS organizes work into ten operations across three layers. Most are user-driven; two fire silently as part of normal conversation (see [What runs silently](#what-runs-silently)).

### Storage

| Operation | When to use | Example phrases |
|---|---|---|
| **file** | Save something into stable storage | *"file this PDF"*, *"process my Downloads"*, *"save this receipt"* |
| **find** | Retrieve something from storage | *"find my passport"*, *"show me my Acme receipts"*, *"where did I put X?"* |
| **keep** | Maintenance — drift, unsorted items, deferred work | *"clean up storage"*, *"anything in unsorted?"*, *"review the todos"* |
| **rule** | Establish or change a routing rule | *"from now on, X items go to Y"*, *"drop the Acme naming rule"* |

### Knowledge

| Operation | When to use | Example phrases |
|---|---|---|
| **recall** | Look up prior context (often implicit, see below) | *"what's John Doe's email?"*, *"have we discussed X before?"* |
| **encode** | Capture a fact, decision, or event (often implicit, see below) | *"remember this"*, *"save that decision"* |
| **reflect** | Maintenance — duplicates, gaps, weak connections | *"review the knowledge graph"*, *"consolidate duplicates"*, *"any gaps?"* |
| **direct** | Establish a directive about what knowledge should track | *"always record meeting outcomes"*, *"track project status going forward"* |

### Admin

| Operation | When to use | Example phrases |
|---|---|---|
| **setup** | First-time setup or environment verification | *"set up CFS"*, *"verify the environment"* |
| **test** | Validate flows against test cases | *"run the CFS tests"* |

## What runs silently

Two operations fire as part of normal conversation, without you asking:

- **`recall`** runs at the start of each turn when the user references known context (people, projects, decisions, prior conversations). The agent reads relevant nodes from the knowledge layer before responding, so its answer is grounded in your context rather than generic defaults.
- **`encode`** runs at the end of a turn when something worth remembering came up — a decision, a new entity, a process you articulated, an event. The agent records it quietly and may surface a one-liner so you know something was captured.

You generally don't notice these unless they produce something visible. That's by design: the system is meant to fade into the background of your normal AI work. If you want to see what's been captured, look in `Memory/Episodic/` and `Memory/Semantic/`.

## Your first ingestion

CFS is most useful when populated, but ingestion goes wrong fastest when done all at once. The recommended approach is staged.

**1. Run setup.**

Ask the agent to set up CFS. Confirm the storage backend, addresses, and that the directory structure was created. See [flows/admin/setup.md](../flows/admin/setup.md) for what setup walks through.

**2. Pick a small, bounded source.**

A single Downloads folder. One project's working files. A handful of receipts from a month. Something where you can eyeball every result.

**3. Ask the agent to file it.**

Point the agent at the source. The file flow handles content extraction, routing, and naming. Source material is left unchanged — CFS copies into managed space.

**4. Review what landed where.**

Walk through the routed items. If the routing felt wrong for a category, tell the agent: *"X items should go to Y from now on"* — the rule operation records it for future sessions. If a naming pattern wasn't right, say so.

**5. Expand the next batch.**

Once a few small batches feel right, point the agent at larger collections. The accumulated rules from earlier batches should make later batches need less correction.

**6. Schedule periodic maintenance (optional).**

If your harness supports scheduled tasks, wire `keep` and `reflect` to a regular cadence. Storage hygiene and knowledge consolidation work best as background tasks rather than crisis-driven cleanups. See [flows/storage/keep.md](../flows/storage/keep.md) and [flows/knowledge/reflect.md](../flows/knowledge/reflect.md).

## Maintenance rhythms

Two operations exist for ongoing health:

- **`keep`** — storage hygiene. Reviews drift, processes anything in `Unsorted/`, works through deferred todos. Run manually when storage feels untended, or schedule for routine pickup.
- **`reflect`** — knowledge consolidation. Surfaces duplicate semantic nodes, weak connections, gaps in coverage. Run when the knowledge layer feels noisy, or schedule.

Manual runs surface findings for your review. Scheduled runs do the same; nothing destructive happens without explicit consent (see [refs/admin/safety.md](../refs/admin/safety.md)).

## When things go wrong

A few common failure modes and where to look:

- **Misrouted file.** Move it manually to the correct location, then tell the agent where it should have gone — the rule operation adjusts future routing.
- **Wrong name.** Rename it manually; tell the agent if the naming rule was off so the rule can be corrected.
- **Incorrect knowledge entry.** Edit the node directly, or ask the agent to revise it.
- **Lost track of what happened.** Logs live in `Admin/<layer>/logs/`. Deferred work lives in `Admin/<layer>/todo/`.

For bugs in the flows themselves, file an issue against the repo with a description of what you said, what happened, and what you expected.
