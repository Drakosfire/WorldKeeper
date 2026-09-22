# Source Index — World Keeper

**Status:** CURRENT EVIDENCE INDEX
**Purpose:** record ancestry, reviewed revisions, and the exact claims each source can support. Sources are evidence; this index and the World Keeper authority hierarchy determine how they are used.

## Precedence for this repository

1. `Docs/Steward/STEWARD-ANCHOR-worldkeeper.md`
2. `Docs/Architecture/ARCHITECTURE-worldkeeper.md`
3. `Docs/Architecture/BOUNDARY-dungeonbuddy-worldkeeper-dungeonmind.md`
4. `Docs/Design/DESIGN-governed-world-change-lifecycle.md`
5. versioned `Docs/Design/CONTRACT-*` documents
6. `Docs/Roadmaps/ROADMAP-worldkeeper.md`
7. this index and the external sources below

External repository architecture and contracts outrank chat/history within their own repositories, but they do not silently override accepted World Keeper design.

## Snapshot and repository conditions

This index was created from the local repositories on 2026-09-22.

| Repository | Observed revision | Condition | Use |
| --- | --- | --- | --- |
| WorldKeeper | reviewed WK-0 bootstrap base `09c24dc86937f76647d67c7fb6dba08fce5b39d6`; this correction follows it | documentation-only repository bootstrap; the correction commit is intentionally not named here because this file cannot contain its own final SHA | current local authority after correction |
| DungeonMindBuddy | current side-quest authority `19593ae6...`; historical reviewed #745 head `b7e71379399905b7853d3ee67459511b2669b003`; local current `c3e5153570cad720c2eff8c110c07ec255a699ad` | local working tree contains unrelated UI edits; side-quest authority is the direct ancestry for World Keeper, while b7e is retained for older review/implementation evidence | source-to-World semantics, corrected interaction boundary, and migration evidence |
| DungeonMind | verified current `origin/main` `1fc03aa21e406d9a7cb07d0e4792e202fe281375`; local checkout remains at `13fe863...` | local working tree contains unrelated performance/contract work; the indexed sources were verified at current main rather than inferred from the stale local checkout | durable library boundary and authority |

The Buddy handoff also identifies PR #745 review `5279631534` as a design review that held the draft for precision. That review identifier is preserved as process evidence; the durable claims used here come from the checked-in reviewed head and current DungeonMind documents.

## DungeonMind sources

| Source | Status | What it proves | What World Keeper inherits | What World Keeper does not inherit |
| --- | --- | --- | --- | --- |
| `DungeonMind/README.md` at `1fc03aa...` | CURRENT AUTHORITY in DungeonMind | DungeonMind is an independent governed world-knowledge library; it owns durable knowledge, immutable revisions, evidence/provenance, scope/admissibility, profile identity, retrieval, and governed publication | the durable lower-layer ownership boundary; correctness-first posture | no product UI, agent harness, product-local source presentation, or requirement to expose Mind DTOs |
| `DungeonMind/Docs/Architecture/ARCHITECTURE.md` at `1fc03aa...` | CURRENT AUTHORITY in DungeonMind | one World Graph per world; immutable revisions/head CAS; evidence as validity; explicit reads; governed writes; profiles own domain meaning | exact parent, immutable child, read pinning, fail-closed evidence and scope principles | DungeonMind's internal package layout and its own read-context implementation |
| `DungeonMind/Docs/Architecture/AUTHORITY.md` at `1fc03aa...` | CURRENT AUTHORITY in DungeonMind | accepted precedence, graph/source/evidence authority, client boundary, write authority, profile authority | no current-head inference, no foreign graph reconstruction, source revalidation, publication receipts/recovery | source index does not let historical Buddy behavior override current Mind authority |
| `DungeonMind/src/dungeonmind/contracts/evidence.py` at `1fc03aa...` | CURRENT AUTHORITY in DungeonMind | durable source-artifact, source-revision, and evidence-reference representations with opaque `locator`/`uri` fields | World Keeper may bind evidence to admitted artifact/revision and authority-owned locator identity | no distinct v0 occurrence-to-object publication operation; evidence fields are not mention-binding authority |
| `DungeonMind/src/dungeonmind/contracts/vnext/source.py` at `1fc03aa...` | CURRENT AUTHORITY in DungeonMind | versioned evidence contracts retain independent locator forms including `source_span_ref_id`, `source_locator`, and `line_ref` | preserve locator identity without conflating it with a World-object occurrence assertion | no lossless v0 translation from these evidence fields to a distinct occurrence-to-object write |
| `DungeonMind/Docs/Decisions/ADR-0015-lossless-source-provenance-v2.md` at `1fc03aa...` | CURRENT AUTHORITY in DungeonMind | source locator forms such as `source_span_ref_id`, `locator`, `uri`, `source_locator`, and `line_ref` are independent; v2 provenance is lossless and fail-closed | preserve the distinction between source evidence and a future occurrence assertion | no client-defined byte-offset contract and no authorization to invent an occurrence write operation |
| `DungeonMind/Docs/Decisions/ADR-0022-independent-library-and-agent-harness-boundary.md` at `1fc03aa...` | CURRENT AUTHORITY in DungeonMind | agent harness/model/tool loop/context budgeting belongs to the client; DungeonMind authorizes only its own operations | World Keeper must also remain a semantic client-facing layer, not an agent harness | no MindTurn/agent/context behavior is automatically a Keeper responsibility |
| `DungeonMind/Docs/Roadmaps/ROADMAP.md` at `1fc03aa...` | CURRENT AUTHORITY in DungeonMind | current library roadmap and its evidence-driven posture | consult for compatibility and sequencing when implementation begins | not a World Keeper implementation schedule |

