# Contract — PreparedWorldChange v0

**Status:** WK-1 DESIGN CONTRACT — READY FOR REVIEW, implementation not authorized
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
  preparation_generation
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

## Minimal application capabilities

WK-1 fixes the smallest transport-neutral capability family as:

```text
prepare_change(intent) -> PreparedWorldChange
commit_prepared_change(prepared_change_id, confirmation)
  -> CommittedWorldChange
recover_change(change_request_id, prepared_change_id/generation, recovery_binding)
  -> RecoveryResult
read_exact_change_result(readback_locator)
  -> ExactWorldChangeReadback
```

Commit and recovery remain distinct semantic capabilities. A commit publishes
the exact reviewed preparation after explicit confirmation. Recovery establishes
the outcome of that same transaction when the caller may have lost the commit
response. A transport may combine them behind one implementation endpoint, but
it must preserve the distinction and the result states.

`read_exact_change_result` is intentionally narrower than the eventual World
query façade. It is the minimum read contract needed to prove one committed
change at one exact child revision.

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

WK-1 selects opaque prospective result handles. For each `create_object`, the
prepared change exposes a stable mapping:

```text
local_ref → prospective_object_ref
```

Relationship endpoints in the prepared view resolve to
`prospective_object_ref` or an exact durable object reference. The handle is
stable only for this `prepared_change_id` and generation; it is not a durable
object ID and does not expose DungeonMind's ID-generation algorithm. The
confirmation binding seals the mapping. After publication, the committed
receipt maps the same local reference to the emitted durable object ID.

This gives the reviewer an exact endpoint without creating a placeholder or
requiring a client to predict durable IDs.

### Warnings and ambiguities

Warnings are inspectable and do not silently become identity decisions. Examples include similar existing objects, non-fatal projection ambiguity, or profile-specific advisory concerns. An unresolved semantic ambiguity that would make publication unsafe is a failure, not merely a warning.

### Source/evidence and occurrence summary

The review includes enough source identity to show what grounded the interpretation: artifact/revision/location identity, admissibility status, and relevant evidence summary. If the intent contains an explicit occurrence/mention binding, the prepared change shows that as a separate interpreted operation and does not infer it from the evidence summary. Creating a source-grounded object or assertion alone must not appear as a mention link. Internal evidence rows, SQL keys, and storage joins are not part of the public contract.

For v0, the source representation is an immutable `source_revision_id` plus an
optional UTF-8 byte `SourceSpan` (`start_offset`, `end_offset`, and
`selected_text_digest`). Evidence links may use only the artifact/revision
identity when no exact occurrence was selected. An explicit
`link_source_occurrence` operation must carry the span and its target; the
prepared record displays that binding separately from supporting evidence.

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

The binding is not a durable World revision and is not a user-visible secret.
Confirm must reject a changed intent, substituted source, changed parent,
altered local mapping, or mismatched prepared identity. The binding includes
`prepared_change_id`, `change_request_id`, `preparation_generation`, the
canonical prepared-record digest, and a version/key identifier. A keyed
integrity mechanism may be used internally, but the public contract exposes
only the opaque binding.

The explicit confirmation supplied to commit is conceptually:

```text
Confirmation
  decision = confirm
  change_request_id
  prepared_change_id
  preparation_generation
  confirmation_binding
  actor/policy confirmation context
```

The actor/policy context records the authority for the confirmation; it does
not turn World Keeper into a product approval workflow or agent harness.

## Prepared-change storage decision

WK-1 selects a **retained-record plus tamper-evident-binding hybrid**.

The canonical prepared record is retained by a World Keeper workflow store and
is immutable for its preparation generation. The confirmation binding prevents
cross-record substitution or client mutation; it is not the sole source from
which a new interpretation is reconstructed. The workflow store is not a World
Graph, identity ledger, evidence authority, or publication store. It is an
adapter boundary that may be in-process for the first reference path and may
use durable storage when prepared changes must survive process restart.

This choice provides inspectability, explicit revocation/invalidation, and
safe recovery without requiring a network deployment or exposing a signed
DungeonMind contribution. If a non-durable deployment loses its prepared
record on restart, the safe result is `prepared_change_not_found` and
re-prepare; it must never reconstruct an unverified meaning from client input.
The durable publication/recovery record remains owned by DungeonMind.

Binding key rotation is operational rather than semantic: bindings carry a
version/key identifier, old verification keys remain available through the
maximum prepared lifetime, and a retired key makes the preparation
unconfirmable rather than weakening verification.

## Lifecycle and invalidation states

The prepared record and its transaction record distinguish these states:

```text
active
expired
invalidated
commit_pending
committed
not_committed
outcome_unknown
```

- `active`: this exact preparation may be explicitly confirmed while all
  authority checks pass.
- `expired`: the operational retention/confirmation window elapsed. It is not
  evidence that the meaning changed; it cannot be confirmed and requires
  re-prepare.
- `invalidated`: the meaning or authority no longer matches. Reasons include
  changed intent digest, changed source admissibility, changed identity/profile
  state, revoked policy, or an explicit caller cancellation.
- `commit_pending`: a governed publication attempt exists; the caller must not
  create a new generation until commit or recovery establishes its outcome.
- `committed`: one child revision and receipt are authoritative. Repeated
  commit/recovery returns that same result; it cannot be reinterpreted.
