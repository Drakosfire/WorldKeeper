# World Keeper repository operating law

This repository is in **WK-5 CONSUMER COMPOSITION BOUNDARY — ACTIVE**.
The current checked-in authority says:

```text
IMPLEMENTATION: LIMITED AUTHORIZATION — WK-5 COMPOSITION ONLY
```

The custom-predicate compatibility amendment in the Steward anchor separately
authorizes only rehydrating DungeonMind V3 semantic profiles in the accepted
prepare/compile path and repinning the DungeonMind dependency. It does not
extend WK-5 into product mapping or a new lifecycle.

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

- WK-5 may expose the accepted prepare/commit lifecycle through a
  transport-neutral application protocol and a DungeonMind-backed composition
  root under `Docs/Plans/HANDOFF-wk5-consumer-composition-boundary-v1.md`.
- Do not add HTTP endpoints, World Keeper persistence, migrations, an agent
  harness, vector storage, automatic deduplication, or a second graph engine.
- Do not add prepared workflow persistence, a recovery ledger, confirmation
  bindings, HTTP, or durable identity allocation. WorldKeeper must not
  reproduce the V5.4 allocator. Product adapters remain later work.
- Do not redesign or duplicate prepare, commit, publication, recovery, or
  exact-child verification semantics. The runtime only wires accepted services.
- Do not copy DungeonMindBuddy modules wholesale. Classify current seams as product behavior, migration evidence, World Keeper responsibility, or DungeonMind responsibility before moving anything.
- A future implementation change must name the authority document and the explicit authorization that permits it.
- Before handing work back, run documentation-oriented checks, inspect the complete diff, and report the exact branch, commit, status, and unresolved questions.

## Execution policy

- An explicitly authorized handoff or implementation lease is execution authority for its stated scope. Execute it without asking for separate permission to begin.
- For an already-authorized handoff, editing, testing, committing, pushing, and opening or updating its pull request are ordinary completion steps. Do not ask for separate permission for those steps.
- A review request, review verdict, or pasted review is review-only unless it explicitly grants or references an active implementation lease; it does not authorize implementation by itself.
- If work reaches a stated scope or STOP condition, or requires broader authority, stop and report the blocker rather than broadening the lease.
- Merging a pull request is separate from opening or updating it and still requires explicit authorization.
