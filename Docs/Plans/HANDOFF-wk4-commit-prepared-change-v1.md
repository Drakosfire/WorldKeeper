---
pr_body_template: |
  ## Handoff pointer
  - Repository: Drakosfire/WorldKeeper
  - Direction: STEWARD → CODE
  - Slice: WK-4 — commit prepared change + exact child verification
  - Handoff: Docs/Plans/HANDOFF-wk4-commit-prepared-change-v1.md
  - Base: 3c1132e9c3a63571984704bf66bcf5bf482b7bd8
  - Accepted WK-3 head: 1c5e3d1262239ba8faf6fca75fbc0aa756d7a2a7
  - DungeonMind V5.4 merge: 6edb9e40d1dc930f537c66deb1afbd1b99002844

  The checked-in handoff, cumulative diff, focused tests, and exact-head
  verification are the review contract.
---

# HANDOFF — WK-4 commit prepared change + exact child verification

**Status:** READY FOR IMPLEMENTATION
**Repository:** `Drakosfire/WorldKeeper`
**Base:** `3c1132e9c3a63571984704bf66bcf5bf482b7bd8` — merged PR #4
**Accepted WK-3 head:** `1c5e3d1262239ba8faf6fca75fbc0aa756d7a2a7`
**WK-3 disposition:** `WK_3_PREPARE_WORLD_CHANGE_ACCEPTED`
**DungeonMind V5.4 merge:** `6edb9e40d1dc930f537c66deb1afbd1b99002844`
**Suggested branch:** `kernel/wk4-commit-prepared-change`
**Suggested PR:** `WK-4: commit prepared change and verify exact child`

## 1. Mission

Given one intact WK-3 `PreparedWorldChange` that the caller explicitly confirms:

```text
PreparedWorldChange
  → real DungeonMind V5.4 prospective publication
  → durable V5.3 receipt + V5.4 client-op mapping
  → exact immutable child read-back
  → VerifiedCommittedChange
```

WorldKeeper coordinates the call and reshapes the verified result. DungeonMind
continues to own allocation, CAS, atomic publication, replay/recovery, and graph
truth.

Primary question:

> Can WorldKeeper commit exactly one accepted WK-3 prepared meaning through the
> accepted DungeonMind V5.4 path, preserve DungeonMind's deterministic failure
> semantics, verify the exact published child independently, and return the
> durable client-op → ID mapping without adding a WorldKeeper recovery ledger,
> durable identity allocator, or second graph authority?

Final disposition:

```text
WK_4_COMMIT_AND_VERIFY_ACCEPTED
```

## 2. First commit — authority transition

Record PR #4:

```text
accepted head:
  1c5e3d1262239ba8faf6fca75fbc0aa756d7a2a7

merge:
  3c1132e9c3a63571984704bf66bcf5bf482b7bd8

disposition:
  WK_3_PREPARE_WORLD_CHANGE_ACCEPTED

verification:
  ruff PASS
  pyright PASS
  pytest 28 PASS
  diff-check PASS
  imports PASS
```

Then set:

```text
WK-3 COMPLETE
WK-4 ACTIVE — commit prepared change + exact child verification
```

Do not authorize persistence, HTTP, or product integration.

## 3. Core design decision — commit the prepared value, not an ID lookup

WK-4 implements:

```text
commit_prepared_change(
    prepared: PreparedWorldChange,
    confirmed_by: str,
) -> VerifiedCommittedChange
```

It does **not** implement an ID-only prepared-state lookup.

Reason:

- WK-3 intentionally created no prepared-state database.
- `PreparedWorldChange` is already immutable and digest-sealed.
- DungeonMind recovery uses `prepared_change_id` / publication identity.
- Adding a WorldKeeper store merely to recover the prepared payload would mix a
  separate persistence capability into WK-4.

The existing conceptual product surface:

```text
commit_change(prepared_change_id, confirmed_by)
```

remains a later workflow/adapter concern if a real caller demonstrates need for
server-side prepared lookup.

This is not permission to weaken identity:

```text
publication_id == prepared.prepared_change_id
```

remains binding.

## 4. Confirmation semantics

`confirmed_by` must be nonblank.

It means only:

```text
the caller explicitly authorized publication of this exact PreparedWorldChange
```

WK-4 does not claim `confirmed_by` is durable DungeonMind audit data.

Do not add actor fields to DungeonMind contracts, include `confirmed_by` in V5.4
allocation identity, mutate the sealed WK-3 plan, or create a confirmation-token
system.

If durable actor/audit provenance becomes required, stop and design it separately.

## 5. Application result

Add an immutable WorldKeeper-owned result equivalent to:

```text
VerifiedCommittedChange
  prepared_change_id
  dungeonmind_publication_id
  expected_parent_revision_id
  child_revision_id
  child_graph_payload_sha256

  object_results[]
    client_op_id
    durable_object_id

  assertion_results[]
    client_op_id
    durable_assertion_id
    semantic_role = fact | relationship

  verification
    exact_child_read_back = true
```

