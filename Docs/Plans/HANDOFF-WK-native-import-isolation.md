# V10 prerequisite — native WorldKeeper import isolation

Status: IMPLEMENTED — exact-head qualification/review pending. Owner: MIND, under the operator's explicit full-lane execution,
review and merge authority. Base: `3e79dbd` (fresh remote main, docs-only after
accepted WK `ef9c50f2d6aa89a35e9408f83fc4d0ba47825ca2`). This assignment is
pinned before runtime edits. It narrows imports, not transaction semantics.

## Outcome and dependency order

Importing native DungeonMind runtime/preparation/compiler/commit from the
WorldKeeper integration must not import WorldKeeper's classic in-process
adapter. Preserve that exact read-only historical adapter behind explicit
`worldkeeper.integrations.dungeonmind.compat`, and retain its existing direct
`.in_process` module for historical imports. Remove the classic symbol from the
current integration root; do not add a lazy fallback there.

One coherent, independently reviewable WorldKeeper PR. Serial delivery: this
slice, then explicit Buddy dependency repin and native consumer qualification;
Core consumer qualification follows its actual dependency boundary. Neither a
source checkout nor a WorldKeeper merge updates the running Buddy process.
The old integration-root classic import is intentionally retired; historical
callers must opt into `compat` or their existing direct historical module.

Predecessors: Buddy #4207 accepted native manual UI; Core #244 checkpoint merge
`e83ab2664f6c953f4a8726ff053b24703440452a`; Buddy #4215 classic manual retirement
merge `c19f4d90dc5628399009cdd12831d01bc5dd2c83`, tested head
`3cdd67cbcb324f81d992c799fce17e5bf00b5895`, review `5988124380`.
That bounded acceptance retains full UI's 102 failures and two report-only
collection extras; no aggregate-green or deployed-cutover claim follows.

## Exact five-path write lease

1. This handoff: contract, evidence and honest next gates.
2. `src/worldkeeper/integrations/dungeonmind/__init__.py`: remove eager classic
   adapter import/export; preserve all native exports exactly.
3. `src/worldkeeper/integrations/dungeonmind/compat.py`: new explicit historical
   re-export of the unchanged `.in_process.DungeonMindInProcessAuthority` class.
4. `tests/test_package_boundary.py`: current versus compatibility exports,
   identity preservation and cold subprocess import rejection tripwire.
5. `tests/test_dungeonmind_inprocess_boundary.py`: historical import opt-in only;
   preserve the actual historical read/refusal assertions unchanged.

No edits to adapters, preparation/commit/runtime algorithms, contracts, domain
schema bundle, requests/receipts, dependency manifests/lock, CI, transport,
persistence, database, provider, serving processes or stored data. Do not touch
PR #15's documentation regions or replace the stale anchor wholesale. Its documentation
lease does not own these runtime/test regions; this MIND
assignment owns the named regions under the operator's authority.

## Owning proof and qualification

A cold subprocess must block importing the WK `.in_process` module and still
import the integration root, native runtime, preparation/compiler and commit
exports. Assert the retired root symbol is absent; a root export-list edit alone
is insufficient. In a separate subprocess the explicit compatibility import
must resolve to the identical original class. Keep and execute existing actual
historical adapter behavior tests, not merely import assertions.

This does not claim Core's native package imports are themselves classic-free:
Core currently has independent eager classic initializer edges. That is a later
Core retirement slice, not grounds to weaken the precise WK tripwire.

Use a dedicated retained task environment from the unchanged WK lock and build
an installed wheel into task-owned Projects storage. Run the full WK suite,
Ruff and Pyright on the exact final head; execute cold import proof against the
installed wheel, with no WK/Core source overlay. Inspect the cumulative five-path
diff and obtain independent exact-head review. Preserve failures and distinguish
source diagnostics, installed-package execution and any later unexecuted merge.
No frozen retrieval baseline rerun. No resync of the accepted Buddy environment.

## Remaining false and safe next work

V10 is not complete. Core public classic writers and direct projection/read
paths still require actual retirement or named historical disposition; merely
hiding exports does not retire callable authority. Buddy presentation helpers
still import classic read modules. Historical receipt recovery must remain exact
and read-only before removing its writer dependency. Core operator attestations
need explicit quarantine without rewriting immutable fields. After retirement:
compatible primary/fallback deployment, later-write-safe rollback/restart and
V11 deployed latency/work/memory and authorization/citation acceptance remain.

The serving stack is unchanged. No new bridge or ingestion is required.

## Resource ownership

Reuse the clean, fully merged, inactive WorldKeeper checkout on verified Projects
UUID `48fa5d10-fe99-4557-9fc9-d8a2a4b41ac8`, on this new non-main branch. All
standalone outputs and isolated environment/cache live under
`/home/drakosfire/Projects/.codex/v7-elderwyld-scope/{scratch,cache}/v10-wk-native-import`.
MIND retains these through the full goal for qualification/recovery. No manual
deletion authorized; cleanup follow-up requires active-process/mount, dirty data,
unique-commit protection and explicit approved scope. No reclaimed bytes claimed.

## Implementation checkpoint

Lease pin: `fefc4a6` before runtime edits; independent Hubble readiness PASS.
Reused original clean, merged checkout after no active process cwd was found.
Working candidate installed-wheel diagnostics: all 98 tests pass, zero skips;
Ruff passes; Pyright zero errors/warnings. The wheel resolves outside the source
checkout in a separate retained environment, Python3.14.3, using unchanged locked
Core4ccd. Accepted Buddy Core90a5/WKef9 environment remains untouched. Downstream
qualification must preserve Core90a5 while adopting the accepted WK ref.

Final exact-head results belong to the PR and task evidence, not this earlier
working diagnostic. Source-inspection tests inspect source intentionally; runtime
imports and cold subprocesses execute the installed wheel. No execution is
claimed for a future merge tree. The initial Ruff invocation attempted its
default cache on a read-only path; rerunning with `--no-cache` passed, with no
source or configuration workaround.
