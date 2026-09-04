# Safety

Operational safety rules for all CFS flows. All agents must follow these.

---

## Source protection

External source material is read/copy only. No CFS flow may move, rename, or delete external source files regardless of origin. There are no exceptions — if source mutation is needed for an extraordinary reason, the user must perform it manually.

The one exception is CFS's own unsorted inbox (`storage.unsorted`). Items in unsorted are CFS-managed and are removed after filing — this is the intended behavior, not a violation of source protection.

For the knowledge layer, source material is the conversation context — read but never mutated. Encoded knowledge nodes are CFS-managed and live under the knowledge address.

External sources defined in `config.yaml` `sources:` (read-only locations and services CFS may pull from for filing or encoding) are subject to the same rule — pull only, never mutate. Sensitive identifiers within source addresses (account names, workspace IDs) follow the sensitivity rules in § Sensitive data handling below.

## User consent

**Every destructive operation on user data requires explicit user consent.** No thresholds, no carve-outs. If consent cannot be obtained in the current session, create a todo capturing the proposed action and its rationale — the next keep or reflect run surfaces it via todo triage.

**User data** is anything under any active layer's configured addresses — Archive, Library, Projects, Unsorted for storage; Memory for knowledge.

**Destructive operations** (consent required, always):
- Deleting a file or folder
- Moving an item (any destination — including between locations within a class, cross-entity, or into/out of a collection)
- Renaming a file, folder, entity, or collection — any count, including a single rename
- Overwriting existing content
- Merging, dissolving, or restructuring collections or knowledge nodes
- Any mutation where the agent is uncertain of the outcome

**Non-destructive operations** (autonomous, no consent required):
- Creating a new folder
- Copying/filing a **new** item into an existing or new folder (the source is preserved by the source protection rule, and the destination didn't have this item)
- Reading content

**Admin state is self-managed.** Flow-internal operations on CFS admin state — todo lifecycle transitions (renaming `pending` → `complete`), appending resolution notes to todo bodies, writing execution logs — do not require consent. They are CFS's control plane, not user data.

When requesting consent, present:
- What will change (specific paths and actions).
- Why (the rule, finding, or rationale driving the change).
- What could go wrong (the risk if the action is incorrect).

When consent is not obtainable, record all three fields in the todo so a future session can act on it with full context.

## Sensitive data handling

- **Never send document content externally** for research or identification. Filing is local-only.
- **Minimize sensitive data in logs and todos.** Record decisions and paths, not document contents. See `refs/admin/logging.md` sensitivity section.
- **Targets and sources are user-only artifacts.** Agents may suggest targets via todos but must not write them directly.

## Private sessions

A private session is any session the harness or the user marks as incognito, ephemeral, or not to be persisted. CFS follows the same posture as the harness's own memory: dormant by default.

- Do not load or operate CFS in a private session unless the user explicitly asks for it within that session. No recall, no encode, no filing, no logs, no todos — every flow leaves a trace.
- Opt-in is per session and applies from the moment it is given. Nothing said before it is encoded unless the user says so.
- Never encode content from a private session afterwards, from another session, or from a transcript.
- Do not infer privacy from content. Only an explicit harness signal or user cue ("off the record", "don't remember this") sets it.

## Backend dispatch

Address grammar and backend declarations are defined in `refs/admin/addressing.md`. Operating on a remote backend requires a capability that speaks its API; choice of capability is covered in `SKILL.md` § Prerequisites. The two invariants below are mandatory for any remote backend:

- **Mutations go through the backend's API.** All creates, moves, renames, deletions, and uploads must be performed server-side via the backend's API. Never mutate a remote backend through any local path that happens to surface its content (e.g., a sync mount).
- **Reads may use a declared mirror.** A remote backend's `mirrors:` map declares per-machine local sync paths. The agent may read file contents through the mirror entry whose key matches the active local backend; never write, move, or delete through it. The mirror may lag recent server-side mutations — when acting on a just-mutated item, prefer a fresh API read.

If no available capability satisfies these invariants for an active backend, stop and report — do not improvise through unsafe paths.

**Inert addresses.** Addresses whose backend is not active in the current session (no matching local backend; no API capability for a remote backend) are typed references that cannot be resolved here. Flows must log and soft-skip operations on inert addresses — never error, never improvise.

These rules are protocol-agnostic. Flows do not need to know whether a given address is local, Google Drive, or some future backend — they dispatch on the address, the capability answers.

## Operational boundaries

- **One approved operation at a time.** Do not chain destructive operations under a single approval; each destructive action needs its own consent, with verification in between.
- **Log everything.** Every flow execution must be logged per `refs/admin/logging.md`.
- **Err towards inaction on user data.** For filing (copy-only, corrections allowed later), prefer filing under a best guess with a todo over leaving the item unfiled. For any destructive operation, the default is to create a todo — proceeding without consent is a bug.
- **Report anomalies.** Unexpected filesystem state (sync conflicts, permission errors, missing files) should be logged and escalated, not silently resolved.
