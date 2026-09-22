# Architecture — World Keeper

**Status:** CURRENT ARCHITECTURE AUTHORITY
**Phase:** WK-1 — TRANSPORT-NEUTRAL APPLICATION CONTRACTS
**Implementation:** NOT AUTHORIZED

## Mission

```text
application intent
→ semantic interpretation against governed World truth
→ reviewable prepared change
→ explicit confirmation
→ governed durable publication through DungeonMind
→ exact application-facing read-back
```

World Keeper exists to make the transition from an application's proposed meaning to durable World truth semantically explicit and safe. It is the layer where application intent becomes an exact World transaction.

## Three-layer model

| Layer | Owns | Does not own |
| --- | --- | --- |
| DungeonBuddy and other clients | UI, source selection, user/agent intent, local workflow, review presentation, result presentation | DungeonMind graph-write representation, durable identity authority, publication storage |
| World Keeper | application-level change intent, semantic interpretation, source-grounding coordination, local-reference resolution, prepare/review/confirm binding, recovery coordination, application-oriented reads | UI, agent harness, graph persistence, the durable identity ledger |
| DungeonMind | World identity and scope, immutable revisions and head, source/evidence/provenance, semantic-profile identity, projection/retrieval, governed contribution review/publication, repositories and persistence | product interaction, selected text, document editors, agent/model/tool loops |

World Keeper is in front of DungeonMind. It must use DungeonMind authority rather than recreate it.

## Write architecture

The application submits a transport-neutral `WorldChangeIntent`. World Keeper validates and interprets the entire transaction against:

- one World and scope;
- one exact parent revision or the current parent selected by an explicit policy;
- admissible source/evidence context;
- existing durable objects and relationship endpoints;
- semantic-profile and visibility constraints;
- transaction-local dependencies;
- identity advice and any explicit identity decision.

It returns a `PreparedWorldChange` that explains the exact proposed meaning,
including prospective local-object identities/materializations that dependent
relationships already resolve to. Review happens in the client, but the
prepared interpretation is authoritative input to review. Confirmation must
identify that exact prepared change. DungeonMind then performs its governed
publication against the expected parent, returning an immutable child revision
and durable result identities; commit does not allocate an object and repair
its relationships afterward.

```text
WorldChangeIntent
        │
        ▼
World Keeper prepare
  validate + interpret + resolve
  no durable mutation
        │
        ▼
PreparedWorldChange
  exact parent + source + operations + prospective results
        │
        ▼
client review / human or policy confirmation
        │
        ▼
World Keeper commit or recover
  prove binding + coordinate DungeonMind publication
        │
        ▼
immutable child revision + receipt
        │
        ▼
exact child read-back
```

Prepare and confirm are not two interpretations of the same request. Confirm publishes the prepared interpretation. A changed proposal, source, identity state, or parent must invalidate or reject confirmation.

## Read architecture

World Keeper is not write-only. Clients should be able to ask for World knowledge through an application-oriented contract without learning DungeonMind storage structures. The eventual read family may include:

- current World head and an exact historical revision;
- object lookup and deterministic search;
- relationships and bounded neighborhood;
- source/evidence and provenance views;
- campaign, focus, visibility, and admissibility projections;
- query results suitable for a client surface.

The exact read façade is open. DungeonMind remains authoritative for revision pinning, scope, admissibility, evidence validation, projection, and retrieval semantics. World Keeper may compose or reshape those results for application needs, but it may not reconstruct a foreign graph, broaden visibility, or turn a read into a repair write.

Reads and writes remain separate:

```text
WRITE: source-grounded intent → interpretation → prepared change → confirm → publication
READ:  exact revision → scoped/admissible projection → retrieval/result
```

## Source and evidence boundary

The client supplies the source context it is acting from: an artifact, source
revision, and, where available, a DungeonMind-admitted locator identity. World
Keeper owns the application-facing meaning of that grounding and ensures a
proposed change has an admissible evidence path. DungeonMind owns durable
source identity, evidence records, provenance admission, locator semantics, and
revalidation. Occurrence/mention binding is deferred from implementable v0
until DungeonMind exposes a distinct durable occurrence-to-object write
contract.

The browser or client may not turn a local path, byte digest, or untrusted source label into publication authority. Confirm must re-prove the same selected source/evidence pair that prepare sealed.

## Identity boundary

World Keeper interprets the requested operation:

```text
use an existing object
create a distinct object
explicitly reconcile identities
```

Similarity, duplicate detection, and candidate ranking are advice. They never silently change canonical identity. DungeonMind remains the durable identity authority and ledger. Automatic merge is not part of bootstrap authorization.

## Revision and concurrency semantics

Every prepared change is bound to an exact parent revision and the authority state used to interpret it. DungeonMind publication must enforce expected-parent compare-and-swap semantics and produce one immutable child revision. If another publication advances the parent first, commit fails closed with a stale-parent result or requires re-prepare.

A retry with the same transaction-level `change_request_id` and preparation
generation must recover the original publication from the durable server-side
transaction record rather than create a second child. `confirmation_binding`
authorizes commit only and is not a recovery credential. A per-operation
`operation_id` is not a recovery key. A successful commit is not erased by a
later read/refresh failure; the receipt and refresh outcome are separate facts.

## Failure semantics

World Keeper returns typed, inspectable semantic failures instead of leaking storage or transport exceptions. The initial family is provisional:

```text
invalid_intent
ambiguous_reference
invalid_local_reference
source_inadmissible
identity_conflict
inexpressible
stale_parent
prepared_change_mismatch
authority_unavailable
integrity_failure
publication_failed
```

The service fails closed when it cannot prove source authority, endpoint validity, exact prepared binding, parent freshness, or durable publication outcome. The final taxonomy is a contract decision, not an implementation convenience.

## Transport and process independence

The application contract must not require HTTP. A separate repository is not a mandate for a network process. The likely progression is:

```text
independent repository
→ transport-neutral application API
→ in-process DungeonMind-backed reference implementation
→ optional HTTP/service host when deployment needs it
```

Retries, network errors, authentication, and lifecycle concerns belong at a transport/deployment boundary when one exists; they must not redefine semantic World Keeper contracts.

## Extensibility

DungeonBuddy is the first client, not the definition of World Keeper. The generic core must work for a human UI, an agent proposal, a batch importer, or another structured-fiction application using the same governed intent family. Client-specific workflow labels, campaign UI concepts, model prompts, and agent tools remain outside the core.

Game-specific meanings belong in versioned semantic profiles or client behavior. The generic contract must not assume that every object is an NPC, location, monster, session, or campaign element.

## Non-goals for this architecture phase

This document does not authorize HTTP endpoints, persistence, migrations, vector storage, automatic deduplication, generic ontology generation, an agent harness, a second graph engine, DungeonMind schema changes, live traffic migration, or mutation of an existing World.
