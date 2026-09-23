---
pr_body_template: |
  ## Handoff pointer
  - Repository: Drakosfire/WorldKeeper
  - Direction: STEWARD → CODE
  - Slice: WK-3 — prepare World change
  - Handoff: Docs/Plans/HANDOFF-wk3-prepare-world-change-v1.md
  - Base: e84f6bea90ba05c25be83b6b2c7c08751cac2608
  - DungeonMind prerequisite: V5.4 accepted head c7700f98e62732cbd1c021270f5366a77c24ea9b
  - DungeonMind merge: 6edb9e40d1dc930f537c66deb1afbd1b99002844

  The checked-in handoff, cumulative diff, focused tests, and independently
  rerun verification are the review contract. The PR body is transport metadata.
---

# HANDOFF — WK-3 prepare World change

**Created:** 2026-09-23
**Status:** READY FOR IMPLEMENTATION — DungeonMind prerequisite accepted
**Repository:** `Drakosfire/WorldKeeper`
**Canonical handoff path:** `Docs/Plans/HANDOFF-wk3-prepare-world-change-v1.md`
**Suggested branch:** `kernel/wk3-prepare-world-change`
**Suggested PR title:** `WK-3: prepare World change against DungeonMind V5.4`
**WorldKeeper implementation base:** `e84f6bea90ba05c25be83b6b2c7c08751cac2608`
**Predecessor:** WorldKeeper PR #3 — ownership/gate re-anchor
**DungeonMind accepted prerequisite:** PR #75 — V5.4 prospective-reference identity allocation + substitution
**DungeonMind accepted head:** `c7700f98e62732cbd1c021270f5366a77c24ea9b`
**DungeonMind final PASS review:** `5296514025`
**DungeonMind disposition:** `V5_4_PROSPECTIVE_REFERENCE_PUBLICATION_ACCEPTED`
**DungeonMind merged main:** `6edb9e40d1dc930f537c66deb1afbd1b99002844`
**Named successor:** `WK-4 — commit prepared change + exact child verification`

> This is a **prepare-only** implementation slice.
>
> It authorizes WorldKeeper to interpret, validate, bind, and compile one
> reviewable prospective transaction against exact DungeonMind authority.
> It does **not** authorize publication.
>
> No code in this PR may call `publish_prospective_contribution`,
> `publish_governed_materialization`, `publish_publication`,
> `publish_prospective_publication`, or any other DungeonMind mutation seam.

---

## §1 Mission and primary question

### Mission

Implement the first runtime capability authorized by the re-anchored ownership
model:

```text
WorldChangeIntent
  + exact current DungeonMind vNext authority
  + exact pinned DomainContract / SemanticProfile descriptors
→ PreparedWorldChange
  + exact compile-ready DungeonMind V5.4 prospective plan
  + no durable mutation
```

The prepared result must be reviewable without exposing or predicting future
DungeonMind entity/assertion IDs.

### Primary question

> Given one semantic World change intent containing create-new objects, explicit
> existing-object references, object facts, and relationships that may depend on
> same-intent creates, can WorldKeeper produce one immutable, reviewable
> `PreparedWorldChange` bound to the exact current DungeonMind parent and
> authority context, and losslessly compile it into the accepted DungeonMind
> V5.4 prospective contract without publishing, allocating, predicting, or
> reserving durable graph identities?

A PASS answers only that question.

It does **not** prove commit, recovery orchestration, product integration, HTTP,
or prepared-workflow persistence.

---

## §2 Authority transition required before runtime work

The checked-in WorldKeeper authority is still deliberately stale: it says WK-3
is blocked against DungeonMind `1fc03aa…`.

The first commit of this PR must update repository authority to the now-true
state:

```text
WK-1 ACCEPTED
WK-2 ACCEPTED
DungeonMind V5.2 ACCEPTED
DungeonMind V5.3 ACCEPTED
DungeonMind V5.4 ACCEPTED

WK-3 ACTIVE
WK-3 IMPLEMENTATION AUTHORIZED
```

Record:

```text
DungeonMind PR #75
accepted head:
  c7700f98e62732cbd1c021270f5366a77c24ea9b

final PASS:
  5296514025

disposition:
  V5_4_PROSPECTIVE_REFERENCE_PUBLICATION_ACCEPTED

merge:
  6edb9e40d1dc930f537c66deb1afbd1b99002844
```

