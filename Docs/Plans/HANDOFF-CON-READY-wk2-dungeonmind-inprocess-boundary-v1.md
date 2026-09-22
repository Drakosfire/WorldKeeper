# Handoff — WK-2 DungeonMind-backed in-process reference boundary

**Status:** ACTIVE LIMITED IMPLEMENTATION LEASE
**World Keeper base:** `f3126e1d4f486599503e8ebacabb73f3d6242a3b`
**DungeonMind authority:** `1fc03aa21e406d9a7cb07d0e4792e202fe281375`

## Authorized scope

WK-2 may establish an importable, transport-neutral Python package with a
World Keeper-owned read-only governed-authority seam and a DungeonMind
in-process adapter. It may prove exact head and revision reads, source/revision
correlation, finalized-publication evidence reads, World Keeper-owned witness
types, and the absence of adapter writes.

The adapter may use DungeonMind repositories and graph readers internally. It
must not expose DungeonMind DTOs as its public seam or duplicate graph, source,
identity, publication, or persistence authority.

## Explicit exclusions

This lease does not authorize `prepare_change`, `commit_prepared_change`, World
Keeper recovery orchestration, confirmation binding implementation, prepared
workflow persistence, semantic intent compilation, prospective identity
planning, HTTP, a database, migrations, Buddy integration, or live-world
mutation. DungeonMind writes are permitted only in test fixture setup needed to
construct real downstream state.

## Required proof

- An exact revision remains readable after the DungeonMind head advances.
- Source revision/artifact mismatch fails closed.
- Finalized-publication reads return terminal parent-to-child evidence.
- Runtime adapter tests prove that no DungeonMind mutation method is called.
- Tests, lint, and type checks run against the exact pinned DungeonMind SHA.

The steward anchor, architecture, lifecycle design, and versioned contracts
remain higher authority. WK-3 and WK-4 require separate authorization.
