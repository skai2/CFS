# Routing Test Cases

Test that the file flow routes items to the correct storage class, entity, and domain/category.

---

## Archive routing — Identity domain

| # | Input description | Expected class | Expected entity | Expected domain |
|---|---|---|---|---|
| R01 | A scanned passport for John Doe, issued 2019 | Archive | John | Identity |
| R02 | A digital driver's license for John Doe, issued 2022 | Archive | John | Identity |
| R03 | A birth certificate for John Doe | Archive | John | Identity |
| R04 | A voter registration card for John Doe | Archive | John | Identity |
| R05 | A vehicle registration document for John's car | Archive | John's car (or similar) | Identity |

## Archive routing — Finance domain

| # | Input description | Expected class | Expected entity | Expected domain |
|---|---|---|---|---|
| R06 | A bank statement for John Doe from First National Bank, January 2024 | Archive | John | Finance |
| R07 | A tax filing receipt for John Doe, 2023 fiscal year | Archive | John | Finance |
| R08 | A payment receipt from a restaurant, paid by John Doe, $85.50 | Archive | John | Finance |
| R09 | A business expense receipt for accounting services, paid by Acme Corp. Source file is prefixed `CORP-` | Archive | Acme | Finance |
| R10 | An electricity bill for Riverside Apt, paid by John Doe. Source file is prefixed `PROP-` | Archive | Riverside | Finance |

## Archive routing — Health domain

| # | Input description | Expected class | Expected entity | Expected domain |
|---|---|---|---|---|
| R11 | An MRI scan report for John Doe, lumbar spine, dated 2023-05-18 | Archive | John | Health |
| R12 | A prescription for medication for John Doe, from Dr. Smith | Archive | John | Health |
| R13 | A dental x-ray for John Doe | Archive | John | Health |

## Archive routing — Career domain

| # | Input description | Expected class | Expected entity | Expected domain |
|---|---|---|---|---|
| R14 | John Doe's CV in English, updated 2024 | Archive | John | Career |
| R15 | A university transcript from State University for John Doe | Archive | John | Career |
| R16 | A professional certification in project management for John Doe | Archive | John | Career |
| R17 | An employment recommendation letter for John Doe from a former manager | Archive | John | Career |

## Archive routing — Assets domain

| # | Input description | Expected class | Expected entity | Expected domain |
|---|---|---|---|---|
| R18 | A warranty document for John Doe's laptop purchased in 2023 | Archive | John | Assets |
| R19 | A 2FA recovery key for John Doe's cloud service account | Archive | John | Assets |
| R20 | A WhatsApp chat backup export (zip file) for John Doe | Archive | John | Assets |

## Archive routing — Career domain (relationship-centric)

| # | Input description | Expected class | Expected entity | Expected domain |
|---|---|---|---|---|
| R24 | An employment contract for John Doe at Acme Corp | Archive | John | Career |

## Archive routing — Clients domain

| # | Input description | Expected class | Expected entity | Expected domain |
|---|---|---|---|---|
| R47 | A service contract between Acme Corp and client BigCo | Archive | Acme | Clients |
| R48 | A monthly invoice issued by Acme Corp to client BigCo | Archive | Acme | Clients |
| R49 | A proposal from Acme Corp for a potential engagement with BigCo | Archive | Acme | Clients |
| R50 | A freelancer's (John Doe, sole proprietor) service log for client work | Archive | John | Clients |

## Archive routing — Legal domain

| # | Input description | Expected class | Expected entity | Expected domain |
|---|---|---|---|---|
| R21 | A rental lease agreement for John Doe's apartment, signed 2023 | Archive | John | Legal |
| R22 | A health insurance policy document for John Doe | Archive | John | Legal |
| R23 | A property purchase contract for Riverside Apt. Binding agreement between buyer and seller. | Archive | Riverside | Legal |

## Archive routing — Events domain

| # | Input description | Expected class | Expected entity | Expected domain |
|---|---|---|---|---|
| R25 | A flight itinerary for John Doe's trip to Tokyo, July 2024 | Archive | John | Events |
| R26 | Concert tickets for a music festival, purchased by John Doe | Archive | John | Events |
| R27 | An airline loyalty program membership card for John Doe | Archive | John | Events |

## Library routing

| # | Input description | Expected class | Expected category |
|---|---|---|---|
| R28 | An MP3 album by Artist Name — 12 tracks in a folder | Library | Audio |
| R29 | A movie file (MKV) — "Film Title (2023)" | Library | Video |
| R30 | A TV series episode — "Series Name S01E01" | Library | Video |
| R31 | A personal photo album from a vacation — folder of JPEGs | Library | Images |
| R32 | An ebook (EPUB) — "Book Title" by Author Name | Library | Books |
| R33 | A comic book (CBZ) — "Series Name #001 (2020)" | Library | Books |
| R34 | A game ROM — Super Mario World (USA).sfc | Library | Games |
| R35 | A portable application — rclone binary with documentation | Library | Tools |

## Projects routing

| # | Input description | Expected class | Expected entity |
|---|---|---|---|
| R36 | A git repository for a web application being built by John Doe | Projects | John |
| R37 | A design workspace (Figma project files) for Acme Corp client work | Projects | Acme |
| R38 | A data analysis environment (Jupyter notebooks) for John's personal project | Projects | John |

## Cross-cutting routing

| # | Input description | Expected entity | Expected domain | Rationale |
|---|---|---|---|---|
| R39 | A health insurance POLICY document for John | John | Legal | Binding instrument about entity itself, not health info |
| R40 | A health insurance claim PAYMENT receipt for John | John | Finance | Money moved |
| R41 | Medical test RESULTS for John from the insurance claim | John | Health | Health information |
| R42 | A diploma from State University for John | John | Identity | Academic credential (formal identity) |
| R43 | Coursework folder from State University for John | John | Career | Educational material — relationship with institution |
| R44 | A family vacation photo album | — | — (Library/Images) | Content value, not administrative |
| R45 | Active planning for an upcoming trip (itinerary drafts, booking research) | John | — (Projects) | Active time-bound work |
| R46 | A settled past trip itinerary (trip already happened) | John | Events | Settled experience documentation |
| R51 | An employment contract for John at Acme Corp | John | Career | Relationship-centric — trajectory through Acme |
| R52 | A client contract between Acme Corp and client BigCo | Acme | Clients | Relationship-centric — trajectory with client |
| R53 | Acme Corp's own articles of incorporation | Acme | Legal | Entity's own legal standing, not a relationship |
| R54 | Acme Corp's health insurance policy for employees | Acme | Legal | Entity's own insurance, not a client relationship |
