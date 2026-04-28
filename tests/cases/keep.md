# Keep Test Cases

Test keep flow behavior: todo triage, structural scanning, collection evaluation, and target suggestions.

---

## Todo triage

| # | Scenario | Expected behavior |
|---|---|---|
| K01 | A pending todo says "entity name may be incomplete" and the filesystem shows the entity folder already uses the fuller name | Mark complete — already resolved |
| K02 | A pending todo says "verify passport issue date" — the item is an image the agent can read | Read the image, verify the date, rename if wrong, mark complete |
| K03 | A pending todo says "verify which entity this belongs to" — requires user knowledge | Present to user with context and options, leave pending |
| K04 | A completed todo from a previous run | Skip — already resolved |

## Structural scanning

| # | Scenario | Expected behavior |
|---|---|---|
| K05 | Two files at the same location have identical MD5 hashes | Flag as duplicate, request consent to delete one |
| K06 | A folder named "Entity (1)" exists alongside "Entity" | Identify as sync artifact, merge contents if non-empty, remove the (1) folder |
| K07 | An empty folder exists that is not a structural folder (not a domain or category) | Remove it |
| K08 | An empty domain folder (e.g., Archive/John/Finance/ with no items) | Leave it — structural folder |
| K09 | A file has `.JPG` extension | Rename to `.jpeg` per naming convention |
| K10 | A receipt filename doesn't match the target naming format | Rename to conform, or create todo if content inspection needed |

## Collection evaluation

| # | Scenario | Expected behavior |
|---|---|---|
| K11 | A domain has 5 items from the same institution (e.g., 5 bank statements from First National) | Suggest forming a collection to the user via todo |
| K12 | A domain has 3 items from the same institution | Do not suggest — below 5-item threshold |
| K13 | Two collections exist for the same grouping (e.g., "First Natl" and "First National Bank") | Merge into one with the canonical short name, request consent (>5 items) |
| K14 | A Career domain has institution folders with 2-3 items each | Leave as-is — Career institution groupings are exempt from threshold |
| K15 | A target says "receipts flat in Receipts/" but vendor subfolders exist | Dissolve vendor subfolders into Receipts, request consent |

## Target suggestions

| # | Scenario | Expected behavior |
|---|---|---|
| K16 | Keep identifies all receipts in a location follow a consistent naming pattern not yet codified | Create a todo suggesting the pattern as a target |
| K17 | Keep identifies an inconsistent naming pattern across 50 items | Create a todo describing the inconsistency and suggesting a resolution, do NOT rename autonomously |
| K18 | Keep identifies a useful structural pattern (e.g., all health records could benefit from a "Lab Results" subfolder) | Create a todo suggesting it, do NOT create the subfolder |

## Multi-location awareness

| # | Scenario | Expected behavior |
|---|---|---|
| K19 | Entity "John" has projects in both the default cloud location and a local additional location | Recognize as the same entity across locations, scan both |
| K20 | A duplicate file exists across two locations for the same class | Flag as cross-location duplicate, request consent with location context |
