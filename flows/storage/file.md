# File

File an item into the CFS storage layer. All operations on source material are non-destructive — read or copy only, never move, rename, or delete regardless of origin. Log every execution per `refs/admin/logging.md`.

## Scope

Handles both external items and internally created items.

## Prerequisites

- Read `config.yaml` for storage layer addresses, backend declarations, and any defined external sources (`sources:`). See `refs/admin/safety.md` § Backend dispatch for the rule on how to operate on each, and § Source protection — external sources are pull-only, never mutated.

## Input

- A named source from `config.yaml` `sources:` (e.g., "process my downloads") — agent resolves the source's address and pulls items.
- An ad-hoc filepath, folder, or download — pulled directly.
- Internal items: agent-generated content, conversation artifacts.
- One or more items may be provided at once (a data context).
- If no source is specified, check the `storage.unsorted` address in `config.yaml` for pending items.

## Output

- Filed item(s) at their target location(s) in the storage layer.
- Items removed from unsorted after filing (if sourced from `storage.unsorted`).
- Execution log in `{admin}/storage/logs/` (mandatory).
- Todos in `{admin}/storage/todo/` for any unresolved uncertainties.

## Instructions

### Step 1: Understand

**Objective:** Determine what each item is, who or what it belongs to (if applicable), its language, and its context.

**Produces:** For each unit — item type, entity (for Archive/Projects), language, key facts.

Identify discrete units within the input — each unit goes through steps 1–6 independently. Unit boundaries may shift during this step; when they do, reassess and adjust before continuing.

Never file based on the original filename alone.

1. `{admin}/storage/sources.md` — check for source-specific interpretation rules before reading the item.
2. Read the item directly — using whatever extraction capability is needed for the format (some complex binary formats may require a capability beyond agent-native).
3. If unreadable, fall back to context: filename, path, extension, surrounding files. Log the uncertainty.
4. If still unclear, create a todo for user review. Do not research externally — filing handles sensitive personal data that must not leave the local system.

### Step 2: Route

**Objective:** Determine the primary filing location within the CFS scaffold.

**Produces:** Storage class and target path (e.g., Archive/Entity/Domain, Library/Category, Projects/Entity/Project).

1. `refs/storage/routing.md` — follow the decision tree for storage class, entity, and domain or category.
2. `{admin}/storage/sources.md` — overrides routing when applicable, including location directives (which named location within a class).
3. `config.yaml` — resolve the address. If a source directive specifies a named location, use its address. Otherwise, use the class default.

### Step 3: Locate

**Objective:** Determine the final destination within the routed location.

**Produces:** Exact target address for filing.

1. Inspect the storage at the target — check for existing subfolders and collections.
2. `{admin}/storage/targets.md` — targets directing items to specific subfolders override filesystem structure.
3. Check for duplicates — if a true duplicate exists, do not file. If a new version, file both. Err towards versioning.

### Step 4: Name

**Objective:** Determine the correct filename.

**Produces:** Final filename with extension.

1. `refs/storage/naming.md` — general conventions. Structural hierarchy uses the system language, item filenames use the document's language.
2. Peers — examine similar or related items at the final location. Conform to their naming pattern.
3. `{admin}/storage/targets.md` — established naming patterns override peers and general conventions.

If no guidance exists from any source, decide a pattern based on content and context. Future items will use this as a peer reference.

### Step 5: File

**Objective:** Copy the item to its target location.

1. Dispatch on the target address per `refs/admin/safety.md` § Backend dispatch.
2. Create the destination folder if it doesn't exist.
3. Copy the item.

### Step 6: Verify

**Objective:** Confirm the filing is correct and flag any issues.

After filing each unit:

- **Consistency** — verify items landed correctly. No split folders or sync conflict artifacts (e.g., `(1)` suffixed duplicates).
- **Entity completeness** — did content reveal a fuller entity name? Create a todo if needed.
- **Misroutes** — did this item reveal a previously filed item is in the wrong location? Create a todo.

## Examples

### Example 1: Scanned document with misleading filename

Input: A PDF in `laptop_a:Downloads` named `vacc_2024.pdf`.

Actions:
1. **Understand** — read the PDF. The cryptic filename suggests a vaccination card; content reveals a customs declaration. Language: French. Entity: J. Doe.
2. **Route** — settled record → Archive / J Doe / Finance (import duty = money moving).
3. **Locate** — inspect `Archive/J Doe/Finance/`. No subfolders, no duplicates.
4. **Name** — no rules or peers. Name from content: `2024-10-31 - Déclaration en Douane.pdf`.
5. **File** — copy to `Archive/J Doe/Finance/2024-10-31 - Déclaration en Douane.pdf`.
6. **Verify** — full name "John Doe" found in content. Create todo for entity name verification.

Result: Content extraction changed entity, routing, and filename versus the original.

### Example 2: Music albums from a single folder

Input: A folder `laptop_a:Downloads/Beethoven_Symphonies/` with two symphony albums in FLAC.

Actions:
1. **Understand** — two albums, two discrete units. Process each independently.
2. **Route** — curated media → Library / Audio.
3. **Locate** — inspect `Library/Audio/`. No existing `Beethoven/` folder.
4. **Name** — audio convention per `refs/storage/naming.md`: `Beethoven/Symphony No. 5 (1808)/` and `Beethoven/Symphony No. 9 (1824)/`.
5. **File** — copy each album to `Library/Audio/Beethoven/...`.
6. **Verify** — no issues.

Result: Two units filed from one data context.

## Troubleshooting

**Content unreadable**
Cause: Unsupported format, corrupted file, or image without extractable text.
Solution: Fall back to context cues (filename, path, extension, surrounding files). Log as warning, create a todo for user review. Do not research externally.

**Routing ambiguous**
Cause: Item serves multiple purposes (e.g., health insurance policy — health or legal?).
Solution: File by primary purpose. Consult `refs/storage/domains.md` for boundary rules.

**Entity name unknown or incomplete**
Cause: Content doesn't contain a full proper name.
Solution: Use best available name. Create a todo for verification — corrections are allowed.

**Package broken into individual files**
Cause: A multi-file unit (repo, album, app folder) was split during processing.
Solution: Route and name the root folder as one item. Internal structure is preserved.

**Duplicate or suffixed folders**
Cause: Sync conflict between local filesystem and cloud API operations.
Solution: File into the correct folder. Create a todo proposing the merge-and-remove for the duplicate — cleanup of existing content requires approval and is handled by keep.

## References

| Document | When to consult |
|---|---|
| `refs/admin/safety.md` | All steps — operational safety rules |
| `refs/storage/routing.md` | Step 2 — filing location |
| `refs/storage/naming.md` | Step 4 — naming conventions |
| `refs/admin/logging.md` | All steps — logging |
| `{admin}/storage/sources.md` | Steps 1, 2 — source interpretation and routing |
| `{admin}/storage/targets.md` | Steps 3, 4 — established patterns |
| `config.yaml` | Prerequisites — storage addresses and backends |
