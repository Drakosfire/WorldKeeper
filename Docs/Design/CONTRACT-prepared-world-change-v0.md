# Contract — PreparedWorldChange v0

**Status:** DESIGN CONTRACT — v0 proposal, implementation not authorized
**Version:** `prepared-world-change/v0`
**Owner:** World Keeper boundary

This is a conceptual review contract. It defines what must be reviewable and what confirm must bind; it does not freeze a token encoding, persistence table, or DungeonMind DTO.

## Purpose

`PreparedWorldChange` is the exact interpretation of one `WorldChangeIntent` against one governed World authority. It is the thing a user or policy confirms. It must answer:

> What exactly will become World truth if I confirm?

## Conceptual shape

```text
PreparedWorldChange
  prepared_change_id
  change_request_id
  world_id
  scope_context
  parent_revision_id
  source_evidence_summary
  interpreted_operations[]
  prospective_results
  warnings / ambiguities
  confirmation_binding
  lifecycle metadata
```

## Required review information

### Transaction identity and authority

The prepared change identifies the whole transaction through `change_request_id`, plus the target World, selected scope/profile context, exact parent revision, and the authority snapshot that matters to interpretation. `change_request_id` is the one transaction-level idempotency/recovery identity for the prepared/publication lifecycle. It is not any individual operation's `operation_id`, and an operation ID must never be used to recover or deduplicate the whole change. The prepared change must not imply that the current head remains unchanged forever; staleness is a commit-time condition.

### Interpreted operations

The prepared representation describes the semantic operations after validation and reference resolution. It must show:

- operation identity and client-local correlation;
- create versus existing-object use;
- object kind/label/meaning as interpreted under the profile;
- relationship predicate and fully resolved endpoints;
- source occurrence/evidence grounding;
- any omitted or rejected intent with a truthful reason.

It may present a stable application view while keeping DungeonMind contribution/materialization structures private.

### Prospective durable results

For each local object proposal, the prepared change exposes a stable prospective result identity or an equivalent reviewable handle. Confirm must use the same mapping. A relationship that targets a local object must show that resolution in the prepared view; it may not appear as an unresolved placeholder.

The public contract does not yet decide whether prospective identifiers are deterministic durable IDs, opaque result handles, or another stable representation. That choice must preserve exact confirm binding and one-transaction publication.

### Warnings and ambiguities

Warnings are inspectable and do not silently become identity decisions. Examples include similar existing objects, non-fatal projection ambiguity, or profile-specific advisory concerns. An unresolved semantic ambiguity that would make publication unsafe is a failure, not merely a warning.

### Source/evidence and occurrence summary

The review includes enough source identity to show what grounded the interpretation: artifact/revision/location identity, admissibility status, and relevant evidence summary. If the intent contains an explicit occurrence/mention binding, the prepared change shows that as a separate interpreted operation and does not infer it from the evidence summary. Creating a source-grounded object or assertion alone must not appear as a mention link. Internal evidence rows, SQL keys, and storage joins are not part of the public contract.

## Confirmation binding

The prepared change carries an opaque or otherwise tamper-evident binding over the exact facts that confirm must not change:

```text
change request / publication identity
world / scope / profile context
parent revision
source selector and admitted source/evidence identity
interpreted operations and local-reference mapping
identity state relevant to interpretation
binding/version metadata
```

The binding is not a durable World revision and is not a user-visible secret. Confirm must reject a changed intent, substituted source, changed parent, altered local mapping, or mismatched prepared identity. Token TTL/expiry is an open operational decision; expiry cannot weaken mismatch detection.

## Commit preconditions

Commit may proceed only when:

1. the caller explicitly confirms the prepared change;
2. the confirmation binding verifies;
3. the selected source/evidence pair can be re-proven;
4. the expected parent is still valid;
5. all local references still resolve within the prepared transaction;
6. DungeonMind accepts the governed publication;
7. an existing publication is recovered when the transaction-level `change_request_id` / publication identity was already applied.

If a precondition fails, no new child may be created by silently reinterpreting the request.

## Receipt expectations

A successful committed result must expose enough identity to establish:

```text
prepared change → change request / publication identity
parent revision → child revision
local object reference → durable object identity
source/evidence interpretation → child read-back
```

The receipt should include the child revision, durable object mappings, publication/recovery status, and an exact read-back locator. Whether it directly includes durable relationship IDs or expects exact child-revision navigation remains an open design question.

Receipt success is independent from subsequent client refresh success. A client must not resurrect committed local drafts because a read refresh failed.

## Lifecycle and recovery

Prepared changes may expire or become stale. A stale prepared change is not automatically rebased. The client must re-prepare so the new meaning can be reviewed.

Recovery takes the original transaction-level `change_request_id` / publication identity and binding. It may return `committed`, `not_committed`, or `outcome_unknown` according to the eventual authority contract. It must never use one semantic `operation_id` as a substitute for the whole transaction or create a second interpretation just because a prior response was lost.

## Failure classes

The initial semantic family is:

```text
prepared_change_not_found
prepared_change_expired
prepared_change_mismatch
stale_parent
source_inadmissible
invalid_local_reference
identity_conflict
authority_unavailable
integrity_failure
publication_failed
```

Exact names and recoverability are not frozen. The client-facing distinction between invalid meaning, stale authority, and unknown publication outcome is required.

## Privacy and representation boundary

The prepared contract must not leak:

- DungeonMind `GraphContribution` or persistence DTOs;
- internal evidence table IDs when an application identity is sufficient;
- database topology or SQL errors;
- signing key material;
- agent prompts, model state, or product conversation state.

An implementation may use those internally, but the application contract remains semantic and versioned.

## Explicitly undecided

Bootstrap intentionally leaves these for the next design slice:

1. prepared-change storage versus stateless signed binding;
2. expiry duration and invalidation mechanism;
3. prospective identity representation;
4. relationship receipt handle policy;
5. policy/human approval metadata shape;
6. whether a commit operation is a distinct public method or an implementation of a single publish façade.
