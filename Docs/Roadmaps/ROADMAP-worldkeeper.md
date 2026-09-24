# Roadmap — WorldKeeper

**Status:** WK-1 and WK-2 accepted; DungeonMind V5.4 accepted; WK-3 active
**Implementation:** limited authorization — WK-3 prepare only

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

**State:** ACTIVE / PREPARE-ONLY IMPLEMENTATION AUTHORIZED.

WK-3 implements non-mutating semantic interpretation, exact parent and
authority binding, source/evidence admissibility, and complete local-reference
resolution against the DungeonMind publication contract.

## WK-4 — Commit prepared change and verify exact child

**State:** NAMED SUCCESSOR / NOT AUTHORIZED.

Commit coordination, verified receipts, and product integration follow only
after WK-3 is accepted. HTTP, persistence,
migrations, agent harnesses, vector storage, automatic dedupe, and generic
reconciliation remain outside this bootstrap unless separately authorized.
