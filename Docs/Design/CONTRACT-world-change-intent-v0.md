# Contract — WorldChangeIntent v0

**Status:** DESIGN CONTRACT — v0 proposal, implementation not authorized
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

### Transaction identity

`change_request_id` identifies one complete intent and its resulting prepared/publication transaction. It is supplied by the caller, stable for retries of that same transaction, and is the transaction-level idempotency and recovery key. One prepared transaction has one such identity and can produce at most one publication outcome. It is not a durable World revision or object identity. A caller may also include a client/workflow identity for result reconciliation; the Keeper must not treat a client-local ID as a World object ID.

The publication record may use an internal or durable `publication_operation_id` for the same transaction-level identity. If that name exists internally, it must map one-to-one to `change_request_id`; it must never be confused with an operation inside `operations[]`.

### World and scope

The intent identifies the target World and may carry a campaign, focus, visibility, or other scope context. The final v0 representation is open, but the meaning must be explicit enough to prevent a write intended for one World or scope from being interpreted in another.

### Source context and evidence grounding

The client supplies source context and, where applicable, evidence links supporting the requested World interpretation:

```text
source_context
  artifact reference
  source revision reference
  optional source location/occurrence context
  client context for presentation
```

Artifact and revision identity are authoritative only after Keeper/DungeonMind admission or revalidation. A local file path, browser digest, or display label is not sufficient publication authority. A span may be an exact durable occurrence identity, a bounded offset, or another versioned form accepted by a later profile; the v0 wire shape remains open.

Evidence grounding and occurrence/mention binding are separate semantic facts. `source_context` and an operation's `source_links` say what source material supports a proposed World fact. They do not, by themselves, assert that particular source words refer to a particular durable object or deserve mention navigation. Creating a source-grounded object or assertion must not implicitly create an occurrence binding.

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

Declares that an operation uses an existing governed object. The durable reference is interpreted at the prepared parent revision and must identify an object admissible in the requested World/scope. A candidate label or similarity match is not itself a durable reference.

### `link_source_occurrence`

Requests an explicit occurrence/mention binding: these source words or this durable source occurrence refer to this World object or operation result. This is distinct from evidence grounding. DungeonMind owns the durable evidence/provenance representation and any durable occurrence-binding record, but a source-grounded object does not receive this binding implicitly. A link to a transaction-local object resolves only within this intent.

Conceptually, the operation carries a source occurrence/span reference and a target reference. The final v0 occurrence identity and link-kind vocabulary remain open. A client may use the resulting binding for mention navigation or a pill only when the governed World projection says the binding is truthful.

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

## Reference rules

1. `change_request_id` identifies the whole transaction and is the only v0 idempotency/recovery identity.
2. Every operation identity is non-empty and unique within one intent. An `operation_id` identifies one semantic operation only; it is never the publication/recovery key.
3. Every local reference identifier is non-empty and unique within one intent.
4. A local reference resolves to exactly one `create_object` operation in that intent.
5. A durable reference resolves against the exact prepared World authority.
6. Missing, duplicate, wrong-kind, cross-intent, or ambiguous references fail closed.
7. No client may submit a fabricated durable ID for an object that the same transaction creates.
8. The order of operations must not change the meaning; dependency resolution is semantic, not a client-side two-phase protocol.
9. Source/evidence links never imply occurrence/mention bindings; only `link_source_occurrence` or a later explicit operation can create that assertion.

## Identity and ambiguity rules

Similarity and duplicate advice may be returned during prepare, but it does not choose identity. The v0 operation family does not authorize automatic merge, split, delete, or generic edit operations. An explicit identity-reconciliation operation may be added only by a later contract decision.

## Validation boundary

World Keeper validates request shape and semantic dependencies. DungeonMind validates durable World, source/evidence, profile, identity, scope, and publication authority. Neither client-side UI validation nor an agent prompt is a substitute for Keeper/DungeonMind validation.

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
- direct persistence or SQL;
- a required HTTP transport;
- an agent/tool-loop protocol;
- implicit publication without a prepared-change confirmation.

## Versioning rule

Any change to operation meaning, reference resolution, source authority, confirmation binding, or failure behavior requires a new version or an explicit reviewed compatibility decision. Internal DungeonMind representation changes do not require a World Keeper contract change if the semantic contract and receipts remain stable.
