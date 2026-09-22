# Steward Anchor — World Keeper

**Status:** WK-1 ACCEPTED / WK-2 ACTIVE
**Phase:** WK-2 — DUNGEONMIND-BACKED IN-PROCESS REFERENCE BOUNDARY
**Implementation:** LIMITED AUTHORIZATION — WK-2 ONLY
**Repository:** `WorldKeeper`

## Mission

World Keeper turns source-grounded application intent into a validated, reviewable, governed World transaction and exposes the resulting World knowledge back to applications.

The durable division is:

```text
DungeonBuddy / other clients
  capture intent, source context, interaction, and result presentation

World Keeper
  interpret intent, resolve references, coordinate prepare/review/confirm,
  and provide application-oriented World reads

DungeonMind
  own durable World truth, evidence, identity authority, revisions,
  projection/retrieval, and governed publication
```

World Keeper is not simple storage. DungeonMind remembers; World Keeper decides how an application's proposed meaning should be interpreted against governed World truth and coordinates the transition from proposal to durable truth.

## Current repository state

WK-0 repository bootstrap was accepted at `62a6f5671b8387c0d35ecb491489cbd253e9f6c8`.
WK-1 was accepted through PR #1 at `22035df4e413f96d88a2414c673a428bbd3f4f32`,
merged to `main` at `f3126e1d4f486599503e8ebacabb73f3d6242a3b`. WK-2 is now
the only authorized implementation slice:

- root README and repository operating law;
- steward, architecture, and boundary authority;
- governed write-lifecycle design;
- v0 intent and prepared-change contracts;
- coarse roadmap;
- source/ancestry index;
- a read-only, in-process DungeonMind authority seam and conformance harness.

WK-2 may implement only World Keeper-owned witnesses and a read-only
DungeonMind adapter. No HTTP service, World Keeper schema/persistence,
migration, live-world operation, prepare/commit behavior, recovery
orchestration, confirmation binding, or semantic compiler is authorized.

## Authority hierarchy

When documents disagree, use this order:

1. This steward anchor.
2. `Docs/Architecture/ARCHITECTURE-worldkeeper.md`.
3. `Docs/Architecture/BOUNDARY-dungeonbuddy-worldkeeper-dungeonmind.md`.
4. `Docs/Design/DESIGN-governed-world-change-lifecycle.md`.
5. Versioned `Docs/Design/CONTRACT-*` documents.
6. `Docs/Roadmaps/ROADMAP-worldkeeper.md`.
7. `Docs/Sources/SOURCE-INDEX-worldkeeper.md` and the historical/source documents it indexes.

The source index records ancestry and evidence. It cannot silently override accepted World Keeper design. A newer decision must update the appropriate authority document rather than live only in a source repository or conversation.

## Required pickup order

For a fresh agent or contributor:

1. This anchor.
2. The root `README.md`.
3. Architecture.
4. Boundary.
5. Write lifecycle.
6. Intent contract v0.
7. Prepared-change contract v0.
8. Roadmap.
9. Source index when historical or implementation evidence is required.

## Non-negotiable design commitments

- The application-facing write family is World-level intent, not DungeonMind graph DTOs.
- Prepare interprets the complete proposed transaction against one exact governed World parent and admissible source/evidence context.
- Review shows the exact prepared meaning. Explicit human or policy confirmation remains mandatory before durable publication.
- Confirm is bound to the prepared meaning. A changed proposal, source authority, identity state, or parent fails closed or requires re-prepare.
- Same-transaction local references are first-class. They resolve to prospective durable results in one coherent publication; no placeholder objects or follow-up repair writes.
- Identity advice is not identity authority. Duplicate suggestions never silently merge objects.
- Read-back at the published child revision is part of write correctness.
- World Keeper must be transport-independent and must not become an agent harness.
- The v0 application surface is `prepare_change`, `commit_prepared_change`,
  `recover_change`, and a narrow exact-child `read_exact_change_result`
  capability.
- `change_request_id` is the transaction-level idempotency/recovery identity;
  `prepared_change_id` plus `preparation_generation` identify one exact
  interpretation; `operation_id` is never a publication/recovery key.
- Prepared changes use a retained canonical workflow record plus a
  tamper-evident confirmation binding. The workflow record is not World truth
  and does not require HTTP or a World Keeper database.
- Once a commit can begin, a separate crash-surviving transaction/publication
  recovery record must preserve the generation-bound `publication_operation_id`
  and lifecycle/outcome mapping. Ordinary prepared-payload expiry cannot erase
  an in-flight or unknown publication outcome.
