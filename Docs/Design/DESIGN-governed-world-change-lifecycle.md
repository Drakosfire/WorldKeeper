# Design — Governed World Change Lifecycle

**Status:** CURRENT WK-1 DESIGN AUTHORITY — READY FOR REVIEW
**Phase:** WK-1 — TRANSPORT-NEUTRAL APPLICATION CONTRACTS
**Implementation:** NOT AUTHORIZED

## Purpose

This design defines the semantic lifecycle that World Keeper must preserve when it is eventually implemented. It does not prescribe HTTP, a database schema, a token format, or DungeonMind's internal contribution representation.

```text
AUTHOR
  local, reversible application intent
      ↓
PREPARE
  interpret the complete transaction against exact governed truth
      ↓
REVIEW
  show exactly what would become World truth
      ↓ explicit human or policy confirmation
COMMIT / RECOVER
  publish or recover exactly that prepared meaning
      ↓
RESULT
  immutable child revision, durable identities, exact read-back
```

`prepare` is an authority operation even when the client presents it as one part of a single Publish flow. It is not a second user wizard stage by necessity.

## WK-1 capability surface

The smallest transport-neutral application API is:

```text
prepare_change(intent) -> PreparedWorldChange
commit_prepared_change(prepared_change_id, explicit_confirmation)
  -> CommittedWorldChange
recover_change(change_request_id, prepared_change_id/generation, recovery binding)
  -> RecoveryResult
read_exact_change_result(readback_locator)
  -> ExactWorldChangeReadback
```

Commit and recovery are separate semantic capabilities. Commit authorizes the
exact prepared meaning. Recovery determines whether that same transaction
already committed when the caller may have lost the response. A transport may
combine their plumbing, but it may not collapse their result semantics.

The fourth capability is deliberately narrow: it proves one committed change
at one exact child revision and does not define the broader World read/query
façade.

## State model

| State | Meaning | Durable World mutation |
| --- | --- | --- |
| authored | client-local intent is being edited | none |
| prepared | Keeper has interpreted and sealed one exact change/generation | none |
| expired | the operational confirmation window elapsed | none |
| invalidated | the prepared binding no longer matches the intent or authority | none |
| confirmed | a caller explicitly accepted the prepared change | not by confirmation alone |
| publishing | Keeper is coordinating the generation-bound DungeonMind publication | at most one governed attempt |
| committed | one immutable child revision and receipt are known | one child revision |
| not_committed | authority proves this generation produced no child | none |
| outcome_unknown | publication may have happened but is not yet provable | unknown until recovery |

The client may hide these backend states, but it must not hide the difference between local intent, prepared meaning, and durable result.

## Prepare semantics

Prepare validates and interprets the entire `WorldChangeIntent` as one transaction. It must:

1. identify the World and applicable scope/profile;
2. resolve the exact parent revision and relevant authority state;
3. validate source context and establish an admissible evidence interpretation;
4. validate operation identities and references;
5. resolve durable endpoints against the exact parent;
6. resolve transaction-local endpoints to prospective durable results;
7. apply semantic-profile, visibility, and expressibility rules;
8. record warnings and ambiguities without silently choosing identity;
9. assign a new `prepared_change_id` and `preparation_generation`;
10. produce a reviewable prepared change and an exact confirmation binding.

Prepare does not publish, create placeholder nodes, advance a head, mutate source bytes, or reserve a durable identity in a way that changes World truth.

## Review semantics

The prepared representation must let a user or policy understand:

- which World and parent revision are affected;
- what objects, references, relationships, and source links will be created or changed;
- which proposed objects are new and which refer to existing durable objects;
- how every transaction-local reference resolves;
- what source/evidence grounds the interpretation;
- which warnings or ambiguities remain;
- what confirmation will authorize.

The review surface may be product-specific. The prepared meaning may not be.

## Confirm and publication semantics

Confirm must prove that the submitted confirmation is bound to the prepared change, including at minimum:

