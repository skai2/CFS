# Naming

How to name files and folders in the CFS structure.

---

## General rules

- **Natural, readable names** — capitalize and space as you naturally would
- **No unsafe characters** — avoid `/ : * ? " < > |` (cross-platform hazard)
- **Preserve accents and diacritics** — use the correct spelling of names and words. Accents are not unsafe characters.
- **Name for findability** — use the name you would search for. Completeness serves findability only when the short form is ambiguous. "CV" over "Curriculum Vitae", "ID" over "Identification Document". Add detail only when it aids recognition or disambiguation.
- **Descriptive, not from source** — name what the item IS, not where it came from or its original filename
- **File extensions are mandatory and lowercase** — every file must have an extension. If the source has none, detect the file type and add it. Extensions are always lowercase. Use full modern forms (`.jpeg` not `.jpg`, `.html` not `.htm`)
- **Category-specific conventions override** these defaults when applicable (see below)

## Language

**Structural hierarchy uses the configured system language** (`language` in `config.yaml`). Storage classes, domains, and categories are named in the system language. When the system language is not English, translate the structural names accordingly.

**Item filenames use the document's own language.** During Step 1 (Understand), identify the document's language. The filename preserves that language regardless of the system language — a French invoice stays in French, a Japanese receipt stays in Japanese.

Examples with English system language and French document:
```
Archive/Jean Dupont/Finance/2024-10-31 - Facture EDF.pdf
```

Examples with French system language and French document:
```
Archives/Jean Dupont/Finances/2024-10-31 - Facture EDF.pdf
```

Examples with English system language and English document:
```
Archive/John Doe/Finance/2024-10-31 - Utility Invoice.pdf
```

## Entity names

- Identity names, not relationships: `John` not `My Brother`
- Use the shortest unambiguous name. First name if unique within the system. Add surname or detail only for disambiguation (two Johns → `John Doe`, `John Smith`).
- If a new entity creates ambiguity with an existing one, file the new item under a disambiguated name and create a todo proposing the rename of the existing entity folder. Renaming an existing entity folder requires user approval (see `refs/admin/safety.md` § User consent).

## Structural names (fixed, not user-renamed)

- Storage classes: `Archive`, `Library`, `Projects`
- Archive domains: `Identity`, `Finance`, `Health`, `Career`, `Clients`, `Assets`, `Legal`, `Events`
- Library categories: `Audio`, `Video`, `Images`, `Books`, `Games`, `Tools`

## Content extraction before naming

Never name from the original filename alone. Read the document content first. A file named with a cryptic abbreviation might be one type of document but actually contain another — the content determines the name, not the source filename.

## Archive

Date-prefixed descriptive names. Use the most specific meaningful date available: `YYYY` when only year is known, `YYYY-MM-DD` when day is known, `YYYY-MM-DD-HHmm` when time disambiguates or is inherently significant. Prefer the creation date — when the document was issued, signed, recorded, or transacted. When only derivative dates are available (expiry, renewal), infer the creation date if possible or use the best available date and log the uncertainty.

| Pattern | Example |
|---|---|
| `[date] - [Descriptive Name].[ext]` | `2024-10-31 - Utility Invoice.pdf` |
| `[date] - [Descriptive Name].[ext]` | `2025-03 - Blood Test Results.pdf` |

### Collection names

Collection names describe what the group contains, not just the grouping attribute. Follow the same descriptive, natural, language-aware principles as item names.

| Instead of | Use |
|---|---|
| `Acme Bank/` | `Acme Bank Statements/` |
| `2024 Tax/` | `2024 Tax Filings/` |
| `Corp Inc/` | `Corp Inc Receipts/` |
| `Gym/` | `Gym Receipts/` |

## Library

Library items follow established media conventions. These conventions create natural folder groupings from the first item — see `refs/storage/collections.md`.

### Audio

Follows MusicBrainz Picard / Plex / Jellyfin conventions.

| Type | Pattern | Example |
|---|---|---|
| Album | `Artist/Album (Year)/Track - Title.ext` | `Beethoven/Symphony No. 9 (1824)/01 - Allegro ma non troppo.flac` |
| Multi-disc | `Artist/Album (Year)/Disc-Track - Title.ext` | `Pink Floyd/The Wall (1979)/1-01 - In the Flesh.flac` |
| Compilation | `Various Artists/Album (Year)/Track - Artist - Title.ext` | `Various Artists/Soundtrack (2024)/01 - Artist - Song.flac` |
| Singleton | `Artist/Title.ext` | `Artist/Single Name.mp3` |

### Video

Follows Plex / Jellyfin / Kodi conventions.

| Type | Pattern | Example |
|---|---|---|
| Film | `Title (Year)/Title (Year).ext` | `Blade Runner (1982)/Blade Runner (1982).mkv` |
| Series | `Series (Year)/Season NN/Series - SNNENN - Episode Title.ext` | `The Wire (2002)/Season 01/The Wire - S01E01 - The Target.mkv` |
| Personal | `YYYY-MM-DD - Description.ext` | `2024-06-15 - Graduation Ceremony.mp4` |

### Images

Follows photographer / Lightroom conventions.

| Type | Pattern | Example |
|---|---|---|
| Event album | `YYYY/YYYY-MM-DD - Event/YYYYMMDD_HHMMSS.ext` | `2024/2024-06-15 - Tokyo Trip/20240615_143022.jpg` |
| Standalone | `YYYY-MM-DD - Description.ext` | `2024-03-20 - Product Screenshot.png` |

### Books

Follows Calibre conventions.

| Type | Pattern | Example |
|---|---|---|
| Book | `Author/Title (Year).ext` | `Isaac Asimov/Foundation (1951).epub` |
| Comic | `Series (Year)/Series #NNN (Year).ext` | `Batman (2016)/Batman #001 (2016).cbz` |
| Paper | `Author (Year) - Title.ext` | `Turing (1950) - Computing Machinery and Intelligence.pdf` |

### Games

| Type | Pattern | Example |
|---|---|---|
| ROM | `Platform/Title (Region).ext` | `Nintendo - SNES/Super Mario World (USA).sfc` |
| Other | Game name | `Witcher 3`, `Factorio` |

ROMs follow No-Intro naming conventions.

### Tools

Use the tool's official or commonly recognized name with natural spacing. Developer folder names often omit spaces — restore them.

| Pattern | Example |
|---|---|
| Official name with spacing | `Cheat Engine` (not `CheatEngine`) |
| Already natural | `rclone`, `Voicemeeter` |
| Known abbreviation | `ADB` (universally recognized) |
| Obscure abbreviation | `Logitech G Hub` (not `LGHUB`) |

## Projects

| Pattern | Example |
|---|---|
| Project name | `My App`, `Client API` |
