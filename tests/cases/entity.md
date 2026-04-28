# Entity Test Cases

Test entity identification, the independence test, disambiguation, and naming.

---

## Independence test — passes (should be own entity)

| # | Input description | Expected entity type | Expected entity name | Rationale |
|---|---|---|---|---|
| E01 | An electricity bill for Riverside Apt, paid by John Doe | Property | Riverside | Bill persists with the property, not the owner |
| E02 | A tax payment for Acme Corp, paid from John's personal bank account | Organization | Acme | Company obligations persist regardless of owner |
| E03 | A vehicle registration renewal for John's car (VIN: ABC123) | Vehicle | Specific car name | Registration follows the vehicle across owners |
| E04 | A condominium fee for Riverside Apt | Property | Riverside | Fee follows the property |

## Independence test — fails (belongs to a person's entity)

| # | Input description | Expected entity | Expected domain | Rationale |
|---|---|---|---|---|
| E05 | A bank account statement for John at First National | John | Finance | Account ceases when closed |
| E06 | A Netflix subscription receipt for John | John | Finance | Subscription ceases when cancelled |
| E07 | A receipt for a toothbrush purchased by John | John | Finance | Purchase belongs to the buyer |
| E08 | A password manager export for John's accounts | John | Assets | Accounts are managed by the person |

## Entity disambiguation

| # | Scenario | Expected behavior |
|---|---|---|
| E09 | Filing a document for "John" when no entity named "John" exists yet | Create entity "John" |
| E10 | Filing a document for "John Smith" when entity "John" already exists and is the same person | File under existing "John" entity (findability — shortest unambiguous) |
| E11 | Filing a document for a DIFFERENT "John" when entity "John" already exists | Create "John Smith" for the new one, suggest renaming the existing "John" to disambiguate |
| E12 | Filing a document that reveals entity "John" 's full name is "John Alexander Doe" | File under "John" (no rename needed — first name is still unambiguous) |

## Entity naming — findability

| # | Input | Expected entity name | Rationale |
|---|---|---|---|
| E13 | A document for someone named Maria Garcia (only Maria in the system) | Maria | Shortest unambiguous — first name unique |
| E14 | A document for an organization named "Acme Corporation Ltd." | Acme | Shortest recognizable — no legal suffixes |
| E15 | A document for a property at "123 Riverside Drive, Apt 802" | Riverside (or similar short form) | Findable short name, not full address |
