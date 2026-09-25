# Source Index — WorldKeeper

**Status:** CURRENT EVIDENCE INDEX
**Snapshot:** 2026-09-24

Sources prove facts; they do not override the steward, architecture, boundary,
lifecycle, or versioned contract documents.

## Reviewed revisions

| Source | Revision / condition | What it proves | What it does not prove |
| --- | --- | --- | --- |
| WorldKeeper | accepted WK-2 PR #2 head `15739eb2688992fe8f977d006b1e9153047753a9` | accepted WK-2 boundary proof and its history | authorization for WK-3 implementation |
| WorldKeeper | accepted WK-3 PR #4 head `1c5e3d1262239ba8faf6fca75fbc0aa756d7a2a7`; merged `3c1132e9c3a63571984704bf66bcf5bf482b7bd8` | immutable prepare contract, V5.4 compilation, and exact-head verification with 28 tests | permission for persistence, HTTP, or product integration |
| DungeonMind | V5.4 accepted head `c7700f98e62732cbd1c021270f5366a77c24ea9b`; merged `main` `6edb9e40d1dc930f537c66deb1afbd1b99002844`; final PASS `5296514025` | prospective allocation/substitution, atomic publication, V5.3 receipt/replay/recovery, durable result mapping | WorldKeeper allocation logic or authorization to publish in WK-3 |
| DungeonMindBuddy | side-quest authority `19593ae6d5a0ba583eaac063d772abaf9a42d74d` | product interaction boundary and migration evidence | WorldKeeper authority or DungeonMind contract |
| DungeonMindBuddy historical review | `b7e71379399905b7853d3ee67459511b2669b003` | older source-to-World transaction evidence | current Buddy authority |

## DungeonMind prospective-publication finding and resolution

The historical `1fc03aa…` authority answered **no** to whether DungeonMind already
accepts `create A` plus a dependent relationship to A, allocates A's durable ID
during the same atomic publication, substitutes it everywhere, and returns the
mapping.

Evidence inspected at `origin/main`:

- `src/dungeonmind/contracts/contribution.py` — `GraphContributionAssertionV2`
  carries `subject_object_id` and `object_object_id`.
- `src/dungeonmind/application/review_materialization_v6.py` —
  `GraphMaterializerV6.apply_edge` rejects absent endpoints and requires them
  to be present in the materialized object set.
- `src/dungeonmind/application/review_publication.py` —
  `publish_finalized_review` materializes a review before calling the graph
  publication repository.
- `src/dungeonmind/application/repositories.py` — `WorldGraphRepository`
  publishes an already-materialized `PublishRevisionCommand` with immutable
  revision and expected-parent semantics.
- `tests/conformance/test_review_materialization_v6.py` and
  `tests/conformance/test_review_publication.py` — current characterization and
  atomic publication/replay evidence; no prospective endpoint contract.

DungeonMind V5.4 resolves that gap. Prospective handles remain transaction-local;
DungeonMind owns deterministic type-separated allocation, substitutes before
materialization, rejects predicted-ID bypass and parent collisions, validates
the mapping at the repository boundary, commits revision/head/event/receipt/map
atomically, and replays the exact mapping after retries or lost responses.
WorldKeeper may compile to the accepted contract but must not reproduce its
allocator or publish during WK-3.

## Retained evidence classifications

- **CURRENT:** the ownership simplification and prerequisite in the current
  architecture, boundary, contracts, lifecycle, steward, and roadmap.
- **HISTORICAL EVIDENCE:** earlier WK-1 deterministic prospective-identity,
  generation, recovery, and explicit capability analysis. It proved safety
  concerns but is superseded as the selected ownership model.
- **DEFERRED:** occurrence binding, generic reconciliation, automatic dedupe,
  cryptographic confirmation transport, and broad Keeper reads.

Evidence grounding remains distinct from occurrence/mention binding. Similarity
is advisory; it never silently changes durable identity.
