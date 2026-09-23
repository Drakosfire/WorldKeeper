# Boundary — DungeonBuddy, WorldKeeper, and DungeonMind

**Status:** CURRENT BOUNDARY AUTHORITY
**Phase:** WK-1/WK-2 accepted; WK-3 prepare active
**Implementation:** LIMITED AUTHORIZATION — WK-3 PREPARE ONLY

## Boundary statement

```text
DungeonBuddy captures and presents application intent.
WorldKeeper compiles that intent into one exact semantic transaction.
DungeonMind owns durable governed World truth and publication.
```

| Responsibility | DungeonBuddy | WorldKeeper | DungeonMind |
| --- | --- | --- | --- |
| interaction and reversible drafts | owns | no | no |
| source selection and presentation | owns context | validates coherence | owns durable source/provenance authority |
| create-new vs use-existing choice | obtains explicit choice | validates and preserves choice | owns durable identity |
| similarity/duplicate suggestions | presents advisory candidates | does not decide by similarity | supplies governed facts/search |
| local references | creates `client_op_id` and `result_of(...)` links | resolves completely in prepared meaning | V5.4 allocates and substitutes only during publication |
| preparation | requests and reviews | owns semantic interpretation | supplies authoritative reads/admission |
| durable publication | confirms UX | coordinates one governed call | allocates IDs, materializes, advances immutable head atomically |
| publication outcome/retry | presents result | reshapes verified result | owns durable outcome and replay/recovery |
| ordinary World reads | consumes product adapter as needed | no general façade | owns exact/search/neighborhood/evidence reads |

## Accepted prospective publication boundary

DungeonMind V5.4 at merged authority `6edb9e40…` accepts prospective create
references, allocates type-separated durable IDs at its owning boundary,
substitutes them through dependents before materialization, publishes atomically,
and returns durable mappings. WK-3 may compile to this accepted syntax but may
not call publication or predict/reproduce the allocation.

No object-first/dependent-repair sequence, automatic merge, second graph, or
WorldKeeper durable recovery ledger is permitted.