The authority update must explicitly say what V5.4 proved:

- prospective `client_op_id` handles are transaction-local, not durable IDs;
- DungeonMind owns deterministic type-separated entity/assertion allocation;
- `result_of(client_op_id)` substitution completes before materialization;
- create-new cannot silently adopt an existing parent identity;
- ordinary V1 items cannot bypass prospective syntax using predicted IDs;
- repository authority independently validates allocation, child presence, and
  parent absence before mutation;
- revision + head + event + V5.3 receipt + V5.4 result mapping commit atomically;
- exact replay and lost-response recovery return the same durable mapping;
- WorldKeeper must not reproduce the allocator.

The prior blocked documents remain useful historical evidence, but their
`1fc03aa…` gate text is no longer current authority.

---

## §3 Ownership and non-negotiable boundaries

### DungeonBuddy

Owns:

```text
interaction
reversible draft editing
selection UX
similarity/duplicate presentation
explicit create-new vs use-existing choice
review presentation
result presentation
```

### WorldKeeper

WK-3 owns:

```text
semantic intent shape
structural validation
exact current-parent binding
exact DomainContract / SemanticProfile binding
exact evidence-reference binding
create-new vs use-existing preservation
same-transaction client_op_id dependency validation
reviewable prepared meaning
lossless compile to DungeonMind V5.4 prospective syntax
opaque prepared-change identity
```

WorldKeeper does **not** own:

```text
durable entity/assertion allocation
identity similarity decision
automatic dedupe/merge
graph persistence
revision publication
head advancement
durable publication outcome
general World reads
a recovery ledger
```

### DungeonMind

Owns:

```text
durable identity
V5.4 prospective allocation and substitution
DomainContract / SemanticProfile authoritative validation
immutable revision identity
expected-parent CAS
atomic publication
V5.3 receipt/replay/recovery
V5.4 result mapping
exact durable read authority
```

---

## §4 Critical implementation decision — prepare does not allocate

This is the most important WK-3 rule.

WorldKeeper may create and validate:

```text
result_of("npc-7")
```

It may compile that to DungeonMind:

```text
ProspectiveEntityRef(client_op_id="npc-7")
```

It may **not**:

- call DungeonMind's internal allocator;
- hash `(space_id, publication_id, client_op_id, result_kind)` itself;
- expose an `ent:*` or `asrt:*` value as the expected future identity;
- treat a provisional identity as part of prepared review;
- reserve an ID;
- create a placeholder graph object;
- publish the object before its dependents.

The reviewable identity is the prospective handle:

```text
result_of(client_op_id)
```

not a predicted durable ID.

The exact DungeonMind V5.4 allocator is intentionally not exported as a public
application API. WorldKeeper must preserve that boundary.

---

## §5 WK-3 application contract

Implement immutable WorldKeeper-owned runtime contracts.

Exact Python filenames/classes are implementation latitude, but the semantic
shape is binding.

### 5.1 WorldChangeIntent

Conceptual shape:

```text
WorldChangeIntent
  space_id
  producer
  operations[]
```

`space_id` is the exact DungeonMind vNext authority space to prepare against.

Do **not** infer a DungeonMind `space_id` from a legacy `world_id` inside this
slice. Product-specific World → space selection belongs outside this contract.
If a caller wants a product correlation ID, it may retain it outside the
authority-bearing semantic intent.

A successful prepare always binds the current exact head observed for this
`space_id`.

### 5.2 Endpoint references

WorldKeeper-owned endpoint union:

```text
DurableObjectRef
  durable_object_id

ResultOf
  client_op_id
```

Rules:

- `DurableObjectRef` must exist in the exact parent.
- `ResultOf(x)` must name one `create_object` in this same intent.
- `ResultOf` may not refer to a relationship/fact assertion result.
- unresolved or cross-intent handles fail prepare.

### 5.3 Create object

Conceptual shape:

```text
CreateObject
  client_op_id
  facts[]
```

The object identity itself carries no product meaning in DungeonMind vNext.
Meaning such as label, kind, title, role, or other non-relational properties is
expressed as typed assertion facts.

A fact is conceptually:

