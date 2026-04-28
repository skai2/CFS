# Update

Update the local CFS project clone to a newer upstream version with explicit preflight checks, impact review, and rollback capability. Never overwrite local customizations without explicit user approval. Log every execution per `refs/admin/logging.md`.

## Scope

Maintains the CFS project repository itself (flows, refs, docs, tools). This flow does not update user data in Archive/Library/Projects/Memory; it updates the CFS instructions and tooling that operate on that data.

Default strategy is conservative:
- Read-only preflight first.
- Fast-forward update only (no implicit merge/rebase).
- Explicit user confirmation before any mutating git operation.

## Prerequisites

- Access to the local CFS git repository.
- Access to the configured upstream remote (typically `origin`).
- Read `refs/admin/safety.md` for operational boundaries and escalation behavior.
- Read `BOOTSTRAP.md` for post-update bootstrap implications.

## Input

- Optional target reference (default: tracked upstream branch for current branch).
- Optional mode:
  - `check` (preflight + impact report only, no mutation)
  - `apply` (perform update if safe and approved)
  - `rollback` (return to pre-update checkpoint)

## Output

- Baseline snapshot: current branch, local HEAD commit, upstream target commit, dirty/divergence status.
- Update plan with risk classification and required approvals.
- If applied: repository updated to new commit (or explicitly aborted), plus post-update impact summary.
- If applied and accepted: active agent/session context refreshed by re-reading updated CFS entry files before continuing normal work.
- If rollback requested and approved: repository returned to checkpoint commit.
- Execution log in `{admin}/admin/logs/` (mandatory).

## Instructions

### Step 1: Baseline

**Objective:** Capture current repository state and establish a checkpoint anchor.

**Produces:** `before` snapshot (commit, branch, status, divergence, local modifications).

1. Inspect repository state: current branch, HEAD commit, remotes, tracking branch, clean/dirty working tree, staged/unstaged/untracked files, and local commits ahead/behind upstream.
2. Classify local modifications:
   - tracked edits (likely customizations),
   - untracked additions,
   - local commits not on upstream.
3. Record checkpoint data in the run context and log:
   - `before_sha`,
   - current branch,
   - tracking reference,
   - dirty/divergence summary.

### Step 2: Preflight safety gate

**Objective:** Determine whether update can proceed safely and what user decisions are required.

**Produces:** Safety verdict (`safe`, `requires_decision`, `blocked`) and required user prompts.

1. Hard-stop conditions (do not proceed automatically):
   - no git remote/tracking target resolvable,
   - unresolved conflicts in working tree,
   - local changes that would be overwritten by update.
2. Decision-required conditions:
   - dirty tree (tracked/untracked changes),
   - local commits ahead/diverged from upstream,
   - untracked files that may conflict with incoming paths.
3. For each non-safe condition, present what/why/risk and explicit options:
   - abort,
   - preserve customization first (commit/stash/patch/branch),
   - proceed with user-approved strategy.
4. If mode is `check`, stop after reporting verdict and recommendations.

### Step 3: Fetch and analyze incoming changes

**Objective:** Determine what would change and whether follow-up actions are likely required.

**Produces:** Impact report against `before_sha` and target upstream commit.

1. Fetch upstream refs (read-only to local content).
2. Compute candidate update range (`before_sha..target_sha`) and summarize:
   - commit list,
   - changed files,
   - high-impact paths.
3. Map changes to likely follow-ups:
   - `BOOTSTRAP.md` or procedural shape changes (`refs/knowledge/*`, `flows/knowledge/encode.md`, `flows/knowledge/reflect.md`) → likely bootstrap re-run review.
   - `config.example.yaml`, `refs/admin/addressing.md`, `flows/admin/setup.md` → config/addressing review.
   - `refs/admin/safety.md` → safety acknowledgment before next destructive maintenance flows.
   - `SKILL.md` or `flows/*` → behavior change review for active operations.
   - `tools/*` → tool setup/version review before tool use.
4. Present a concise plan: target commit, expected update method, detected risks, and post-update recommendations.

### Step 4: Confirm and checkpoint

**Objective:** Obtain explicit approval and create rollback metadata before mutating.

1. Ask for explicit confirmation to apply update with the proposed method.
2. Before mutation, ensure rollback anchor is explicit:
   - `before_sha` recorded,
   - branch name recorded.
3. If user declines, stop with no mutation.

