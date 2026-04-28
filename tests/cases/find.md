# Find Test Cases

Test find flow behavior: query understanding, location narrowing, search, and presentation.

---

## Specific item search

| # | Query | Expected behavior |
|---|---|---|
| F01 | "Find my passport" | Narrow to user's entity / Identity. Locate passport file(s). Present with path. |
| F02 | "Find the Riverside electricity bill from March" | Narrow to Riverside entity / Finance / Receipts. Filter by date and "electricity". |
| F03 | "Find Acme Corp's accounting receipts" | Narrow to Acme entity / Finance / Receipts. Filter by "accounting". |

## Filtered search

| # | Query | Expected behavior |
|---|---|---|
| F04 | "Show me all receipts from January 2024" | Search Receipts across all entities. Filter by 2024-01 prefix. |
| F05 | "List all items filed for Riverside" | Browse Riverside entity. List all domains and items. |
| F06 | "What legal documents do I have?" | Search Legal domain across all entities. List items. |

## Exploratory browsing

| # | Query | Expected behavior |
|---|---|---|
| F07 | "What entities exist in the system?" | List all entity folders across all Archive and Projects locations. |
| F08 | "Show me the structure of my Career domain" | Browse user's entity / Career. Present subfolders, item counts. |
| F09 | "How many receipts does each entity have?" | Count items in Finance/Receipts across all entities. Present summary. |

## Multi-location search

| # | Query | Expected behavior |
|---|---|---|
| F10 | "Find all of John's projects" | Search Projects across all configured locations (default + additional). Present results with location context. |
| F11 | "Is there a duplicate of this file anywhere?" | Search across all locations for all classes. Check by name and content hash. |

## Edge cases

| # | Query | Expected behavior |
|---|---|---|
| F12 | "Find my passport" but no passport exists | Report not found. Suggest checking Identity domain or searching by different terms. |
| F13 | "Find documents from 2019" (broad, could match many) | Summarize by entity/domain rather than listing hundreds of files. |