```text
CreateFact
  client_op_id
  predicate
  value = literal | term_ref
  assertion_metadata
```

Each fact needs its own `client_op_id` because DungeonMind V5.4 allocates a
durable assertion ID for every prospective assertion.

The fact subject is implicitly:

```text
result_of(CreateObject.client_op_id)
```

Do not support entity-ref fact values in WK-3. Use `create_relationship` for
entity-to-entity assertions. This keeps the first semantic surface narrow and
unambiguous.

### 5.4 Use existing

Conceptual shape:

```text
UseExisting
  durable_object_id
```

This is a reviewable explicit identity choice.

It produces **no** DungeonMind contribution item by itself.

Prepare validates that the object exists in the exact parent.

A later relationship may refer to the same durable object directly.

No similarity lookup, alias fallback, lexical lookup, or automatic replacement
is allowed.

### 5.5 Create relationship

Conceptual shape:

```text
CreateRelationship
  client_op_id
  source = DurableObjectRef | ResultOf
  predicate
  target = DurableObjectRef | ResultOf
  assertion_metadata
```

This compiles to exactly one DungeonMind `ProspectiveCreateAssertion` with an
entity-ref value.

Its durable assertion ID remains unknown at prepare time.

### 5.6 Assertion metadata

WorldKeeper must use a typed immutable metadata representation that is
losslessly convertible to DungeonMind `AssertionMetadata`.

It may not use an untyped `dict[str, Any]` property bag.

It must preserve, at minimum, the exact DungeonMind semantic fields required by
the accepted contract:

```text
scope
visibility
epistemic_basis
claim_mode
standing
evidence_ref_ids
temporal_scope
domain_metadata
```

The implementation may define WorldKeeper-owned mirror value objects or a
similarly strict transport-neutral representation.

WorldKeeper must **not** invent policy meaning. It preserves the semantic
metadata supplied by the semantic caller and binds it to the exact
DomainContract/SemanticProfile authority selected for prepare.

DungeonMind remains authoritative for final vocabulary/admission validation at
publication.

---

## §6 PreparedWorldChange

A successful preparation returns one frozen WorldKeeper-owned object.

Conceptual shape:

```text
PreparedWorldChange
  prepared_change_id
  dungeonmind_publication_id
  prepared_at

  space_id
  expected_parent_revision_id
  parent_graph_payload_sha256

  domain_contract_ref
  semantic_profile_ref

  evidence_witnesses[]

  prepared_operations[]
  prospective_handles[]

  compiled_plan_digest
  warnings[]
```

### Required identity rule

For WK-3 v0:

```text
dungeonmind_publication_id == prepared_change_id
```

This is the simplest accepted realization of the existing design:

- the prepared ID is opaque;
- every successful prepare gets a new prepared ID;
- re-prepare gets a new ID;
- the same prepared ID reconstructs the same DungeonMind publication identity;
- WorldKeeper does not need a second publication-ID namespace;
- the V5.4 allocator remains DungeonMind-owned.

`prepared_change_id` must be generated by WorldKeeper as an opaque fresh ID.
Its exact random/opaque format is implementation latitude.

Tests must inject a deterministic ID factory rather than pinning randomness.

Do **not** make `prepared_change_id` a future entity/assertion ID.

### Immutability

The prepared object must be caller-isolated:

- frozen dataclasses/immutable tuples are preferred;
- mutable caller input may not mutate the prepared result afterward;
- mutable DungeonMind Pydantic objects must not be stored by reference in a
  way that lets the caller rewrite prepared meaning.

---

## §7 Exact authority binding

WK-3 preparation uses the accepted DungeonMind vNext authority, not legacy
World Graph publication.

Add a narrow WorldKeeper preparation authority seam conceptually equivalent to:

```text
GovernedPreparationAuthority
  read_current_space(space_id)
    -> PreparationAuthorityWitness | None
```

The WorldKeeper-owned witness must contain enough exact immutable authority to
bind prepare without exposing a general read façade:

```text
PreparationAuthorityWitness
  space_id
  head_revision_id
  graph_payload_sha256

  domain_contract_ref
  semantic_profile_ref

  durable_entity_ids
  evidence_witnesses
```

Evidence witness should preserve exact authority identity needed for review,
for example:

