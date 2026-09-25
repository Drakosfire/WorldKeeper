# Steward Anchor — WorldKeeper

**Status:** WK-1/WK-2/WK-3/WK-4 ACCEPTED / WK-5 ACTIVE
**Implementation:** LIMITED AUTHORIZATION — WK-5 CONSUMER COMPOSITION ONLY
**Repository:** `WorldKeeper`
**Current decision:** [ownership simplification](../Design/DECISION-worldkeeper-ownership-simplification.md)

## Bounded custom-predicate compatibility amendment

The user-authorized custom-predicate follow-up permits a surgical compatibility
change against DungeonMind PR #77: pin its exact commit, preserve the sealed
`dm_semantic_profile_v3` descriptor through WorldKeeper prepare/compile, and
prove an authored `entity_ref` relationship term survives unchanged. This is
not authorization to change WK-3/WK-4 lifecycle semantics, choose predicate
meaning for a consumer, initialize a World, or migrate a V2-pinned World to V3.
The dependency PR remains a prerequisite until accepted and merged.

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
WK-5 ACTIVE — expose accepted prepare + commit through composition only
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
or any V5.4 allocator logic. WK-5 also stops if composition requires new
semantics, product mapping, source admission, or first-world initialization.

Earlier WK-1 and WK-2 documents and commits remain truthful historical evidence;
they are not silently rewritten. Their deterministic-ID and recovery-ledger
choices are superseded by the current ownership decision.
