# 2026-07-16-09 — VERIFY.REQ.HOME_LISTING_WIDGET_UX.05

## Claim

Deferred home listing async widget loads >= 20 products within 3000 ms client-side at 100k; anti-pattern: static placeholder only

## Acceptance gates

- corpus_at_least_100k
- home_has_deferred_marker
- widget_samples_collected
- widget_p95_within_threshold (<= 3000 ms)
- widget_loads_min_products (>= 20)

## Verdict

**Verified.** Widget fetch to `/widgets/cms/navigation/{navId}` returns **24 product boxes** at p95 **1620 ms** (gate <= 3000 ms). Home shell retains deferred placeholder; async path loads real listing HTML.
