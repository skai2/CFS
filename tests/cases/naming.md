# Naming Test Cases

Test naming conventions: findability, dates, language, extensions, accents, and format compliance.

---

## General naming — findability

| # | Input description | Expected name contains | Should NOT contain |
|---|---|---|---|
| N01 | John Doe's Curriculum Vitae in English | `CV` | `Curriculum Vitae` |
| N02 | A Power of Attorney document | `POA` | `Power of Attorney` |
| N03 | A document about Value Added Tax | `VAT` | `Value Added Tax` |
| N04 | An Identification Document | `ID` | `Identification Document` |
| N05 | John Doe's passport | `Passport` (or local-language equivalent if document is non-English) | — |

## Date prefix — creation date preference

| # | Input description | Source filename | Expected date prefix | Rationale |
|---|---|---|---|---|
| N06 | A passport that expires in 2029, issued 2019-05-27 | `2029 Passport.jpg` | `2019-05-27` | Creation/issue date, not expiry |
| N07 | A driver's license expiring 2027, issued 2022-01-15 | `2027 License.pdf` | `2022-01-15` | Issue date from content |
| N08 | A bank statement for January 2024, generated Feb 1 | `Statement Jan 2024.pdf` | `2024-01` | Period date, not generation date |
| N09 | A tax filing for fiscal year 2023, filed April 2024 | `Tax 2024.pdf` | `2023` | Fiscal year is the relevant date |
| N10 | An item with only an expiry date visible, standard 5-year validity | `2028 Card.jpg` | `2023` (inferred) | Inferred creation date, logged as warning |

## Language-aware naming

| # | Input description | Document language | System language | Expected filename language |
|---|---|---|---|---|
| N11 | A French invoice | French | English | French (document language) |
| N12 | A Japanese passport | Japanese | English | Japanese (document language) |
| N13 | An English employment contract | English | English | English |
| N14 | A German tax document | German | German | German |

## File extensions

| # | Input | Expected extension | Rationale |
|---|---|---|---|
| N15 | A file with no extension, detected as PNG | `.png` | Extension mandatory, detected and added |
| N16 | A file with `.JPG` extension | `.jpeg` | Lowercase, modern full form |
| N17 | A file with `.jpg` extension | `.jpeg` | Modern full form |
| N18 | A file with `.PDF` extension | `.pdf` | Lowercase |
| N19 | A file with `.HEIC` extension | `.heic` | Lowercase |

## Accents and diacritics

| # | Input description | Expected name contains | Should NOT contain |
|---|---|---|---|
| N20 | A French document referencing "café" | `café` | `cafe` |
| N21 | A German document referencing "Köln" | `Köln` | `Koln` |
| N22 | A Spanish document referencing "España" | `España` | `Espana` |

## Receipt naming format (per targets)

| # | Input description | Expected filename pattern |
|---|---|---|
| N23 | Personal electricity payment, $112.56, from utility company, ref period March 2024 | `YYYY-MM-DD - John - Utility - $112.56 - (Ref 2024-03) Electricity.[ext]` |
| N24 | Business accounting payment, $440, Acme Corp paying Accountant Co, ref Dec 2024 | `YYYY-MM-DD - Acme - Accountant - $440 - (Ref 2024-12) Accounting.[ext]` |
| N25 | Personal purchase, no ref period, bought a laptop for $1299.99 | `YYYY-MM-DD - John - None - $1299.99 - Laptop.[ext]` |
| N26 | Payment where payee is unknown, amount $500 | `YYYY-MM-DD - John - None - $500 - [Detail].[ext]` |
