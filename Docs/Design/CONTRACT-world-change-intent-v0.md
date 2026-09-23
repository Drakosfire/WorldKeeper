# Contract — WorldChangeIntent v0

**Status:** CURRENT APPLICATION CONTRACT, WK-3 implementation blocked
**Owner:** WorldKeeper boundary
**Decision:** [ownership simplification](DECISION-worldkeeper-ownership-simplification.md)

This is a transport-neutral semantic contract, not a Python model, HTTP schema,
or DungeonMind DTO. It is accepted as design; implementation is not authorized
until the DungeonMind prerequisite is proved.

## Shape

```text
WorldChangeIntent
  client/change correlation supplied by the caller
  world and optional application context
  source/evidence context
  operations[]
```

Create operations carry a caller-controlled `client_op_id`. A dependent
operation refers to `result_of(client_op_id)` or to an explicitly selected
existing durable object. This is semantic transaction-local identity, not a
durable graph ID or an ID-generation algorithm.

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
commit_change(prepared_change_id, confirmed_by) -> VerifiedCommittedChange
get_change_result(prepared_change_id) -> not_started | committed | outcome_unknown
```

`recover_change`, `read_exact_change_result`, mandatory cryptographic
confirmation tokens, and a WorldKeeper durable recovery ledger are not required
semantic capabilities. Durable publication outcome and replay belong to
DungeonMind; exact child verification remains mandatory before WorldKeeper
returns a successful result.

## Gating decision

DungeonMind `1fc03aa…` currently accepts materialized assertions with durable
endpoint IDs, not prospective references. WK-3 cannot implement this contract
by predicting IDs or publishing objects before dependent relationships. The
DungeonMind prospective-publication prerequisite must be available and proved
at its owning boundary first.

Earlier WK-1 contract text is retained in repository history as historical
evidence, including its same-transaction safety analysis. It is not current
authority for identity allocation or recovery vocabulary.
