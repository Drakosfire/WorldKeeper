# World Keeper

**Status:** WK-1 accepted / WK-2 in-process boundary proof active
**Implementation:** limited authorization — WK-2 only

World Keeper is the semantic transaction layer between applications and DungeonMind. It turns source-grounded application intent into validated, reviewable World changes, commits confirmed changes through DungeonMind's governed authority, and exposes World knowledge back to clients.

```text
DungeonBuddy / other clients
  interaction + source selection + application intent
                    │
                    ▼
              World Keeper
  semantic interpretation + prepare/review/confirm lifecycle
                    │
                    ▼
               DungeonMind
  durable governed World knowledge, revisions, evidence, retrieval
```

The intended durable loop is:

```text
source-grounded intent
→ exact interpretation
→ reviewable prepared World change
→ explicit confirmation
→ immutable publication
→ exact read-back
```

World Keeper owns the application-facing meaning of a proposed World change, transaction-local reference resolution, source-grounding interpretation, prepared-change review, confirmation binding, and application-oriented World reads. DungeonMind remains the durable knowledge authority: it owns immutable revisions, source/evidence records, identity authority, projection/retrieval semantics, and governed publication.

World Keeper does not own the UI, the agent harness, graph persistence, a second graph engine, or the DungeonMind schema. It is not a replacement for DungeonMind and it is not an agent runtime.

## Start here

Read the repository authority in this order:

1. [Steward anchor](Docs/Steward/STEWARD-ANCHOR-worldkeeper.md)
2. [Architecture](Docs/Architecture/ARCHITECTURE-worldkeeper.md)
3. [Boundary](Docs/Architecture/BOUNDARY-dungeonbuddy-worldkeeper-dungeonmind.md)
4. [Write lifecycle](Docs/Design/DESIGN-governed-world-change-lifecycle.md)
5. [Intent contract v0](Docs/Design/CONTRACT-world-change-intent-v0.md)
6. [Prepared-change contract v0](Docs/Design/CONTRACT-prepared-world-change-v0.md)
7. [Roadmap](Docs/Roadmaps/ROADMAP-worldkeeper.md)
8. [Source index](Docs/Sources/SOURCE-INDEX-worldkeeper.md) when ancestry or evidence is needed

World Keeper now contains a narrowly authorized WK-2 reference package. It
implements only the in-process DungeonMind governed-authority seam and test
harness: exact head/revision, source/provenance, and finalized-publication
reads expressed as World Keeper-owned witnesses. Semantic prepare/commit,
recovery orchestration, workflow persistence, and HTTP remain unauthorized.
