# 2026-07-15-02 — VERIFY.REQ.STOREFRONT_HOME_P95.01

> **Status: Planned.** Freeze the gates in `run.py` BEFORE implementing.

## Claim

Storefront home page p95 total response time <= 1500 ms on verification/bench/request fixed set (demo catalog); anti-pattern: do not cache only / or disable middleware for the bench

## Acceptance gates (frozen)

- [x] `bench_ran` — request harness exits 0
- [x] `samples_collected` — ≥ 10 home samples
- [x] `home_p95_within_threshold` — p95 ≤ 1500 ms on `home`

## Verdict

Baseline (2026-07-15): **Verified** on demo catalog. Home p95 ~195 ms (threshold
1500 ms) on the fixed request set.
