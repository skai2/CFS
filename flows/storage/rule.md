# Rule

Establish, change, or remove a user rule in `{admin}/storage/sources.md` or `{admin}/storage/targets.md`. Sources and targets are user-only artifacts — this flow writes them only at the user's direct instruction and with confirmed wording. Log every execution per `refs/admin/logging.md`.

## Scope

Handles user directives that update administrative policy:

- **Source rules** — how to interpret items from a known origin. Written to `{admin}/storage/sources.md`.
- **Target rules** — location-scoped naming or structural patterns. Written to `{admin}/storage/targets.md`.

Does not cover:

- `config.yaml` changes — see `flows/admin/setup.md`.
- CFS universal conventions in `refs/` — see `dev/develop.md` (project-contributor flow, outside the runtime skill).
- One-off preferences for the current task (no persistence) — the relevant storage flow handles them inline.

## Prerequisites

- Read `config.yaml` for storage layer addresses and the admin address.
- Read `{admin}/storage/sources.md` and `{admin}/storage/targets.md` for existing entries.
- Read `refs/_templates/sources.md` and `refs/_templates/targets.md` for entry format.

## Input

- A user directive establishing, modifying, or removing a rule.

## Output

- Updated `{admin}/storage/sources.md` or `{admin}/storage/targets.md`.
- Zero or one `keep` todo capturing retroactive reconciliation scope, when applicable.
- Execution log in `{admin}/storage/logs/` (mandatory).

## Instructions

### Step 1: Understand

**Objective:** Determine exactly what rule is being established, changed, or removed.

**Produces:** Scope (which location or origin the rule applies to), duration (standing vs one-off), and action (add / modify / remove).

1. Identify the scope — entity-wide, class-wide, one location, one source origin.
2. Confirm the rule is meant to persist. One-off preferences for the current task are not rules; redirect to the relevant flow.
3. If scope or intent is ambiguous, ask for clarification before proceeding.

### Step 2: Classify

**Objective:** Determine where the rule belongs.

**Produces:** Target artifact — `{admin}/storage/sources.md` or `{admin}/storage/targets.md`.

1. **Source** — interprets items from a known origin (prefix conventions, value mappings, entity overrides for shared sources). Goes in `sources.md`.
2. **Target** — location-scoped naming or structural pattern at a destination. Goes in `targets.md`.
3. If the directive is mixed (e.g., "items from Corp Bank go to Finance/Banking with name X"), split into a source rule and a target rule.

### Step 3: Draft

**Objective:** Produce the exact entry text, per the artifact's format.

1. `refs/_templates/sources.md` or `refs/_templates/targets.md` — follow the format.
2. Include `created` and `updated` dates — today's date for new entries; bump `updated` for modifications.
3. Present the exact wording to the user. Sources and targets are user-only artifacts — proceed only after the user confirms the text.

### Step 4: Commit

**Objective:** Write the entry to the admin artifact.

1. Append (new entries) or modify (changes) the relevant file.
2. For removals, remove the entry and note the reason in the log.
3. The admin artifact is CFS-managed state — the write is flow-internal and requires no further consent beyond the user's confirmation of the wording.

### Step 5: Reconcile

**Objective:** Assess whether the rule retroactively applies to existing filed items, and either run keep or queue a todo.

1. Assess retroactive scope:
   - Rule that only governs future items → no reconciliation needed.
   - Rule that would rename, re-route, or restructure existing items → reconciliation needed.
2. Present the choice to the user:
   - Run `keep` now, scoped to the affected locations — keep proposes specific changes via its normal steps, each destructive action gated on consent per `refs/admin/safety.md`.
   - Create a `keep` todo describing the expected scope and the rule driving it, for the next keep run to pick up.
3. Execute per the user's choice. Do not auto-reconcile.

### Step 6: Verify

**Objective:** Confirm the rule is recorded and follow-through is scheduled.

