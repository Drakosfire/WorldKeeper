---
pr_body_template: |
  ## Handoff pointer
  - Repository: Drakosfire/WorldKeeper
  - Direction: STEWARD → CODE
  - Slice: WK-5 — consumer composition boundary
  - Handoff: Docs/Plans/HANDOFF-wk5-consumer-composition-boundary-v1.md
  - Base: cdbd13ca981f9ff062c2cbb750f320a28626f9a3
  - WK-4 accepted head: 95f29ce519312690419b89727605eeac26e6e98b
  - WK-4 merge: cdbd13ca981f9ff062c2cbb750f320a28626f9a3
  - DungeonMind V5.4 merge: 6edb9e40d1dc930f537c66deb1afbd1b99002844

  The checked-in handoff, cumulative diff, focused tests, and exact-head
  verification are the review contract.
---

# HANDOFF — WK-5 consumer composition boundary

**Status:** READY FOR IMPLEMENTATION  
**Repository:** `Drakosfire/WorldKeeper`  
**Implementation branch:** `kernel/wk5-consumer-composition-boundary`  
**Base:** `cdbd13ca981f9ff062c2cbb750f320a28626f9a3`  
**WK-4 accepted head:** `95f29ce519312690419b89727605eeac26e6e98b`  
**WK-4 merge:** `cdbd13ca981f9ff062c2cbb750f320a28626f9a3`  
**WK-4 disposition:** `WK_4_COMMIT_AND_VERIFY_ACCEPTED`  
**DungeonMind V5.4 merge:** `6edb9e40d1dc930f537c66deb1afbd1b99002844`  
**Suggested PR title:** `WK-5: expose consumer composition boundary`

## 1. Why this is next

WK-3 and WK-4 now prove the complete existing-world semantic transaction:

```text
WorldChangeIntent
→ PreparedWorldChange
→ explicit confirmation
→ DungeonMind V5.4 atomic publication
→ exact immutable child verification
→ VerifiedCommittedChange
```

The remaining gap is not another semantic capability. It is **consumer
composition**.

A real client should not need to know how to manually assemble:

```text
DungeonMindVNextPreparationAuthority
+ WorldChangePreparer
+ DungeonMindVNextCommitAuthority
+ WorldChangeCommitter
```

to use the accepted lifecycle.

Current DungeonBuddy boundary evidence also identifies direct DungeonMind
publication-driver code as debt and says a later product migration must answer
how product confirmation works without Buddy owning DungeonMind publication.
WorldKeeper now has the semantics required for ordinary existing-world changes,
but it does not yet expose one stable consumer-facing runtime seam.

WK-5 closes only that gap.

## 2. Mission

Expose the accepted WK-3/WK-4 lifecycle as one small, stable in-process consumer
contract and one DungeonMind-backed composition implementation.

Target use:

```python
service = DungeonMindWorldKeeperRuntime(...)

prepared = service.prepare_change(intent)

# caller reviews prepared meaning

result = service.commit_prepared_change(
    prepared,
    confirmed_by="user:keeper",
)
```

The consumer contract must remain transport-neutral:

```text
WorldChangeService
  prepare_change(intent) -> PreparedWorldChange
  commit_prepared_change(prepared, confirmed_by) -> VerifiedCommittedChange
```

The DungeonMind-specific runtime wires the already accepted services and
adapters. It does not create a second implementation path.

Final disposition:

```text
WK_5_CONSUMER_COMPOSITION_ACCEPTED
```

## 3. First implementation commit — authority transition

Record WK-4 as complete:

```text
PR #5
accepted head:
  95f29ce519312690419b89727605eeac26e6e98b

merge:
  cdbd13ca981f9ff062c2cbb750f320a28626f9a3

disposition:
  WK_4_COMMIT_AND_VERIFY_ACCEPTED

verification:
  ruff PASS
  pyright PASS / 0 errors
  pytest 50 PASS
  diff-check PASS
  imports PASS
```

