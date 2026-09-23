# Design — Governed World Change Lifecycle

**Status:** CURRENT LIFECYCLE AUTHORITY, WK-3 implementation blocked
**Phase:** WK-1/WK-2 accepted; DungeonMind prerequisite next
**Decision:** [ownership simplification](DECISION-worldkeeper-ownership-simplification.md)

## Lifecycle

```text
AUTHOR       Buddy owns reversible local intent
PREPARE      WorldKeeper interprets without durable mutation
REVIEW       caller confirms one immutable prepared meaning
PUBLISH      DungeonMind allocates, materializes, and advances atomically
VERIFY       WorldKeeper reads the exact immutable child
RESULT       caller receives the verified durable mapping
```

WorldKeeper's local states are only `active`, `expired`, and `invalidated`.
DungeonMind owns durable publication states and outcome recovery. This design
does not create a seven-state cross-authority machine or a second Keeper
recovery ledger.

## Prepare and confirmation invariants

Prepare binds exact expected parent, source/evidence context, authority, and
semantic operations. It binds each local reference to one exact prospective
create result within the prepared transaction. Dependents are resolved to that
result before confirmation, but no future durable ID is predicted or reserved.

Confirmation can publish only that exact meaning. Stale parent, changed
authority, changed evidence, or changed proposal fails closed and requires a
new `prepared_change_id`. There is no object-first publication followed by
dependent repair, automatic merge, or dedupe.

Each immutable `prepared_change_id` deterministically derives one stable
DungeonMind publication/idempotency identity, or is itself that identity.
DungeonMind durably records and replays the outcome under it. Commit retries
and lost-response resolution reconstruct it from the caller-held prepared ID
alone, so no retained WorldKeeper prepared state or mirrored recovery ledger is
needed. A re-prepare creates both a new prepared ID and publication identity.

## DungeonMind gate

At inspected DungeonMind `1fc03aa…`,
`GraphContributionAssertionV2` carries durable endpoint fields and
`GraphMaterializerV6.apply_edge` requires both endpoints to be present in the
materialized object set. `publish_finalized_review` publishes an already
materialized graph payload through `WorldGraphRepository.publish_revision`.
No current contract accepts a prospective endpoint, allocates it during the
same publication, substitutes it through dependent assertions, and returns the
mapping.

The next implementation slice belongs to DungeonMind and must prove:

1. prospective references are scoped to one publication;
2. each prospective reference maps to one newly allocated durable ID;
3. dependent operations use the substituted ID before publication;
4. validation precedes atomic expected-parent head advancement;
5. failure leaves the prior head readable;
6. retry by publication identity is idempotent;
7. lost responses resolve from durable evidence; and
8. the result returns prospective/client-operation-to-durable mappings.

Until then, `WK-3 implementation is BLOCKED`.

## Deferred capabilities

`recover_change`, `read_exact_change_result`, mandatory cryptographic
confirmation bindings, `preparation_generation`, generic reconciliation,
generic WorldKeeper reads, speculative policy fields, and automatic identity
merging are deferred. `get_change_result(prepared_change_id)` is optional until
a caller demonstrates a need for status inspection independent of commit retry.
Exact child read-back remains mandatory internally before WorldKeeper returns a
successful commit result. Evidence grounding remains separate from
occurrence/mention binding.

The superseded WK-1 lifecycle text remains historical evidence in prior commits;
it is not current authority for a durable-ID allocator or Keeper recovery API.
