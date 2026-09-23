# Handoff — DungeonMind prospective-reference atomic publication prerequisite

**Status:** BLOCKING FOLLOW-ON / DESIGN HANDOFF ONLY
**Owning repository:** DungeonMind
**Source authority inspected:** `origin/main` at `1fc03aa21e406d9a7cb07d0e4792e202fe281375`
**WorldKeeper consequence:** WK-3 implementation remains unauthorized

## Required capability

Add the smallest DungeonMind-owned publication contract that accepts one
transaction containing prospective creates and dependent assertions:

```text
publish(expected_parent, idempotency_key,
        create P,
        relationship source=P target=existing durable B)
  -> immutable child revision,
     P -> durable object ID,
     relationship -> durable relationship ID
```

## Required proof

1. Prospective references are scoped to one publication transaction.
2. Each prospective reference maps to exactly one allocated durable identity.
3. Dependents are substituted before materialization; placeholders cannot publish.
4. Validation occurs before expected-parent atomic head advancement.
5. Failure leaves the previous head readable.
6. Retrying the same publication identity replays the same result idempotently.
7. A lost response can be resolved from durable DungeonMind evidence.
8. The result returns prospective/client-operation-to-durable mappings and exact
   child revision evidence.

## Current gap evidence

WorldKeeper inspected `GraphContributionAssertionV2` in
`src/dungeonmind/contracts/contribution.py`, `GraphMaterializerV6.apply_edge`
in `src/dungeonmind/application/review_materialization_v6.py`,
`publish_finalized_review` in `src/dungeonmind/application/review_publication.py`,
and the related conformance tests. The current contract requires durable
`subject_object_id` and `object_object_id` endpoints and has no prospective
materialization mapping.

This handoff does not authorize changes in WorldKeeper, does not authorize
WorldKeeper to predict durable IDs, and does not broaden the DungeonMind work
into a graph-kernel rewrite. Once this contract is implemented and proved in
DungeonMind, return the exact contract, tests, and immutable revision to the
WorldKeeper steward for WK-3 re-evaluation.
