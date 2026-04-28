# Collections

When and how to group items into collections.

---

## What is a collection

A collection is a folder at the same level as individual items, containing related items. Collections are the final structural layer — items within collections are flat.

## Library convention-driven grouping

Library categories use naming conventions that create natural folder groupings from the first item (e.g., `Artist/Album`, `Series/Season`, `Author/Title`). These convention-driven groupings are not subject to the threshold below — they form immediately as dictated by `refs/storage/naming.md`.

The rules below apply primarily to **archive domains** and to library items that fall outside convention-driven patterns.

## When to create a collection

During filing, evaluate:

1. **Does an existing collection match this item?** → Add to it (filing is copy-only; no existing item is moved).
2. **No match, but are there 4+ existing items that share a grouping attribute with this item?** → File the new item flat at its class location. Create a todo proposing collection formation with the canonical name and the moves needed for the existing peers — moving existing user-data items requires user approval (see `refs/admin/safety.md` § User consent). The `keep` flow processes the todo.
3. **Neither** → File as an individual item.

## What counts as a grouping attribute

Collections group items that share one of:

- **Institutional source** — all statements from one bank, all records from one hospital
- **Temporal cluster** — all tax documents for one year, all receipts from one trip
- **Recurring administrative category** — all utility bills, all pay stubs from one employer

**The test:** would this grouping help someone browsing the container find related items faster?

**What does NOT justify a collection:**
- Grouping by file format (all PDFs together)
- Grouping by vague topic (all "important" things)
- Grouping that would leave only 1-2 items outside the collection (just use flat)

## Examples

```
Archive/John Doe/Finance/
  Acme Bank Statements/                    ← collection (institutional source)
    2024-01 - Statement.pdf
    2024-02 - Statement.pdf
    2024-03 - Statement.pdf
    2024-04 - Statement.pdf
    2024-05 - Statement.pdf
  2024-10-31 - Utility Invoice.pdf         ← individual item (no pattern yet)

Library/Audio/
  Beethoven/                               ← convention-driven (artist folder)
    Symphony No. 5 (1808)/
      01 - Allegro con brio.flac
    Symphony No. 9 (1824)/
      01 - Allegro ma non troppo.flac
```

Collection naming follows `refs/storage/naming.md` — descriptive, complete, language-aware. The name describes what the group contains, not just the grouping attribute.
