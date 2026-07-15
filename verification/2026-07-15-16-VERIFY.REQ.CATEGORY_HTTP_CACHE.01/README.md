# 2026-07-15-16 — VERIFY.REQ.CATEGORY_HTTP_CACHE.01

## Claim

Category storefront p95 <= 120 ms after HTTP cache warmup with persistent session cookie and X-Symfony-Cache hit.

## Verdict

**Failed.** p95 **203 ms** (healthy latency) but no cache hit — rotating `session-=` cookie prevents Symfony HTTP cache store/hit. Missing capability: sessionless anonymous cache path.