Map DungeonMind exactly:

```text
result_kind=entity    → durable_object_id
result_kind=assertion → durable_assertion_id
```

Do not invent a separate relationship ID. Native vNext relationships are
assertions.

## 6. Failure model

Preserve distinctions.

Before known commit:

```text
PreparedChangeIntegrityFailure
PreparedChangeStale
PreparedChangeConflict
CommitAuthorityIntegrityFailure
```

Genuine unknown outcome:

```text
KnowledgePublicationOutcomeUnknownError
→ CommittedChangeOutcomeUnknown
```

Expose at least:

```text
prepared_change_id
publication_id
expected_published_revision_id
retry_safe = true
```

Known commit but exact read-back unavailable:

```text
CommittedChangeVerificationUnavailable
  prepared_change_id
  publication_id
  child_revision_id
  retry_safe = true
  committed = true
```

This is **not** outcome-unknown. Retry the same prepared value; DungeonMind
replays the committed result and WorldKeeper retries verification.

Known commit but exact child incoherent/corrupt:

```text
CommittedChangeVerificationIntegrityFailure
  committed = true
  child_revision_id
```

Do not erase known durable success.

## 7. Narrow commit authority seam

Add a WorldKeeper application protocol conceptually:

```text
GovernedCommitAuthority
  commit_and_verify(prepared)
    -> CommitAuthorityWitness
```

WorldKeeper-owned witness:

```text
CommitAuthorityWitness
  space_id
  publication_id
  expected_parent_revision_id
  child_revision_id
  child_graph_payload_sha256
  results[]
```

`WorldChangeCommitter` validates confirmation, calls this seam, and reshapes the
witness into `VerifiedCommittedChange`.

Do not expose DungeonMind repository types through the top-level WorldKeeper
application contract.

## 8. DungeonMind commit adapter

Add a focused native-vNext adapter, e.g.:

```text
src/worldkeeper/integrations/dungeonmind/vnext_commit.py
```

For one prepared value:

1. call WK-3 `compile_prepared_change_to_dungeonmind(prepared)`;
2. load the **exact prepared parent revision** by ID, not current head;
3. verify parent ID, payload digest, and pinned descriptor refs;
4. decode/build exact `ParsedKnowledgeRevision`;
5. call real DungeonMind:
   `publish_prospective_contribution(...)`;
6. consume the returned V5.3/V5.4 aggregate;
7. independently read the exact published child by revision ID;
8. verify it before returning success.

Do not pre-check current head to help CAS. DungeonMind owns stale-parent
authority.

## 9. Exact-child verification

Verify:

```text
receipt/result identities agree
publication_id == prepared_change_id
child revision ID == returned published_revision_id
child.parent_revision_id == prepared.expected_parent_revision_id
child graph digest matches durable publication evidence
child exists and is published
```

Build expected result roles from WK-3 operations:

```text
CreateObject.client_op_id       → entity/object
CreateFact.client_op_id         → assertion/fact
CreateRelationship.client_op_id → assertion/relationship
UseExisting                      → no result
```

Require:

- one binding for every result-producing client op;
- no extra binding;
- exact result kind;
- durable ID exists in the exact child.

For relationships, verify exact child assertion:

```text
assertion ID == returned assertion ID
subject:
  durable source → exact durable entity
  result_of(x)   → durable entity returned for x
target:
  durable target → exact durable entity
  result_of(x)   → durable entity returned for x
```

For facts, verify:

```text
assertion ID == returned fact assertion ID
subject == returned object ID
predicate/value/metadata == prepared fact after WK-3 conversion
```

Verification is against the exact immutable child. It does not require the child
to remain current.

## 10. Replay semantics

Retry means the same exact `PreparedWorldChange`.

DungeonMind owns replay.

Required witness:

```text
commit A
→ descendant B advances head
→ retry A
→ same A receipt/mapping
→ verify historical child A
→ no head rewind / second event
```

Changed prepared content under the same prepared ID must fail WK-3 digest
binding before publication.

## 11. Canonical witness

Parent:

```text
ent:castle
```

Prepared:

```text
create npc-7
relationship rel-4:
  source = result_of(npc-7)
  predicate = lab:located_at
  target = ent:castle
```

Commit:

```text
one child revision
npc-7 → ent:<allocated>
rel-4 → asrt:<allocated>
```

Verify:

```text
allocated entity exists
allocated assertion exists
assertion.subject == npc-7 durable entity
assertion.target == ent:castle
child.parent == prepared expected parent
```

Exact retry returns the same IDs and child.

## 12. Files in scope

Bookkeeping:

```text
AGENTS.md
README.md
Docs/Steward/STEWARD-ANCHOR-worldkeeper.md
Docs/Roadmaps/ROADMAP-worldkeeper.md
Docs/Design/CONTRACT-prepared-world-change-v0.md
Docs/Design/CONTRACT-world-change-intent-v0.md
Docs/Design/DESIGN-governed-world-change-lifecycle.md
Docs/Plans/HANDOFF-wk4-commit-prepared-change-v1.md
```