## DungeonMindBuddy architecture sources

| Source | Status | What it proves | What World Keeper inherits | What World Keeper does not inherit |
| --- | --- | --- | --- | --- |
| `DungeonMindBuddy/Docs/Design/ARCHITECTURE-campaign-supergraph.md` at reviewed head `b7e71379...` | ACCEPTED ANCESTRY | one World-owned supergraph; campaign-scoped assertions/evidence/chronology; many projections; surfaces never own graph behavior; separate read/write paths | source-first product boundary, world-versus-campaign distinction, projection/read separation | Buddy's surface names, historical overlay implementation, or current sequencing authority |
| `DungeonMindBuddy/Docs/Plans/HANDOFF-CON-READY-worldkeeper-sidequest-v1.md` at `19593ae6...` | CURRENT AUTHORITY in Buddy / ACCEPTED ANCESTRY here | direct rationale for extracting World Keeper and corrected source↔World interaction semantics: evidence grounding is not occurrence/mention binding; authoring is continuous; prepare/confirm and exact local-reference publication remain governed; a grounded object does not automatically deserve a source pill/link | the corrected interaction distinction and the reason for the three-project boundary | Buddy's side-quest workflow, route names, and implementation lease are not World Keeper authorization |
| `DungeonMindBuddy/Docs/Design/DESIGN-source-to-world-authoring-interaction-contract.md` at `b7e71379...` | HISTORICAL PRE-SIDEQUEST DESIGN EVIDENCE | continuous source ↔ World authoring; durable refs differ from source occurrences; local refs in one transaction; identity advice is not identity authority; publish/read-back continuity | local-ref and exact-result ancestry, source-first interaction principle | its pre-sidequest interaction framing is not current authority; the corrected current semantics are indexed at the `19593ae6...` side-quest handoff and are not themselves the Keeper API |
| `DungeonMindBuddy/Docs/Plans/HANDOFF-CON-READY-source-to-world-transaction-semantics-v1.md` at `b7e71379...` | IMPLEMENTATION EVIDENCE / BLOCKED at its source head | same-batch object + relationship must publish atomically; invalid local refs, stale parent, changed proposal fail closed; receipt maps local object to durable node | adversarial proof requirements and one-child invariant | Buddy file allowlists, route names, and its activation process |
| `DungeonMindBuddy/Docs/Plans/PLAN-CON-READY-authoring-v2-derived-gold-ablation-loop-v1.md` | ACCEPTED ANCESTRY / ACTIVE in Buddy at local current source | human authoring → durable World truth → derived gold; current World authority is DungeonMind; agent is not first author | product continuity and the rule that durable truth precedes derived evaluation output | Buddy's V2 sequencing, UI implementation, or permission to start Keeper implementation |
| `DungeonMindBuddy/Docs/Plans/HANDOFF-CON-READY-authoring-v2-governed-world-commit-v1.md` | IMPLEMENTATION EVIDENCE | existing prepare/commit seam re-resolves and re-proves source, enforces stale parent, publishes one immutable revision, returns created node IDs, and supports idempotent recovery | exact source/parent binding and read-back requirements | `POST` routes, `recapArtifactId`, `sourceRunId`, or Buddy response DTOs as public Keeper contract |
| `DungeonMindBuddy/Docs/Design/DESIGN-graph-object-authoring-surface.md` | HISTORICAL / TRANSITIONAL | source-first selection, local staging, explicit review/confirm, authored corrections; explicitly says Buddy-owned graph storage is superseded | interaction lessons and local/reversible authoring principle | authored overlay/event log and gold fixtures as durable World truth |

