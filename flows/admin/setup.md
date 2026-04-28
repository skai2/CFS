# Setup

First-time CFS setup or environment verification. Every step is idempotent — safe to re-run without overwriting or destroying existing data. Log every execution per `refs/admin/logging.md`.

## Scope

Initializes or verifies a CFS environment: configuration, storage scaffolding, admin files, capability confirmation, and optional periodic-flow scheduling.

## Prerequisites

- Access to the CFS project repository.
- `config.example.yaml` available as a template.

## Input

- A new environment with no existing CFS configuration.
- Or an existing environment needing verification or repair.

## Output

- `config.yaml` with user-configured backends and addresses.
- Directories created at configured addresses (only those enabled).
- Admin directory with per-section subsections: `admin/` (with `logs/`, `todo/`), `storage/` (with `logs/`, `todo/`, `sources.md`, `targets.md`), and, if knowledge is active, `knowledge/` (with `logs/`, `todo/`).
- Capabilities confirmed for each configured non-local backend (and any user-requested CFS-bundled tools installed).
- Periodic schedules wired for `reflect` and/or `keep` where the harness supports it (or noted as on-demand only).
- For local multi-harness environments, optional bootstrap performed per `BOOTSTRAP.md` (skill and procedural symlinks).
- Execution log in `{admin}/admin/logs/` (mandatory).

## Instructions

### Step 1: Configure

**Objective:** Ensure `config.yaml` exists and is complete.

1. If `config.yaml` exists, read and verify it. Do not overwrite.
2. If `config.yaml` does not exist, copy from `config.example.yaml`.
3. Inspect host signals (`hostname` / `uname -n`, `scutil --get LocalHostName`, `scutil --get ComputerName`, etc.) and propose a local backend declaration for this machine — a lowercase identifier-safe name plus a `match:` block of the inspected fields. Confirm the proposed name with the user; write the `type: local` backend entry to `backends:`. See `refs/admin/addressing.md` for the grammar. (Skip in environments with no local filesystem to declare — pure cloud workers.)
4. Prompt the user to decide:
   - Which layers to activate (`storage.active`, `knowledge.active`). At least one must be active.
   - Any remote backends to declare under `backends:` (gdrive, etc.). See `config.example.yaml` for the shape and `refs/admin/addressing.md` for the grammar. If a remote backend has a local sync mount on this machine, declare a `mirrors:` entry keyed to the local backend from the previous sub-step.
   - Storage addresses (Archive, Library, Projects, Unsorted) — only if storage layer is active.
   - Knowledge address (Memory) — only if knowledge layer is active.
   - Admin address — always required regardless of layer activation.
   - Any external sources to declare under `sources:` (read-only locations or services CFS may pull from for filing or encoding — downloads folder, email, calendar, etc.). Optional; can be added later. See `config.example.yaml` for the shape.
   - Default language.

### Step 2: Create structure

**Objective:** Create directory scaffolding at configured paths. Only create directories for active layers. Never delete or overwrite existing directories.

1. Read `config.yaml` for all configured addresses and backends.
2. Create directories by dispatching on address per `refs/admin/safety.md` § Backend dispatch.
3. **Admin** (always): create Admin directory and `admin/{logs,todo}/` and `storage/{logs,todo}/`. If knowledge is active, also create `knowledge/{logs,todo}/`.
4. **If storage is active**: create Archive, Library, Projects, and Unsorted directories at their default addresses. Also create directories for any additional named locations.
5. **If knowledge is active**: create Memory directory and the type subdirs (`Episodic/`, `Semantic/`, `Procedural/`).
6. Skip any directory that already exists.

### Step 3: Initialize admin files

**Objective:** Create base admin files if they don't exist. Never overwrite existing files.

1. If `storage/targets.md` does not exist under the Admin path, create it from `refs/_templates/targets.md`.
2. If `storage/sources.md` does not exist under the Admin path, create it from `refs/_templates/sources.md`.
3. If either file already exists, leave it unchanged and report its status.

### Step 4: Confirm capabilities

**Objective:** Confirm the agent has a capability for each configured non-local backend (per `refs/admin/safety.md` § Backend dispatch) and for each defined external source.

1. For each non-local backend in `config.yaml`, identify which capability will be used — agent-native, MCP, installed CLI, or a CFS-bundled reference implementation. Confirm with the user when ambiguous.
2. For each external source in `config.yaml` `sources:`, identify which capability resolves the source's scheme (filesystem, email, calendar, web, app-native MCP, etc.). Sources are read-only; missing capabilities are graceful — the agent will surface unresolved references and continue.
3. If the user wants to use a CFS-bundled tool, point them to `tools/README.md` for the catalog and per-tool setup. Bundled tools are opt-in and installed individually — only install what's needed for the chosen capabilities.
4. If a configured backend has no available capability and the user does not want to install a bundled option, stop and report — CFS cannot operate that backend. (External sources without capability are not blocking — they just become unresolvable.)

