# Boundary — DungeonBuddy, WorldKeeper, and DungeonMind

**Status:** CURRENT BOUNDARY AUTHORITY
**Phase:** WK-1/WK-2 accepted; DungeonMind prerequisite before WK-3
**Implementation:** NOT AUTHORIZED

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
| local references | creates `client_op_id` and `result_of(...)` links | resolves completely in prepared meaning | receives prospective references only after future contract exists |
| preparation | requests and reviews | owns semantic interpretation | supplies authoritative reads/admission |
| durable publication | confirms UX | coordinates one governed call | allocates IDs, materializes, advances immutable head atomically |
| publication outcome/retry | presents result | reshapes verified result | owns durable outcome and replay/recovery |
| ordinary World reads | consumes product adapter as needed | no general façade | owns exact/search/neighborhood/evidence reads |

## Prospective publication prerequisite

The current DungeonMind contract at `1fc03aa…` requires materialized edge
endpoints to be durable `subject_object_id` and `object_object_id` values.
WorldKeeper therefore cannot safely implement WK-3 by allocating or predicting
those IDs. DungeonMind must add and prove an owning-boundary contract that
accepts prospective create references, substitutes each allocated durable ID
through all dependents in one publication, and returns the mapping.

No object-first/dependent-repair sequence, automatic merge, second graph, or
WorldKeeper durable recovery ledger is permitted.