## DungeonMindBuddy implementation evidence

| Source | Status | What it proves | Extraction treatment |
| --- | --- | --- | --- |
| `apps/live_control_server/services/graph_object_authoring_prepare.py` | IMPLEMENTATION EVIDENCE | request validation, expressibility checks, prepared response, signed binding, exact source/parent/proposal facts, local relationship handling seam | preserve semantics; redesign at the Keeper boundary; do not freeze Python models or classifier |
| `apps/live_control_server/services/graph_object_authoring_commit.py` | IMPLEMENTATION EVIDENCE | commit revalidation, publication/recovery orchestration, receipt and committed proposal handling | use as behavior evidence and migration inventory; remove duplication after Keeper adoption |
| `apps/live_control_server/ports/world_graph_authority.py` | IMPLEMENTATION EVIDENCE / MIGRATION SEAM | exact World view, identity snapshot, expected-parent, relationship/read-back and publication concepts | classify as an adapter seam; DungeonMind remains durable authority |
| `apps/live_control_server/ports/world_graph_source_admission.py` | IMPLEMENTATION EVIDENCE / MIGRATION SEAM | source identity, admission, and confirm-time re-proof distinction | preserve source/evidence safety; do not expose Buddy port shape as Keeper contract |
| `apps/live_control_server/integrations/dungeonmind/` | IMPLEMENTATION EVIDENCE | Buddy-specific adapters for reads, writes, contribution mapping, source admission | likely retirement or thinning after extraction; no wholesale move |

## Accepted semantic findings

These findings are the reason this repository exists:

1. Prepare-time prospective identity is part of safety. Publishing objects, receiving IDs, then rewriting relationships is weaker than preparing the complete transaction.
2. Local operation/reference identifiers must be unique inside an intent; ambiguity fails before prepare succeeds.
3. WK-1 decides that a committed v0 receipt maps each relationship `operation_id` directly to its durable `relationship_id`. That operation identity is a result correlation key only; it is not the publication or recovery identity.
4. Buddy's current expressibility classifier is implementation evidence, not architecture. Semantic expressibility belongs at the Keeper boundary eventually.
5. Source admission and graph publication are one application-facing semantic workflow even though DungeonMind owns the durable records and publication authority.
6. Identity suggestions are not identity decisions.
7. A public prospective object handle is opaque, but prepare must bind it internally to an exact prospective durable identity/materialization. Dependent relationships must resolve to that exact materialization before confirmation.
8. Evidence grounding remains distinct from occurrence/mention binding. Because the current DungeonMind source contracts expose evidence locators but no distinct occurrence-to-object write operation, occurrence binding is deferred from implementable World Keeper v0.

## Conflicts and caveats discovered

- The handoff's reviewed source head `b7e71379...` exists locally and contains the source-to-World contract and blocked transaction handoff. The checked-out Buddy branch has moved to `c3e51535...` and has unrelated working-tree edits; this index does not treat those edits as authority.
- The current Buddy side-quest authority is identified as `19593ae6...` in the reviewed handoff, but that revision is not present in this local clone. Its indexed claims are limited to the corrected interaction semantics established by the review; implementation details must be re-read from the exact source revision before extraction work.
- The Buddy source contract is marked proposed/blocked for its own implementation lane. Its safety findings are accepted ancestry for this bootstrap, not authorization to continue that lane here.
- DungeonMind's local working tree at `13fe863...` contains unrelated uncommitted performance/contract work. This bootstrap relies on the matching committed source set verified at current `origin/main` `1fc03aa...`, not on local changes.
- The earlier source handoff left relationship result handles open. WK-1 resolves that question as `relationship operation_id → durable relationship_id`; this index is updated in the same decision.

No observed source conflict defeats the three-layer thesis. The main uncertainty is sequencing and contract shape, not ownership.

## Use rule

When later work needs a claim not represented here, update this index and the relevant authority document in the same design decision. Do not promote an implementation detail, branch-local patch, or chat reconstruction into World Keeper authority by implication.
