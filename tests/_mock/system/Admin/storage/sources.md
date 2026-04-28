# Sources

Source-specific interpretation rules for understanding, routing, and naming items from known origins.

---

## Format

Each entry describes a source location, what it contains, and how to interpret its items.

Each entry includes `created` and `updated` dates for orientation.

---

## Sources

### Test source batch (tests/_mock/source)
(created: 2026-04-10, updated: 2026-04-10)

- Files prefixed `CORP-` are business expenses for Acme Corp. Route to the Acme Corp entity, not the individual. Beneficiary: "Acme".
- Files prefixed `PROP-` are property expenses for Riverside Apt. Route to the Riverside entity. Beneficiary: "Riverside".
- All other files are personal items for John Doe. Route to the John entity.
