# Design — Governed World Change Lifecycle

**Status:** CURRENT BOOTSTRAP DESIGN AUTHORITY
**Phase:** DESIGN / REPOSITORY BOOTSTRAP
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

## State model

| State | Meaning | Durable World mutation |
| --- | --- | --- |
| authored | client-local intent is being edited | none |
| prepared | Keeper has interpreted and sealed one exact change | none |
| invalidated | the prepared binding no longer matches the intent or authority | none |
| confirmed | a caller explicitly accepted the prepared change | not by confirmation alone |
| publishing | Keeper is coordinating DungeonMind publication/recovery | at most the one governed operation |
| committed | one immutable child revision and receipt are known | one child revision |
| failed | the operation was rejected or could not prove its outcome | none unless recovery proves a prior commit |

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
9. produce a reviewable prepared change and an exact confirmation binding.

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
- request/operation identity;
- intent/proposal digest;
- World identity and expected parent revision;
- source selector and admitted source/evidence identity;
- relevant semantic-profile and identity state;
- confirmation policy/human decision where applicable.

Confirm must not reinterpret the original intent against today's state. It may revalidate the sealed authority and re-prove the source/evidence pair; any material mismatch fails closed or requires re-prepare.

DungeonMind then owns atomic expected-parent publication. The intended result is one immutable child revision. If publication already happened and the response was lost, recovery with the same transaction-level `change_request_id` / publication identity must return that result rather than publish another child. A per-operation `operation_id` is never sufficient to recover or deduplicate the whole change.

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

Prepared expiry may be needed for operational reasons; its duration and whether expiry is a contract field remain open. Expiry must not weaken exact binding.

## Result and read-back

A successful commit is complete only when the caller can establish:

```text
parent revision → published child revision
local object proposal → durable object identity
requested relationship → exact durable relationship/read-back result
source/evidence relationship → admissible evidence at the child
```

The receipt must distinguish durable publication from a later refresh failure. Whether relationship IDs are returned directly or derived through exact child read-back is open and recorded in the prepared contract.

## Failure and recovery

Failure is typed and inspectable. The application must not receive raw database exceptions as its semantic contract. At minimum, Keeper distinguishes invalid intent, invalid local reference, source inadmissibility, identity conflict, stale parent, prepared mismatch, authority unavailability, integrity failure, and publication failure.

Recovery is a semantic operation identified by the original transaction-level `change_request_id` / publication identity. It may prove that a prior commit exists, retry a safe idempotent publication, or report that the outcome remains unknown. A semantic operation's `operation_id` is only an intra-transaction identifier and cannot serve as the recovery key. Recovery may not invent a new meaning to make a retry succeed.

## Current implementation evidence

DungeonMindBuddy currently demonstrates this safety shape through its authoring prepare/commit services, source-admission ports, exact-parent authority adapter, signed confirmation binding, and idempotent publication/recovery path. These are accepted semantic evidence, not a permanent World Keeper module layout. In particular, the public Keeper contract must not freeze Buddy's `GraphContribution` DTOs, namespace, request models, or current expressibility classifier.

## Explicit non-goals

This design does not authorize automatic deduplication, identity merge, delete/edit semantics, an agent harness, source-markdown mutation, direct graph edits, or a transport-specific endpoint family.