```text
evidence_ref_id
source_artifact_id
source_revision_id?
evidence_role
locator/source-anchor summary where already durable
```

Do not expose arbitrary full graph payload through the WorldKeeper public
application contract.

### DungeonMind in-process adapter

Add a vNext preparation adapter that uses the accepted native authority:

```text
KnowledgeRevisionRepository.get_head(space_id)
KnowledgeRevisionRepository.get_revision(space_id, revision_id)
decode_native_graph_payload(...)
build_parsed_knowledge_revision(...)
```

or equivalent accepted helpers.

It must:

1. read current head;
2. read the exact head revision;
3. verify exact revision/payload integrity through DungeonMind;
4. extract exact entity/evidence IDs and pinned DomainContract/SemanticProfile
   refs;
5. return WorldKeeper-owned immutable witnesses;
6. map DungeonMind persistence-unavailable to `AuthorityUnavailable`;
7. map integrity/other fail-closed DungeonMind errors to
   `AuthorityIntegrityFailure`.

This remains a narrow preparation boundary, not a generic read façade.

### Legacy WK-2 seam

Do not delete the accepted WK-2 read-only adapter in this PR.

WK-3 adds the native vNext preparation seam beside it. Legacy compatibility
cleanup/cutover is separate work.

---

## §8 DomainContract and SemanticProfile descriptors

DungeonMind V5.4 publication requires the exact
`DomainContractDescriptor` and `SemanticProfileDescriptorV2`, while the exact
parent revision pins their refs/digests.

WK-3 prepare receives the exact descriptors as explicit configured inputs to
the preparation service/compiler.

Prepare must verify:

```text
descriptor identity/revision/digest
==
exact parent pinned ref identity/revision/digest
```

A mismatch fails prepare.

WorldKeeper does not create a new descriptor registry in this PR.

WorldKeeper does not weaken the descriptor check by trusting a caller-provided
name alone.

The prepared review stores the exact pinned refs/digests, not a mutable
descriptor object as product-editable data.

The compile-ready internal plan may retain isolated descriptor snapshots needed
by WK-4, but caller mutation must not change them.

---

## §9 Evidence binding

Assertion metadata may refer only to exact evidence IDs visible in the exact
parent authority witness.

For every evidence ID used by a fact/relationship:

```text
evidence_ref_id must exist in exact parent
```

Prepare records the corresponding evidence witness in `PreparedWorldChange`.

`ProspectiveKnowledgeContribution.source_refs` is the deterministic sorted
unique set of source artifact IDs reached by the used evidence witnesses.

Evidence means support/provenance only.

WK-3 does not infer:

```text
source occurrence -> object
mention -> object
span -> object
```

Occurrence/mention binding remains deferred.

---

## §10 Structural prepare validation

Before returning success, fail closed on at least:

- blank `space_id`;
- missing current head;
- corrupt current head/revision;
- duplicate result-producing `client_op_id`;
- duplicate/ambiguous use of one client op across object/fact/relationship
  results;
- `ResultOf` pointing to no same-intent `create_object`;
- `ResultOf` pointing to a fact/relationship assertion result;
- durable endpoint absent from the exact parent;
- evidence ref absent from the exact parent;
- descriptor/ref digest mismatch;
- malformed assertion metadata;
- empty operation list;
- a create object with semantically invalid local structure;
- compiler output containing unresolved WorldKeeper handles after adaptation.

This slice does not implement similarity matching or dedupe.

An explicit create-new operation stays create-new.

---

## §11 Lossless DungeonMind V5.4 compilation

Add a pure integration compiler.

Conceptually:

```text
compile_prepared_change_to_dungeonmind(prepared)
  -> DungeonMindPreparedProspectivePlan
```

The compile result contains exact isolated values required by WK-4:

```text
ProspectiveKnowledgeContribution
ContributionDisposition[]
GovernedPublicationIdentity
DomainContractDescriptor
SemanticProfileDescriptorV2
publication_id
```

### Required mapping

#### Create object

```text
CreateObject(client_op_id="npc-7")
→ ProspectiveCreateEntity(
     item_id = internal transaction-local item ID,
     client_op_id = "npc-7"
   )
```

Each object fact becomes:

