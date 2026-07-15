# Shopware Autoresearch — Results Log

> Auto-updated by optimization waves. Registry ground truth: `verification/registry.csv`

## Wave 1 — 2026-07-15

### Summary table

| Claim | Strand | Status | Before p95 | After p95 | Notes |
|---|---|---|---:|---:|---|
| VERIFY.REQ.HTTP_CACHE_STOREFRONT.01 | Request | **Failed** | ~195 ms (home) | 3123 ms | Home dev overhead dominates; no cache hit |
| VERIFY.CACHE.OPCACHE_WARMUP.01 | Request | **Failed** | ~195 ms (home) | 3082 ms | `cache:warmup` does not fix home slowness |
| VERIFY.STOREAPI.ASSOCIATION_TRIM.01 | API | **Failed** | ~97 ms | 110 ms | Includes trim marginal; threshold 85 ms not met |
| VERIFY.STOREAPI.PAGINATION_LIMIT.01 | API | **Failed** | ~97 ms | 104 ms | Within noise of baseline |
| VERIFY.SCALE.ADMIN_SEARCH_ES_TUNING.01 | Scale | **Failed** | ~301 ms | 308 ms | Opensearch heap bump alone insufficient |
| VERIFY.SCALE.STOREFRONT_LISTING_P95.01 | Scale | **Verified** | — | **184 ms** | Aggregation trim on category listing @ 100k |

**Wave 1 score:** 1 Verified, 5 Failed (honest negatives)

### Strang 1 — Request-Performance

**Hypothesis:** HTTP cache warmup + TTL tuning and Symfony `cache:warmup` lower storefront home p95.

**Implementation:**
- `compose.override.yaml`: `SHOPWARE_HTTP_CACHE_ENABLED=1`, `SHOPWARE_HTTP_DEFAULT_TTL=7200`
- `scripts/warmup-http-cache.sh`, `scripts/warmup-app-cache.sh`

**Result:** Home page remains ~3 s p95 while category (~187 ms) and search (~251 ms) stay healthy. Symfony HTTP cache never reports a hit on `/` — likely blocked by session/cookie variance and dev-mode storefront overhead (Vite). Opcode/app warmup does not address this bottleneck.

**Missing capability:** Dev-stack home route has ~3 s fixed overhead unrelated to HTTP/object cache; needs isolated investigation (see follow-up `VERIFY.REQ.HOME_DEV_OVERHEAD.01`).

### Strang 2 — API-Performance

**Hypothesis:** Trim default associations and set lightweight includes on bare `POST /store-api/product` requests.

**Implementation:** `extensions/AutoresearchPerf` plugin — `ProductListRouteOptimizer` decorator.

**Result:** p95 moved from baseline ~97 ms to ~104–110 ms (no improvement; slightly worse within variance). Lightweight includes alone do not beat the baseline gate thresholds (85–90 ms).

**Missing capability:** DAL still hydrates calculated prices and core fields; needs explicit field projection or Elasticsearch-backed list route (see `VERIFY.STOREAPI.FIELD_PROJECTION.02`).

### Strang 3 — Katalog-Skalierung

**Hypothesis A:** Opensearch JVM heap + product index refresh lowers admin search p95 at 100k.

**Implementation:** `compose.override.yaml` opensearch `768m` heap; `scripts/es-tune.sh` (fixed: `dal:refresh:index --only product`).

**Result:** Admin search p95 308 ms vs 250 ms gate (baseline ~301 ms). No measurable win.

**Hypothesis B:** Drop facet aggregations on default category listing at 100k.

**Implementation:** `ProductListingCriteriaSubscriber` in AutoresearchPerf.

**Result:** **Verified** — category listing p95 **184 ms** at 100k products (gate ≤ 2500 ms). Major ES cost removed from default navigation listing.

---

## Follow-up queue (auto-generated)

