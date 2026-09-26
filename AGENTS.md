# WorldKeeper repository operating law

WorldKeeper is the semantic transaction coordinator between reversible application intent and DungeonMind durable World truth. Durable workstream status does **not** belong in this file; read `Docs/Steward/STEWARD-ANCHOR-worldkeeper.md` for current pickup.

## Ecosystem execution core — overmind-agent-core-v1

These rules are intentionally shared across active DungeonMind ecosystem repositories. Repository-specific law may add constraints, but it must not weaken this core.

1. **Re-anchor before action.** Fetch the current remote default branch and inspect relevant open PRs/active work before editing, reviewing, or merging. Chat history, stale handoffs, and local `main` are not current authority.
2. **Respect ownership boundaries.** Cross-repository architecture and sequencing belong in DungeonOverMind; runtime/product implementation belongs in the repository that owns the capability. When a change crosses owners, name the contract.
3. **Handoffs are portable bounded contracts.** A handoff may live on `main`, a branch, a PR, or another durable pinned ref/location. Its location alone neither activates nor invalidates it. Execution authority comes from explicit authorization/status, a pinned authority/ref, and bounded scope/write ownership. Do not require a handoff to be merged to `main` unless the specific workstream explicitly makes that a gate.
4. **Finish authorized implementation work all the way to a PR.** Once implementation is authorized, ordinary completion includes: implement → test/verify → inspect the cumulative diff → commit intended changes → push the branch → open or update the assigned PR. If no PR exists, open it. Do not stop with intended work only local, uncommitted, or unpushed and wait for another prompt to commit/push/open the PR.
5. **Merge is separate authority.** Opening/updating a PR is part of implementation completion; merging it is not. Merge only when the user or the repository's explicit process authorizes merge.
6. **Use isolated Git lanes.** Do not develop on local `main`. Use a branch/worktree or equivalent isolated checkout, and treat file/runtime/state collisions as coordination problems rather than relying on Git conflicts.
7. **Keep slices bounded.** One implementation slice should deliver one independently useful capability. A second capability, new durable/public contract, or unplanned extra PR is a stop/split signal unless explicitly authorized.
8. **Verify at the owning boundary.** Review the exact cumulative base→head diff and prove behavior at the layer that owns the invariant. A green helper test is not evidence for a boundary it does not exercise.
9. **Settle after merge.** Re-anchor, synchronize mutable authority that now became stale, and prune superseded process/transition scaffolding. Git history is the default archive; preserve a separate archive copy only when it carries unique durable evidence.

## Authority and pickup

- Begin with `Docs/Steward/STEWARD-ANCHOR-worldkeeper.md`, then follow its current pickup order.
- The steward anchor owns changing workstream state. Architecture/decisions/contracts own stable semantics. Historical handoffs and source material are evidence only.
- Do not treat DungeonMindBuddy implementation details or chat reconstruction as WorldKeeper authority.
- Keep unresolved design questions explicitly unresolved. Missing authority is a stop condition, not permission to invent an endpoint, persistence layer, schema, or lifecycle.

## Correctness invariants

- WorldKeeper interprets application intent; DungeonMind owns durable World truth.
- Prepare is non-mutating and binds one exact interpreted change to exact parent/source/evidence/authority context.
- Confirm publishes only that prepared meaning. Changed proposals, changed authority, or stale parents require fail-closed handling or re-prepare.
- Transaction-local references are scoped to one prepared intent, unique, and resolved completely before publication.
- Prospective handles are not predicted durable IDs. DungeonMind owns durable identity allocation/substitution.
- Identity similarity is advisory. Automatic identity merging is not implicitly authorized.
- A successful write includes exact immutable child verification; an HTTP/service success alone is not durable proof.
- Reads/projections do not mutate interpretation or repair writes.
- DungeonMind owns durable publication receipts/replay/recovery. WorldKeeper must not create a second durable truth or recovery ledger.

## Repository restrictions

- Keep WorldKeeper transport-neutral unless current accepted authority explicitly authorizes a transport.
- Do not add persistence, migrations, an Agent harness, vector storage, automatic deduplication, a second graph, generic read façade, or DungeonMind allocator/recovery logic merely for convenience.
- Do not copy DungeonMindBuddy modules wholesale. Separate product behavior from reusable semantic transaction behavior before moving anything.
- A change that broadens WorldKeeper authority must name the accepted architecture/decision that grants that authority.
- Before handback, report the exact branch/head, cumulative changed paths, verification results, and unresolved stop conditions.

## Review-only requests

A review request, pasted review, or reviewer verdict is review authority, not implementation authority, unless it explicitly grants or references an active implementation lease.
