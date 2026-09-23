# Steward Anchor — WorldKeeper

**Status:** WK-1 ACCEPTED / WK-2 ACCEPTED / WK-3 BLOCKED
**Implementation:** WK-3 NOT AUTHORIZED
**Repository:** `WorldKeeper`
**Current decision:** [ownership simplification](../Design/DECISION-worldkeeper-ownership-simplification.md)

## Pickup order

Read this anchor first, then the current architecture, boundary, lifecycle,
versioned contracts, source index, and roadmap. The anchor outranks the other
WorldKeeper documents. Historical sources are evidence only.

## Current ownership

DungeonBuddy owns product interaction, reversible drafts, explicit identity
choice, similarity presentation, review UX, and result presentation.

WorldKeeper is an application transaction coordinator/compiler. It owns intent
shape, semantic interpretation, exact same-transaction reference resolution,
prepared meaning, confirmation coordination, and verified-result reshaping. It
does not own durable graph identity, a second graph, policy/admission truth,
general World reads, or a durable recovery ledger.

DungeonMind owns durable object and relationship identity, source/provenance,
semantic profile and scope/admission policy, immutable revisions, expected
parent/CAS, atomic publication, durable publication outcome/recovery, and
general World reads.

## Accepted invariants

- Prepare is non-mutating and binds exact parent, authority, source, evidence,
  and semantic meaning.
- Local references resolve to one exact prospective create result before
  confirmation; a prospective handle is not a future durable ID.
- DungeonMind must allocate and substitute durable IDs consistently during one
  atomic publication. Object-first publication and dependent repair are barred.
- Confirmation publishes only the exact prepared meaning; stale authority fails
  closed and requires re-prepare.
- Every immutable `prepared_change_id` maps one-to-one to a stable DungeonMind
  publication/idempotency identity; retries and lost responses use that durable
  authority, not a second Keeper recovery ledger.
- Evidence support does not imply occurrence or mention binding.
- Similarity is advisory; automatic merge/dedupe is not authorized.
- Exact immutable child read-back is mandatory before a successful result.

## Gating decision

At DungeonMind `origin/main` `1fc03aa21e406d9a7cb07d0e4792e202fe281375`, the
materialization contract requires durable relationship endpoint IDs. It does
not expose the prospective-publication primitive required by WK-3. The next
implementation is a small DungeonMind-owned contract and proof, not WorldKeeper
runtime work.

```text
WK-3 implementation is BLOCKED
until DungeonMind prospective-reference atomic publication is available
and proved at its owning boundary.
```

## Explicit stop conditions

Stop rather than broaden authority if work would add WorldKeeper persistence,
HTTP, migrations, agent harnesses, vector storage, automatic dedupe, generic
reconciliation, a general read façade, `recover_change`, mandatory
`preparation_generation`, or any WK-3 implementation before the DungeonMind
gate is accepted.

Earlier WK-1 and WK-2 documents and commits remain truthful historical evidence;
they are not silently rewritten. Their deterministic-ID and recovery-ledger
choices are superseded by the current ownership decision.
