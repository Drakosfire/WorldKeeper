# Steward Anchor — WorldKeeper

**Status:** WK-1 THROUGH WK-5 COMPLETE / V3 COMPATIBILITY MERGED
**Implementation:** NO ACTIVE IMPLEMENTATION LEASE
**Repository:** `WorldKeeper`
**Current decision:** [ownership simplification](../Design/DECISION-worldkeeper-ownership-simplification.md)

## Current merged state

Re-anchored to `main@b692266a55276536fa6b90a0464e19961ce89324`. The
open-PR inventory was empty before this settlement branch.

- WK-5 consumer composition PR #7: head
  `c1aeb157e14f2c07036e6346e93b2e47a228f387`, merged as
  `8a5efb96b69dc9ca136288ecc80f67c1ed027bd1`.
- Bounded V3 custom-predicate compatibility PR #8: reviewed head
  `49a8620f066ce7ef8972a699020c012f50af9158`, merged as
  `a0a70db275cf6c5f3876fe7b4d2a557de12388f5`.
- Governance PR #9: head `d5e2d56b025629ea0e95d922b4d29974254d038e`,
  merged as `b692266a55276536fa6b90a0464e19961ce89324`. `AGENTS.md` now
  carries stable operating law; this anchor carries changing workstream state.

These merges close the prior WK-5 and V3 compatibility lanes. They do not
activate a successor. Any new implementation needs its own bounded authority.

## Completed bounded custom-predicate compatibility

The completed custom-predicate follow-up pinned DungeonMind PR #77's reviewed
runtime head `0f709d76fdc53bac9c9258d1751463ae2c76ca71`, preserved the sealed
`dm_semantic_profile_v3` descriptor through WorldKeeper prepare/compile, and
proved an authored `entity_ref` relationship term survives unchanged. It did
not change WK-3/WK-4 lifecycle semantics, choose predicate meaning for a
consumer, initialize a World, or migrate a V2-pinned World to V3.
DungeonMind #77 merged as `a9051f02dfd95e051a83c1d74b26bb04a2b3e5bf`
after `SEMANTIC_PROFILE_V3_SUBSTANTIVE_PASS`. DungeonMind PR #78 finalized its
authority at reviewed head `19cf798d9b8ed9c63eb41d585b5e6ad46d99f5a0`,
Cycle 2 PASS `5322577539`, and merge
`54a419f99057d96e0c4e7620d8bd8ccc6816fb62`. The accepted disposition is
`SEMANTIC_PROFILE_V3_OPEN_PREDICATE_NAMESPACES_ACCEPTED`. This accepts scoped
V3 predicates; it does not provide a V2→V3 profile transition for existing Worlds.

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
- Every immutable `prepared_change_id` deterministically derives one stable
  DungeonMind publication/idempotency identity (or is itself that identity).
  DungeonMind durably records and replays the outcome; retries and lost
  responses reconstruct it from the caller-held prepared ID alone, not a second
  Keeper recovery ledger.
- Evidence support does not imply occurrence or mention binding.
- Similarity is advisory; automatic merge/dedupe is not authorized.
- Exact immutable child read-back is mandatory before a successful result.

## DungeonMind prerequisite disposition

DungeonMind PR #75 V5.4 is accepted at
`c7700f98e62732cbd1c021270f5366a77c24ea9b`, final PASS `5296514025`, disposition
`V5_4_PROSPECTIVE_REFERENCE_PUBLICATION_ACCEPTED`, and merged to `main` at
`6edb9e40d1dc930f537c66deb1afbd1b99002844`.

```text
WK-3 COMPLETE — accepted head `1c5e3d1262239ba8faf6fca75fbc0aa756d7a2a7`,
merged as `3c1132e9c3a63571984704bf66bcf5bf482b7bd8`
WK-4 COMPLETE — accepted head `95f29ce519312690419b89727605eeac26e6e98b`,
merged as `cdbd13ca981f9ff062c2cbb750f320a28626f9a3`
WK-5 COMPLETE — consumer composition PR #7 merged as
  `8a5efb96b69dc9ca136288ecc80f67c1ed027bd1`
V3 COMPATIBILITY MERGED — PR #8 merged as
  `a0a70db275cf6c5f3876fe7b4d2a557de12388f5`
```

V5.4 proves transaction-local prospective handles, DungeonMind-owned
type-separated allocation, substitution before materialization, create-new
parent-collision rejection, predicted-ID bypass rejection, repository-boundary
allocation validation, atomic revision/head/event/receipt/result-map commit,
and exact replay/lost-response recovery. WorldKeeper must not reproduce the
allocator.

## Explicit stop conditions

Stop rather than broaden authority if work would add WorldKeeper persistence,
HTTP, migrations, agent harnesses, vector storage, automatic dedupe, generic
reconciliation, a general read façade, `recover_change`, prepared persistence,
or any V5.4 allocator logic. The completed WK-5 lease did not authorize new
semantics, product mapping, source admission, or first-world initialization;
none is authorized by this settlement.

Earlier WK-1 and WK-2 documents and commits remain truthful historical evidence;
they are not silently rewritten. Their deterministic-ID and recovery-ledger
choices are superseded by the current ownership decision.
