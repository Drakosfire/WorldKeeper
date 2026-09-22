# World Keeper repository operating law

This repository is in **DESIGN / REPOSITORY BOOTSTRAP**. The current checked-in authority says:

```text
IMPLEMENTATION: NOT AUTHORIZED
```

## Authority and pickup

- Begin with `Docs/Steward/STEWARD-ANCHOR-worldkeeper.md` and follow its pickup order.
- The steward anchor outranks architecture; architecture outranks the boundary; the boundary outranks lifecycle design; versioned contracts outrank the roadmap; historical/source material is evidence only.
- Do not treat DungeonMindBuddy implementation details or a chat handoff as World Keeper authority. Use `Docs/Sources/SOURCE-INDEX-worldkeeper.md` to record what an external source proves and what it does not prove.
- Keep unresolved design questions explicitly unresolved. A missing decision is a stop condition, not an invitation to invent a schema or endpoint.

## Correctness invariants

- World Keeper interprets application intent; DungeonMind owns durable World truth.
- Prepare is non-mutating and binds an exact interpreted change to an exact World parent and source/evidence context.
- Confirm publishes only that prepared meaning. A changed proposal, changed authority, or stale parent fails closed or requires re-prepare.
- Transaction-local references are scoped to one prepared intent, unique, and resolved completely before publication.
- Identity similarity is advisory. Automatic identity merging is not authorized by this bootstrap.
- A successful write includes exact child-revision read-back; a successful HTTP response alone is not proof of durable truth.
- Reads do not mutate interpretation or identity, and projections do not repair writes.

## Work restrictions

- Do not add runtime service code, HTTP endpoints, persistence, migrations, an agent harness, vector storage, automatic deduplication, or a second graph engine during bootstrap.
- Do not copy DungeonMindBuddy modules wholesale. Classify current seams as product behavior, migration evidence, World Keeper responsibility, or DungeonMind responsibility before moving anything.
- A future implementation change must name the authority document and the explicit authorization that permits it.
- Before handing work back, run documentation-oriented checks, inspect the complete diff, and report the exact branch, commit, status, and unresolved questions.
