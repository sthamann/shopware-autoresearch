# API-Performance harness (Strang 2)

Fixed Store API and Admin API endpoints on the live Docker stack.

## Endpoints

| Name | Family | Path | Notes |
|---|---|---|---|
| `store_api_product_list` | Store API | `POST /store-api/product` | `limit=25`, sales-channel access key |
| `admin_api_product_search` | Admin API | `POST /api/search/product` | `limit=25`, `term=product`, OAuth bearer |

Primary scalar for starter claim `VERIFY.STOREAPI.PRODUCT_LIST_P95.01`: p95 of
`store_api_product_list`.

Access key and admin token are resolved at runtime via the password grant and
Admin API — not hardcoded in the harness.

## Run

```bash
./verification/bench/api/run_bench.sh
```
