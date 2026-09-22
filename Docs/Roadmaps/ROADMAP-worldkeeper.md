# Roadmap — World Keeper

**Status:** COARSE DESIGN ROADMAP
**Implementation:** NOT AUTHORIZED
**Planning rule:** each phase requires an explicit reviewed slice; this is not a 20-PR implementation schedule.

## Guardrails

World Keeper should reduce conceptual complexity in the ecosystem. A repository split is not automatically a process split, and a new service name is not permission to add HTTP, a database, retries, or deployment machinery before the semantic boundary is proven.

Every implementation phase must state:

- the contract and invariant it proves;
- the exact DungeonMind capability it consumes;
- the Buddy seam it replaces or retires;
- the adversarial tests and read-back evidence required;
- what remains unauthorized after the phase.

## Coarse phases

### WK-0 — Repository bootstrap / architecture

**State:** this phase.
Create the steward anchor, ownership architecture, boundary, lifecycle design, v0 contracts, source index, and coarse roadmap. No runtime implementation.

### WK-1 — Transport-neutral application contracts

**State:** DESIGN COMPLETE — READY FOR REVIEW

Resolve the open questions needed to implement a minimal application API: intent, prepared change, confirmation, commit/recovery, result/read-back, and semantic failure classes. Keep the contract independent of HTTP and DungeonMind internal DTOs.

**Resolved for review:** four semantic capabilities; retained prepared record plus tamper-evident binding; explicit lifecycle/invalidation states; stable `change_request_id` across safe re-prepare generations; immutable source revision plus optional UTF-8 byte spans; opaque prospective object handles; direct relationship result IDs; exact child-pinned read-back; and the required adversarial outcomes.

**Gate:** steward/reviewer acceptance of the updated v0 contracts and lifecycle design. Acceptance authorizes a later narrow implementation handoff; it does not itself authorize runtime code.

### WK-2 — DungeonMind-backed in-process reference boundary

Build the smallest reference implementation using the existing DungeonMind application/library authority. Prove the repository/process boundary without introducing network complexity. This phase should exercise real World, source, evidence, revision, and publication semantics through narrow adapters.

WK-2 is seam and test-harness proof only. It may establish transport-neutral fixtures, capability probes, and a narrow in-process adapter, but it must not implement or expand World Keeper semantic behavior before WK-1 freezes the application contract; prepare and commit behavior belong to WK-3 and WK-4.

**Gate:** one non-UI client or fixture can call the transport-neutral contract; no duplicate graph or identity authority exists; direct read-back is proven.

### WK-3 — Prepare World change

Implement non-mutating interpretation of the v0 intent family. Prove exact parent binding, source/evidence admissibility, profile/scoping checks, same-transaction local references, deterministic prospective results, and truthful warnings/failures.

**Gate:** adversarial tests show missing, duplicate, wrong-kind, and external local references fail closed; prepare never advances the World head.

### WK-4 — Commit and recover prepared change

Implement explicit confirmation, exact binding verification, stale-parent failure, atomic DungeonMind publication, idempotent recovery, receipts, and exact child read-back.

**Gate:** one confirm produces at most one immutable child; retries recover; stale or modified preparations cannot publish; local-to-durable object mapping is proven.

### WK-5 — World read/query façade

Add only the application-oriented read capabilities demonstrated by a client: exact revision/head, object lookup, search, relationships/neighborhood, evidence/provenance, and scoped/admissible projections. Keep DungeonMind retrieval semantics authoritative.

**Gate:** read results are pinned, fail closed for inadmissible knowledge, and never mutate interpretation or identity.

### WK-6 — DungeonBuddy pilot client

Move one narrow source-grounded authoring loop from Buddy to World Keeper. Preserve source-first interaction, local reversible drafts, explicit review/confirm, stale-parent behavior, and exact result read-back. Keep unrelated product surfaces in Buddy.

**Gate:** the pilot demonstrates user-visible continuity from source selection to durable child revision and result inspection.

### WK-7 — Move authoring semantic compiler out of Buddy

Transfer only the semantic compilation and source/evidence choreography that are proven Keeper responsibilities. Keep product UI, local staging, and agent harness behavior in Buddy. Do not transfer code merely because it currently sits near an authoring service.

**Gate:** the Keeper contract is the one semantic authority for the pilot path; Buddy no longer needs DungeonMind-specific contribution construction.

### WK-8 — Delete replaced Buddy adapters and orchestration

Retire migration-era adapters, duplicate expressibility logic, and compatibility paths only after the Keeper-backed client has independent evidence. Deletion is part of extraction correctness: the old path must not remain a second authority.

**Gate:** no live consumer depends on the retired path; ownership and source indexes are synchronized.

### WK-9 — Second-client / generalization proof

Use a non-DungeonBuddy consumer or a batch/import workflow to test that the contracts are genuinely application-level. Use this evidence to decide whether an optional service transport or additional semantic-profile work is justified.

**Gate:** generality is demonstrated by a named client requirement, not by speculative extension hooks.

## Sequencing rules

- Do not begin WK-2 until WK-1 has accepted the application contract.
- Do not begin any UI extraction until WK-3 and WK-4 prove the safety boundary.
- Do not add an HTTP host as a prerequisite for WK-2 through WK-4.
- Do not authorize automatic merge, generic ontology generation, agent harness work, vector storage, or DungeonMind schema redesign as hidden dependencies.
- If a phase discovers that a responsibility belongs in DungeonMind or Buddy, update the boundary and return the work to design rather than forcing it into Keeper.
