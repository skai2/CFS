# Keep

Keep the CFS storage layer healthy — consistency, navigability, and quality. Log every execution per `refs/admin/logging.md`.

## Scope

Four goals:
1. **Organized** — no duplicates, correct naming, consistent formatting, rules enforced.
2. **Navigable** — structure is easy to browse, collections group related items, no clutter.
3. **Current** — items added or modified since the last run are reviewed; anything unresolved becomes a todo for next time.
4. **Resolved** — pending todos are triaged, actionable items are addressed or escalated to the user.

## Prerequisites

- Read `config.yaml` for storage layer addresses and backend declarations. See `refs/admin/safety.md` § Backend dispatch for the rule on how to operate on each — keep performs many mutations (renames, moves, deletions) and must dispatch through a capability that operates on the backend's API.
- Read `{admin}/storage/targets.md` for established patterns.

## Input

- A specific target location to operate on.
- Or no target — orient from recent logs in `{admin}/storage/logs/` (where new items landed, what warnings were raised). Focus on locations with recent activity or unresolved issues.

## Output

- Cleaned and consistent storage structure.
- Execution log in `{admin}/storage/logs/` (mandatory).
- Resolved todos in `{admin}/storage/todo/` (marked complete with notes).
- New todos for suggested rules or issues requiring user input.

## Instructions

### Step 1: Triage todos

**Objective:** Process pending items in `{admin}/storage/todo/`.

For each todo:

- **No user-data mutation needed** — content re-extraction from existing files, verifying a filing decision, updating todo notes, closing todos made obsolete by subsequent state. Resolve it, mark complete, log.
- **User-data mutation needed** — entity name corrections, misroute fixes, proposed renames, proposed merges. Present the proposed action with what/why/risk per `refs/admin/safety.md` § User consent. If approved in-session, execute and mark complete. If not approved or user unavailable, update the todo with the fully specified proposal and leave it pending for next run.
- **Requires user decision beyond consent** — ambiguous routing, entity disambiguation, preference decisions. Present context and suggested options; update the todo with the decision.
- **No longer relevant** — already resolved by a subsequent filing or prior keep run. Mark complete with a note.

### Step 2: Review recent changes

**Objective:** Surface items added or modified since the last keep run that may need review — items dropped in directly, edits made outside CFS flows, or sync artifacts that slipped through.

The watermark is the timestamp of the most recent prior keep log in `{admin}/storage/logs/` (filename format `YYYY-MM-DD-HHMM-<level>-keep.log`). On the first-ever keep run there is no prior log — skip this step with a notice; the current run establishes the baseline for next time.

For each configured storage address:

1. List items modified or created after the watermark, dispatching per `refs/admin/safety.md` § Backend dispatch. Filter by modification/creation time via the capability used for the backend.
2. For each hit, classify:
   - **In unsorted** — a pending item the user added. Hand off to the `file` flow (filing is copy-only, autonomous).
   - **New, outside unsorted** — the user placed this directly. Check that routing and naming fit the location. If fine, no action. If not, create a todo proposing a re-file with the target address, proposed name, and rationale — do not execute a move.
   - **Modified** — content or metadata changed. Check naming still reflects content; check for sync-conflict artifacts (`(1)` suffixes, duplicate siblings). Record observations; any remediation that would rename, move, merge, or delete existing content requires user approval — create a todo.
3. The next keep run picks up pending todos via Step 1 — do not re-flag the same delta across runs.

### Step 3: Scan structure

**Objective:** Identify structural and naming issues and propose remedies. Scan all configured locations for each class (default + additional). Any mutation on existing user-data items requires user approval — see `refs/admin/safety.md` § User consent.

1. `{admin}/storage/targets.md` — check for targets that apply to each location.
2. `refs/storage/naming.md` — general naming conventions.
3. Inspect the storage at each location and observe:

