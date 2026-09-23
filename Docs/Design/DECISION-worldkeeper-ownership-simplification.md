# Decision — WorldKeeper thin coordinator and DungeonMind prospective publication

**Status:** CURRENT DESIGN AUTHORITY
**Decision date:** 2026-09-22
**WorldKeeper baseline:** `732c3c394a5b56843612841c7b7e4a0def53cd70`
**Accepted WK-2 PR #2 head:** `15739eb2688992fe8f977d006b1e9153047753a9`
**Historical DungeonMind gap inspection:** `1fc03aa21e406d9a7cb07d0e4792e202fe281375`
**Accepted DungeonMind V5.4 merge:** `6edb9e40d1dc930f537c66deb1afbd1b99002844`

## Decision

WorldKeeper is an application transaction coordinator/compiler. It interprets
application intent, validates semantic coherence, prepares one reviewable
meaning, coordinates confirmation, and reshapes a verified DungeonMind result.
It is not a graph, identity allocator, policy engine, durable recovery ledger,
or general-purpose World read façade.

DungeonBuddy owns interaction and reversible local state. DungeonMind owns
durable World truth: object and relationship identity, source and provenance,
profile/scope/admission policy, immutable revisions, expected-parent/CAS
semantics, atomic publication, durable publication outcome, recovery, and
general World reads.

## Prospective-reference decision

Prepare binds each local reference to one exact prospective create result within
one immutable prepared transaction. Dependents are semantically resolved to
that same prospective result before confirmation. Prepare does not know or
reserve a future DungeonMind object ID.

Commit may assign the durable ID only through one atomic DungeonMind
publication. DungeonMind must allocate the ID, substitute it consistently in
all dependent assertions, materialize the complete transaction, and return the
prospective/client-operation-to-durable-result mapping. Object-first publication
followed by relationship repair is forbidden. WorldKeeper must not invent a
deterministic future ID.

The preferred caller identity is `client_op_id`; dependents use
`result_of(client_op_id)`. WorldKeeper does not retain separate semantic
namespaces for `operation_id`, `local_ref`, and a future durable identity.

## Simplified lifecycle

One `prepared_change_id` identifies one exact immutable prepared meaning. It
deterministically derives exactly one DungeonMind publication/idempotency
identity (or is itself that identity). Every commit retry and lost-response
inquiry can therefore reconstruct the same DungeonMind identity from the
caller-held prepared ID alone; DungeonMind durably records and replays the
outcome under that identity. A re-preparation creates a new prepared ID and
therefore a new publication identity; DungeonBuddy may retain its own draft
correlation. WorldKeeper does not mirror this outcome in a durable ledger.
WorldKeeper local lifecycle is limited to `active`, `expired`, and
`invalidated`. DungeonMind owns publication outcomes such as `not_published`,
`committed`, and `outcome_unknown`.

The v0 semantic surface is intentionally small:

```text
prepare_change(intent) -> PreparedChange
commit_change(prepared_change_id, confirmed_by) -> VerifiedCommittedChange
```

`get_change_result(prepared_change_id)` is optional until a caller needs status
inspection independently of retrying `commit_change`. `recover_change`,
`read_exact_change_result`, cryptographic confirmation bindings, and a second
WorldKeeper recovery ledger are not mandatory v0 semantics. A successful commit
still performs exact child-revision read-back internally before returning a
verified result.

## DungeonMind prerequisite — accepted

At historical DungeonMind `1fc03aa…`, the answer was **no**: its then-current
materialization contract did not accept prospective endpoints. The relevant
authority is `GraphContributionAssertionV2` in
`src/dungeonmind/contracts/contribution.py`; its edge fields are
`subject_object_id` and `object_object_id`. `GraphMaterializerV6.apply_edge`
in `src/dungeonmind/application/review_materialization_v6.py` rejects missing
endpoints and requires both IDs in the materialized object set. The publication
path is `publish_finalized_review` in
`src/dungeonmind/application/review_publication.py`, which materializes the
review and delegates an already-materialized payload to
`WorldGraphRepository.publish_revision`.

The surrounding guarantees are present and remain authoritative: immutable
revisions, expected-parent validation, atomic head advancement, governed
publication records, replay of an existing publication, and exact graph reads.
The missing primitive is an atomic publication transaction such as:

```text
publish(expected_parent, idempotency_key,
        create P, dependent relationship P -> existing B)
  -> child revision, P -> durable object ID,
     dependent relationship -> durable relationship ID
```

DungeonMind V5.4 now proves allocation, consistent substitution,
pre-publication validation, atomicity, idempotency, lost-response outcome
resolution, and the returned mapping at the owning boundary. It was accepted at
`c7700f98…` and merged at `6edb9e40…`. Therefore:

```text
WK-3 preparation implementation is ACTIVE
WK-4 publication/commit/recovery remains unauthorized.
```

## Preserved invariants and deferrals

- Prepare is non-mutating and binds exact parent, authority, evidence, and meaning.
- Confirmation publishes only that meaning; stale authority fails closed.
- Same-transaction local references resolve completely before confirmation.
- Evidence support never implies occurrence/mention binding; occurrence binding remains deferred.
- Similarity and duplicate presentation remain Buddy concerns; no automatic dedupe.
- Merge, split, unmerge, reconciliation, generic policy fields, and speculative schema axes are deferred.
- No HTTP, persistence, migrations, agent harness, vector storage, or second graph engine is authorized.

The earlier WK-1 deterministic prospective-identity design remains historical
evidence of same-transaction safety. It is not the selected current ownership
model and must not be implemented as a WorldKeeper ID allocator.
