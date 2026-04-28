# Develop

Work on the CFS project itself. For project contributors — not part of the runtime skill. Follow this flow before making changes.

## Scope

Covers all development work on CFS: design changes, documentation, refs, flows, tools, and code.

## Prerequisites

- Read `SKILL.md` — project entry point, orientation, operations overview.
- Read `docs/spec.md` — full design specification (Principles, then the Part relevant to your task).
- Read the relevant `refs/` document if your task involves routing, naming, domains, categories, or collections.

If this is your first session on the project, also:

- Explore the project structure — `ls` the directories, read file headers, understand what exists and where.
- Run `bash dev/setup.sh` to install the project's pre-commit hooks (secrets detection, PII scan, Python lint/format, commit message convention). Requires `pre-commit` on `PATH` — install via `pip3 install pre-commit` or `brew install pre-commit`.

Do not skip this. CFS is a design-heavy project where decisions are interconnected. Changes made without understanding the design context risk contradicting established principles or duplicating resolved decisions.

## Input

- A task or change request — from the user, from a todo, or self-identified during review.

## Output

- Committed changes to the CFS project repository.
- Updated `docs/spec.md` if design decisions changed.

Git history is the audit trail; develop runs do not log to user admin paths.

## Instructions

### Step 1: Plan

**Objective:** Understand the task and determine the approach.

1. Identify which layer the task affects: storage (Part I), knowledge (Part II), operation (Part III), or the project itself.
2. Check `docs/spec.md` Open Questions for known unresolved tensions.
3. If the task involves a design decision, discuss before implementing.

Follow the three CFS principles:

- **Simplicity first** — don't add structure, complexity, or abstraction beyond what the task requires.
- **Opinionated by design** — make decisions with reasoning, don't create optionality where a clear choice exists.
- **Durability over features** — prefer plain text, standard formats, and approaches that outlast tools.

### Step 2: Implement

**Objective:** Make the changes following CFS conventions.

Guidelines by document type:

**Refs** — self-contained, single-purpose, tight. No rationale, no history — just rules and examples.

**Flows** — complete operational procedures. Follow `refs/_templates/flow.md` for structure. Reference refs, don't duplicate them.

**Spec** — design rationale. Why decisions were made, what influenced them, what's unresolved. It explains; refs and flows operationalize.

**Tools** — minimal utilities that support the flows. Plain text inputs and outputs. No dependencies on specific AI providers or platforms.

Don't duplicate content across documents. Reference instead.

### Step 3: Commit

**Objective:** Create well-structured commits with clear rationale.

Follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**

| Type | When |
|---|---|
| `feat` | New feature or capability |
| `fix` | Bug fix or correction |
| `docs` | Documentation changes |
| `refactor` | Restructuring without changing behavior |
| `chore` | Maintenance, cleanup, dependencies |
| `test` | Adding or updating tests |

**Scope** — use the affected area when helpful: `docs(spec)`, `refs(routing)`, `flows(file)`, `feat(tools)`.

**Guidelines:**
- Subject line — imperative mood, lowercase, no period, under 72 characters.
- Body — explain WHY, not just what. Link to relevant design decisions or open questions.
- One concern per commit — don't bundle unrelated changes.

Pre-commit hooks run automatically on each commit — secrets detection, PII scanning, Python linting, and commit convention enforcement. If a hook fails, fix the issue and re-commit.

### Step 4: Review

**Objective:** Verify changes are consistent and complete before pushing.

- Verify changes are consistent with `docs/spec.md` principles and design decisions.
- Verify refs remain self-contained (no cross-dependencies between ref docs).
- Verify no PII in any committed file (pre-commit hooks catch structured PII automatically, but review for names and contextual PII manually).
- Run `git diff` and review your own changes.

If your changes affect the design (not just implementation), update `docs/spec.md` to reflect the decision.

For significant changes to flows, refs, or routing logic, consider running `flows/admin/test.md` (the test flow) to validate against test cases.

## Examples

### Example 1: Documentation change

```
docs(spec): clarify events domain coherence principle

The events domain was identified as the broadest archive domain in
external review. Added explicit "experiential documentation" framing
and tightened boundary rules with neighboring domains.
```

### Example 2: New flow

```
feat(flows): draft file flow

Complete filing workflow covering external and internal items.
References routing, naming, domains, categories, and collections refs.
```

### Example 3: Bug fix

```
fix(refs): correct insurance routing in domains.md

Health insurance policy was ambiguously described. Clarified that
the policy document routes to legal, not health.
```

## References

| Document | When to consult |
|---|---|
| `refs/admin/safety.md` | All steps — operational safety rules; changes to safety itself start here |
| `SKILL.md` | Step 1 — project orientation |
| `docs/spec.md` | Steps 1, 4 — design rationale and principles |
| `refs/_templates/flow.md` | Step 2 — flow structure standard |
| `dev/setup.sh` | Prerequisites — install pre-commit hooks |
