# Roadmap — WorldKeeper

**Status:** WK-1 and WK-2 accepted; WK-3 blocked on DungeonMind prerequisite
**Implementation:** WK-3 not authorized

## Accepted history

- **WK-0:** repository boundary and authority bootstrap accepted.
- **WK-1:** transport-neutral application contracts accepted.
- **WK-2:** read-only DungeonMind-backed in-process boundary proof accepted.

The earlier contracts remain historical evidence for safety properties such as
same-transaction reference resolution and exact child verification. They do not
authorize a WorldKeeper durable-ID allocator or recovery ledger.

## Next prerequisite — DungeonMind prospective publication

This is the next implementation slice, below WorldKeeper. DungeonMind must
accept one semantically resolved publication containing prospective creates and
dependent references, allocate durable identities exactly once, substitute
them consistently, publish one immutable child atomically, honor expected-parent
and idempotency semantics, resolve lost responses durably, and return
prospective/client-operation-to-durable-result mappings.

The owning-boundary proof must cover validation-before-head-advance, failure
preserving the prior head, retry replay, and exact result read-back. If the
implementation belongs in DungeonMind, this repository supplies the decision
and pointer; it does not implement that primitive here.

The concrete follow-on is recorded in
`Docs/Plans/HANDOFF-dungeonmind-prospective-publication-prerequisite-v1.md`.

## WK-3 — Prepare World change

**State:** DESIGN REVIEW / BLOCKED / implementation not authorized.

WK-3 may begin only after the DungeonMind prerequisite is available and proved.
It will implement non-mutating semantic interpretation, exact parent and
authority binding, source/evidence admissibility, and complete local-reference
resolution against the DungeonMind publication contract.

## Later work

Commit coordination, verified receipts, and product integration follow only
after WK-3 design and the prerequisite are accepted. HTTP, persistence,
migrations, agent harnesses, vector storage, automatic dedupe, and generic
reconciliation remain outside this bootstrap unless separately authorized.