Then authorize exactly:

```text
WK-4 COMPLETE
WK-5 ACTIVE — CONSUMER COMPOSITION BOUNDARY ONLY
```

Do not use this transition to authorize product integration, HTTP, persistence,
new write semantics, source admission, or first-world initialization.

## 4. Public application contract

Add a transport-neutral protocol, preferred name:

```python
class WorldChangeService(Protocol):
    def prepare_change(
        self,
        intent: WorldChangeIntent,
    ) -> PreparedWorldChange: ...

    def commit_prepared_change(
        self,
        prepared: PreparedWorldChange,
        confirmed_by: str,
    ) -> VerifiedCommittedChange: ...
```

Preferred path:

```text
src/worldkeeper/application/service.py
```

Requirements:

- imports only WorldKeeper application contracts / typing;
- no DungeonMind imports;
- no Buddy imports;
- no transport concepts;
- no repository concepts;
- no persistence lifecycle;
- no new error vocabulary.

Export `WorldChangeService` from:

```text
worldkeeper.application
worldkeeper
```

This protocol is the stable type that a product integration may depend on later.

## 5. DungeonMind composition runtime

Add one concrete integration composition root, preferred:

```text
src/worldkeeper/integrations/dungeonmind/runtime.py

DungeonMindWorldKeeperRuntime
```

It may depend on the existing accepted DungeonMind integration boundary.

Constructor shape may vary slightly, but should remain equivalent to:

```python
DungeonMindWorldKeeperRuntime(
    *,
    repository: KnowledgeRevisionRepository,
    domain_contract: DomainContractDescriptor,
    semantic_profile: SemanticProfileDescriptorV2,
    clock: Callable[[], datetime],
    prepared_id_factory: Callable[[], str] | None = None,
)
```

Internally it must construct exactly:

```text
DungeonMindVNextPreparationAuthority(repository)
→ WorldChangePreparer(...)

DungeonMindVNextCommitAuthority(repository)
→ WorldChangeCommitter(...)
```

and expose only:

```text
prepare_change(...)
commit_prepared_change(...)
```

Both operations must use the **same repository instance** supplied at
composition.

Export the concrete runtime from:

```text
worldkeeper.integrations.dungeonmind
```

Do not export DungeonMind-specific types from top-level `worldkeeper`.

## 6. No semantic reimplementation

WK-5 is wiring, not another implementation of prepare or commit.

The runtime must delegate to:

```text
WorldChangePreparer.prepare_change
WorldChangeCommitter.commit_prepared_change
```

It must not independently:

- validate intent;
- generate or rewrite prepared IDs;
- compile prospective contributions;
- allocate durable IDs;
- call DungeonMind publication functions;
- inspect publication receipts;
- verify exact children;
- map result bindings;
- catch/remap accepted WorldKeeper errors.

The accepted WK-3/WK-4 services remain the only semantic application paths.

## 7. Error behavior

All current application errors pass through unchanged.

Examples:

```text
InvalidWorldChange
PreparedChangeIntegrityFailure
PreparedChangeStale
PreparedChangeConflict
CommitAuthorityIntegrityFailure
CommittedChangeOutcomeUnknown
CommittedChangeVerificationUnavailable
CommittedChangeVerificationIntegrityFailure
```

WK-5 adds no wrapper error and no generic `WorldKeeperError`.

A consumer must retain the distinctions already established by WK-3/WK-4.

## 8. Production ID behavior

If `prepared_id_factory` is omitted, the composition runtime must preserve the
existing WorldKeeper-owned default fresh opaque ID generation.

Deterministic factory injection remains test/composition support only.

Do not move ID generation into the DungeonMind runtime class.

## 9. Consumer witness

Required canonical witness:

```text
existing parent:
  ent:castle

intent:
  create npc-7
  create rel-4
    source = result_of(npc-7)
    predicate = lab:located_at
    target = ent:castle
```