- `confirmation_binding` authorizes commit of an active preparation only. Once
  publication begins, recovery is resolved from the durable server-side
  `change_request_id` plus generation record and must outlive the ordinary
  confirmation-binding verification window.
- Safe re-prepare retains `change_request_id` and increments the preparation
  generation only after the prior generation is proven not committed or safely
  invalidated. Committed or unknown outcomes require recovery first.
- v0 uses immutable source artifact/revision identity plus optional
  DungeonMind-admitted locator identity; evidence support remains distinct from
  explicit occurrence/mention binding. Occurrence binding is deferred from
  implementable v0 because the current DungeonMind authority has no distinct
  durable occurrence-to-object write contract.
- Prepared local objects use opaque prospective handles, but prepare binds each
  handle internally to an exact prospective durable identity/materialization and
  binds dependent relationships to it before confirmation. Committed v0
  receipts return direct relationship operation → durable relationship IDs,
  with exact child read-back still mandatory.
- WK-2 is a read-only boundary proof. It may read exact heads, immutable
  revisions, source/revision provenance, and finalized publication evidence
  through DungeonMind; it may not publish or create a second durable authority.

## Remaining design questions

WK-1 resolves the smallest application contract. The following remain open
without blocking the semantic contract:

1. When is an optional network host justified, after an in-process contract proof?
2. Which broader World Keeper read operations are true application façades versus direct, well-scoped DungeonMind capabilities?
3. What exact policy/human approval metadata is needed beyond the explicit confirmation fact?
4. Which semantic-profile and scope inputs belong in a later contract versus being resolved from World context?
5. What exact DungeonMind landing contract, canonical source-byte/digest
   semantics, and read-back should govern a future occurrence-binding
   operation?
6. What is the smallest v0 operation family beyond create, reference, and
   relationship creation once that deferred family is revisited?
7. What operational store, retention duration, key-management provider, and
   transport mapping implement the accepted prepared lifecycle and its durable
   recovery record?

## STOP conditions

Stop and return to design review if work would require any of the following:

- implementing outside the explicit WK-2 read-only boundary lease;
- making World Keeper own graph persistence, a new identity ledger, or DungeonMind schema;
- leaking `GraphContribution`, evidence-record, publication, or persistence DTOs as the public World Keeper contract;
- silently changing a prepared transaction during confirm;
- accepting unresolved, duplicate, external, or wrong-kind local references;
- automatic identity merging or deduplication;
- adding a network boundary solely because the repository is separate;
- adding a client-specific agent/tool loop to the generic core;
- mutating live Eldyrwild or moving production traffic.

## Next permitted work

WK-2 is active under
`Docs/Plans/HANDOFF-CON-READY-wk2-dungeonmind-inprocess-boundary-v1.md`.
The permitted work is the narrow in-process, read-only authority seam and its
tests against DungeonMind `1fc03aa21e406d9a7cb07d0e4792e202fe281375`. WK-3
and WK-4 behavior remain unauthorized pending separate review.

## Accepted WK-1 invariants

WK-1 is ready for review when a fresh contributor can answer yes to all of these:

- World Keeper is clearly distinct from both DungeonBuddy and DungeonMind.
- Semantic transaction interpretation is the central responsibility.
- Prepare/confirm is exact and implementation-neutral.
- Source/evidence and identity responsibilities are divided coherently.
- Local-reference uniqueness and fail-closed resolution are explicit.
- Exact-parent/stale-parent behavior and read-back are part of correctness.
- Undecided contracts are marked open.
- A non-DungeonBuddy client and an in-process deployment remain possible.
- Nothing here recreates DungeonMind or makes World Keeper an agent harness.
- The roadmap starts with contracts and evidence, not endpoints.
- A transaction has one recovery identity, one preparation generation at a time,
  and no per-operation recovery ambiguity.
- A prepared record can be inspected, invalidated, expired, or safely recovered
  without reconstructing meaning from untrusted client input.
- Evidence grounding and occurrence/mention binding have separate contract
  representations, and occurrence binding is explicitly deferred from
  implementable v0 pending DungeonMind authority.
- Prospective handles are public abstractions over exact prepare-time durable
  identity/materialization; dependent relationships never wait for commit-time
  identity allocation or repair.
- A crash after publication begins cannot erase the generation-bound recovery
  identity or permit an unsafe re-prepare.
- A committed result names the exact child and can be proven through a narrow
  child-pinned read-back capability.
