# 2026-07-16-12 — VERIFY.REQ.HOME_LISTING_WIDGET_TIGHT.06

## Claim

Deferred home listing widget p95 <= 1000 ms at >= 100k with ES trim on widget route; anti-pattern: reduce product limit below 20

## Acceptance gates

- corpus_at_least_100k
- home_has_deferred_marker
- widget_samples_collected
- widget_p95_within_threshold (<= 1000 ms)
- widget_loads_min_products (>= 20)
- improved_vs_wave5 (< 1620 ms)

## Verdict

**Failed (honest negative).** `WidgetListingTrimSubscriber` trims aggregations/filters on `frontend.cms.navigation.page`, but widget p95 **1598 ms** vs gate **1000 ms** (Wave 5: 1620 ms, −22 ms marginal). Full CMS page render dominates; sub-1000 ms needs listing-only partial route.