Through only the composed runtime:

```text
prepare_change
→ immutable PreparedWorldChange

commit_prepared_change
→ one VerifiedCommittedChange
→ npc-7 maps to ent:<allocated>
→ rel-4 maps to asrt:<allocated>
→ exact child read-back true
```

Then retry the same prepared value through the same runtime and prove:

```text
same child
same mapping
no duplicate publication event
```

This test is not permission to duplicate the WK-4 verification suite. It is a
consumer-boundary proof that composition preserves it.

## 10. Boundary fitness proof

Add focused source/contract checks proving:

### Application protocol stays generic

```text
src/worldkeeper/application/service.py
```

must contain no imports from:

```text
dungeonmind
DungeonBuddy
FastAPI
database drivers
```

### Composition does not bypass accepted services

```text
src/worldkeeper/integrations/dungeonmind/runtime.py
```

must not import/call:

```text
publish_prospective_contribution
publish_prospective_publication
allocate_prospective_result_id
get_prospective_publication
```

It should wire the existing WK-3/WK-4 classes, not their underlying primitives.

### Top-level package stays transport-neutral

`worldkeeper` may export `WorldChangeService` and existing application
contracts/errors/services.

It must not top-level export:

```text
KnowledgeRevisionRepository
DomainContractDescriptor
SemanticProfileDescriptorV2
DungeonMindWorldKeeperRuntime
```

The concrete runtime remains under the explicit DungeonMind integration
namespace.

## 11. Scope

Preferred runtime paths:

```text
src/worldkeeper/application/service.py                         # create
src/worldkeeper/application/__init__.py
src/worldkeeper/__init__.py
src/worldkeeper/integrations/dungeonmind/runtime.py            # create
src/worldkeeper/integrations/dungeonmind/__init__.py
```

Preferred tests:

```text
tests/test_wk5_consumer_composition.py                         # create
tests/test_package_boundary.py
```

Authority/bookkeeping may update:

```text
AGENTS.md
Docs/Steward/STEWARD-ANCHOR-worldkeeper.md
Docs/Roadmaps/ROADMAP-worldkeeper.md
Docs/Architecture/ARCHITECTURE-worldkeeper.md
Docs/Architecture/BOUNDARY-dungeonbuddy-worldkeeper-dungeonmind.md
Docs/Design/DESIGN-governed-world-change-lifecycle.md
Docs/Plans/HANDOFF-wk5-consumer-composition-boundary-v1.md
```

### README collision rule

PR #6 (`docs/worldkeeper-why-it-exists`) is a disjoint documentation effort
but also edits `README.md`.

Do not make WK-5 depend on PR #6.

Avoid editing `README.md` in WK-5 while PR #6 is open. If PR #6 merges before
WK-5 is ready, rebase onto current `main` and only then make any status-only
README correction if genuinely necessary.

## 12. Explicit non-goals

Do not add:

```text
DungeonBuddy imports or DTOs
Buddy proposal translation
Buddy Graph Review adapters
HTTP routes / FastAPI
prepared-change persistence
WorldKeeper database tables or migrations
get_change_result
recover_change
commit-by-ID lookup
source/evidence creation or admission
first-world initialization
occurrence/mention binding
similarity/dedupe
merge/split/reconciliation
general World reads
background workers
new DungeonMind contracts
DungeonMind allocator logic
new publication semantics
```

Do not modify DungeonMind.

## 13. Why Buddy mapping is not in this PR

A future Buddy consumer still owns translation from product-local drafts and
review UX into the already accepted `WorldChangeIntent`.

That future migration must decide, with Buddy authority, which existing product
write flow is the first real consumer.

WK-5 must not guess that mapping inside WorldKeeper.

This slice makes the boundary consumable; it does not perform the product
migration.

## 14. Required tests

At minimum:

