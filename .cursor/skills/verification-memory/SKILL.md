---
name: verification-memory
description: >-
  Queries the generated verification memory (tools/memory.py) — claims
  (ground truth) + plans (proposals), research fronts, per-claim dossiers,
  plan-to-claim links, BM25 search. Use when asking what was already tried,
  what plans exist for a topic, claim neighborhood, or before registering a
  new claim.
---

# Verification Memory

Rules: `verification-memory.mdc`, `verification-lifecycle.mdc`
Sibling skills: `plan-fact-check` (verdicts against code), `honest-negative`
(Failed closure)

One command instead of reading hundreds of claim folders and plan documents.

| Layer | Ground truth? | Source |
|---|---|---|
| **Claims** | Yes | `registry.csv` + claim README + `last_run.json` |
| **Plans** | No (proposals) | `<plans_dir>/*.md` |

Auto-rebuild on staleness (fast, stdlib) — never invalidate manually.

## Commands

```bash
python3 tools/memory.py fronts               # fronts: claims + linked plans
python3 tools/memory.py fronts --track perf  # one front
python3 tools/memory.py tree --claims        # track -> family -> claims
python3 tools/memory.py query "cache eviction latency"   # BM25: [CLAIM]/[PLAN]
python3 tools/memory.py plans "migration"    # BM25 plans only
python3 tools/memory.py show <CLAIM_ID>      # dossier
python3 tools/memory.py related <CLAIM_ID>   # deps, siblings, plans, similar
python3 tools/memory.py recent --days 3      # recently moved
python3 tools/memory.py build                # force rebuild
```

Every query command accepts `--json` (machine-readable, for subagents).

## Standard workflows

| Question | Command |
|---|---|
| "Was X already tried? Is there a plan?" | `query "X"` → `show <claim>` / read plan file |
| "Which plans reference claim Y?" | `show Y` → `referenced by plans:` |
| "Neighborhood of a claim?" | `related <claim>` (deps, supersedes, family, similar) |
| Status of a research front | `fronts --track <id>` |
| Before `register.py` (duplicate check, **mandatory**) | `query "<topic>"` — claims **and** plans |
| Why is a claim Failed / which gates red? | `show <claim>` → `gates: … FAILED: …` |
| Downstream sweep after a Failed | `show <claim>` → `required by:` line |
| Onboarding into an area | `tree --claims --track <id>` + `plans "<topic>"` |
| Context after days away | `recent --days 3` |

## Generated files (never edit, never commit)

| File | Content |
|---|---|
| `<verification_dir>/memory/index.json` | Claims + plans + reverse plan refs |
| `<verification_dir>/memory/MEMORY.md` | Digest: tracks → families → claims |

## Do not

- Cite registry status from `MEMORY.md` without checking `registry.csv`
  on any contradiction
- Treat plans as ground truth or as Verified status
- Commit or hand-edit `<verification_dir>/memory/`
- Register a new claim without a prior `query` on the topic
