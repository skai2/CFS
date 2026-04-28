# Logging

How to record operations and actionable items. Every flow execution must be logged.

---

## Location

Logs and todos live under per-section admin paths, resolved from the `admin:` field in `config.yaml`:

- **Admin flows** (setup, test) — `{admin}/admin/logs/` and `{admin}/admin/todo/`
- **Storage layer flows** (file, find, keep, rule) — `{admin}/storage/logs/` and `{admin}/storage/todo/`
- **Knowledge layer flows** (encode, recall, reflect, direct) — `{admin}/knowledge/logs/` and `{admin}/knowledge/todo/`

Create these directories if they don't exist.

## Filename convention

Log and todo filenames use a system-internal convention distinct from user-facing storage names: **lowercase, underscores bind words, hyphens separate components.** This applies to all CFS admin and project files (logs, todos, project source). Storage files in the user's filesystem use natural naming — see `refs/storage/naming.md`.

Specific filename formats are documented per type below.

## Logs

One log file per flow execution. Records what happened — decisions, observations, outcomes.

### Filename

```
YYYY-MM-DD-HHmm-[highest level]-[flow name].log
```

Examples:
```
2024-10-31-1430-warn-file.log
2024-11-02-0900-info-keep.log
2024-11-05-1015-error-file.log
```

Highest level is the most severe level recorded within the file: `info` < `warn` < `error`.

### Line format

```
YYYY-MM-DDTHH:MM:SS [level]: [description]
```

### Levels

| Level | When |
|---|---|
| `info` | Routine operations, decisions made, summaries |
| `warn` | Uncertainties, low confidence decisions, anomalies |
| `error` | Failures, items that couldn't be processed |

### Content guidance

Use judgment about detail level:

- **Uneventful operations** — brief summaries. Unit identified, routed, named, filed. One or two lines per unit.
- **Eventful operations** — full detail. What was found, what was unexpected, what decision was made and why, with paths and references.
- **Batch summary** — close every log with a summary line: units processed, warnings, errors.

### Sensitivity

Logs and todos handle sensitive personal data. They must not become a shadow knowledge base of extracted personal facts.

- **Default to minimal detail.** Record what happened and where, not what was in the document. Log the decision, not the content.
- **Never log extracted personal facts** — names, amounts, account numbers, tax IDs, medical details — unless essential for the actionability of a specific todo.
- **Reference items by path, not by content.** `Archive/Entity/Finance/2024-10-31 - Receipt.pdf` is sufficient. Do not quote or summarize document contents in log entries.
- **Todos should describe the issue and action needed**, not reproduce sensitive source material. "Entity name may be incomplete" is enough — do not include the candidate names.

### Example log

```
2024-10-31T14:30:01 info: Processing data context: 2 items from laptop_a:Downloads
2024-10-31T14:30:05 info: Unit 1/2: eDBV_2024.pdf
2024-10-31T14:30:08 info: Content extracted — customs declaration identified
2024-10-31T14:30:09 warn: Filename was misleading — routing and naming adjusted based on content
2024-10-31T14:30:10 info: Routed to Archive/[entity]/Finance
2024-10-31T14:30:11 info: Named per content and naming conventions
2024-10-31T14:30:12 warn: Entity name may be incomplete — fuller name found in content
2024-10-31T14:30:13 info: Todo created: entity_name_verification
2024-10-31T14:30:14 info: Filed to Archive/J Doe/Finance/2024-10-31 - Customs Declaration.pdf
2024-10-31T14:30:18 info: Unit 2/2: receipt_2024.pdf
2024-10-31T14:30:20 info: Content extracted — purchase receipt, J Doe, 2024-10-15
2024-10-31T14:30:21 info: Routed to Archive/J Doe/Finance, named: 2024-10-15 - Receipt.pdf
2024-10-31T14:30:22 info: Filed. No issues.
2024-10-31T14:30:25 info: Collection evaluation: 2 items in Archive/J Doe/Finance/ — below threshold.
2024-10-31T14:30:26 info: Batch complete. 2 units filed, 2 warnings, 0 errors.
```

## Todos

Separate from logs. Todos are actionable items that need attention — flagged for review, triage, redo, or user feedback.

### Filename

```
YYYY-MM-DD-HHmm-[pending|complete]-[descriptive_title].md
```

Examples:
```
2024-10-31-1430-pending-entity_name_incomplete_for_j_doe.md
2024-11-02-0900-pending-possible_misroute_insurance_claim.md
2024-11-05-1015-complete-entity_name_incomplete_for_j_doe.md
```

Status changes are reflected by renaming the file: `pending` → `complete`.

### Content

Free-form markdown with AI judgment. Always include:

- **Datetime** — when created
- **Source** — which flow and operation created it
- **Description** — what needs attention and why
- **Affected items** — paths to relevant files
- **Suggested next steps** — what to do about it

Update the content as the todo progresses — add resolution notes, decisions made, actions taken.

### Example todo

```markdown
# Entity Name Verification

Created: 2024-10-31T14:30
Source: file flow (flows/storage/file.md)

## Description

Content extraction revealed a fuller entity name than the one used for
the entity folder. Verification needed before renaming.

## Affected Items

- Archive/[entity]/Finance/ (and all items within)

## Suggested Next Steps

1. Review the source item to verify the correct full name
2. Rename entity folder if confirmed
3. Update any references to the old path
```

## When to create a todo

Not every warning needs a todo. Todos are for items that require human judgment or action beyond the current operation:

- Entity name needs verification or correction
- Item may be misrouted but agent isn't confident enough to re-route
- Content extraction failed and item needs re-evaluation
- Duplicate detected but unclear which version to keep
- User feedback needed on a routing or naming decision

Warnings that are fully resolved within the current operation (e.g., adjusted routing based on content extraction) are logged but don't need a todo.