### Step 5: Confirm scheduling

**Objective:** Identify the scheduling capability available in the harness and offer to wire periodic flows. Optional — flows always work on-demand.

1. Identify what scheduling capability the harness offers — harness-native scheduler, OS scheduler (cron, launchd, Task Scheduler), agent platform routine, or none. Confirm with the user when ambiguous.
2. If a scheduling capability is available, suggest wiring periodic runs for the maintenance flows of each active layer:
   - `reflect` (knowledge layer, if active) — consolidates and strengthens the knowledge graph between active sessions. Cadence per the user's preference.
   - `keep` (storage layer, if active) — cleans drift, triages todos, processes recent changes. Cadence per the user's filing volume.
3. The user wires the schedule through their harness's mechanism; CFS does not store or manage scheduling state. Note the chosen cadence in the setup log for future reference.
4. If no scheduling capability is available, flag that these flows must be run on-demand and continue. This does not block setup.

### Step 6: Bootstrap (optional, local environments)

**Objective:** For environments where the user wants CFS visible across multiple agent harnesses (Claude Code, Cursor, Windsurf, Codex, Gemini CLI, etc.), establish symlinks from the canonical CFS clone and from each procedural skill into the harness skill paths.

1. If the user runs only one harness or doesn't want cross-harness loading, skip this step.
2. Otherwise, follow `BOOTSTRAP.md` at the project root — it lists known harness skill paths and the procedure to symlink (a) the CFS skill itself and (b) each procedural skill (`Memory/Procedural/<name>/`) into them. Optionally append a load-CFS instruction to home-dir agent files (`~/.claude/CLAUDE.md`, `~/AGENTS.md`, etc.) for guaranteed loading.
3. Bootstrap requires the canonical CFS to be at a local path (or accessible via a configured mirror entry for cloud-backed locations); procedural symlinks specifically need a `mirrors:` entry keyed to the active local backend if Memory is on a remote backend.
4. Bootstrap is idempotent — re-run after creating new procedural skills (per encode flow) or whenever symlinks need refresh.

### Step 7: Verify

**Objective:** Confirm the environment is ready for operation.

- `config.yaml` is complete with all required addresses and any non-local backends declared.
- All directories for active layers exist at their configured addresses.
- Admin sections present: `admin/` and `storage/` (always); `knowledge/` if active. Storage admin section contains `sources.md`, `targets.md`, `logs/`, `todo/`; admin and knowledge admin sections contain `logs/`, `todo/`.
- If knowledge is active, Memory contains the type subdirs `Episodic/`, `Semantic/`, `Procedural/`.
- Each configured non-local backend has a confirmed capability (or the user has accepted that it will not be operated).
- Periodic flows are scheduled or noted as on-demand only.
- `config.yaml` is gitignored and not committed (contains sensitive path information).
- Report any issues found.

## Troubleshooting

**config.yaml addresses point to nonexistent locations**
Cause: User specified addresses that don't exist yet or are misspelled.
Solution: Create the directories via the appropriate capability for the backend, or correct the addresses. Confirm with the user.

**Backend-prefixed address but backend not declared**
Cause: An address uses a scheme prefix (e.g., `gdrive:...`) but no matching entry exists under `backends:`.
Solution: Declare the backend in `config.yaml`, or change the address to use a declared backend.

**No capability available for a configured backend**
Cause: The agent has no native, MCP, CLI, or installable bundled option that speaks the backend's API in this environment.
Solution: Stop and report. CFS cannot operate the backend without a capability that satisfies the backend dispatch invariants in `refs/admin/safety.md`.

**Admin files already exist with content**
Cause: Re-running setup on an existing environment.
Solution: Do not overwrite. Report their status — they may contain user-defined targets and sources.

**Both layers set to inactive**
Cause: User disabled both storage and knowledge.
Solution: At least one layer must be active. Prompt the user to enable one.

## References

| Document | When to consult |
|---|---|
| `refs/admin/logging.md` | All steps — logging |
| `refs/admin/safety.md` | All steps — operational safety rules; Step 4 — backend dispatch and capability invariants |
| `refs/admin/addressing.md` | Step 1 — address grammar, backend declarations, match fields, mirrors |
| `config.example.yaml` | Step 1 — configuration template |
| `refs/_templates/targets.md` | Step 3 — targets file template |
| `refs/_templates/sources.md` | Step 3 — sources file template |
| `tools/README.md` | Step 4 — catalog of optional CFS-bundled tools and per-tool setup |
