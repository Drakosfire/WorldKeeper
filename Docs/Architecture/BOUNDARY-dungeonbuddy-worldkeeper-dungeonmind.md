# Boundary — DungeonBuddy, World Keeper, and DungeonMind

**Status:** CURRENT BOOTSTRAP BOUNDARY AUTHORITY
**Phase:** DESIGN / REPOSITORY BOOTSTRAP
**Implementation:** NOT AUTHORIZED

## Boundary statement

```text
DungeonBuddy captures and presents intent.
World Keeper interprets intent into an exact governed World transaction.
DungeonMind owns durable governed World truth.
```

The repository split is not permission to copy every current Buddy module into a new package. Current code is migration evidence. Ownership follows the semantic responsibility and the safety guarantee, not the current filename.

## Responsibility matrix

| Responsibility | DungeonBuddy / other clients | World Keeper | DungeonMind |
| --- | --- | --- | --- |
| UI state and surface flow | owns | no | no |
| source selection and source presentation | owns product choice and context | validates and interprets grounding | stores/proves durable source identity and provenance |
| user-authored or agent-proposed intent | captures and edits | consumes and validates semantically | no product intent |
| working local transaction | stages and presents reversible edits | defines semantic validity and dependency rules | no unresolved local references |
| duplicate/similarity suggestions | presents | interprets as advisory evidence | supplies governed facts and identity state |
| identity decision | requests an explicit choice | validates/plans the requested operation | persists canonical identity authority |
| transaction-local references | creates local operation IDs | resolves completely within the prepared intent | receives only resolved durable endpoints |
| semantic contribution construction | no long-term knowledge of internal DTOs | owns translation/orchestration at its boundary | consumes its governed contribution/publication contract |
| graph revisions and head | displays returned identities | coordinates expected-parent semantics | owns immutable revisions and atomic head publication |
| source/evidence records | supplies context | coordinates application-facing admissibility | owns durable records and provenance rules |
| publication | requests confirmation | coordinates prepare/commit/recovery | owns durable mutation authority |
| recovery and idempotency | consumes result | exposes semantic recovery operation | owns durable publication evidence and recovery behavior |
| object/search/neighborhood reads | presents results | offers application-facing façade | owns projection/retrieval semantics |
| agent harness, prompts, tools, retries | owns when applicable | no | no |

The `semantic contribution construction` row is intentionally boundary-sensitive. World Keeper owns the application-to-DungeonMind translation responsibility; it must not expose DungeonMind's internal representation as its public contract. The final in-process adapter shape is open.

## Client → Keeper interaction

Clients may send:

- World identity and optional scope/focus;
- source context selected by the user or workflow;
- user-authored fields and operation choices;
- durable references already known to the client;
- transaction-local operation/reference IDs;
- actor/caller context needed for policy evaluation;
- a client request identity for idempotent recovery.

Clients must not be required to construct `GraphContribution` records, evidence records, identity-ledger operations, publication IDs, database rows, or persistence structures. A client may receive a prepared change and commit receipt, but those are World Keeper contracts, not permission to author DungeonMind internals.

## Keeper → Mind interaction

World Keeper asks DungeonMind for the governed facts and operations it needs:

1. resolve the exact World parent and applicable scope/profile state;
2. validate or admit the source/evidence pair;
3. inspect existing objects and endpoints;
4. interpret and assemble one complete prospective change;
5. bind the prepared change to exact authority;
6. publish/recover through expected-parent and durable operation semantics;
7. read back the exact child revision.

DungeonMind must never receive an unresolved `local:*` endpoint or a client-local path as if it were durable World authority.

## Current Buddy seams: migration classification

| Current seam | Bootstrap classification | Extraction implication |
| --- | --- | --- |
| `graph_object_authoring_prepare.py` / `graph_object_authoring_commit.py` | implementation evidence for prepare/confirm, source re-proof, stale-parent failure, and receipt behavior | preserve safety properties; do not copy request/response models as the public Keeper contract |
| `world_graph_authority.py` and source-admission ports | migration-era storage-neutral seams | useful evidence for required semantics; replace or adapt when Keeper can call DungeonMind directly |
| `integrations/dungeonmind/` | client-specific adapters to an already independent authority | much of this should disappear from Buddy or become a thin client adapter after extraction |
| authoring UI/local proposal store | DungeonBuddy product behavior | stays in the client; Keeper accepts the resulting semantic intent |
| current expressibility classifier | transitional product repair | do not freeze it as architecture; semantic expressibility belongs at the Keeper boundary eventually |
| prepare signing / exact parent binding | accepted safety property | preserve exact binding, regardless of token or digest implementation |
| authored overlay / gold workflow | historical or product/evaluation behavior | not durable World truth; do not move it wholesale |

The checked-in source index pins the reviewed Buddy head and current source heads so future extraction work can distinguish accepted semantics from branch-local implementation state.

## Ownership rules that must survive extraction

### Source-first authoring

The client can begin from highlighted text, an existing World object, or a relationship context. It owns the interaction and local draft. Keeper owns the meaning of the resulting World intent and its grounding.

### One coherent transaction

An object plus a relationship to that object is one proposed transaction. No create/publish/discover/repair sequence is allowed as a substitute for resolving local references during prepare.

### Advisory identity

Same label, similarity, or an extracted candidate does not equal same identity. A client can request a distinct object even when overlap is visible. Only an explicit reconciliation operation may alter canonical identity.

### Exact publication

The child revision, local-to-durable mappings, and source/evidence relationship must be read back from the exact publication result. Refresh and presentation linking are separate read concerns.

## Deliberate non-boundaries

World Keeper does not own:

- selected text, document editors, or campaign-specific navigation;
- model/provider selection, prompts, tool loops, retries across product tools, or conversation state;
- PostgreSQL schema, graph revision storage, source ledger, or identity ledger;
- a second projection engine or a client-side graph reconstruction;
- automatic merge/dedupe or generic ontology generation.

DungeonMind does not own product interaction or agent harness behavior. DungeonBuddy does not own durable World truth. The boundary is invalid if either statement becomes false by convenience.

## Boundary review questions

Before implementation is authorized, reviewers must be able to identify for each proposed module:

- the user/client requirement it serves;
- whether it interprets intent or stores durable truth;
- the exact DungeonMind contract it consumes;
- why the responsibility is not in the client or in DungeonMind;
- the proof of local-reference, parent, evidence, and read-back correctness;
- the deletion or retirement path for the Buddy seam it replaces.
