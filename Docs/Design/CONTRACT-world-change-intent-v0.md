# Contract — WorldChangeIntent v0

**Status:** CURRENT APPLICATION CONTRACT, WK-4 commit active
**Owner:** WorldKeeper boundary
**Decision:** [ownership simplification](DECISION-worldkeeper-ownership-simplification.md)

This is a transport-neutral semantic contract, not a Python model, HTTP schema,
or DungeonMind DTO. WK-3 implementation is authorized only for non-mutating
prepare and lossless DungeonMind V5.4 prospective compilation.

## Shape

```text
WorldChangeIntent
  client/change correlation supplied by the caller
  world and optional application context
  source/evidence context
  operations[]: create_object | use_existing | create_relationship
```

The minimal operation family is deliberately concrete:

```text
create_object
  client_op_id
  admitted object meaning (for example qualified kind, label, and evidence)

use_existing
  durable_object_id

create_relationship
  client_op_id
  source = result_of(create_object.client_op_id) | durable_object_id
  predicate
  target = result_of(create_object.client_op_id) | durable_object_id
  evidence
```

`use_existing` is an explicit identity choice, never similarity inference. A
relationship endpoint may use only an exact selected durable object or the
result of a `create_object` in the same intent. `client_op_id` is transaction-
local semantic identity, not a durable graph ID or an ID-generation algorithm.

## Interpretation guarantees

- WorldKeeper validates shape and interprets create-new versus use-existing.
- Every local reference resolves to one exact prospective create result before
  confirmation; unresolved placeholders are not reviewable.
- Prepare is non-mutating and binds exact parent revision, authority, source,
  evidence, and semantic meaning.
- Similarity and duplicate suggestions are advisory Buddy/DungeonMind input;
  they never silently merge or change identity.
- Evidence grounding does not imply occurrence or mention binding. Occurrence
  binding remains deferred until DungeonMind exposes its distinct write contract.

## Capability boundary

The selected v0 semantic surface is:

```text
prepare_change(intent) -> PreparedWorldChange
commit_prepared_change(prepared, confirmed_by) -> VerifiedCommittedChange
```

The ID-only `commit_change(prepared_change_id, confirmed_by)` surface is a later
workflow concern because WorldKeeper has no prepared-state database.
`get_change_result(prepared_change_id)` is optional until a demonstrated caller
needs independent status inspection. `recover_change`,
`read_exact_change_result`, mandatory cryptographic confirmation tokens, and a
WorldKeeper durable recovery ledger are not required semantic capabilities.
Durable publication outcome and replay belong to DungeonMind; exact child
verification remains mandatory before WorldKeeper returns a successful result.

## Stable publication identity and receipt

Every immutable `prepared_change_id` deterministically derives one stable
DungeonMind publication/idempotency identity, or is itself that identity.
DungeonMind durably records and replays the outcome under it. Consequently a
retry or lost-response inquiry reconstructs the identity from the caller-held
prepared ID alone; it never depends on retained WorldKeeper prepared state.
Re-preparing produces a new prepared ID and a new publication identity;
WorldKeeper does not persist a second ledger merely to mirror DungeonMind's
outcome.

The minimum successful `VerifiedCommittedChange` receipt contains:

```text
prepared_change_id
DungeonMind publication identity
exact child_revision_id
create_object client_op_id -> durable_object_id
create_relationship client_op_id -> durable_assertion_id
exact child-revision read-back verification
```

Native vNext relationships are assertions; WorldKeeper does not invent a
separate relationship identity. A known commit whose exact child is temporarily
unavailable remains committed and retry-safe, distinct from an unknown
publication outcome.

## Gating decision

DungeonMind V5.4 at merged authority `6edb9e40…` accepts prospective references
and owns allocation/substitution. WK-3 compiles `result_of(client_op_id)` to
that syntax without predicting IDs. WK-4 commits that immutable prepared value
and verifies the exact child.

Earlier WK-1 contract text is retained in repository history as historical
evidence, including its same-transaction safety analysis. It is not current
authority for identity allocation or recovery vocabulary.
