# World Keeper

**Status:** WK-1 accepted / WK-2 accepted / WK-3 prepare active
**Implementation:** limited authorization — WK-3 prepare only

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
DungeonMind V5.4 is accepted and merged at
`6edb9e40d1dc930f537c66deb1afbd1b99002844`. It owns prospective identity
allocation and substitution, atomic publication, durable replay, and result
mapping. WK-3 may now prepare and losslessly compile to that contract without
publishing or predicting durable IDs.

```text
WK-3 ACTIVE — PREPARE ONLY
WK-4 commit and exact-child verification remain unauthorized.
```

No HTTP host, persistence, migrations, agent harness, vector storage,
automatic dedupe, merge/split workflow, publication, commit, or recovery is
authorized by this repository state.
