# Request-Performance harness (Strang 1)

Fixed storefront HTTP request set on Shopware demo data until the scale corpus
is seeded.

## Request set

| Name | Path | Method |
|---|---|---|
| `home` | `/` | GET |
| `category` | `/page/cms/019f64c64f7971f09730538de8dd1f67` | GET |
| `product_search` | `/search?search=main` | GET |

Primary scalar for starter claim `VERIFY.REQ.STOREFRONT_HOME_P95.01`: p95 of
`home`.

## Run

```bash
./verification/bench/request/run_bench.sh
```

Output: JSON with per-request latencies and aggregate `p50_ms` / `p95_ms`.
