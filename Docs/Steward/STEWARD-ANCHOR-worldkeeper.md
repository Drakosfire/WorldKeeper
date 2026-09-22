# Steward Anchor — World Keeper

**Status:** CURRENT DESIGN AUTHORITY
**Phase:** DESIGN / REPOSITORY BOOTSTRAP
**Implementation:** NOT AUTHORIZED
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

This bootstrap repository began empty of product/runtime files. The intended initial state is a small, reviewable document set only:

- root README and repository operating law;
- steward, architecture, and boundary authority;
- governed write-lifecycle design;
- two versioned v0 design contracts;
- coarse roadmap;
- source/ancestry index.

No runtime service, schema, endpoint, persistence adapter, migration, or live-world operation is authorized by this anchor.

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

## Open design questions

These are deliberately not resolved by bootstrap:

1. What is the smallest transport-neutral application API, and when is an optional network host justified?
2. Which World Keeper read operations are true application façades versus direct, well-scoped DungeonMind capabilities?
3. Should receipts expose a local relationship operation → durable relationship ID mapping, or should exact relationship identity be derived from child-revision read-back?
4. What are the durable storage/lifecycle, expiry, and invalidation mechanisms for a prepared change, and how does the decided `change_request_id` map to any internal `publication_operation_id`?
5. Which source occurrence/span forms can be accepted in v0 while preserving DungeonMind provenance authority?
6. Which semantic-profile and scope inputs belong in the v0 intent contract versus being resolved from World context?
7. What exact policy governs warnings, ambiguities, and an explicit identity-reconciliation operation?
8. What is the smallest v0 operation family beyond create, reference, link-occurrence, and relationship creation?

## STOP conditions

Stop and return to design review if work would require any of the following:

- implementing before implementation authorization is changed;
- making World Keeper own graph persistence, a new identity ledger, or DungeonMind schema;
- leaking `GraphContribution`, evidence-record, publication, or persistence DTOs as the public World Keeper contract;
- silently changing a prepared transaction during confirm;
- accepting unresolved, duplicate, external, or wrong-kind local references;
- automatic identity merging or deduplication;
- adding a network boundary solely because the repository is separate;
- adding a client-specific agent/tool loop to the generic core;
- mutating live Eldyrwild or moving production traffic.

## Next permitted work

The next slice is a design/review decision that resolves the smallest transport-neutral application contract and prepared-change lifecycle. Only after that decision is accepted may an implementation slice be authorized. The safest first implementation is expected to be an in-process reference path against DungeonMind, but that is a roadmap hypothesis, not current authorization.

## Bootstrap review answers

The bootstrap is ready for review only if a reader can answer yes to all of these:

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
