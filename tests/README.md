# Tests

CFS test system — validates flows, refs, and routing logic against declarative test cases.

## Structure

```
tests/
  cases/          Test case definitions (routing, entity, naming, safety, keep, find)
  _mock/          Isolated mock environment for test agents
    config.yaml   Points to mock paths (not real storage)
    source/       Test input items (placeholder files)
    system/       Mock CFS storage structure
      Archive/
      Library/
      Projects/
      Admin/      Mock admin state — per-section subsections
        admin/      logs/, todo/
        storage/    sources.md, targets.md, logs/, todo/
        knowledge/  logs/, todo/
```

## Running tests

Follow `flows/admin/test.md`. The test flow:

1. Verifies isolation capability (can spawn separate agent contexts)
2. Reads test cases from `cases/`
3. Spawns a fresh agent for each case with only:
   - `SKILL.md` as the entry point
   - `tests/_mock/config.yaml` as the config path
   - The test input description
4. Compares the agent's decisions against expected outcomes
5. Reports pass/fail per case and category

## Important

- Each test agent must run in a **separate context** — no access to expected answers.
- The runner passes `tests/_mock/config.yaml` explicitly to each test agent.
- Test agents should be instructed to use the provided config path, not look for a root-level config.yaml.