| Claim ID | Depends on | Hypothesis |
|---|---|---|
| VERIFY.REQ.HOME_DEV_OVERHEAD.01 | HTTP_CACHE fail | Isolate ~3 s home dev overhead (Vite/session) vs ~180 ms category |
| VERIFY.STOREAPI.FIELD_PROJECTION.02 | ASSOCIATION_TRIM fail | Explicit field projection to reach ≤ 80 ms Store API p95 |
| VERIFY.SCALE.ADMIN_SEARCH_INDEX_WARM.02 | ES_TUNING fail | Full index refresh + warm queries for admin search ≤ 260 ms |
| VERIFY.SCALE.STOREFRONT_LISTING_TIGHT.02 | LISTING verified | Tighten category listing gate to ≤ 150 ms with aggregation trim |

## Honest negatives

| Claim | Root cause |
|---|---|
| VERIFY.REQ.HTTP_CACHE_STOREFRONT.01 | Home route not cacheable in dev; 3 s p95 unrelated to HTTP cache |
| VERIFY.CACHE.OPCACHE_WARMUP.01 | Same home bottleneck; Symfony warmup irrelevant |
| VERIFY.STOREAPI.ASSOCIATION_TRIM.01 | Includes trim insufficient for 12%+ latency reduction |
| VERIFY.STOREAPI.PAGINATION_LIMIT.01 | No measurable pagination/includes win at limit=25 |
| VERIFY.SCALE.ADMIN_SEARCH_ES_TUNING.01 | JVM heap-only tuning: 308 ms vs 250 ms target |

## Next wave recommendations

**Wave 2 priority order:**

1. `VERIFY.SCALE.STOREFRONT_LISTING_TIGHT.02` — build on verified aggregation trim (quick win potential)
2. `VERIFY.SCALE.ADMIN_SEARCH_INDEX_WARM.02` — fix index refresh command + query warm
3. `VERIFY.REQ.HOME_DEV_OVERHEAD.01` — unblock Strang 1 (profile home vs category)
4. `VERIFY.STOREAPI.FIELD_PROJECTION.02` — deeper API payload optimization

## Wave 2 — 2026-07-15

### Summary table

| Claim | Strand | Status | Target p95 | Measured p95 | Notes |
|---|---|---|---:|---:|---|
| VERIFY.SCALE.STOREFRONT_LISTING_TIGHT.02 | Scale | **Failed** | ≤ 150 ms | 177 ms | Close — aggregation trim holds; tighter gate not met |
| VERIFY.SCALE.ADMIN_SEARCH_INDEX_WARM.02 | Scale | **Failed** | ≤ 260 ms | 307 ms | Index refresh + 10× query warm: no gain |
| VERIFY.REQ.HOME_DEV_OVERHEAD.01 | Request | **Failed** | home ≤ 500 ms | 3087 ms | Home 17.6× slower than category (175 ms) |
| VERIFY.STOREAPI.FIELD_PROJECTION.02 | API | **Failed** | ≤ 80 ms | 109 ms | Dropping calculatedPrice from includes: marginal |

**Wave 2 score:** 0 Verified, 4 Failed

### Key findings

- **Listing headroom:** Category listing at 100k is **177 ms** p95 — already strong from Wave 1 aggregation trim; 150 ms needs different approach (HTTP cache on category, ES query shape).
- **Admin search floor:** ~307 ms appears stable across heap tuning, index refresh, and query warming at 100k.
- **Home dev bottleneck confirmed:** Home **3087 ms** vs category **175 ms** (17.6× ratio) — Strang 1 blocked until dev pipeline overhead on `/` is addressed.
- **Store API floor:** ~109 ms with minimal includes — calculated price hydration likely dominates; sub-80 ms needs architectural change.

### Wave 3 recommendations

1. Profile home route (Vite HMR, session bootstrap, ESI blocks) — target sub-500 ms home
2. Accept category listing ~177 ms as near-optimal; focus scale wins on admin search
3. Admin search: try Admin API search criteria tuning (source filtering, no aggregations)
4. Store API: Elasticsearch-backed list route or cached price snapshots

---

## Artifacts

| Path | Purpose |
|---|---|
| `extensions/AutoresearchPerf/` | Store API + listing optimizations plugin |
| `compose.override.yaml` | HTTP cache TTL, plugin mount, Opensearch heap |
| `scripts/warmup-*.sh`, `scripts/es-tune.sh` | Warmup helpers for gates |