```text
ProspectiveCreateAssertion(
  item_id = internal item ID,
  client_op_id = fact.client_op_id,
  subject = ProspectiveEntityRef(
    client_op_id = create_object.client_op_id
  ),
  predicate = ...,
  value = LiteralValue | TermRefValue,
  metadata = exact converted AssertionMetadata
)
```

#### Use existing

Produces no contribution item.

It exists for explicit review/identity validation only.

#### Create relationship

```text
source ResultOf(x)
  -> ProspectiveEntityRef(client_op_id=x)

source DurableObjectRef(y)
  -> DurableEntityRef(entity_id=y)

target ResultOf(x)
  -> ProspectiveEntityRefValue(
       entity=ProspectiveEntityRef(client_op_id=x)
     )

target DurableObjectRef(y)
  -> ProspectiveEntityRefValue(
       entity=DurableEntityRef(entity_id=y)
     )
```

Relationship operation becomes one `ProspectiveCreateAssertion`.

### Internal item IDs

DungeonMind V5.4 intentionally distinguishes:

```text
item_id
client_op_id
```

WorldKeeper must preserve that distinction.

Generate transaction-local `item_id` values deterministically from
WorldKeeper-owned prepared meaning, for example a namespaced digest over:

```text
prepared_change_id
item role
client_op_id
```

Exact encoding is implementation latitude.

Requirements:

- item IDs are stable for the exact prepared record;
- item IDs are not graph IDs;
- item IDs are not equal to the caller's `client_op_id`;
- item IDs are not exposed as future durable entity/assertion identities.

### Contribution envelope

Compile to:

```text
ProspectiveKnowledgeContribution
  contribution_id = internal ID derived from prepared_change_id
  space_id = prepared.space_id
  producer = intent producer
  produced_at = prepared.prepared_at
  source_refs = deterministic source artifact IDs from used evidence
  status = "finalized"
  items = flattened prospective items in deterministic semantic order
```

No rejected/unresolved operation is silently compiled.

For a successful WK-3 preparation, every emitted DungeonMind item receives an
`accepted` `ContributionDisposition`.

If WorldKeeper cannot safely accept an operation, prepare fails instead of
creating a misleading partially accepted review in this first runtime slice.

### Publication identity

Compile:

```text
GovernedPublicationIdentity
  operation_ids = (prepared_change_id,)
  created_at = prepared.prepared_at
  expected_parent_revision_id = prepared.expected_parent_revision_id
```

The exact same values must be reused by WK-4 commit.

---

## §12 Compiled-plan digest

`PreparedWorldChange` must bind the exact compile-ready meaning without exposing
future durable IDs.

Compute a canonical digest over WorldKeeper's isolated compile-ready plan:

```text
prepared_change_id
publication_id
space_id
expected_parent_revision_id
parent payload digest
pinned descriptor refs/digests
ProspectiveKnowledgeContribution semantic content
ContributionDisposition semantic content
GovernedPublicationIdentity semantic content
```

Call it conceptually:

```text
compiled_plan_digest
```

Exact canonicalization is implementation latitude but must be deterministic and
covered by tests.

Changing any authority-bearing input must change the digest.

The digest is an integrity witness, not a future graph identity.

---

## §13 What WK-3 must never call

Add import/source guards proving WK-3 preparation runtime does not call or
import mutation entrypoints such as:

```text
publish_prospective_contribution
publish_governed_materialization
publish_publication
publish_prospective_publication
commit_expected_parent
```

It must not receive a mutable repository write capability merely because the
same DungeonMind repository protocol includes publication methods.

Prefer a read-only protocol/adapter surface.

A fake authority used in tests should fail loudly if any mutation method is
invoked.

---

## §14 Small acceptance witness

The required end-to-end prepare witness is intentionally small.

Exact current parent contains an existing durable entity:

```text
ent:castle
```

Intent:

```text
create_object
  client_op_id = "npc-7"

create_relationship
  client_op_id = "rel-4"
  source = result_of("npc-7")
  predicate = lab:located_at
  target = durable("ent:castle")
  metadata = exact pinned semantic/evidence metadata
```

Prepare must return a reviewable form showing:

```text
npc-7 = prospective create
rel-4.source = result_of(npc-7)
rel-4.target = ent:castle
expected parent = exact current head
publication identity = prepared_change_id
```

