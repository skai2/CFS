# Find

Retrieve items from the CFS storage layer. Log every execution per `refs/admin/logging.md`.

## Scope

Handles retrieval by specific query, by category/criteria, or by exploratory browsing. Read-only — find never modifies the storage layer.

## Prerequisites

- Read `config.yaml` for storage layer addresses and backend declarations. See `refs/admin/addressing.md` for the grammar and `refs/admin/safety.md` § Backend dispatch for how to operate on each — note that a remote backend's mirror, where declared, may lag the authoritative source.

## Input

- A query from the user: a specific item description, a category or criteria to filter by, or a browsing goal.

## Output

- Located item(s) with their full path(s) and relevant context.
- Execution log in `{admin}/storage/logs/` (mandatory).

## Instructions

### Step 1: Understand the query

**Objective:** Determine what the user is looking for and what kind of search is needed.

**Produces:** Search type (specific, filtered, exploratory) and known attributes (entity, domain, category, date range, keywords).

1. Identify what's being sought — a specific item, a set of items matching criteria, or a general browse.
2. Extract known attributes from the query: entity name, domain, category, date range, content type, keywords.
3. If the query is ambiguous, ask the user for clarification.

### Step 2: Narrow

**Objective:** Identify the most likely location(s) in the storage structure.

**Produces:** One or more target paths to search.

1. `refs/storage/routing.md` — use the decision tree in reverse to narrow the search. If the entity is known, go directly to their folder. If the domain or category is known, narrow further.
2. Inspect the storage across all configured locations for the class (default + additional). See `refs/storage/routing.md` multi-location awareness.
3. If the location cannot be narrowed, prepare for a broad search across all storage locations.

### Step 3: Search

**Objective:** Find matching items at the target location(s).

**Produces:** List of matching items with paths.

1. For specific items — look for exact or near matches by name, date, or content type.
2. For filtered searches — list items matching the criteria (date range, keyword in filename, content type).
3. For exploratory browsing — present the structure and contents of the target location, with item counts and summaries.
4. If initial results are insufficient, broaden the search to parent or sibling locations.

### Step 4: Present

**Objective:** Return results with useful context.

1. List matched items with full paths.
2. For each item, provide relevant context: date, entity, domain/category, filename.
3. If many results, summarize by grouping (by date, by type, by subfolder) and let the user drill down.
4. If no results, suggest alternative locations or broader search terms.

## Examples

### Example 1: Specific item

Input: "Find my passport"

Actions:
1. **Understand** — specific item search. Known attributes: identity document, likely the user's entity.
2. **Narrow** — Archive / [user's entity] / Identity.
3. **Search** — look for files matching "passport" in the Identity folder.
4. **Present** — `Archive/John Doe/Identity/2019-05-27 - Passport.pdf` found.

Result: Item located with path.

### Example 2: Filtered search

Input: "Show me all Acme Corp receipts from March 2026"

Actions:
1. **Understand** — filtered search. Entity: Acme Corp. Domain: Finance/Receipts. Date range: 2026-03.
2. **Narrow** — Archive / Acme Corp / Finance / Receipts.
3. **Search** — filter items with `2026-03` date prefix.
4. **Present** — 8 receipts found, listed with payee and amount from filenames.

Result: Filtered list returned.

### Example 3: Exploratory browse

Input: "What do I have filed for Riverside Apt?"

Actions:
1. **Understand** — exploratory browse. Entity: Riverside Apt.
2. **Narrow** — Archive / Riverside Apt.
3. **Search** — list all domains and items under the entity.
4. **Present** — Finance/Receipts: 6 items (5 electricity bills, 1 condominium fee).

Result: Entity overview with structure and counts.

## Troubleshooting

**Entity not found**
Cause: Entity name in the query doesn't match any existing entity folder.
Solution: List existing entities and suggest the closest match. Entity names may differ from how the user refers to them.

**Too many results**
Cause: Broad query matching many items.
Solution: Summarize by grouping and ask the user to refine. Don't dump hundreds of filenames.

**Item expected but not found**
Cause: Item may be filed under a different entity, domain, or name than expected.
Solution: Broaden the search. Check sibling domains, other entities, or search by content keywords across the storage layer.

## References

| Document | When to consult |
|---|---|
| `refs/admin/safety.md` | All steps — operational safety rules |
| `refs/storage/routing.md` | Step 2 — understanding storage structure for narrowing |
| `refs/storage/entities.md` | Step 2 — entity identification |
| `refs/admin/logging.md` | All steps — logging |
| `config.yaml` | Prerequisites — storage addresses and backends |
