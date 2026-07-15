---
name: claim-lifecycle
description: >-
  Implements verification claims — register.py, init_folder.py, frozen gates,
  tools/run.py, honest promotion. Use when adding a feature, creating a claim,
  promoting Planned to Verified/Failed, or following the lifecycle before
  writing feature code.
---

# Claim Lifecycle

Rule: `verification-lifecycle.mdc`

## Laws

- No green `tools/run.py` → feature is **not** implemented.
- An autoresearch `keep` on main ≠ Verified.
- No measured positive impact → feature stays off or is deleted.

## Before implementation

0. `python3 tools/memory.py query "<topic>"` — was this tried, with what
   result? (skill `verification-memory`; mandatory duplicate check)
1. `python3 tools/scan.py` — coverage, duplicates, orphans
   (periodically: `--stale-planned` — Planned triage blocked/stale/fresh)
2. `python3 tools/register.py <CLAIM_ID> "<claim text>"` — registry row,
   `status=Planned`. Claim text = falsifiable sentence **with thresholds and
   anti-patterns**. New family → assign a track in `tracks.json`
   (register.py warns otherwise). Re-scope → `--supersedes <old claim>`.
3. `python3 tools/init_folder.py <CLAIM_ID>` — folder `YYYY-MM-DD-NN-CLAIM_ID`
4. Freeze acceptance gates in the claim's `run.py` + README **before**
   feature code. A gate that cannot fail is not a gate — run it once with
   the change absent and require a red result.
5. README + CHANGELOG for touched modules; declare the claim's `scope`
   (paths it may edit) in the registry row.

## After implementation

```bash
python3 tools/run.py <CLAIM_ID>     # official pass; writes status back
```

- Exit 0 → `Verified`. Exit 1 → `Failed` (skill `honest-negative`).
- Then run your project's own audits (lint, typecheck, contract checks).
- The claim `README.md` verdict paragraph is what the memory index will
  show forever — write it for the next agent.

## Claim anatomy (what a good claim text contains)

1. **What** changes and where (one sentence)
2. **Measurable thresholds** ("p95 latency <= 250 ms on the fixed bench",
   "test pass rate >= 99%", "memory footprint delta <= +2%")
3. **Anti-patterns** — the shortcuts that would fake the result, named
   explicitly so the gate can defend against them

## Fast iteration

During harness development use dev shortcuts (skill `fast-iteration`), but
the official pass is always the full `tools/run.py <CLAIM_ID>` with no
reuse and no subsetting.