The compiled DungeonMind plan must contain:

```text
ProspectiveCreateEntity(client_op_id="npc-7")

ProspectiveCreateAssertion(
  client_op_id="rel-4",
  subject=ProspectiveEntityRef(client_op_id="npc-7"),
  value=ProspectiveEntityRefValue(
    entity=DurableEntityRef(entity_id="ent:castle")
  )
)
```

It must contain **no** future `ent:<allocated>` or `asrt:<allocated>` prediction.

No repository head/revision/event/receipt changes are allowed during this
witness.

---

## §15 Repeatability and re-prepare semantics

Two successful calls to prepare the same semantic intent against the same exact
authority are allowed to produce different opaque `prepared_change_id` values.

That is intentional.

Each successful prepare is a new reviewable preparation and therefore a new
DungeonMind `publication_id`.

Within one returned `PreparedWorldChange`:

- all semantics are immutable;
- repeated compilation returns the same exact compiled plan/digest;
- every same-intent `ResultOf` resolves to the same prospective handle;
- no durable identity is predicted.

If the DungeonMind head changes, a new prepare binds the new head and gets a new
prepared ID.

WK-3 does not rebase an existing prepared change.

---

## §16 Files in scope

### Authority/bookkeeping

| Action | Path |
|---|---|
| Modify | `AGENTS.md` |
| Modify | `README.md` |
| Modify | `Docs/Steward/STEWARD-ANCHOR-worldkeeper.md` |
| Modify | `Docs/Architecture/ARCHITECTURE-worldkeeper.md` |
| Modify | `Docs/Architecture/BOUNDARY-dungeonbuddy-worldkeeper-dungeonmind.md` |
| Modify | `Docs/Design/DECISION-worldkeeper-ownership-simplification.md` |
| Modify | `Docs/Design/CONTRACT-world-change-intent-v0.md` |
| Modify | `Docs/Design/CONTRACT-prepared-world-change-v0.md` |
| Modify | `Docs/Design/DESIGN-governed-world-change-lifecycle.md` |
| Modify | `Docs/Roadmaps/ROADMAP-worldkeeper.md` |
| Modify | `Docs/Sources/SOURCE-INDEX-worldkeeper.md` |
| Create | `Docs/Plans/HANDOFF-wk3-prepare-world-change-v1.md` |

### Dependency pin

| Action | Path |
|---|---|
| Modify | `pyproject.toml` |
| Modify | `uv.lock` |

Pin DungeonMind to accepted merged authority:

```text
6edb9e40d1dc930f537c66deb1afbd1b99002844
```

Do not pin the old `1fc03aa…`.

### Application runtime

Preferred surface:

| Action | Path |
|---|---|
| Create | `src/worldkeeper/application/contracts.py` |
| Create | `src/worldkeeper/application/preparation.py` |
| Modify | `src/worldkeeper/application/authority.py` |
| Modify | `src/worldkeeper/application/__init__.py` |
| Modify | `src/worldkeeper/__init__.py` |

Exact file split may differ if the implementation stays equally narrow.

### DungeonMind integration

| Action | Path |
|---|---|
| Create | `src/worldkeeper/integrations/dungeonmind/vnext_prepare.py` |
| Modify | `src/worldkeeper/integrations/dungeonmind/__init__.py` |

Do not mutate the accepted legacy WK-2 `in_process.py` unless a tiny shared
error-helper extraction is demonstrably necessary.

### Tests

| Action | Path |
|---|---|
| Create | `tests/test_wk3_prepare_world_change.py` |
| Create | `tests/test_dungeonmind_vnext_prepare_boundary.py` |
| Modify | `tests/test_package_boundary.py` |

The existing WK-2 conformance test must remain green.

### Bounded discovery exception

Up to two additional test-only/helper paths are allowed if implementation
discovers an existing package-boundary or authority fixture that must be
updated because the repository phase moves from WK-2-only to WK-3-active.

No additional runtime, transport, persistence, HTTP, or migration path may
enter through this exception.

---

## §17 Explicitly out of scope

Do not implement in WK-3:

