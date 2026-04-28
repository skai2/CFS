# Categories

The 6 content categories for the library.

---

## Resolution question

**What kind of content is this?** Type-based, not topic-based. A music video's primary content type is Video. A podcast transcript is Books (published written work). When ambiguous, the primary sensory modality or consumption mode determines the category.

## Category definitions

### Audio
Sound content consumed or created.

Contains: music, podcasts, audiobooks, recordings, sound effects.

Unit examples: an album folder, a podcast episode, a voice memo.

### Video
Moving image content consumed or created.

Contains: movies, TV shows, personal recordings, clips, anime.

Unit examples: a movie file, a season folder, a home video.

### Images
Still visual content consumed or created.

Contains: photos, art, screenshots, wallpapers, diagrams.

Unit examples: a photo event album (folder), an art collection, individual image files.

### Books
Published written works consumed for reference or reading.

Contains: ebooks, comics, papers, articles, reference publications.

Unit examples: an epub, a PDF textbook, a comic series folder.

### Games
Interactive entertainment — played, not just consumed.

Contains: video games, tabletop games, board games, mods, saves, game data.

Unit examples: a game folder with saves/configs/mods, a ROM file, a tabletop PDF.

Internal structure is opaque — CFS organizes to the game unit, not inside it.

### Tools
Functional software — used to accomplish tasks.

Contains: portable applications, utilities, scripts, personal automations, AI skills.

Unit examples: a portable app folder, a script file, a skill definition folder.

Internal structure is opaque — CFS organizes to the tool unit, not inside it.

## Scope

CFS manages what the user personally curates:
- Tools: portable apps, scripts, automations. NOT system-installed software, NOT package-managed dependencies.
- Games: curated files (ROMs, standalone games, tabletop PDFs, save archives). NOT platform-managed installs (Steam, GOG).

## Carrier vs. concept

Three categories are carrier-based (Audio, Video, Images — by sensory modality). Three are concept-based (Books, Games, Tools — by what the content is). When a file could go either way (e.g., a music video), the primary content type determines the category.
