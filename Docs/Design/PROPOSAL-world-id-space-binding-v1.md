# Proposal — World ID to DungeonMind space binding

**Status:** PROPOSED / BLOCKED — not accepted WorldKeeper authority
**Review base:** `main@662a028fb1882719c4c3e192134a1a6b7a58026c`
**Implementation:** NONE AUTHORIZED
**Decision owner:** WorldKeeper Architecture / PRIME

This proposal records the corrected owner split relayed by PRIME on 2026-09-30.
It is not yet captured in the checked-in WorldKeeper architecture authority and
grants no write lease. The current steward anchor still says there is no active
implementation lease.

## Provisional owner split

- **DungeonMind**, first: owns idempotent canonical space-ID minting/provisioning,
  source/evidence IDs, evidence records, graph truth, and publication. The
  current initializer is not the minting capability; MIND must add that
  predecessor. WorldKeeper must not invent graph/evidence IDs or fabricate
  sources/assertions.
- **DungeonBuddy**, after DEMO C1 releases its lease: owns the durable product
  World registry and its `PENDING → ACTIVE` World-ID-to-MIND-space-ID binding.
  It owns user-facing import/confirmation and supplies World ID; callers do not
  select a DungeonMind space directly.
- **WorldKeeper**, after both predecessors merge: owns the typed binding port,
  domain validation, and prepare/commit revalidation. It reads an active-binding
  witness from the Buddy registry; its pure package does not persist the mapping.

## Proposed binding invariants

1. A `world_id` resolves only through an explicit durable binding. Unknown or
   unbound Worlds fail closed.
2. One World has exactly one dedicated DungeonMind space; one space cannot be
   bound to two Worlds. Buddy's durable registry owns `PENDING → ACTIVE` and
   uniqueness. Ordinary reassignment is rejected; populated-World migration or
   rebind needs an explicit migration path and receipt.
3. `campaign_id` is not a World key or alias. Equal World/campaign strings do
   not create a binding or grant access. World ID and space ID are never
   implicitly equal.
4. Consumer `WorldChangeIntent` is World-ID keyed; callers do not choose a raw
   `space_id`. The prepared value records World ID and the resolved MIND space
   (or an accepted binding version) so commit can revalidate through
   WorldKeeper's typed port.
5. Prepare resolves only the bound space, reads its exact current parent, and
   accepts evidence refs only when they occur in that parent. It records the
   exact parent revision and graph digest. Commit rechecks the binding and then
   delegates unchanged to WK-4; existing stale-parent and exact-child behavior
   remains authoritative.
6. Binding an empty World creates no source, evidence, object, or assertion.
   Initialization is the existing DungeonMind capability, not a WorldKeeper
   contribution.

## Existing DungeonMind prerequisite and unresolved boundary

DungeonMind main `4758fe812b539ad8209031ae22c05d36f7636957` exports
`initialize_empty_knowledge_space` from
`src/dungeonmind/application/vnext/__init__.py`, implemented in
`src/dungeonmind/application/vnext/initialization.py`. It creates a canonical
empty genesis with no entities, assertions, or evidence, and uses
`initialization_id` for durable exact retry.

The initializer requires a caller-supplied `space_id`; it does **not** mint
that ID. Corrected architecture assigns MIND a first predecessor slice for
idempotent canonical space-ID minting/provisioning. Buddy's later registry
activation must consume that result/receipt. Do not substitute a WorldKeeper
UUID, campaign ID, or unverified caller-chosen alias.

WorldKeeper currently has no durable World-binding store or persistence
dependency, and corrected architecture assigns the durable registry to Buddy.
Buddy's registry contract and read port, lifecycle/receipt fields, uniqueness
and concurrency behavior, restart semantics, and populated-World
rebind/migration protocol must be pinned before WorldKeeper paths can be frozen.
An in-memory repository is test-only and cannot prove Buddy's durable behavior.

## Explicit hold

No implementation lease is active. Hold WorldKeeper code until MIND's
space-ID mint/provisioning predecessor and Buddy's durable registry predecessor
merge, their public receipt/read contracts are pinned, and WorldKeeper's
validation-port/lifecycle scope is recorded in checked-in authority with a new
bounded handoff. This proposal does not activate that handoff.