1. `DungeonMindWorldKeeperRuntime` structurally satisfies `WorldChangeService`;
2. canonical prepare + commit works only through the runtime public methods;
3. same prepared retry returns the same exact verified result/no extra event;
4. runtime default preparation generates distinct fresh IDs;
5. injected deterministic ID factory is preserved for tests;
6. blank confirmation still raises the existing confirmation failure;
7. stale prepared change still raises `PreparedChangeStale` unchanged;
8. tampered prepared value still raises `PreparedChangeIntegrityFailure` unchanged;
9. protocol source has no DungeonMind/product/transport imports;
10. runtime source has no direct publication/allocator/recovery primitive calls;
11. top-level package does not leak DungeonMind integration types;
12. WK-2/WK-3/WK-4 suite remains green.

Do not recreate every WK-4 adversarial corruption test through the facade.

## 15. Verification

Run:

```bash
uv sync --locked
uv run ruff check .
uv run pyright
uv run pytest -q
git diff --check
uv run python -c "import worldkeeper; import worldkeeper.integrations.dungeonmind"
```

Report:

```text
exact head
test count
DungeonMind installed SHA:
6edb9e40d1dc930f537c66deb1afbd1b99002844
```

WorldKeeper currently has no GitHub Actions workflow, so exact-head local
verification remains required in the handback.

## 16. Commit story

Recommended:

```text
1. STEWARDSHIP: accept WK-4 and activate WK-5
2. BUILD: define WorldChangeService consumer contract
3. BUILD: compose DungeonMind WorldKeeper runtime
4. PROOF: consumer boundary and regression witness
```

Keep commits independently reviewable.

## 17. Acceptance rubric

- [ ] WK-4 recorded complete at exact accepted/merge SHAs.
- [ ] WK-5 authority is composition-only.
- [ ] `WorldChangeService` contains only accepted prepare/commit methods.
- [ ] generic application contract imports no DungeonMind/product/transport code.
- [ ] concrete DungeonMind runtime lives only in integration namespace.
- [ ] runtime wires existing WK-3/WK-4 services rather than reimplementing them.
- [ ] same repository instance backs prepare and commit.
- [ ] existing errors pass through unchanged.
- [ ] production default prepared-ID ownership remains WorldKeeper.
- [ ] no persistence, HTTP, status API, or product mapping enters the slice.
- [ ] canonical consumer prepare→review→commit witness passes.
- [ ] retry remains exactly idempotent.
- [ ] top-level package does not leak DungeonMind types.
- [ ] all prior tests remain green.
- [ ] exact-head verification passes.

Final disposition:

```text
WK_5_CONSUMER_COMPOSITION_ACCEPTED
```

## 18. Successor after WK-5

WK-5 should leave WorldKeeper's existing-world transaction bootstrap
**consumer-ready**.

The next justified work is expected to be a **DungeonBuddy consumer-integration
handoff**, selecting one real Buddy governed-write workflow and replacing its
direct publication-driver responsibility with the `WorldChangeService`
boundary.

That is separate repository authority and is not authorized by this handoff.

Do not invent WK-6 merely to keep WorldKeeper busy. A later WorldKeeper semantic
capability requires concrete consumer evidence.

## 19. Stop conditions

Stop and return to Steward if implementation requires:

- changing `WorldChangeIntent`, `PreparedWorldChange`, or
  `VerifiedCommittedChange` semantics;
- a new DungeonMind contract;
- a WorldKeeper database or durable lifecycle;
- Buddy-specific product fields;
- HTTP or service hosting;
- source admission / initialization;
- a third application operation beyond accepted prepare + commit;
- direct use of DungeonMind publication/allocation primitives from the new
  composition runtime.

## 20. Handback

Return only:

```text
PR / branch / base / exact head
commit list
changed paths
actual WorldChangeService shape
actual DungeonMindWorldKeeperRuntime constructor + public methods
consumer witness result
retry result
boundary/source-guard results
exact-head verification
DungeonMind pinned SHA
out-of-scope confirmation
final disposition
```
