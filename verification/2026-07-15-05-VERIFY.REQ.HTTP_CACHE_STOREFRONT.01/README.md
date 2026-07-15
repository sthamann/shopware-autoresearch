# 2026-07-15-05 — VERIFY.REQ.HTTP_CACHE_STOREFRONT.01

> **Status: Planned.** Freeze the gates in `run.py` BEFORE implementing.

## Claim

Storefront home p95 on request bench <= 170 ms after HTTP cache warmup (baseline ~195 ms); X-Symfony-Cache must show hit on warmed home requests; anti-pattern: disable cache or bench only cold misses

## Acceptance gates (freeze a priori)

- [ ] gate 1: <metric> <op> <threshold>
- [ ] gate 2: ...

## Verdict

**Failed (2026-07-15).** After HTTP cache warmup and TTL=7200, home p95 measured **3123 ms**
(vs 170 ms gate; baseline ~195 ms). `X-Symfony-Cache` never showed a hit on `/`. Category
and search endpoints remained ~180–250 ms. **Missing capability:** dev-mode home route has
~3 s overhead unrelated to HTTP cache — session/cookie or Vite dev pipeline.