```text
commit_change
commit_prepared_change
get_change_result
recover_change
publication retry orchestration
lost-response recovery orchestration
exact child read-back after publication
VerifiedCommittedChange runtime
prepared-change durable persistence
WorldKeeper database tables
WorldKeeper migrations
HTTP/API host
DungeonBuddy adapter
agent harness
identity similarity search
automatic dedupe
merge/split/reconciliation
occurrence/mention binding
general DungeonMind read façade
legacy World write migration
bridge-genesis cutover
V5.4 allocator reproduction
```

Do not add an in-memory fake commit path "for testing."

The next slice must consume the real DungeonMind V5.4 publication boundary.

---

## §18 Required tests

### Application contract

1. intent and prepared records are immutable/caller-isolated;
2. blank/duplicate result-producing `client_op_id` fails;
3. `ResultOf` resolves only to same-intent `create_object`;
4. `ResultOf` cannot target fact/relationship assertion results;
5. durable endpoint absent from parent fails;
6. evidence absent from parent fails;
7. DomainContract ref/digest mismatch fails;
8. SemanticProfile ref/digest mismatch fails;
9. empty intent fails;
10. explicit create-new remains a prospective create; no existing object is
    substituted.

### Preparation authority

11. current exact head is bound;
12. exact head revision payload digest is bound;
13. parent entity/evidence witnesses are isolated;
14. DungeonMind unavailable maps to `AuthorityUnavailable`;
15. DungeonMind corruption/fail-closed errors map to
    `AuthorityIntegrityFailure`;
16. authority adapter performs no writes.

### Compilation

17. create object compiles to `ProspectiveCreateEntity`;
18. object fact compiles to `ProspectiveCreateAssertion` whose subject is
    `result_of(object)`;
19. relationship prospective source compiles to `ProspectiveEntityRef`;
20. durable target compiles to `DurableEntityRef`;
21. two references to one create retain one same `client_op_id`;
22. use-existing creates no DungeonMind item;
23. every emitted prospective item has an accepted disposition;
24. `item_id != client_op_id`;
25. no compiled model contains predicted allocated `ent:*` / `asrt:*` IDs for
    prospective results;
26. compiled contribution is `status="finalized"`;
27. source refs are deterministic from bound evidence;
28. publication ID equals prepared ID;
29. operation IDs contain the prepared ID exactly once;
30. repeated compilation of one prepared object is identical;
31. any authority-bearing mutation changes the plan digest or fails preparation.

### Non-mutation

32. head before prepare == head after prepare;
33. revision/event/receipt/prospective-result counts unchanged;
34. fake mutation methods are never called;
35. WK-3 source has no import/call of DungeonMind publication entrypoints.

### Canonical witness

36. `npc-7` + dependent `rel-4 -> ent:castle` compiles exactly to accepted
    V5.4 prospective syntax;
37. review output contains prospective handles only;
38. no future durable ID appears.

### Regression

39. existing WK-2 tests remain green;
40. package import remains service-host independent;
41. no `commit_change`/`commit_prepared_change` export exists yet.

---

## §19 Verification commands

Run at minimum:

```bash
uv sync --locked

uv run ruff check .
uv run pyright

uv run pytest -q
git diff --check

git diff --name-only e84f6bea90ba05c25be83b6b2c7c08751cac2608...HEAD
git diff --stat e84f6bea90ba05c25be83b6b2c7c08751cac2608...HEAD
```

Also record:

```text
python -c "import dungeonmind; import worldkeeper"
```

and a dependency proof showing the installed DungeonMind source is pinned to
the accepted merged V5.4 authority.

If repository CI exists, report exact-head CI.

Do not invent a benchmark requirement for this slice; prepare is small and
pure. If performance evidence reveals a material issue, report it rather than
adding caching/storage.

---

## §20 Nano-commit contract

Recommended reviewable story:

```text
1. STEWARDSHIP: accept DungeonMind V5.4 and authorize WK-3
   - authority docs
   - roadmap
   - source index
   - canonical handoff
   - no runtime implementation

2. BUILD: pin WorldKeeper to accepted DungeonMind V5.4
   - pyproject.toml
   - uv.lock
   - dependency/import proof

3. BUILD: define WK-3 immutable preparation contracts
   - intent
   - endpoints
   - prepared result
   - preparation authority witness
   - no DungeonMind mutation

4. BUILD: add vNext preparation authority + V5.4 compiler
   - read-only native authority adapter
   - lossless prospective compilation
   - no allocator/publish calls

5. PROOF: exercise WK-3 canonical preparation witness
   - structural failures
   - authority binding
   - no mutation
   - V5.4 compile shape
   - WK-2 regression
```