Application:

```text
src/worldkeeper/application/contracts.py
src/worldkeeper/application/authority.py
src/worldkeeper/application/commit.py            # create
src/worldkeeper/application/__init__.py
src/worldkeeper/__init__.py
```

DungeonMind integration:

```text
src/worldkeeper/integrations/dungeonmind/vnext_commit.py  # create
src/worldkeeper/integrations/dungeonmind/__init__.py
```

Tests:

```text
tests/test_wk4_commit_prepared_change.py          # create
tests/test_dungeonmind_vnext_commit_boundary.py   # create
tests/test_package_boundary.py
```

Reuse the WK-3 compiler. Do not duplicate it.

Up to two extra test/helper paths are allowed if strictly required.

Any new persistence, HTTP, migration, product adapter, or DungeonMind source path
is a stop.

## 13. Explicitly out of scope

Do not implement:

```text
prepared-change database/store
commit by prepared_change_id lookup
WorldKeeper migrations
WorldKeeper durable recovery ledger
get_change_result
recover_change
HTTP/API host
DungeonBuddy integration
background jobs/workers
confirmation tokens/signatures
durable confirmed_by audit
similarity/dedupe
identity merge/reconciliation
source/evidence creation
occurrence/mention binding
general read façade
allocator reproduction
bridge/cutover
```

Do not modify DungeonMind.

## 14. Required adversarial proof

At minimum:

1. canonical create + dependent relationship commits and verifies;
2. object + fact maps entity/object and assertion/fact correctly;
3. `UseExisting` produces no result binding;
4. blank `confirmed_by` fails before publication;
5. tampered prepared value fails digest before publication;
6. stale parent remains typed stale;
7. changed request under same publication ID remains conflict;
8. post-commit response loss recovers through DungeonMind;
9. exact retry returns same child/mapping;
10. replay after descendant verifies historical child;
11. missing/extra/wrong-kind binding fails verification;
12. binding to absent child entity/assertion fails;
13. relationship subject/target mismatch fails;
14. fact predicate/value/metadata mismatch fails;
15. exact child unavailable after known commit reports committed verification
    unavailable, not outcome-unknown;
16. exact child corruption after known commit reports committed integrity failure;
17. genuine DungeonMind outcome-unknown maps retry-safe;
18. no WorldKeeper persistent mutation exists;
19. no allocator import/call exists;
20. WK-2/WK-3 tests remain green.

## 15. Verification

Run:

```bash
uv sync --locked
uv run ruff check .
uv run pyright
uv run pytest -q
git diff --check
uv run python -c "import dungeonmind; import worldkeeper"
```

Report exact head and installed DungeonMind SHA:

```text
6edb9e40d1dc930f537c66deb1afbd1b99002844
```

WorldKeeper currently has no GitHub Actions workflow, so exact-head local
verification is required.

## 16. Nano-commit story

```text
1. STEWARDSHIP: accept WK-3 and activate WK-4
2. BUILD: define verified commit result + failure contracts
3. BUILD: add DungeonMind V5.4 commit/verify adapter
4. BUILD: add WorldChangeCommitter
5. PROOF: adversarial commit/replay/exact-child witness
```

## 17. Acceptance rubric

- [ ] WK-3 recorded accepted/merged; WK-4 active.
- [ ] Core commit consumes immutable `PreparedWorldChange`.
- [ ] No prepared-state persistence introduced.
- [ ] Nonblank explicit confirmation required.
- [ ] WK-3 plan digest rechecked before publication.
- [ ] Real DungeonMind V5.4 publication path used.
- [ ] WorldKeeper does not allocate/predict IDs.
- [ ] Stale/conflict/integrity/outcome-unknown remain distinct.
- [ ] Known commit + readback unavailable is not mislabeled outcome-unknown.
- [ ] Exact immutable child independently read and verified.
- [ ] Object/fact/relationship mappings complete and exact.
- [ ] Replay returns same child/mapping after descendant.
- [ ] No recovery ledger/database/HTTP leaked in.
- [ ] WK-2/WK-3 tests remain green.
- [ ] Exact-head verification passes.

Final disposition:

```text
WK_4_COMMIT_AND_VERIFY_ACCEPTED
```

## 18. Stop conditions

Stop and rebrief if WK-4 requires:

- a WorldKeeper durable prepared store;
- a new DungeonMind contract;
- reproducing V5.4 allocation;
- changing accepted WK-3 prepared meaning;
- a second publication/recovery ledger;
- HTTP/product integration to prove correctness;
- durable confirmation/audit semantics;
- general graph query APIs;
- another independently useful capability.

## 19. Handback

Return only:

```text
PR / branch / base / exact head
commit list
changed paths
public commit/result/error shapes
canonical witness result
retry-after-descendant result
known-commit/readback-failure result
exact-head verification
DungeonMind pinned SHA
out-of-scope confirmation
final disposition
```
