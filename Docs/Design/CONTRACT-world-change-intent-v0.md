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
  request_identity
  world
  optional_scope
  source_context
  actor_context
  operations[]
```

### Request identity

The request identity is supplied by the caller and is stable for retries of the same authored transaction. It is not a durable revision identity. A caller may also include a client/workflow identity for result reconciliation; the Keeper must not treat a client-local ID as a World object ID.

### World and scope

The intent identifies the target World and may carry a campaign, focus, visibility, or other scope context. The final v0 representation is open, but the meaning must be explicit enough to prevent a write intended for one World or scope from being interpreted in another.

### Source context

The client supplies the source grounding for the requested interpretation:

```text
source_context
  artifact reference
  source revision reference
  optional occurrence/span reference
  client context for presentation
```

Artifact and revision identity are authoritative only after Keeper/DungeonMind admission or revalidation. A local file path, browser digest, or display label is not sufficient publication authority. A span may be an exact durable occurrence identity, a bounded offset, or another versioned form accepted by a later profile; the v0 wire shape remains open.

### Actor context

Actor/caller context identifies who or what proposed the intent and provides policy inputs. It is not an agent harness contract and it does not grant direct DungeonMind write authority.

## v0 operation family

The initial semantic family is intentionally small:

### `create_object`

Proposes a new World object with:

```text
operation_id       unique within the intent
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

Requests an explicit relationship between a source occurrence and a World object or operation result. It is the application-facing form of source grounding; DungeonMind owns the durable evidence/provenance representation. A link to a transaction-local object resolves only within this intent.

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

1. Every operation identity is non-empty and unique within one intent.
2. Every local reference identifier is non-empty and unique within one intent.
3. A local reference resolves to exactly one `create_object` operation in that intent.
4. A durable reference resolves against the exact prepared World authority.
5. Missing, duplicate, wrong-kind, cross-intent, or ambiguous references fail closed.
6. No client may submit a fabricated durable ID for an object that the same transaction creates.
7. The order of operations must not change the meaning; dependency resolution is semantic, not a client-side two-phase protocol.

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
