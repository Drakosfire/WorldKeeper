# Architecture — WorldKeeper

**Status:** CURRENT ARCHITECTURE AUTHORITY
**Phase:** WK-1 and WK-2 accepted; WK-3 design review blocked
**Implementation:** WK-3 NOT AUTHORIZED
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
DungeonMind must eventually materialize prospective creates and dependent
operations atomically, then return the mapping. WorldKeeper must never publish
an object first and repair a dependent relationship later.

The selected v0 concepts are one `prepared_change_id` for one immutable
prepared meaning and caller-controlled `client_op_id` values referenced by
`result_of(client_op_id)`. Each prepared ID maps one-to-one to a stable
DungeonMind publication/idempotency identity so retries and lost responses use
DungeonMind durable evidence without a second Keeper ledger. Prepared local
lifecycle and DungeonMind durable publication outcome are separate authorities.

## Sequencing

WK-1 and WK-2 are accepted. The next implementation is a narrow DungeonMind
prospective-publication prerequisite, not WK-3 runtime behavior. WK-3 becomes
ready only after DungeonMind proves prospective allocation, consistent
substitution, atomic publication, idempotency, lost-response resolution, and
the returned prospective-to-durable mapping.

WorldKeeper runtime implementation remains unauthorized. See the decision
document for retained safety invariants, historical WK-1 evidence, and
explicitly deferred capabilities.
