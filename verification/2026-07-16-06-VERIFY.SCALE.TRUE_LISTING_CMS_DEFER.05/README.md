# 2026-07-16-06 — VERIFY.SCALE.TRUE_LISTING_CMS_DEFER.05

## Claim

True listing CMS page p95 <= 500 ms at >= 100k with deferred product-listing on CMS routes; anti-pattern: remove listing element

## Acceptance gates

- corpus_at_least_100k
- samples_collected (>= 10)
- true_listing_cms_deferred_p95 (<= 500 ms)
- improved_vs_wave4 (< 1681 ms)

## Verdict

**Verified.** Extended deferred product-listing to `frontend.cms.page.full` routes. True listing CMS p95 **200 ms** (Wave 4: 1681 ms). Aggregation trim + defer pattern matches home shell performance.
