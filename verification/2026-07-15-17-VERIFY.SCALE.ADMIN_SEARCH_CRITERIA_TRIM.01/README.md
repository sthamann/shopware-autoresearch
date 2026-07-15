# 2026-07-15-17 — VERIFY.SCALE.ADMIN_SEARCH_CRITERIA_TRIM.01

## Claim

Admin product search p95 <= 260 ms at >= 100k after stripping aggregations and heavy associations on CRUD search.

## Verdict

**Failed.** p95 **316 ms** vs 260 ms gate (Wave 2: 307 ms). `AdminProductSearchCriteriaSubscriber` active; marginal +9 ms vs baseline. Missing capability: OpenSearch `_source` projection or slimmer admin index mapping.
