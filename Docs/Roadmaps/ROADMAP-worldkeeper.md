# Roadmap — WorldKeeper

**Status:** WK-1 through WK-5 complete; V3 compatibility merged
**Implementation:** no active implementation lease

## Accepted history

- **WK-0:** repository boundary and authority bootstrap accepted.
- **WK-1:** transport-neutral application contracts accepted.
- **WK-2:** read-only DungeonMind-backed in-process boundary proof accepted.

The earlier contracts remain historical evidence for safety properties such as
same-transaction reference resolution and exact child verification. They do not
authorize a WorldKeeper durable-ID allocator or recovery ledger.

## Accepted prerequisite — DungeonMind prospective publication

DungeonMind V5.4 now accepts one semantically resolved publication containing prospective creates and
dependent references, allocate durable identities exactly once, substitute
them consistently, publish one immutable child atomically, honor expected-parent
and idempotency semantics, resolve lost responses durably, and return
prospective/client-operation-to-durable-result mappings.

The accepted owning-boundary proof covers validation-before-head-advance,
failure preserving the prior head, retry replay, and exact result read-back.

The completed prerequisite handoff is recorded in
`Docs/Plans/HANDOFF-dungeonmind-prospective-publication-prerequisite-v1.md`.

## WK-3 — Prepare World change

**State:** COMPLETE / `WK_3_PREPARE_WORLD_CHANGE_ACCEPTED`.

WK-3 implements non-mutating semantic interpretation, exact parent and
authority binding, source/evidence admissibility, and complete local-reference
resolution against the DungeonMind publication contract.

## WK-4 — Commit prepared change and verify exact child

**State:** COMPLETE / `WK_4_COMMIT_AND_VERIFY_ACCEPTED`.

WK-4 coordinates commit of an intact prepared value through DungeonMind V5.4,
independently verifies the exact immutable child, and returns a WorldKeeper-owned
verified receipt. HTTP, persistence,
migrations, agent harnesses, vector storage, automatic dedupe, and generic
reconciliation remain outside this bootstrap unless separately authorized.

## WK-5 — Consumer composition boundary

**State:** COMPLETE / PR #7 merged as
`8a5efb96b69dc9ca136288ecc80f67c1ed027bd1`.

WK-5 exposes the accepted prepare and commit lifecycle through one generic
application protocol and one DungeonMind-backed in-process composition root.
Product integration, transport, persistence, source admission, and new write
semantics remain unauthorized.

## Bounded V3 custom-predicate compatibility

PR #8 preserved the accepted DungeonMind V3 profile through prepare/compile
and proved exact authored `entity_ref` relationship predicates through commit
and child read-back. Reviewed head
`49a8620f066ce7ef8972a699020c012f50af9158` merged as
`a0a70db275cf6c5f3876fe7b4d2a557de12388f5`. This did not authorize a
V2-to-V3 migration or a new implementation lane.
