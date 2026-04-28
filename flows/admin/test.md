# Test

Run CFS test cases to validate flows, refs, and routing logic. Log every execution per `refs/admin/logging.md`.

## Scope

Executes test cases from `tests/cases/` against the CFS skill. Each test case is run by an isolated agent that receives only the skill entry point and the test input — no expected answers, no conversation history.

## Prerequisites

- CFS project repository available.
- Ability to spawn subagents or separate context windows.

## Input

- All test cases in `tests/cases/`, or a specific test file.
- Mode: **skill** (default — agents receive SKILL.md) or **baseline** (agents receive only mock paths, no skill).

## Output

- Pass/fail result per test case.
- Summary score per category.
- Detailed report of any failures (expected vs actual).
- Execution log in `{admin}/admin/logs/` (mandatory).

## Instructions

### Step 1: Verify isolation capability

**Objective:** Confirm the runner can execute tests with proper isolation.

Before running any tests, verify you can spawn separate agents (subagents, new context windows, or separate terminals) that:
- Receive only `SKILL.md` as the entry point
- Receive the test input (item description, scenario)
- Have access to the mock config and filesystem at `tests/_mock/`
- Do NOT receive test case definitions or expected answers

If you cannot spawn isolated agents, **stop and report this limitation.** Do not proceed with tests in the same context — results would be meaningless.

### Step 2: Confirm environment

**Objective:** Verify the mock environment is correct and confirm with the user before proceeding.

1. Read `tests/_mock/config.yaml` and report all configured paths.
2. Verify the mock directories exist (Archive, Library, Projects, Admin).
3. Verify mock admin files exist (targets.md, sources.md).
4. Present the environment summary to the user or orchestrating agent and ask for confirmation before proceeding. Do not assume the environment is correct — it may have been modified.

### Step 3: Load test cases

**Objective:** Read and parse all test cases.

1. Read test files from `tests/cases/`.
2. Parse each case: input description, expected outcomes, category.
3. Count total cases per category for scoring.

### Step 4: Execute tests

**Objective:** Run each test case in an isolated agent.

For each test case:

**Skill mode** (default):
1. Spawn a fresh agent with:
   - `SKILL.md` path (the CFS project's SKILL.md)
   - Explicit instruction: "Use `tests/_mock/config.yaml` as your config — do not look for config.yaml at the project root"
   - The test input (item description and any scenario context)
   - The operation to perform (file, find, keep, etc.)
   - Instruction to report decisions without executing (dry-run — describe what you would do, do not copy or modify files)

**Baseline mode** (for performance comparison):
1. Spawn a fresh agent with:
   - NO SKILL.md, NO refs, NO flows, NO admin files
   - Only the mock storage paths: "Archive at `tests/_mock/system/Archive`, Library at `tests/_mock/system/Library`, Projects at `tests/_mock/system/Projects`"
   - The test input and a generic instruction: "Organize this item into the appropriate folder"
   - Instruction to report decisions without executing (dry-run)
   - Explicit constraint: "Do not read or explore any files in this repository. Use only the storage paths and information provided in this prompt. Do not look for documentation, configuration files, or reference materials."
   - The agent must work within the mock paths — do not create folders outside them

In both modes:
2. Collect the agent's reported decisions (entity, domain, category, filename, location, etc.).
3. Do not share expected outcomes with the test agent.

### Step 5: Compare and score

**Objective:** Compare each agent's decisions against expected outcomes.

For each test case:
- **Pass:** all expected fields match the agent's decisions.
- **Fail:** one or more expected fields differ. Record expected vs actual.

Scoring:
- **Strict fields** (must match exactly): storage class, entity, domain/category, location.
- **Flexible fields** (must contain key terms): filename (check for required components, not exact string).

### Step 6: Report

**Objective:** Present results clearly.

Report format:
```
## Test Results — [date]

### Summary
- Total: N cases
- Passed: N
- Failed: N
- Score: N%

### By category
- Routing: N/N
- Naming: N/N
- Entity: N/N
- Safety: N/N
- Keep: N/N

### Failures (if any)
[Case name]: expected [X], got [Y]

### Baseline comparison (if baseline mode was run)
| Category | With CFS | Without CFS | Improvement |
|---|---|---|---|
| Routing | N% | N% | +N% |
| Naming | N% | N% | +N% |
| Entity | N% | N% | +N% |
| Safety | N% | N% | +N% |
```

## Troubleshooting

**Cannot spawn isolated agents**
Cause: Agent harness doesn't support subagents or separate contexts.
Solution: Stop and report. Tests cannot be run without isolation. The user may need to run test agents manually.

**Test agent doesn't follow the skill**
Cause: Test agent didn't read SKILL.md or skipped flow steps.
Solution: Ensure the spawn instruction explicitly directs the agent to read SKILL.md first. If persistent, flag the specific case.

**Non-deterministic results**
Cause: Agent produces different naming or phrasing across runs.
Solution: Use flexible matching for naming fields. Strict matching only for routing decisions (class, entity, domain). If a case fails intermittently, flag it as non-deterministic.

## References

| Document | When to consult |
|---|---|
| `refs/admin/safety.md` | All steps — operational safety rules |
| `refs/admin/logging.md` | All steps — logging |
| `tests/cases/` | Step 2 — test case definitions |
| `tests/_mock/` | Step 3 — mock environment |
