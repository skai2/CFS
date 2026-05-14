# Todo

Create, update, or close a CFS todo as a first-class operation. Provides the canonical procedure when a todo is invoked explicitly — by the user or by an agent outside another running flow. Log every execution per `refs/admin/logging.md`.

## Scope

Manages the lifecycle of items in `{admin}/<layer>/todo/`. Operates on CFS admin state only; never mutates user data in Archive, Library, Projects, or Memory.

**This flow is for explicit, out-of-band invocations.** Other flows (file, keep, rule, encode, reflect) continue to create todos inline as part of their own execution — they know their domain context best. Dispatch here when:

- The user asks to add, update, or close a todo by itself.
- An agent needs to capture a follow-up while not running another flow.
- A todo must cross flow boundaries (e.g., a knowledge concern raised mid-storage work) and the inline path doesn't fit.

When already inside another flow's execution, that flow's "create a todo" instructions take precedence — they carry the contextual fields specific to that domain.

## Prerequisites

- Read `config.yaml` for the `admin:` address.
- See `refs/admin/safety.md` § User consent — todos are admin state (self-managed); creating, updating, or closing them does not require user consent. Mutations on user data referenced by a todo still do.
- Read `refs/admin/logging.md` § Todos for filename format, required body fields, and sensitivity rules. This flow operationalizes that spec — it does not redefine it.

## Input

- **Mode** — one of: `create`, `update`, `close`. Inferred from the trigger verb when unambiguous (e.g., *"create a todo for X"* → create; *"close todo Y"* → close).
- **Subject** (create) — what the new todo concerns.
- **Reference** (update/close) — path, filename, or descriptive title locating the existing todo.
- **Layer** — `storage`, `knowledge`, or `admin`. Required for create; inferred from the existing todo's path for update/close.
- **Body content** (create) — description, affected items, suggested next steps, per `refs/admin/logging.md`.
- **Update content** (update) — what to append or refine.
- **Resolution** (close) — what was done OR why the todo is no longer relevant.

## Output

- New, modified, or renamed todo file under `{admin}/<layer>/todo/`.
- Execution log in `{admin}/admin/logs/` (mandatory).

## Instructions

### Step 1: Resolve mode and layer

**Objective:** Determine which operation to perform and which layer's todo directory to act on.

1. **Mode** — from the trigger verb. If ambiguous, ask.
2. **Layer** (create mode) — route by subject:
   - Concerns Archive / Library / Projects / Unsorted contents, routing, naming, sources, or targets → **storage**.
   - Concerns Memory nodes, links, knowledge consolidation, or promotion → **knowledge**.
   - Concerns CFS admin state itself (logs, todos about todos, the CFS clone) → **admin**.
   - If the subject straddles layers, pick where the action will land. When unclear, ask.
3. **Path** — resolve `{admin}` from `config.yaml`; the todo lives at `{admin}/<layer>/todo/`.
4. For update/close: locate the existing todo file. If the reference is ambiguous (multiple matches, vague title), surface candidates and ask.

### Step 2: Create

**Objective:** Write a new pending todo conforming to `refs/admin/logging.md`.

1. **Filename and body** — per `refs/admin/logging.md` § Todos. Source value for this flow is `todo flow (explicit invocation)`.
2. Write the file. Verify it exists at the resolved path.

### Step 3: Update

**Objective:** Append to or refine an existing pending todo without changing its status.

1. Read the existing todo.
2. Apply the update — typically appending dated notes, refining the Description or Affected items, or revising Suggested next steps as understanding evolves.
3. Do not rename the file. Status remains `pending`.
4. Write and verify.

### Step 4: Close

**Objective:** Mark a pending todo as no longer needing future action.

1. Locate the todo. Must be in `pending` state — if already `complete`, abort with a note.
2. Append a `## Resolution` section to the body, in one of two shapes:
   - **Resolved** — timestamp, action taken, outcome. Use when the work the todo described has been done.
   - **Obsolete** — timestamp, reason no longer relevant, and a pointer to the superseding todo or state if applicable. Use when the todo was overtaken by later events.
3. Rename the file: replace `-pending-` with `-complete-`. No other parts of the filename change.
4. Verify the new filename exists and the old one does not.

### Step 5: Log

**Objective:** Record what happened.

Write a log per `refs/admin/logging.md` § Logs noting mode, layer, and the affected todo filename. For a single-action invocation, a few lines suffices.

## Examples

### Example 1: Create out of band

Input: *"Add a todo to revisit the X cost projection in two weeks — we're waiting on a vendor quote."*

Actions:
1. **Resolve** — mode=create; layer=knowledge (the projection lives in a decision-tracking node).
2. **Create** at `{admin}/knowledge/todo/YYYY-MM-DD-HHmm-pending-revisit_x_cost_projection.md` with description noting the awaiting quote and a suggested next step ("compare quoted price against the projection; update the relevant node if material").
3. **Log**.

Result: explicit todo captured; the next reflect run will surface it.

### Example 2: Close after acting (resolved)

Input: *"Close the entity-rename todo — done, folder renamed."*

Actions:
1. **Resolve** — mode=close; layer=storage; locate the matching pending todo.
2. **Close** — append Resolution (timestamp, action taken: "renamed entity folder"; outcome: "references updated, wikilinks resolve"), rename file from `-pending-` to `-complete-`.
3. **Log**.

Result: todo closed with audit trail; future scans see it as `complete`.

### Example 3: Close as obsolete

Input: *"Cancel that old reingest todo — the refresh replaced it."*

Actions:
1. **Resolve** — mode=close; layer=storage; locate the older pending todo.
2. **Close** — append Resolution (timestamp, "superseded by the refreshed todo at <new filename> which carries current scope and validated subset"), rename to `-complete-`.
3. **Log**.

Result: stale todo retired with provenance preserved.

## Troubleshooting

**Subject straddles layers**
Cause: A finding touches both a storage item and a knowledge node.
Solution: Pick the layer where the action will land. If actions are split across layers, create one todo per layer and cross-reference them in body notes.

**Existing todo not found by reference**
Cause: Reference is ambiguous, layer guess is wrong, or the todo is already `-complete-`.
Solution: List candidates by filename and ask. Never modify a `-complete-` todo to back-fill state; if reopening is intended, create a new pending todo that references the closed one.

## References

| Document | When to consult |
|---|---|
| `refs/admin/logging.md` | All steps — filename format, required fields, sensitivity rules |
| `refs/admin/safety.md` | Step 1 — todos are self-managed admin state; user-data mutations referenced by a todo still require consent when acted on |
| `refs/admin/addressing.md` | Step 1 — resolving `{admin}` and referencing affected items |
| `config.yaml` | Step 1 — `admin:` address |
| Inline-creating flows (`file`, `keep`, `rule`, `encode`, `reflect`) | When already inside one of these, prefer its inline todo guidance over dispatching here |