### Step 5: Apply update (conservative strategy)

**Objective:** Update repository without implicit history rewrites.

1. Use fast-forward-only update on the current branch against its selected upstream target.
2. Do not auto-merge or auto-rebase during this flow.
3. If fast-forward is not possible, stop and report options (manual merge/rebase/cherry-pick path), then await user direction.
4. After apply, capture `after_sha` and resulting status.

### Step 6: Post-update verification and follow-ups

**Objective:** Confirm integrity and surface what the user should do next.

1. Verify repository is in expected state:
   - HEAD at `after_sha`,
   - no unexpected conflicts,
   - working tree status clearly reported.
2. Re-run impact mapping against actually applied range and produce:
   - what changed,
   - what may affect this user's setup,
   - suggested follow-up flow executions (e.g., bootstrap/setup checks).
3. If the user keeps the updated version, refresh runtime context in the current session before continuing:
   - re-read `SKILL.md` and any changed files relevant to upcoming operations (changed flows/refs/tools docs),
   - treat the refreshed files as authoritative for subsequent decisions in this session.
4. Ask user whether to keep this version or rollback to `before_sha`.

### Step 7: Rollback (optional, explicit)

**Objective:** Return to checkpoint when the updated version is not acceptable.

1. Rollback requires explicit user approval (it rewrites the project working copy state).
2. Before rollback, show what will be lost from the updated state.
3. Return HEAD to `before_sha` and verify status.
4. Report final commit and any remaining manual steps.

## Examples

### Example 1: Clean fast-forward update

Input: "Update CFS to latest."

Actions:
1. **Baseline** — branch tracks `origin/main`, tree clean, `before_sha` recorded.
2. **Preflight** — safe to proceed.
3. **Fetch and analyze** — upstream is 4 commits ahead; changed files include `BOOTSTRAP.md` and `SKILL.md`; bootstrap review suggested.
4. **Confirm** — user approves.
5. **Apply** — fast-forward succeeds.
6. **Post-update** — summary presented with recommendation to review bootstrap applicability.

Result: repository updated to latest upstream with clear follow-up actions.

### Example 2: Local customization detected

Input: "Update CFS."

Actions:
1. **Baseline** — tracked edits found in `flows/storage/file.md`.
2. **Preflight** — `requires_decision`; risk of overwrite.
3. **Fetch and analyze** — incoming changes also touch `flows/storage/file.md`.
4. **Confirm** — flow presents options (abort, preserve customization first, or proceed with explicit overwrite strategy).
5. User chooses abort.

Result: no mutation performed; customization preserved.

### Example 3: Apply then rollback

Input: "Update and keep only if no behavior changes."

Actions:
1. **Baseline/Preflight** — safe; checkpoint recorded.
2. **Apply** — fast-forward to `after_sha`.
3. **Post-update** — impact report shows safety policy changes; user prefers to defer adoption.
4. **Rollback** — with explicit approval, return to `before_sha`.

Result: repository restored to pre-update commit with logged rationale.

## Troubleshooting

**Working tree is dirty**
Cause: Uncommitted tracked or untracked local changes.
Solution: Stop and ask user whether to preserve first (commit/stash/patch/branch) or abort. Do not overwrite implicitly.

**Fast-forward not possible**
Cause: Local branch diverged from upstream or has local-only commits.
Solution: Stop and present explicit options; do not auto-merge/rebase in this flow.

**No upstream tracking branch**
Cause: Current branch has no configured remote tracking.
Solution: Ask user to specify target remote/branch, then rerun preflight.

**Update succeeded but behavior changed unexpectedly**
Cause: Upstream changed `SKILL.md`, flows, refs, or safety rules.
Solution: Use post-update impact report; if unacceptable, rollback to `before_sha`.

**Current session still behaves like old version after update**
Cause: The running agent/session is still using pre-update context.
Solution: Re-read `SKILL.md` and changed CFS files before proceeding; for harnesses with persistent cached context, start a fresh session.

## References

| Document | When to consult |
|---|---|
| `refs/admin/logging.md` | All steps — logging |
| `refs/admin/safety.md` | Steps 2, 4, 7 — operational boundaries and escalation |
| `BOOTSTRAP.md` | Steps 3, 6 — bootstrap-related change impact |
| `flows/admin/setup.md` | Step 6 — follow-up setup verification when config/addressing changed |
