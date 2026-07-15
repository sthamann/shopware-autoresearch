---
name: parallel-workers
description: >-
  Coordinates parallel agent sessions and git worktrees for verification work
  without colliding on registry.csv or shared config. Use when launching
  multiple background workers, parallel verification waves, worktree
  isolation, or merging claim branches.
---

# Parallel Workers

Rules: `verification-lifecycle.mdc`, `project-startup.mdc`

## Shared bottlenecks (serialize or isolate)

| File | Risk |
|---|---|
| `<verification_dir>/registry.csv` | Status races, CSV corruption |
| Shared config files | Conflicting default flips |
| Shared caches / fixtures | Invalidation races |

**Rule:** one writer per bottleneck per wave, OR a git worktree per worker
plus sequential merge.

## Locks (built into the tools)

- **Registry lock** (`.registry.lock`): `tools/register.py` and
  `tools/run.py` do read-modify-write of `registry.csv` under an exclusive
  lock-file with stale-PID takeover and atomic replace. Never hand-edit the
  registry during an active wave.
- **Claim run lock** (`<claim-folder>/.run.lock`): two sessions cannot
  officially run the same claim at once. A live holder → `BUSY` (no wait):
  the claim is skipped, its registry status stays untouched (the holder's
  run owns the verdict), and the runner exits non-zero. A dead holder's
  lock auto-clears on the next acquire.
- **Atomic artifacts:** write `last_run.json` via
  `tools/lib/registry.py::atomic_write_json` in new harnesses — a killed
  process must not leave half-written JSON.

## Shared scarce resources

If workers compete for exclusive resources (databases, devices, ports),
add a project-level reservation convention: claim before the run with a
label + TTL, release after, take over only stale (dead-PID) reservations.
Never wait with hand-rolled polling loops in each worker — one shared
mechanism.

## Worker prompt checklist

Paste into every parallel worker:

```text
- Own only these paths: [list disjoint files]
- Do NOT edit registry.csv unless you are the registry coordinator
- On gate failure: honest-negative skill — Failed + missing capability
- Never `git add -A` — stage only your own files
- Report the exact config/flags your run used (no assumed defaults)
```

## Coordinator duties (parent agent)

1. Assign **disjoint file sets** per worker
2. **One** registry editor merges status after all workers finish
3. `python3 tools/scan.py --audit` after any registry change
4. Project health checks **before** push
5. Never bulk-stage while workers still write shared files

## Worktree pattern

```bash
# One worktree per parallel claim; a merge coordinator integrates after green runs
git worktree add ../wt-<claim> -b verify/<claim>
```

## Crash resume (standard)

1. Crash mid-run → re-run a single leg: `<PREFIX>_REUSE=1` +
   `python3 <claim-folder>/run.py --job <name>` (skill `fast-iteration`)
2. Once green → official `python3 tools/run.py <CLAIM_ID>` (respects the
   run lock; a stale lock auto-clears when the holder PID is dead)
