# HANDOFF proposal — World ID to DungeonMind space binding

**Status:** BLOCKED — proposal only; NO IMPLEMENTATION LEASE
**Repository:** `Drakosfire/WorldKeeper`
**Review base:** `662a028fb1882719c4c3e192134a1a6b7a58026c`
**Architecture proposal:** [`PROPOSAL-world-id-space-binding-v1.md`](../Design/PROPOSAL-world-id-space-binding-v1.md)
**Current state:** WK-1 through WK-5 complete; no active implementation lease

This document describes a candidate bounded slice. It is not executable
authority. Do not begin implementation until the stop conditions below are
resolved in accepted WorldKeeper authority and a new lease names this handoff.
The current proposal PR may change only these two documents to record the
provisional split and hold; it is not the successor implementation PR.

## Outcome after activation

Expose governed changes by product `world_id`, resolving through Buddy's durable
`PENDING → ACTIVE` registry mapping to a DungeonMind space. WorldKeeper owns the
typed validation port/domain checks and prepare/commit revalidation, not the
durable store. Preserve accepted WK-3/WK-4 semantics and MIND-owned space and
evidence identities.

## Required decisions before activation

- MIND must merge its first predecessor: idempotent canonical space-ID
  minting/provisioning and an exact receipt. The current initializer accepts a
  caller-supplied ID; it does not satisfy the minting part by itself.
- After DEMO C1 releases its lease, Buddy must merge its durable product-World
  registry with `PENDING → ACTIVE`, atomic one-to-one uniqueness, restart and
  concurrency guarantees, and a read/witness port for WorldKeeper.
- Buddy's registry contract must define explicit populated-World migration or
  rebind evidence. Ordinary reassignment is rejected and same-pair retry is
  idempotent.
- Record the architecture ruling and successor lease in current checked-in
  authority. The existing steward anchor explicitly has no active lease.

## Candidate implementation paths

The following WorldKeeper application paths are a provisional sketch, not a
frozen write allowlist. Revisit them after MIND/Buddy predecessors merge and
their exact contracts are known. Durable storage is owned by Buddy, not WK:

- `src/worldkeeper/application/contracts.py` — make consumer intent World-ID
  keyed and retain the resolved World ID in immutable prepared meaning.
- `src/worldkeeper/application/world_binding.py` — candidate typed binding
  witness/validation port and fail-closed domain rules; no persistence adapter.
- `src/worldkeeper/application/preparation.py` — resolve the explicit binding
  before calling existing prepare logic; preserve exact-parent evidence checks.
- `src/worldkeeper/application/commit.py` — verify the prepared World/space
  pair still matches the binding before delegating to existing WK-4 commit.
- `src/worldkeeper/integrations/dungeonmind/runtime.py` — compose the binding
  service with accepted prepare/commit services; do not duplicate lifecycle or
  call an ID allocator.
- `src/worldkeeper/application/__init__.py` and `src/worldkeeper/__init__.py` —
  export only the accepted public contract.
- Buddy-owned durable registry paths: **TBD by Buddy's accepted predecessor
  PR**; WorldKeeper consumes only its pinned typed read port. No fake WK store.

Buddy UI/import/registry and MIND provisioning code are predecessor slices, not
WorldKeeper changes. The WorldKeeper PR starts only after both merge; it consumes
the MIND-issued space identity and Buddy's active binding witness.

## Proof plan after activation

Add `tests/test_world_binding.py` and
`tests/test_world_binding_runtime.py`, plus focused extensions to existing WK-3
and WK-4 tests where needed:

- unknown and unbound World reject; no default, campaign alias, or implicit
  `world_id == space_id` path;
- WorldKeeper rejects inactive/pending/unbound and cross-World binding
  witnesses; Buddy tests—not WK fakes—own durable uniqueness/reopen/concurrency
  proof;
- use MIND's merged mint/provision operation and receipt to prove an empty
  genesis and exact retry; WorldKeeper adds no source, evidence, entity, or
  assertion;
- evidence present in the bound space's exact parent is accepted and captured;
  an ID only present in another space is rejected;
- prepared World ID, resolved space, exact parent and evidence remain coherent
  through commit; cross-World/tampered binding fails before publication; stale
  parent and exact-child verification remain the existing WK-4 behavior;
- populated-World migration/rebind only follows the accepted explicit protocol.

## Stop conditions

- MIND space-ID source/receipt semantics remain ambiguous;
- either MIND's mint/provision predecessor or Buddy's durable registry/read-port
  predecessor remains unmerged;
- authority does not explicitly grant the binding and persistence scope;
- implementation would add Buddy mapping/UI, source admission, fabricated
  evidence/assertions, generic World reads, or duplicate WK-3/WK-4 behavior.

## Successor implementation PR plan (not opened)

After both predecessors merge and the WorldKeeper authority/lease is accepted,
re-anchor to latest main and open one WK implementation PR for the finalized
validation-port paths and tests. Do not include Buddy's registry or MIND's
provisioner. Suggested title: `WorldKeeper: validate product World bindings`.
This docs-only proposal PR may merge after review to record the owner split and
hold. Its merge grants no implementation authority. Keep the successor
implementation BLOCKED until both predecessors merge, the WorldKeeper authority
is updated, and a new bounded implementation lease is explicitly issued.
