---
name: project-startup
description: >-
  Reading map for substantive work — which big-picture and status docs to
  load before coding, verifying, or analyzing plans. Use when starting
  substantive edits, exploring architecture, onboarding to the repo, or
  before touching core modules.
---

# Project Startup — Reading Map

Entry: `AGENTS.md` (repo root) · Rule: `project-startup.mdc`

**Do not** paste full documents into chat — read the linked files.

## Always (any substantive task)

1. The project's big-picture doc — **§0 one-sentence law + §1 core model**
   (shape: `templates/big-picture.template.md`)
2. Local `README.md` (+ `contract.json`) of the module you touch
3. Code-index tooling before broad grep for structural questions

## By task type (adapt this table to your project)

| Task | Read next | Skill |
|---|---|---|
| Default code edit | Architecture/wiring doc if wiring changes | — |
| New claim / promote | `<verification_dir>/README`, `registry.csv` | `claim-lifecycle` |
| Verify a plan / strategy doc | registry + claim evidence | `plan-fact-check` |
| Failed claim closure | claim `README.md`, `last_run.json` | `honest-negative` |
| "What was tried?" | memory index | `verification-memory` |
| Parallel agent sessions | — | `parallel-workers` |
| Cheap dev loops | — | `fast-iteration` |

## Living status (read selectively)

- Claim tally + fronts: `python3 tools/memory.py fronts`
- Machine truth: `registry.csv`
- Recently moved: `python3 tools/memory.py recent --days 3`

Plans under `<plans_dir>/` are **proposals** — fact-check against registry
and code before believing them (`plan-fact-check`).

## Before merge

Run the project's audit commands (declare them in `AGENTS.md`), plus:

```bash
python3 tools/scan.py --audit
```

## Gate declaration

Before writing feature code, state the claim path:

```text
claim registered -> gates frozen -> implement -> tools/run.py -> Verified | Failed
```

If you cannot name the claim id and its measurable gates — stop and
register one first.
