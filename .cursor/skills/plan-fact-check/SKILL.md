---
name: plan-fact-check
description: >-
  Fact-checks plans and architecture claims against registry.csv, claim
  last_run.json evidence, and real code. Use when analyzing plans, verifying
  strategy documents, judging if a claim exists, checking Planned vs Verified
  status, or answering "does the code actually match this plan?"
---

# Plan Fact-Check

Rules: `verification-lifecycle.mdc`, `metric-integrity.mdc`

Plans are proposals. The registry is ground truth. A plan's self-assessment
is never evidence.

## Workflow

1. **Memory** — `python3 tools/memory.py query "<plan topic>"` and
   `show <CLAIM>` for every claim the plan cites
2. **Registry** — status in `registry.csv` is ground truth, not plan text
3. **Evidence** — read `<claim-folder>/last_run.json` + claim `README.md`
4. **Code** — read the actual symbols with `file:line` citations
5. **Verdict** per item

## Verdict labels

| Verdict | Meaning |
|---|---|
| **CONFIRMED** | Code + evidence match the plan claim |
| **PARTIALLY-TRUE** | Core claim holds but plan omits caveats or is outdated |
| **CONTRADICTED** | Registry or code disproves the plan (e.g. already Verified, behavior changed) |
| **UNVERIFIABLE** | Claim not testable from repo artifacts |

## Report template (one section per item)

```markdown
## N. <artifact or claim>

**EXISTS?** Yes/No — `path/to/file.py`

**Registry:** `<CLAIM_ID>` = Verified | Failed | Planned

**Verdict:** CONFIRMED | PARTIALLY-TRUE | CONTRADICTED | UNVERIFIABLE

**Evidence:** `last_run.json` metric or `file:line` citation

**Note:** (exact gap if PARTIALLY or CONTRADICTED)
```

## Common traps

| Trap | Fix |
|---|---|
| Plan says `Planned`, registry says `Verified` | Trust registry + `last_run.json` |
| Plan cites behavior from old code | Read the current symbol, check CHANGELOG |
| Mechanism verified but capability failed | Separate verdicts: mechanics vs headline metric |
| Plan reopens a terminal negative | Cross-check the Failed claim's "do not retry without" note |

## Do not

- Accept plan self-assessment without registry + code check
- Report dev-shortcut numbers as official results (`metric-integrity.mdc`)
- Propose fixes during a read-only fact-check unless asked
