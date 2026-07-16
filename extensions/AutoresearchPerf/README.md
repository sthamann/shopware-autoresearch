# AutoresearchPerf

Shopware plugin for autoresearch performance optimizations (Waves 1–5).

## Changes

- **ProductListRouteOptimizer** — trims heavy default associations and sets
  lightweight includes for bare `POST /store-api/product` requests.
- **ProductListingCriteriaSubscriber** — drops facet aggregations and default
  listing associations on category navigation requests at 100k+ scale.
- **ProductListingFilterTrimSubscriber** — clears filter handlers on default
  listing requests so AggregationListingProcessor skips facet work.
- **HomeListingRequestSubscriber** — sets `no-aggregations` and disables
  listing filters early on home/CMS navigation routes (root listing layout).
- **AdminProductSearchCriteriaSubscriber** — strips aggregations and heavy
  associations on admin CRUD product search with term at 100k scale.
- **DeferredProductListingCmsElementResolver** — skips synchronous home/CMS
  product-listing load; placeholder + async fetch.
- **StatelessStorefrontSessionSubscriber** — `_stateless` + session reset for
  anonymous cookie-less cacheable GET.
- **AdminProductSearchSourceSubscriber** — OpenSearch `_source.includes` for
  admin grid columns on CRUD product search.
- **AdminProductEntityReaderDecorator** — builds admin grid products from cached
  ES `_source` on CRUD term search, bypassing DAL read.

Mounted via `compose.override.yaml` into `custom/plugins/AutoresearchPerf`.

**Note:** `services.xml` must live at `src/Resources/config/services.xml`
(Shopware bundle path = plugin `src/` directory).
