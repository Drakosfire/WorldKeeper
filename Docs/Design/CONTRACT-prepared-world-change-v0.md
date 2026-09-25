# Contract — PreparedWorldChange v0

**Status:** CURRENT APPLICATION CONTRACT, WK-4 commit active
**Owner:** WorldKeeper boundary
**Decision:** [ownership simplification](DECISION-worldkeeper-ownership-simplification.md)

## Meaning

`PreparedWorldChange` is one exact immutable interpretation of one intent
against one exact governed parent and authority context. One
`prepared_change_id` identifies that meaning. Re-preparation creates a new ID;
it does not mutate or reinterpret the old record.

```text
PreparedWorldChange
  prepared_change_id
  dungeonmind_publication_identity = derive(prepared_change_id)
  world / scope / profile context
  expected_parent_revision_id
  source and evidence context
  interpreted operations
  prospective result handles
  warnings / semantic failures
```

## Prospective references

Each create operation has one `client_op_id` and one exact prospective result
inside this prepared transaction. A dependent relationship must visibly refer
to `result_of(client_op_id)` and is resolved to that same prospective result
before confirmation. The handle is neither a durable object ID nor permission
to publish an object first and repair its dependents later.

DungeonMind, not WorldKeeper, allocates the durable identity during one atomic
publication and returns the mapping. A changed proposal, stale parent,
changed authority, or changed evidence fails closed and requires re-prepare.

## Lifecycle ownership

WorldKeeper may retain only local prepared lifecycle (`active`, `expired`,
`invalidated`). DungeonMind owns durable publication outcomes and idempotent
replay (`not_published`, `committed`, `outcome_unknown`). WorldKeeper does not
mandate a second durable recovery ledger or a separate recovery protocol.

Confirmation preserves the exact prepared meaning. A successful result must be
verified against the exact immutable child revision reported by DungeonMind,
including returned durable object and relationship mappings.

Every `prepared_change_id` deterministically derives exactly one stable
`dungeonmind_publication_identity` (or is itself that identity). DungeonMind
durably records and replays publication outcome under it. Commit retries and
lost-response resolution reconstruct the same identity from the caller-held
prepared ID alone, not from retained WorldKeeper prepared state. A new prepared
ID receives a new publication identity without requiring a second Keeper ledger.

The minimum verified receipt returns the prepared ID, DungeonMind publication
identity, exact child revision, each `create_object client_op_id ->
durable_object_id`, each fact/relationship `client_op_id ->
durable_assertion_id` with semantic role, and proof of exact-child read-back.
Known durable success is preserved when exact-child verification is temporarily
unavailable or fails integrity; it is not relabeled outcome-unknown.

## Non-goals and gate

This contract does not require `recover_change`, `read_exact_change_result`,
`confirmation_binding`, `preparation_generation`, generic reconciliation,
automatic dedupe, generic attributes, or ordinary World read APIs. Those are
deferred unless a later authority decision establishes a concrete need.
`get_change_result(prepared_change_id)` is optional until a demonstrated caller
needs status inspection independently of a commit retry.

DungeonMind V5.4 at merged authority `6edb9e40…` proves prospective allocation,
substitution, atomicity, idempotency, and lost-response resolution. WK-3 may
produce an immutable compile-ready prospective plan. WK-4 may publish exactly
that caller-held prepared value and independently verify its exact child.