- **Naming deviations** — do similar items follow the same pattern? If a target exists, do items conform? Record deviations. Read items directly to fill missing information — using whatever extraction capability is needed for the format. Renames require approval: create a todo listing each proposed before→after and the rule driving it.
- **Duplicates** — identify identical files (by content hash). Create a todo specifying which copy to keep and which to remove, with the rationale (e.g., "keep the better-named version at X; remove Y").
- **Empty folders** — flag via todo proposing deletion. A folder may be a structural intent not yet populated — deletion requires approval.
- **Orphaned structure** — sync race artifacts (e.g., `(1)` suffixed folders). Create a todo proposing the merge-and-remove plan with source and destination paths.

### Step 4: Evaluate collections

**Objective:** Observe whether collections serve navigability and propose changes. Collection creation, formation, consolidation, dissolution, and renaming all move or rename existing user-data items — all require user approval (see `refs/admin/safety.md` § User consent).

1. `{admin}/storage/targets.md` — targets override other considerations. If a target contradicts the current state, propose the reconciling action via todo.
2. `refs/storage/collections.md` — general guidelines for grouping criteria and thresholds.
3. `refs/storage/naming.md` — collection naming conventions.

- **Target enforcement** — if a target contradicts the current state, create a todo specifying the full rename/restructure/dissolve plan.
- **Formation** — if 4+ items share a grouping attribute (institutional source, temporal cluster, recurring category), create a todo proposing the collection name and the moves needed.
- **Consolidation** — if multiple collections exist for the same grouping, create a todo proposing the canonical name and the merge plan (source → destination for each item).
- **Naming** — if a collection name doesn't follow conventions, create a todo proposing the rename.

### Step 5: Suggest targets

**Objective:** Identify patterns that could improve future filing and propose them to the user.

Targets are a user-only artifact — keep must not write to `{admin}/storage/targets.md` directly.

When keep identifies a pattern worth codifying (a naming convention, a structural preference, a collection policy):

1. Create a todo describing the suggested target, its scope, and the rationale.
2. The user will accept, modify, or reject the suggestion. Accepted suggestions are codified via `flows/storage/rule.md`.
3. Only the user writes targets — directly, via AI assistance, or by accepting keep's suggestions.

### Step 6: Verify

**Objective:** Confirm changes are correct and complete.

- **Consistency** — does the structure look right? No unintended side effects?
- **Completeness** — were all pending todos addressed?
- **Log** — write a complete log of all actions taken, decisions made, and items requiring user input.

## Troubleshooting

**Collection names conflict across filing sessions**
Cause: Independent file agents chose different names for the same grouping.
Solution: Create a todo proposing a canonical name and the merge plan. Execute only with approval. Suggest a rule to the user to prevent recurrence.

**Todo requires unavailable information**
Cause: Entity verification or preference decision needs external knowledge.
Solution: Present to the user with full context and suggested options. Do not guess — escalate.

**Large number of items need renaming**
Cause: A rule was established or changed after items were filed under the old pattern.
Solution: Create a todo with the full scope (count, sample of before→after, rule driving the change). Bulk renames require approval — there are no autonomous thresholds.

**Existing structure contradicts a rule**
Cause: A rule was added or changed after items were organized differently.
Solution: Create a todo proposing the reconciling action (rename, restructure, or dissolve) with the full plan. Execute only with approval.

## References

| Document | When to consult |
|---|---|
| `refs/admin/safety.md` | All steps — operational safety rules; Step 2 — backend dispatch for delta listing |
| `refs/storage/collections.md` | Step 4 — collection guidelines |
| `refs/storage/naming.md` | Steps 3, 4 — naming conventions |
| `refs/admin/logging.md` | All steps — logging; Step 2 — prior keep logs provide the watermark |
| `{admin}/storage/targets.md` | All steps — established patterns (takes precedence) |
| `{admin}/storage/todo/` | Step 1 — pending items; Step 2 — items needing review roll over as todos |
| `config.yaml` | Prerequisites — storage addresses and backends |