- The entry appears in the correct artifact with the confirmed wording.
- If reconciliation was chosen, keep was run or a todo was created.
- Write a log summarizing what was recorded and what happens next.

## Examples

### Example 1: New source rule

Input: User says "Files from Corp Bank prefixed `INV-` are employer invoices, not personal. Route to Unimetrics, not to my personal entity."

Actions:
1. **Understand** — entity-shift rule for a known prefix from a specific source; standing.
2. **Classify** — source rule (origin interpretation).
3. **Draft** — entry for `{admin}/storage/sources.md` scoped to the Corp Bank source location, prefix-based routing override. Present text; user confirms.
4. **Commit** — append to `{admin}/storage/sources.md`.
5. **Reconcile** — scan shows 14 existing items under the personal entity matching the prefix. User opts for a keep todo rather than immediate reconciliation.
6. **Verify** — entry present, todo created, log written.

Result: Rule recorded; 14-item re-route queued for next keep run.

### Example 2: Target naming change

Input: User says "Name receipts as `YYYY-MM-DD - Vendor` instead of `YYYY-MM - Vendor`."

Actions:
1. **Understand** — naming pattern change for Receipts collections; standing; applies wherever the Receipts target exists.
2. **Classify** — target rule.
3. **Draft** — modify existing Receipts target in `{admin}/storage/targets.md`, update pattern, bump `updated`. Present; user confirms.
4. **Commit** — modify `{admin}/storage/targets.md`.
5. **Reconcile** — ~60 existing receipts follow the old pattern. User opts to run keep immediately, scoped to Receipts locations. Keep proposes each rename via todos per the unified consent rule.
6. **Verify** — entry updated; keep running; log written.

Result: Target changed; retroactive renames pending user approval during keep.

### Example 3: Rule removal

Input: User says "Drop the Acme Health filename rule — let it fall back to the default pattern."

Actions:
1. **Understand** — rule removal; applies to Acme Health entity.
2. **Classify** — target rule removal.
3. **Draft** — show the user the current entry; confirm removal.
4. **Commit** — remove the entry from `{admin}/storage/targets.md`.
5. **Reconcile** — no retroactive action; existing items retain current names (corrections always allowed later).
6. **Verify** — entry removed; log written.

Result: Rule removed; no retroactive changes.

## Troubleshooting

**Directive ambiguity — rule or one-off?**
Cause: User stated a preference without indicating whether it's a standing rule.
Solution: Ask. If standing, proceed with `rule`. If one-off, redirect to the relevant flow and do not write to admin artifacts.

**Rule conflicts with an existing entry**
Cause: The new directive overlaps or contradicts an existing source or target.
Solution: Present the conflict. Confirm with the user whether the new rule replaces, refines, or coexists with the existing one.

**Rule belongs in `refs/`, not `{admin}/`**
Cause: The user is stating a universal CFS convention, not a location-scoped pattern (e.g., "all filenames should be lowercase").
Solution: This is a design-level change — redirect to `dev/develop.md` for a refs update, not a per-user admin entry.

**User asks to run reconciliation immediately but keep would touch many items**
Cause: A broad rule change implies a large number of renames or moves.
Solution: Proceed — keep will surface each destructive action via todos per `refs/admin/safety.md`. The user approves or queues per item; nothing is executed silently.

## References

| Document | When to consult |
|---|---|
| `refs/admin/safety.md` | Step 5 — consent applies to every user-data mutation during reconciliation |
| `refs/admin/logging.md` | All steps — logging |
| `refs/_templates/sources.md` | Step 3 — source entry format |
| `refs/_templates/targets.md` | Step 3 — target entry format |
| `{admin}/storage/sources.md` | Steps 3, 4 — source rules |
| `{admin}/storage/targets.md` | Steps 3, 4 — target rules |
| `flows/storage/keep.md` | Step 5 — retroactive reconciliation |
| `dev/develop.md` | Troubleshooting — when the rule belongs in `refs/` (project-contributor flow) |
| `config.yaml` | Prerequisites — storage and admin addresses |