- `not_committed`: the authority proves no child was published for this
  generation. A safe re-prepare may advance the generation under the same
  `change_request_id`.
- `outcome_unknown`: the system cannot yet prove whether publication happened.
  Recovery is required; re-prepare and a new publication attempt are blocked.

These are not interchangeable errors. A stale parent is a correctness
invalidation, not expiry. A changed client intent is a binding mismatch, not a
stale-parent rebase. A lost response is an unknown outcome, not permission to
retry with a new meaning.

Only an `active` prepared record may transition to `expired`. A
`commit_pending` or `outcome_unknown` transaction retains the recovery record
until its publication outcome is proven; prepared-payload retention and
publication-outcome retention are separate lifecycle concerns.

## Re-prepare and publication identity

Re-prepare retains the same `change_request_id` for the same logical client
transaction and creates a new `prepared_change_id` with an incremented
`preparation_generation`, but only after the prior generation is known
`not_committed` or otherwise safely invalidated before any publication attempt.

If the prior generation is `committed` or `outcome_unknown`, prepare cannot
silently create a new meaning under that request identity. The caller must
recover first; a committed result closes the transaction, and an unknown
result remains blocked until resolved. A new unrelated client transaction uses
a new `change_request_id`.

When commit begins, Keeper allocates or resolves exactly one internal
`publication_operation_id` for the pair
`(change_request_id, preparation_generation)`. Retries of that governed
publication attempt reuse the same internal identity and exact binding. A
later generation is allowed a new internal publication identity only after the
earlier generation is proven `not_committed`; the transaction record still
enforces at most one committed publication outcome for the
`change_request_id`.

## Commit preconditions

Commit may proceed only when:

1. the caller explicitly confirms the prepared change;
2. the confirmation binding verifies;
3. the selected source/evidence pair can be re-proven;
4. the expected parent is still valid;
5. all local references still resolve within the prepared transaction;
6. DungeonMind accepts the governed publication;
7. an existing publication is recovered when the transaction-level `change_request_id` and its generation-bound publication identity were already applied.

If a precondition fails, no new child may be created by silently reinterpreting the request.

## Receipt expectations

A successful committed result must expose enough identity to establish:

```text
prepared change → change request / publication identity
parent revision → child revision
local object reference → durable object identity
source/evidence interpretation → child read-back
```

The receipt includes the child revision, durable object mappings, publication/recovery status, and an exact read-back locator. WK-1 chooses to return direct relationship result identities for v0:

```text
relationship operation_id → durable relationship_id
```

The mapping is returned only after the relationship exists in the committed
child and is not a publication/recovery identity. Exact child read-back remains
mandatory and proves the returned relationship at `published_revision_id`.

An explicit occurrence-binding operation may likewise return an opaque durable
binding identity or exact child selector as the profile requires; it must not be
inferred from evidence support.

Receipt success is independent from subsequent client refresh success. A client must not resurrect committed local drafts because a read refresh failed.

## Lifecycle and recovery

Prepared changes may expire or become stale. A stale prepared change is not automatically rebased. The client must re-prepare so the new meaning can be reviewed.

Recovery takes the original transaction-level `change_request_id`, the
generation-bound prepared identity, and the recovery binding. It returns one
of:

```text
committed        → the original CommittedWorldChange receipt
not_committed    → authority proves no child was published for that generation
outcome_unknown  → publication outcome still cannot be proven
```

It must never use one semantic `operation_id` as a substitute for the whole
transaction or create a second interpretation just because a prior response
was lost.

## Public contract versus adapter boundary

The public World Keeper contract consists of the semantic intent, prepared
change, explicit confirmation, committed result, recovery result, exact
read-back, source references, and durable result identities described here.

The Keeper↔DungeonMind adapter may additionally use a
`publication_operation_id`, finalized contribution/materialization values,
evidence-record DTOs, identity-ledger records, repository ports, database
transactions, signing keys, and workflow-store records. Those are internal
mechanisms. They must not become required client inputs or public review
representations merely because the first in-process implementation uses them.

## Committed result and exact read-back

The semantic `CommittedWorldChange` result is:

```text
CommittedWorldChange
  change_request_id
  prepared_change_id
  preparation_generation
  published_revision_id
  parent_revision_id
  object_results: local_ref → durable_object_id
  relationship_results: operation_id → durable_relationship_id
  occurrence_binding_results (only for explicit bindings)
  publication_status = committed | recovered
  readback_locator
```

`read_exact_change_result(readback_locator)` is pinned to
`published_revision_id`. It returns the exact created objects, requested
relationships, explicit occurrence bindings, and their admissible supporting
evidence, or a typed absence/inadmissibility result. It never falls back to the
current World head, a later revision, a client-local overlay, or a latest-match
query. This capability proves durable result truth; it is not a replacement
for the later general World read/query façade.

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

## Deliberately left to implementation or later design

WK-1 resolves the semantic contract. These implementation details remain open
without reopening the contract:

1. the concrete prepared-workflow store technology and deployment retention
   configuration;
2. exact expiry duration within the contract's maximum verification window;
3. the concrete keyed-integrity algorithm and key-management provider;
4. policy/human approval metadata shape beyond the explicit confirmation fact;
5. whether a transport exposes the four capabilities as separate routes or a
   combined publish/recovery host operation.
