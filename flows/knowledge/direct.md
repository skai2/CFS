# Direct

Establish, change, or remove a user directive about what the knowledge layer should track and maintain. Log every execution per `refs/admin/logging.md`.

*Status: stub — to be drafted.*

## Scope

Knowledge-layer counterpart to the storage `rule` flow. Handles user-issued directives that govern what the knowledge graph keeps watch on and how it maintains its content — which entities to consistently track, which procedural templates to maintain, what observations to capture on recurring topics, how to handle specific concepts. Directives are user-only artifacts.

Out of scope:
- One-off encoding (use `encode`).
- Knowledge consolidation, link strengthening, or pruning (use `reflect`).

## Prerequisites

- Read `config.yaml` for knowledge layer paths.

## Input

- A user directive establishing, modifying, or removing a knowledge directive.

## Output

- Updated user-directive artifact under `{admin}/knowledge/`.
- Execution log in `{admin}/knowledge/logs/` (mandatory).
