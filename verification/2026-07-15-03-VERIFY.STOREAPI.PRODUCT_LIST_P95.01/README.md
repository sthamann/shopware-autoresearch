# 2026-07-15-03 — VERIFY.STOREAPI.PRODUCT_LIST_P95.01

> **Status: Planned.** Freeze the gates in `run.py` BEFORE implementing.

## Claim

Store API POST /store-api/product (limit=25) p95 latency <= 500 ms on verification/bench/api fixed bench; anti-pattern: do not shrink limit or strip associations to pass

## Acceptance gates (frozen)

- [x] `bench_ran` — api harness exits 0
- [x] `samples_collected` — ≥ 10 Store API samples
- [x] `store_api_p95_within_threshold` — p95 ≤ 500 ms on `store_api_product_list`

## Verdict

Baseline (2026-07-15): **Verified** on empty demo catalog. Store API product list
p95 ~97 ms (threshold 500 ms).
