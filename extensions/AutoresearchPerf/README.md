# AutoresearchPerf

Shopware plugin for autoresearch wave-1 performance optimizations.

## Changes

- **ProductListRouteOptimizer** — trims heavy default associations and sets
  lightweight includes for bare `POST /store-api/product` requests (association
  trim + pagination payload optimization).
- **ProductListingCriteriaSubscriber** — drops facet aggregations on default
  category listing requests to reduce OpenSearch load at 100k+ products.

Mounted via `compose.override.yaml` into `custom/plugins/AutoresearchPerf`.
