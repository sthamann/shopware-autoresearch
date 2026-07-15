# Katalog-Skalierung harness (Strang 3)

Admin product search at declared corpus size. Target: **≥ 100 000 products**.

Until `seed_corpus.sh` has populated the catalog, the bench runs honestly on the
current corpus and reports `product_count` plus `corpus_ready: false`. Scale
claims that require 100k **must fail** until the corpus gate passes.

## Bench flow

| Step | Action |
|---|---|
| 1 | Count products via Admin API (`total-count-mode: 1`) |
| 2 | Benchmark `POST /api/search/product` (`limit=25`, `term=product`) |
| 3 | Emit JSON with `product_count`, `corpus_target`, `corpus_ready` |

Primary scalar for starter claim `VERIFY.SCALE.ADMIN_PRODUCT_SEARCH_P95.01`: p95
admin product search **when** `product_count >= corpus_target`.

## Corpus seeding (stub)

See `seed_corpus.sh` for the planned approach. Not implemented in this bootstrap.

## Run

```bash
./verification/bench/scale/run_bench.sh
```