- prepared-change identity or equivalent opaque binding;
- transaction-level `change_request_id` and preparation generation;
- intent/proposal digest;
- World identity and expected parent revision;
- source selector and admitted source/evidence identity;
- relevant semantic-profile and identity state;
- confirmation policy/human decision where applicable.

Confirm must not reinterpret the original intent against today's state. It may revalidate the sealed authority and re-prove the source/evidence pair; any material mismatch fails closed or requires re-prepare.

DungeonMind then owns atomic expected-parent publication. When a commit attempt
begins, Keeper maps `(change_request_id, preparation_generation)` to exactly one
internal `publication_operation_id` and seals that mapping. Retries reuse the
same internal identity and binding. If publication already happened and the
response was lost, recovery with the transaction-level `change_request_id`,
generation, and binding must return that result rather than publish another
child. A per-operation `operation_id` is never sufficient to recover or
deduplicate the whole change.

## Transaction-local references

Local references are scoped to the one prepared intent. For example:

```text
CreateObject(local_ref = "local:brewery", label = "The Wizard's Tower Brewing Co")
CreateRelationship(source = existing:pippa,
                  predicate = "works_at",
                  target = local:brewery)
```

The following are mandatory:

- local operation/reference IDs are non-empty and unique within the intent;
- each local object reference resolves to exactly one object-creation operation;
- a missing, duplicate, wrong-kind, or outside-transaction reference fails before prepare succeeds;
- all dependent edges are materialized in the same prospective transaction;
- no placeholder durable object or follow-up repair write is accepted.

## Source/evidence semantics

The client names source context. Keeper determines whether the requested World interpretation can be grounded in admissible source/evidence semantics. DungeonMind stores and validates durable source/evidence identity. Evidence grounding is distinct from occurrence/mention binding: supporting a proposed World fact with a source does not by itself assert that particular words refer to a durable object or should receive a pill/link. Only an explicit occurrence-binding operation can make that assertion.

Prepare must bind the selected source strongly enough that confirm cannot swap an artifact, revision, occurrence, or source selector. A client-local path or digest is context, not publication authority. Reads may expose evidence/provenance; they may not silently repair a weak write or invent an occurrence binding.

For v0, source evidence uses an immutable artifact/revision identity and an
optional UTF-8 byte span with a selected-text digest. A span in `source_links`
supports evidence only. `link_source_occurrence` carries the same source-span
identity plus a target and is the only operation that asserts mention/occurrence
identity.

## Identity semantics

Keeper may show duplicate or similarity advice, but it must preserve three distinct actions:

```text
use existing object
create distinct object
explicitly reconcile identities
```

Bootstrap authorizes no automatic identity merge. A same-label create can remain a distinct object when that is the explicit operation and the governed semantic rules permit it.

## Concurrency and staleness

The parent revision used for interpretation is part of the prepared meaning. If the World head advances before confirm, commit must return a stale-parent result or require re-prepare. A client must not silently rebase the change and claim that the original review covered the rebased meaning.

Expiry is an operational retention/confirmation rule, not a correctness
substitute. The contract distinguishes `expired`, `stale_parent`, changed
source/profile/identity authority, changed intent, `committed`, and
`outcome_unknown`. None of the latter correctness states may be silently
collapsed into expiry or automatically rebased.

Re-prepare retains the same `change_request_id` for the same logical client
transaction and increments `preparation_generation`, producing a new
`prepared_change_id`. It is allowed only after the previous generation is
known `not_committed` or was invalidated before any publication attempt. If
the prior result is `committed` or `outcome_unknown`, the caller must recover
first; a new preparation under that identity is blocked. A new unrelated
transaction receives a new `change_request_id`.

## Result and read-back

A successful commit is complete only when the caller can establish:

```text
parent revision → published child revision
local object proposal → durable object identity
requested relationship → exact durable relationship/read-back result
source/evidence relationship → admissible evidence at the child
```

The v0 receipt returns direct durable relationship identities for relationship
operations:

