# Katalog-Skalierung harness (Strang 3)

Admin product search at declared corpus size. Target: **≥ 100 000 products**.

## Corpus seeding

`seed_corpus.sh` bulk-imports bench products via the Shopware Sync API:

1. Skip if `product_count` already ≥ `corpus_target` (from `config.json`).
2. Upsert deterministic `SCALE-BENCH-*` products in batches of 1000
   (`indexing-skip: product` during import for speed).
3. Reuse EUR currency, 19% tax, root category, and Storefront sales channel
   from the existing install.
4. Run `dal:refresh:index` and `es:admin:index` inside the Docker stack.
5. Emit final JSON with `product_count`, `corpus_ready`, and `elapsed_s`.

**Expected runtime** (local Docker, M-series Mac class hardware):

| Phase | Approx. time |
|---|---|
| Sync API upsert (100k × batch 1000) | 3–6 min |
| DAL + admin ES index refresh | 2–10 min |
| **Total cold seed** | **~5–15 min** |

Re-runs are idempotent: already at ≥ 100k → instant skip.

```bash
./verification/bench/scale/seed_corpus.sh
```

## Bench flow

| Step | Action |
|---|---|
| 1 | Count products via Admin API (`total-count-mode: 1`) |
| 2 | Benchmark `POST /api/search/product` (`limit=25`, `term=product`) |
| 3 | Emit JSON with `product_count`, `corpus_target`, `corpus_ready` |

Primary scalar for starter claim `VERIFY.SCALE.ADMIN_PRODUCT_SEARCH_P95.01`: p95
admin product search **when** `product_count >= corpus_target`.

## Run

```bash
# 1. Seed corpus (once per environment)
./verification/bench/scale/seed_corpus.sh

# 2. Benchmark admin search at scale
./verification/bench/scale/run_bench.sh

# 3. Official claim gate
python3 pawl/tools/run.py VERIFY.SCALE.ADMIN_PRODUCT_SEARCH_P95.01
```
