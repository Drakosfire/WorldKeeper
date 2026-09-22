# Contract — WorldChangeIntent v0

**Status:** WK-1 DESIGN CONTRACT — READY FOR REVIEW, implementation not authorized
**Version:** `world-change-intent/v0`
**Owner:** World Keeper boundary

This is a conceptual, transport-neutral contract. It is not a Python model, JSON schema, HTTP request, or DungeonMind contribution DTO.

## Purpose

`WorldChangeIntent` is the application-level request for a proposed change to governed World knowledge. A client can author it without knowing DungeonMind persistence or graph-write representations. World Keeper interprets it against exact World authority and returns a prepared change or a typed failure.

## Conceptual shape

```text
WorldChangeIntent
  change_request_id
  world
  optional_scope
  source_context
  actor_context
  operations[]
```

## Minimal application capability surface

The v0 application contract is four semantic capabilities:

```text
prepare_change(intent) -> PreparedWorldChange
commit_prepared_change(prepared_change_id + explicit confirmation)
  -> CommittedWorldChange
recover_change(change_request_id + preparation_generation)
  -> RecoveryResult
read_exact_change_result(result locator pinned to child revision)
  -> ExactWorldChangeReadback
```

`commit_prepared_change` and `recover_change` are separate capabilities. Commit
means “publish this reviewed prepared meaning.” Recovery means “establish the
outcome of the already-authorized transaction when the caller may not know
whether publication completed.” A transport may expose a single publish
endpoint internally, but it must preserve this semantic distinction.

`confirmation_binding` authorizes commit of an active prepared change; it is
not a recovery credential. Once publication begins, recovery is resolved from
the crash-surviving server-side transaction record using
`change_request_id` and `preparation_generation`. A transport still applies
its normal caller authorization, but recovery cannot depend on a client-held
binding or a confirmation-key lifetime that may end before the publication
outcome is proven.

The read capability is deliberately narrow. It proves one committed change at
one exact child revision; it is not the complete World query façade.

### Transaction identity

`change_request_id` identifies one complete intent and its resulting prepared/publication transaction. It is supplied by the caller, stable for retries of that same transaction, and is the transaction-level idempotency and recovery key. One prepared transaction has one such identity and can produce at most one publication outcome. It is not a durable World revision or object identity. A caller may also include a client/workflow identity for result reconciliation; the Keeper must not treat a client-local ID as a World object ID.

The publication record may use an internal or durable
`publication_operation_id`. It maps one-to-one to a single governed attempt
for `(change_request_id, preparation_generation)`; the transaction record
maps those attempts and enforces at most one committed outcome for the whole
`change_request_id`. It must never be confused with an operation inside
`operations[]`.

### World and scope

The intent identifies the target World and may carry a campaign, focus, visibility, or other scope context. The final v0 representation is open, but the meaning must be explicit enough to prevent a write intended for one World or scope from being interpreted in another.

### Source context and evidence grounding

The client supplies source context and, where applicable, evidence links supporting the requested World interpretation:

```text
source_context
  artifact reference
  source revision reference
  optional authority-owned source locator context
  client context for presentation
```

Artifact and revision identity are authoritative only after Keeper/DungeonMind
admission or revalidation. A local file path, browser digest, or display label
is not sufficient publication authority. A future profile may accept an exact
durable occurrence identity or another versioned locator form, but v0 does not
freeze a client-supplied span or offset representation.

Evidence grounding and occurrence/mention binding are separate semantic facts. `source_context` and an operation's `source_links` say what source material supports a proposed World fact. They do not, by themselves, assert that particular source words refer to a particular durable object or deserve mention navigation. Creating a source-grounded object or assertion must not implicitly create an occurrence binding.

The smallest v0 source/evidence reference is:

```text
SourceRevisionRef
  artifact_id
  source_revision_id

SourceEvidenceLocator (only when DungeonMind has admitted one)
  source_artifact_id
  source_revision_id
  authority-owned locator identity or locator form
```

`SourceRevisionRef` is sufficient to ground a fact when no exact occurrence
was selected. An authority-owned locator may refine the evidence location, but
it remains evidence/provenance and does not assert that source words refer to a
World object. World Keeper v0 does not freeze client-supplied byte offsets,
selected-text digests, or a universal annotation system. Any future occurrence
contract must define canonical source bytes and digest/revalidation semantics
with DungeonMind before it can become implementable.

### Actor context

Actor/caller context identifies who or what proposed the intent and provides policy inputs. It is not an agent harness contract and it does not grant direct DungeonMind write authority.

## v0 operation family