Do not squash conceptual phases during implementation if preserving them makes
review materially easier.

---

## §21 Acceptance rubric

WK-3 is accepted only if all are true:

- [ ] Repository authority records V5.4 acceptance and marks WK-3 runtime
      authorized/active.
- [ ] DungeonMind is pinned to merged V5.4 authority `6edb9e40…`.
- [ ] `WorldChangeIntent` has typed create/use-existing/relationship semantics.
- [ ] Every same-intent prospective reference is validated before review.
- [ ] `PreparedWorldChange` is immutable and bound to exact current parent.
- [ ] Exact DomainContract/SemanticProfile refs/digests are bound.
- [ ] Exact evidence refs are bound.
- [ ] `prepared_change_id` is fresh/opaque.
- [ ] `dungeonmind_publication_id == prepared_change_id`.
- [ ] Compile output uses accepted V5.4 prospective contracts exactly.
- [ ] WorldKeeper never calls or reproduces the V5.4 allocator.
- [ ] No future durable entity/assertion ID is shown in prepared review.
- [ ] Prepare performs zero DungeonMind mutation.
- [ ] Canonical `npc-7` / `rel-4` witness passes.
- [ ] Existing WK-2 conformance remains green.
- [ ] No commit/publication/recovery runtime leaked into this slice.
- [ ] Changed paths remain inside §16 or recorded bounded exception.
- [ ] All required verification is independently rerunnable.

Final accepted disposition:

```text
WK_3_PREPARE_WORLD_CHANGE_ACCEPTED
```

---

## §22 Stop conditions

Stop and rebrief if implementation discovers that WK-3 requires:

- predicting or calling DungeonMind's V5.4 allocator;
- publishing merely to validate prepare;
- a WorldKeeper database or durable prepared store;
- a new DungeonMind write contract;
- mutation of frozen DungeonMind V0/V5.4 contracts;
- a product-specific World → DungeonMind space mapping inside WorldKeeper;
- similarity search to decide identity;
- a generic property bag instead of typed assertion semantics;
- occurrence/mention binding;
- source/evidence creation;
- prospective identity-decision support;
- assertion-result references used as entity endpoints;
- a general DungeonMind read façade;
- HTTP/service transport;
- more than one independently useful capability.

Stop report:

```text
Stop condition:
Observed evidence:
Affected invariant:
Why WK-3 cannot safely absorb it:
Required design/repository follow-on:
What remains safe in parallel:
```

---

## §23 Required implementation handback

Return:

1. PR URL, branch, exact base SHA, exact head SHA;
2. nano-commit list;
3. exact changed-path list and focused diff stat;
4. exact DungeonMind dependency SHA;
5. final WorldKeeper authority status;
6. actual `WorldChangeIntent` and `PreparedWorldChange` runtime shapes;
7. actual preparation-authority witness shape;
8. exact compile mapping to DungeonMind V5.4 types;
9. prepared-ID/publication-ID rule;
10. exact plan-digest material;
11. canonical witness result;
12. proof no durable IDs are predicted;
13. proof no DungeonMind mutation occurred;
14. all verification commands/results;
15. WK-2 regression result;
16. paths outside §16;
17. stop conditions encountered;
18. confirmation that commit/recovery/verification runtime remains unimplemented.

---

## §24 Named successor — WK-4 commit prepared change

After WK-3 acceptance, design the separately governed successor:

```text
WK-4 — commit prepared change + exact child verification
```

Its primary question should be:

> Given one exact immutable `PreparedWorldChange` accepted by the reviewer, can
> WorldKeeper submit its bound DungeonMind V5.4 prospective request under
> `publication_id == prepared_change_id`, preserve deterministic stale /
> conflict / integrity / outcome-unknown semantics, consume the durable V5.4
> client-op → durable-ID mapping, read back the exact committed child revision,
> and return one `VerifiedCommittedChange` without a WorldKeeper recovery
> ledger?

WK-4 must consume the real accepted DungeonMind V5.4 publication path.

Do not pre-implement it in WK-3.
