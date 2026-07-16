# AutoresearchPerf

Shopware plugin for autoresearch performance optimizations (Waves 1–6).

## Changes

- **ProductListRouteOptimizer** — trims heavy default associations and sets
  lightweight includes for bare `POST /store-api/product` requests.
- **ProductListingCriteriaSubscriber** — drops facet aggregations and default
  listing associations on category navigation requests at 100k+ scale.
- **ProductListingFilterTrimSubscriber** — clears filter handlers on default
  listing requests so AggregationListingProcessor skips facet work.
- **HomeListingRequestSubscriber** — sets `no-aggregations` and disables
  listing filters early on home/CMS navigation/widget routes.
- **AdminProductSearchCriteriaSubscriber** — strips aggregations and heavy
  associations on admin CRUD product search with term at 100k scale.
- **DeferredProductListingCmsElementResolver** — skips synchronous home/CMS
  product-listing load; placeholder + async fetch.
- **SessionCachePolicySubscriber** — fixed context token header + cache policy
  for anonymous cookie-less cacheable GET (Wave 6).
- **WidgetListingTrimSubscriber** — aggressive aggregation/filter trim on
  `/widgets/cms/navigation/` route (Wave 6).
- **AdminProductGridSearchController** — query-only grid endpoint at
  `/api/_action/autoresearch/admin-product-grid-search` (OpenSearch with DBAL
  fallback, Wave 6).
- **AdminProductSearchSourceSubscriber** — OpenSearch `_source.includes` for
  admin grid columns on CRUD product search.
- **AdminProductEntityReaderDecorator** — builds admin grid products from cached
  ES `_source` on CRUD term search, bypassing DAL read.

Mounted via `compose.override.yaml` into `custom/plugins/AutoresearchPerf`.

**Note:** `services.xml` must live at `src/Resources/config/services.xml`
(Shopware bundle path = plugin `src/` directory). API routes in
`src/Resources/config/routes.xml`.