The initial semantic family is intentionally small:

### `create_object`

Proposes a new World object with:

```text
operation_id       unique within the intent; never a recovery key
local_ref          non-empty, unique within the intent
kind/profile term  semantic object kind, interpreted under the World profile
label              proposed display/name value
attributes        optional profile-governed fields
source_links      optional operation-level grounding links
```

The `local_ref` is transaction-local. It is not a durable node identity and is never valid outside the prepared intent.

### `reference_existing`

Declares that an operation uses an existing governed object. It carries an
`operation_id` unique within the intent and a durable object reference. The
durable reference is interpreted at the prepared parent revision and must
identify an object admissible in the requested World/scope. A candidate label
or similarity match is not itself a durable reference.

### `create_relationship`

Proposes a relationship with:

```text
operation_id       unique within the intent
source_ref         durable object ref or local_ref
predicate          profile-governed relation term
target_ref         durable object ref or local_ref
attributes        optional profile-governed fields
source_links      optional operation-level grounding links
```

Both endpoints must resolve during prepare. A local endpoint must resolve to an object created by this same intent, not to a relationship operation or a prior transaction.

### Deferred occurrence binding

`link_source_occurrence` remains a future conceptual operation, not an
implementable v0 operation. The current DungeonMind authority exposes source
evidence and locator forms, but not a distinct durable occurrence-to-object
write contract that World Keeper can call losslessly. A source-grounded object
therefore receives no mention/pill/link binding in v0. A later contract may add
the operation only after DungeonMind defines the durable landing record,
translation, canonical source-byte/digest semantics, and exact read-back.

## Reference rules

1. `change_request_id` identifies the whole transaction and is the only v0 idempotency/recovery identity.
2. Every operation identity is non-empty and unique within one intent. An `operation_id` identifies one semantic operation only; it is never the publication/recovery key.
3. Every local reference identifier is non-empty and unique within one intent.
4. A local reference resolves to exactly one `create_object` operation in that intent.
5. A durable reference resolves against the exact prepared World authority.
6. Missing, duplicate, wrong-kind, cross-intent, or ambiguous references fail closed.
7. No client may submit a fabricated durable ID for an object that the same transaction creates.
8. The order of operations must not change the meaning; dependency resolution is semantic, not a client-side two-phase protocol.
9. Source/evidence links never imply occurrence/mention bindings. V0 has no
   implementable occurrence-binding operation; a later reviewed operation may
   create that assertion only after its DungeonMind landing contract exists.

## Identity and ambiguity rules

Similarity and duplicate advice may be returned during prepare, but it does not choose identity. The v0 operation family does not authorize automatic merge, split, delete, or generic edit operations. An explicit identity-reconciliation operation may be added only by a later contract decision.

## Validation boundary

World Keeper validates request shape and semantic dependencies. DungeonMind validates durable World, source/evidence, profile, identity, scope, and publication authority. Neither client-side UI validation nor an agent prompt is a substitute for Keeper/DungeonMind validation.

## Transaction and preparation lifecycle

`change_request_id` identifies one logical application transaction and remains
stable across safe re-prepare generations. Each call to prepare produces a new
`prepared_change_id` and monotonically increasing `preparation_generation`.
Those identities are described by the prepared-change contract. A caller that
starts an unrelated new change must use a new `change_request_id`.

Re-prepare with the same `change_request_id` is allowed only when the prior
generation is known not to have published and the transaction record is not in
`committed` or `outcome_unknown`. If publication may have happened, the caller
must recover the existing transaction outcome before preparing another
generation. This prevents a stale re-prepare from colliding with an earlier
child revision.

## Typed failure principles

The eventual transport may represent these differently, but the semantic classes are:

```text
invalid_intent
ambiguous_reference
invalid_local_reference
source_inadmissible
identity_conflict
inexpressible
authority_unavailable
```

Failures must identify the operation/reference context needed for a client to repair its local intent without exposing internal storage details.

## Explicit exclusions from v0

The contract does not authorize:

- identity merge/reconciliation, delete, or arbitrary edit;
- automatic deduplication;
- raw graph contributions or evidence-record DTOs;
- occurrence/mention binding or client-defined source byte-offset semantics;
- direct persistence or SQL;
- a required HTTP transport;
- an agent/tool-loop protocol;
- implicit publication without a prepared-change confirmation.

## Versioning rule

Any change to operation meaning, reference resolution, source authority, confirmation binding, or failure behavior requires a new version or an explicit reviewed compatibility decision. Internal DungeonMind representation changes do not require a World Keeper contract change if the semantic contract and receipts remain stable.
