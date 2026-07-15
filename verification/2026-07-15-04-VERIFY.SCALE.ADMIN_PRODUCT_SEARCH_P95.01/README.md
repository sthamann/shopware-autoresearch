# 2026-07-15-04 — VERIFY.SCALE.ADMIN_PRODUCT_SEARCH_P95.01

> **Status: Planned.** Freeze the gates in `run.py` BEFORE implementing.

## Claim

Admin API product search p95 <= 3000 ms on verification/bench/scale at >= 100000 products; gate fails honestly when product_count < 100000 until seed_corpus.sh runs; anti-pattern: do not extrapolate from demo catalog or skip corpus gate

## Acceptance gates (frozen)

- [x] `bench_ran` — scale harness exits 0
- [x] `corpus_at_least_100k` — product_count ≥ 100000
- [x] `samples_collected` — ≥ 10 admin search samples
- [x] `admin_search_p95_within_threshold` — p95 ≤ 3000 ms (only meaningful when corpus ready)

## Verdict

Baseline (2026-07-15): **Failed** — honest negative. Admin search p95 ~75 ms would
pass the latency gate, but `product_count=0` (required ≥ 100000). Missing
capability: `verification/bench/scale/seed_corpus.sh` not yet implemented.
