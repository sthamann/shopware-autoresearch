# 2026-07-16-08 — VERIFY.REQ.SESSION_STATELESS_STOREFRONT.05

## Claim

Storefront cacheable GET without Set-Cookie session- achieves X-Symfony-Cache hit; anti-pattern: disable session globally

## Acceptance gates

- samples_collected
- anonymous_no_session_cookie
- category_p95_cached (<= 120 ms)
- http_cache_hit_cookieless

## Verdict

**Failed (honest negative).** `StatelessStorefrontSessionSubscriber` resets session after StorefrontSubscriber and strips cookies, but `session-` cookie still emitted and no `X-Symfony-Cache` hit. Setting `_stateless` throws in dev debug when StorefrontSubscriber uses session. Category p95 **201 ms** uncached.
