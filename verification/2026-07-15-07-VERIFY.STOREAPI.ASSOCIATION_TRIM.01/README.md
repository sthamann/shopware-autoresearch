# 2026-07-15-07 — VERIFY.STOREAPI.ASSOCIATION_TRIM.01

> **Status: Planned.** Freeze the gates in `run.py` BEFORE implementing.

## Claim

Store API POST /store-api/product p95 <= 85 ms on api bench when default heavy associations are trimmed (baseline ~97 ms); response must still return >= 1 product; anti-pattern: empty payload or strip required fields

## Acceptance gates (freeze a priori)

- [ ] gate 1: <metric> <op> <threshold>
- [ ] gate 2: ...

## Verdict

**Failed (2026-07-15).** Store API p95 **110 ms** (gate 85 ms; baseline ~97 ms).
`ProductListRouteOptimizer` includes trim did not beat baseline. Marginal or negative delta.
