# Bootstrap

Optional setup for local environments where you want CFS reliably loaded across one or more agent harnesses on the same machine. CFS is a skill — it works wherever the environment provides a skill loader, including cloud workers, sandboxed agents, and read-only filesystems where bootstrap is either impossible or pointless. Skip bootstrap entirely in those cases.

Two outcomes, achievable independently:

1. **Activation** — make CFS load on every session, silently and without depending on the harness's skill router to decide.
2. **Multi-harness** — make the same CFS clone (and any user-defined procedural skills) loadable from every harness installed on the machine.

CFS does not ship a script. Bootstrap is a procedure described here — the agent or user follows it using whatever filesystem capability is available (shell, native APIs, etc.). Per CFS philosophy: describe what, not how.

## When to bootstrap

- **Local environment, single harness, want guaranteed activation:** Step 2 (home-dir append) alone is enough.
- **Local environment, multiple harnesses on the same machine:** Step 1 (per-harness symlinks) plus Step 2 if you want guaranteed activation. Step 3 (procedural symlinks) if you have user-defined skills to expose.
- **Cloud worker, sandboxed agent, or static / read-only filesystem:** skip bootstrap entirely. The platform's skill mechanism handles loading; trying to bootstrap is impossible (no symlink permissions, immutable home dir) or pointless (no other harnesses, no shared filesystem).
- **Single harness whose skill router already loads CFS reliably:** Step 1 may be sufficient; Step 2 just makes activation deterministic.

## Prerequisites

- CFS project clone at a local, stable path (e.g., `~/Repos/<entity>/cfs/` per CFS's projects-local convention). This becomes the canonical source for any symlinks.
- Filesystem capability for symlink creation (Unix-like: `ln -s` natively; Windows: developer mode or admin).
- Write access to home-dir agent files (for Step 2).

## Known harness skill paths

CFS does not maintain an exhaustive list — paths change as harnesses evolve. Below are paths known to discover skills as of v1; verify against your harness's current docs:

| Harness | Skill discovery path |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Cursor | `~/.cursor/skills-cursor/` (note: not `skills/`) |
| Windsurf | `~/.windsurf/skills/` |
| Codex CLI | `~/.codex/skills/` |
| Gemini CLI | `~/.gemini/skills/` (varies by version; some installs lack skill discovery) |
| Kiro | `~/.kiro/skills/` |
| Generic | `~/.skills/`, `~/.agents/`, `~/.agent/` |

Skip any that don't exist on the machine. Do not create harness directories that the user hasn't installed — that's pollution.

## Procedure

### Step 1: Symlink the CFS skill (discovery)

Makes CFS *findable* by the harness's skill loader. Run for each harness in which you want CFS available.

1. If a CFS entry already exists at `<harness-path>/cfs/`, check whether it's the canonical clone, an older copy, or a stale symlink. Confirm with the user before replacing.
2. Create a symlink: `<harness-path>/cfs/` → `<canonical-clone-path>/`.
3. Verify the symlink resolves and the harness can read `SKILL.md` through it.

The CFS skill at the canonical path is the single source of truth. Updating the clone (git pull) updates every harness instantly.

### Step 2: Append load-CFS instruction to home-dir agent files (activation)

Makes CFS *load* on every session, regardless of whether the harness's skill router would pull it in by description match. The most reliable activation mechanism in any local environment that lets you write to home-dir agent files. Skip when those files are managed elsewhere or read-only.

Known home-dir agent instruction files (verify per harness):

| Harness | File |
|---|---|
| Claude Code | `~/.claude/CLAUDE.md` |
| Generic / multi-agent | `~/AGENTS.md` |
| Gemini | `~/.gemini/GEMINI.md` |
| Cursor | `~/.cursor/rules.md` (varies by version) |

For each file the user wants to update:

1. Check whether a CFS section already exists between the markers below. If so, replace its contents (idempotent re-run); otherwise append.
2. Use markers so re-runs don't duplicate:

```markdown
<!-- CFS-bootstrap -->
## CFS — Cognitive File System

Silently load the `cfs` skill at session start and consult it on every turn per its operating rhythm. Do not announce loading or summarize the skill — absorb the instructions and operate. See `cfs/SKILL.md`.
<!-- /CFS-bootstrap -->
```

3. Confirm with the user before modifying any home-dir file. These are personal configuration; bootstrap proposes, user approves.

### Step 3: Symlink procedural skills (multi-harness, optional)

Exposes user-defined procedural skills (`Memory/Procedural/<skill-name>/`) to every installed harness in the open Skills format, so each is independently loadable. Independent of CFS itself — only relevant when the knowledge layer is active and contains procedural skills.

**Per-step prerequisite:** the knowledge layer's Memory address must resolve to a local path on this machine — either Memory is on the active local backend, or Memory is on a remote backend with a `mirrors:` entry keyed to the active local backend. Without one of these, procedural symlinks can't resolve to real files. See `refs/admin/addressing.md`.

For each procedural directory in `Memory/Procedural/`:

1. Resolve the procedural's local path. If Memory is on a remote backend, use the mirror entry whose key matches the active local backend to resolve to the local sync path.
2. For each known harness skill path that exists:
   - If a symlink with the same name already exists, check whether it points at the current procedural directory. If stale, replace.
   - Create a symlink: `<harness-path>/<skill-name>/` → `<procedural-local-path>/<skill-name>/`.
3. Verify the symlink resolves and the harness can read `SKILL.md` inside.

After creating new procedural skills (via the `encode` flow), re-run bootstrap to expose them. The `reflect` flow includes a maintenance task to surface stale or missing procedural symlinks.

### Step 4: Verify

- Each created symlink resolves to a real file or directory.
- The home-dir append (if performed) appears between the CFS-bootstrap markers.
- The harness lists and can load CFS (and any procedural skills) — verify by invoking the harness if possible.

## Re-running

Bootstrap is idempotent. Re-run when:

- A new procedural skill is created (per `encode` flow).
- A procedural is renamed, merged, or removed (per `reflect` flow consolidation).
- The canonical CFS clone moves to a new path.
- A new harness is installed and the user wants CFS exposed to it.
- The home-dir snippet text changes (e.g., updated activation instructions); markers ensure idempotent replacement.

`reflect`'s Step 5 surfaces procedural symlink currency — when reflect flags a stale or missing symlink, re-run bootstrap.

## What bootstrap does NOT do

- It does not modify the canonical CFS clone or the procedural skill content.
- It does not fetch from cloud — symlinks rely on existing local filesystem access.
- It does not enumerate every possible harness — keep this document updated as new harnesses gain skill conventions.
- It does not run on every CFS session — it's a one-time setup step (per machine, per harness change).
- It does not apply to cloud, sandboxed, or read-only environments — those load CFS via the platform's native skill mechanism.

## Troubleshooting

**Symlink creation fails on Windows.**
Cause: Symlink creation requires elevated privileges or developer mode.
Solution: Enable Developer Mode in Settings, or run with admin rights.

**Procedural symlinks point at non-existent paths.**
Cause: Memory is on a remote backend without a matching mirror for the active local backend, or the configured mirror path is not synced.
Solution: Add a `mirrors:` entry on the relevant backend keyed to the active local backend (see `refs/admin/addressing.md`), ensure the sync client has populated the path, then re-run.

**Harness doesn't see the symlinked CFS skill.**
Cause: Some harnesses cache skill discovery; restart the harness after bootstrap.
Solution: Restart the harness; verify by listing available skills.

**Stale symlinks after a procedural rename or removal.**
Cause: Bootstrap was last run before the rename/removal.
Solution: Re-run bootstrap. Old symlinks will be replaced or pruned.
