# Architecture — WorldKeeper

**Status:** CURRENT ARCHITECTURE AUTHORITY
**Phase:** WK-1 through WK-5 complete; V3 compatibility merged
**Implementation:** no active implementation lease; see the steward anchor
**Decision:** [ownership simplification](../Design/DECISION-worldkeeper-ownership-simplification.md)

## Mission

WorldKeeper is the thin application transaction coordinator/compiler between
DungeonBuddy and DungeonMind. It turns application intent into one exact,
reviewable semantic meaning and coordinates its governed publication. It does
not become a second durable World or recovery system.

```text
DungeonBuddy                 WorldKeeper                  DungeonMind
interaction + drafts  ->  semantic meaning + coordination  -> durable truth
```

## Ownership

| Layer | Owns | Does not own |
| --- | --- | --- |
| DungeonBuddy | selections, drafts, local proposal IDs, similarity presentation, explicit create-new/use-existing choice, review and result UX | durable identity, graph writes, publication state |
| WorldKeeper | intent shape, semantic interpretation, same-transaction dependency resolution, prepared meaning, confirmation coordination, verified result reshaping | graph storage, durable IDs, policy authority, durable recovery ledger, general World reads |
| DungeonMind | durable object/relationship identity, source/provenance, profile/scope/admission policy, immutable revisions, expected-parent/CAS, atomic publication, publication outcome/recovery, exact and general World reads | product interaction and local drafts |

## Current transaction boundary

Prepare binds local references to one exact prospective create result inside one
prepared transaction; it does not predict or reserve a future durable ID.
DungeonMind V5.4 materializes prospective creates and dependent operations
atomically, then returns the mapping. WorldKeeper must never publish
an object first and repair a dependent relationship later.

The selected v0 concepts are one `prepared_change_id` for one immutable
prepared meaning and caller-controlled `client_op_id` values referenced by
`result_of(client_op_id)`. Each prepared ID deterministically derives one
DungeonMind publication/idempotency identity (or is itself that identity), so
retries and lost responses reconstruct it from the caller-held prepared ID and
use DungeonMind durable evidence without a second Keeper ledger. Prepared local
lifecycle and DungeonMind durable publication outcome are separate authorities.

## Sequencing

WK-1 and WK-2 are accepted. DungeonMind V5.4 is accepted and merged at
`6edb9e40…`; WK-3 preparation and WK-4 commit/verification are accepted.

WK-5 composes those accepted services behind a stable in-process consumer
contract. Recovery ledgers, prepared persistence, HTTP, product mapping, and
new write semantics remain unauthorized.