```text
relationship operation_id → durable relationship_id
```

The mapping is not the publication identity. Exact child read-back remains
mandatory and verifies that each returned object, relationship, explicit
occurrence binding, and supporting evidence exists at the published revision.
The receipt must distinguish durable publication from a later refresh failure.

## Failure and recovery

Failure is typed and inspectable. The application must not receive raw database exceptions as its semantic contract. At minimum, Keeper distinguishes invalid intent, invalid local reference, source inadmissibility, identity conflict, stale parent, prepared mismatch, authority unavailability, integrity failure, and publication failure.

Recovery is a semantic operation identified by the original transaction-level
`change_request_id`, generation-bound prepared identity, and recovery binding.
It returns `committed` with the original receipt, `not_committed` when the
authority proves no child was published for that generation, or
`outcome_unknown` when proof is not yet available. A semantic operation's
`operation_id` is only an intra-transaction identifier and cannot serve as the
recovery key. Recovery may not invent a new meaning to make a retry succeed.

## Prepared-record decision

WK-1 selects a retained-record plus tamper-evident-binding hybrid. Keeper
retains an immutable canonical prepared record for each generation in a
workflow-store boundary. The confirmation binding protects against
cross-generation substitution and client mutation; it is not the sole source
from which Keeper reconstructs a meaning. The workflow store is not a graph,
identity ledger, evidence authority, or publication store, and its existence
does not require HTTP or a dedicated World Keeper database.

The first in-process implementation may provide the store through an adapter.
A deployment that needs prepared changes to survive restart must use a durable
store. If the record is unavailable, the safe result is
`prepared_change_not_found` and re-prepare; Keeper must not reconstruct from
untrusted client input. Binding key rotation uses a version/key identifier and
keeps old verification keys available through the maximum preparation window.

## WK-1 adversarial decision table

| Case | Required result |
| --- | --- |
| normal publish | prepare against parent A; review; confirm; one child B; exact read-back of B |
| prepare local object + relationship to it | one prepared interpretation; relationship endpoint is the opaque prospective object handle |
| stale parent before confirm | `stale_parent`; no child; re-prepare required |
| changed source authority | source re-proof fails; no child; prepared change invalidated |
| changed identity/profile authority | authority revalidation fails; no child; prepared change invalidated |
| changed client intent | confirmation digest/binding mismatch; no child; new generation only after safe invalidation |
| duplicate local IDs | fail before prepare succeeds |
| lost publish response | `outcome_unknown` until recovery; recovery returns the original receipt or remains explicit unknown; no second interpretation |
| retry after success | same `change_request_id` returns the same committed result; no second child |
| re-prepare after stale preparation | same request ID, new generation/prepared ID, only after prior generation is proven not committed |
| refresh failure after publication | commit remains successful; refresh/read-back reports its own failure |
| source-grounded object without mention binding | evidence can support publication; no occurrence/pill/link is implied |
| explicit mention binding | separate operation is reviewed and read back as a source-occurrence assertion |

## WK-1 review outcome and next authorization

This design and the companion v0 contracts answer the WK-1 capability,
identity, storage, expiry, re-prepare, source-span, prospective-result,
relationship-result, read-back, and adversarial questions. They remain design
authority only. Implementation is still not authorized until WK-1 review
accepts these decisions and a subsequent handoff grants a narrow
implementation lease.

## Current implementation evidence

DungeonMindBuddy currently demonstrates this safety shape through its authoring prepare/commit services, source-admission ports, exact-parent authority adapter, signed confirmation binding, and idempotent publication/recovery path. These are accepted semantic evidence, not a permanent World Keeper module layout. In particular, the public Keeper contract must not freeze Buddy's `GraphContribution` DTOs, namespace, request models, or current expressibility classifier.

## Explicit non-goals

This design does not authorize automatic deduplication, identity merge, delete/edit semantics, an agent harness, source-markdown mutation, direct graph edits, or a transport-specific endpoint family.
