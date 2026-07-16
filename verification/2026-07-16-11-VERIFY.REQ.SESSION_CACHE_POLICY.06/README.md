# 2026-07-16-11 — VERIFY.REQ.SESSION_CACHE_POLICY.06

## Claim

Storefront cacheable GET achieves X-Symfony-Cache hit without session- cookie via cache policy + context token header; anti-pattern: disable session globally

## Acceptance gates

- samples_collected
- anonymous_no_session_cookie
- category_p95_cached (<= 120 ms)
- http_cache_hit_with_context_token
- cache_policy_marker_present

## Verdict

**Failed (honest negative).** `SessionCachePolicySubscriber` sets fixed `sw-context-token` header and strips session cookies on response, but `session-` cookie still emitted at request time and no `X-Symfony-Cache` hit. Category p95 **186 ms** uncached. Route attribute unavailable at early kernel.request priority — policy marker never applied.
