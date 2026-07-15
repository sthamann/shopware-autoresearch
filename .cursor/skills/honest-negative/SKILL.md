---
name: honest-negative
description: >-
  Documents honest-negative verification outcomes when a claim fails — names
  the exact missing capability, updates the registry to Failed, sweeps
  dependent Planned claims, no shadow fixes. Use when tools/run.py exits 1,
  a claim fails its gates, or an experiment is terminal-negative although the
  mechanism is sound.
---

# Honest Negative (Claim Failed)

Rules: `honest-negatives.mdc`, `metric-integrity.mdc`

## When to use Failed (not abandon, not hide)

- The gate ran cleanly; it failed on **capability**, not a wiring bug
- Mechanism built and provably inert when disabled; enabled shows no lift
  or honest harm
- The missing capability is identifiable and nameable

## Report structure (into the claim README)

```markdown
## Outcome: Honest negative (Failed)

**Claim:** <CLAIM_ID>

**What was proved (mechanics):**
- (structural gates that passed; disabled-baseline was red as required)

**What failed (capability):**
- (exact metric vs frozen threshold, e.g. "p95 310 ms > 250 ms gate")

**Missing capability (name it):**
- One sentence: what the system lacks — not "needs more tuning"

**Do NOT retry without:**
- A new capability, or a new claim with a different scope
```

## Required actions

1. `<claim-folder>/last_run.json` reflects the failure honestly
2. Registry → status **Failed** (not Planned, not Verified)
3. Claim `README.md` — verdict + missing capability (first paragraph;
   the memory index surfaces it)
4. Module `CHANGELOG.md` if code landed (kept OFF or reverted — say which)
5. No default-ON flip of the feature
6. **Downstream sweep:** every **Planned** claim listing this claim in
   `dependencies` gets decided NOW — re-hang onto the named missing
   capability, re-scope, or close (`active=false` + `notes` beginning
   `Closed <date>: <reason / superseded by CLAIM>`; folder stays as
   archive). A replacing claim sets `supersedes=<old claim>`. Check with
   `python3 tools/scan.py --stale-planned` (`--strict` → exit 1 when
   anything is blocked or stale).

## Forbidden "fixes"

- Gaming the measurement (see `metric-integrity.mdc` forbidden wins)
- Reporting a Failed run as success because "the mechanism works"
- Deleting the claim to make the dashboard look better
- Retrying the identical approach in a new claim without a new capability
  (terminal-negative discipline)

## Mechanism vs capability

| | Mechanism verified | Capability failed |
|---|---|---|
| Example | Feature wired, structural gates green | Quality metric under threshold |
| Registry | Failed is OK — record both facts | Never mark Verified |
| Next step | New capability claim | Not: loosen the gate |
