# Sources

Source-specific interpretation rules for understanding, routing, and naming items from known origins. These rules are consulted by the file flow during understanding (Step 1) and may reference external sources defined in `config.yaml` `sources:` (by name) or ad-hoc paths.

---

## Format

Each entry describes a source location, what it contains, and how to interpret its items. Rules are a user-only artifact — only the user can create, modify, or remove them, directly or via AI assistance.

Each entry includes `created` and `updated` dates for orientation.

### Example rule

```markdown
### downloads (defined source) — receipts subfolder
(created: 2026-04-09, updated: 2026-04-09)

- Files prefixed `Company-` are business expenses. Route to the company entity, not the person.
- The `(YY-MM)` portion in filenames indicates billing reference period. Map to `(Ref YYYY-MM)`.
- The `$` followed by amount uses `+` as decimal separator. Map to `R$` with `.` decimal.
```

The header may be a defined-source name (e.g., `downloads`, `work-email`) or an ad-hoc path (e.g., `Archive/Person/Finance/Receipts (original location)`).

---

## Sources

*No source rules established yet.*
