# World Keeper

**Status:** WK-1 accepted / WK-2 accepted / WK-3 design review blocked
**Implementation:** WK-3 not authorized

WorldKeeper is the thin semantic transaction coordinator between application
clients and DungeonMind. DungeonBuddy owns interaction and reversible drafts;
WorldKeeper compiles intent into one exact prepared meaning; DungeonMind owns
durable World truth, identity, policy, publication, recovery, and reads.

```text
DungeonBuddy  ->  WorldKeeper  ->  DungeonMind
interaction       meaning          durable truth
and drafts        and coordination
```

WorldKeeper must not predict future DungeonMind IDs, maintain a second graph or
recovery ledger, or publish an object and repair dependent relationships later.
Prepare binds same-transaction references to exact prospective create results;
DungeonMind must allocate and substitute durable identities atomically during
publication.

The current decision and inspected DungeonMind evidence are recorded in
[`DECISION-worldkeeper-ownership-simplification.md`](Docs/Design/DECISION-worldkeeper-ownership-simplification.md).
At DungeonMind `1fc03aa21e406d9a7cb07d0e4792e202fe281375`, the materialization
contract still requires durable relationship endpoint IDs. Therefore the next
coding slice belongs in DungeonMind, not WorldKeeper.

```text
WK-3 implementation is BLOCKED
until DungeonMind prospective-reference atomic publication is available
and proved at its owning boundary.
```

No HTTP host, persistence, migrations, agent harness, vector storage,
automatic dedupe, merge/split workflow, or runtime WK-3 behavior is authorized
by this repository state.
