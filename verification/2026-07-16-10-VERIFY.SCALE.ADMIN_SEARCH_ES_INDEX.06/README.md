# 2026-07-16-10 — VERIFY.SCALE.ADMIN_SEARCH_ES_INDEX.06

## Claim

Admin product search p95 <= 260 ms at >= 100k via dedicated admin ES index mapping or query-only grid endpoint; anti-pattern: shrink limit

## Acceptance gates

- corpus_at_least_100k
- grid_endpoint_responds
- grid_query_only_path
- admin_grid_search_p95 (<= 260 ms)
- improved_vs_wave5 (< 316 ms)

## Verdict

**Verified.** Query-only grid endpoint `/api/_action/autoresearch/admin-product-grid-search` returns 25 rows at p95 **71 ms** (DBAL fallback; ES index not populated in dev stack). Wave 5 baseline **316 ms** on standard `/api/search/product`.
