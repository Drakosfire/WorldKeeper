# World Keeper

**Status:** WK-1/WK-2/WK-3 accepted / WK-4 commit active
**Implementation:** limited authorization — WK-4 commit + exact-child verify

WorldKeeper is the thin semantic transaction coordinator between application
clients and DungeonMind. DungeonBuddy owns interaction and reversible drafts;
WorldKeeper compiles intent into one exact prepared meaning; DungeonMind owns
durable World truth, identity, policy, publication, recovery, and reads.

```text
DungeonBuddy  ->  WorldKeeper  ->  DungeonMind
interaction       meaning          durable truth
and drafts        and coordination
```

## Why WorldKeeper exists

WorldKeeper owns the transition from **reversible application intent** to
**one exact governed change to durable World truth**.

A product action can look simple:

```text
create npc-7
create relationship rel-4:
  result_of(npc-7) -> works_at -> existing castle
```

Before that can become durable truth, the system must answer transaction-level
questions:

- does `create` really mean create-new rather than use an existing identity?
- what exact parent revision, evidence, and authority did the user review?
- do all `result_of(...)` references resolve to the same prospective result?
- what happens if the parent becomes stale before commit?
- who allocates future durable IDs?
- can the new object and its dependent assertions publish atomically?
- what happens if publication succeeds but the response is lost?
- can a retry recover the same result instead of creating another object?
- can the returned mapping be verified against the exact immutable child?

Those are not primarily UI concerns, and they are not durable graph-storage
concerns. They are application transaction semantics.

That distinction drove the extraction from both neighboring systems.

**DungeonBuddy remains the product client.** It owns drafts, selections,
create-new versus use-existing choice, similarity presentation, review UX,
agent orchestration, and result presentation. If transaction interpretation
lived there, governed World-change semantics would become Buddy-specific and
other clients would need to reproduce them.

**DungeonMind remains the durable knowledge authority.** It owns durable
identity, provenance, semantic admission, immutable revisions, expected-parent
CAS, atomic publication, durable receipts, replay/recovery, and exact reads. If
product interpretation and review workflow lived there, the generic knowledge
kernel would become an application workflow engine.

WorldKeeper sits between them:

```text
Buddy
  "What is the user trying to do?"
        ↓
WorldKeeper
  "What exact semantic transaction does that mean?"
        ↓
DungeonMind
  "What is durably true?"
```

The prospective-identity boundary is the clearest example. WorldKeeper may bind:

```text
result_of("npc-7")
```

but it must not predict the future durable entity ID. DungeonMind allocates that
identity during one atomic publication, substitutes it through every dependent
assertion, and returns the durable mapping.

The same principle applies to recovery. WorldKeeper does not maintain a second
durable ledger answering whether publication happened. The prepared change
provides the stable publication identity; DungeonMind owns the durable receipt
and replay/recovery evidence.

The intended mental model is:

```text
DungeonBuddy  owns possibility and interaction.
WorldKeeper   owns intended change.
DungeonMind   owns durable truth.
```

WorldKeeper exists so a proposal can remain reversible and reviewable until the
moment it becomes exactly one verified durable change—without making the
product become the database or the database become the product.

The current decision and inspected DungeonMind evidence are recorded in
[`DECISION-worldkeeper-ownership-simplification.md`](Docs/Design/DECISION-worldkeeper-ownership-simplification.md).
DungeonMind V5.4 is accepted and merged at
`6edb9e40d1dc930f537c66deb1afbd1b99002844`. It owns prospective identity
allocation and substitution, atomic publication, durable replay, and result
mapping. WK-3 prepares and losslessly compiles to that contract; WK-4 may now
publish an intact prepared value and verify the exact immutable child.

```text
WK-3 COMPLETE — WK_3_PREPARE_WORLD_CHANGE_ACCEPTED
WK-4 ACTIVE — COMMIT PREPARED CHANGE + EXACT-CHILD VERIFY
```

No HTTP host, persistence, migrations, agent harness, vector storage,
automatic dedupe, merge/split workflow, prepared-state persistence, or a
WorldKeeper recovery ledger is authorized by this repository state.
