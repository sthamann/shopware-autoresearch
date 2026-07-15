<?php declare(strict_types=1);

namespace AutoresearchPerf\StoreApi;

use Shopware\Core\Content\Product\SalesChannel\Listing\AbstractProductListingRoute;
use Shopware\Core\Content\Product\SalesChannel\Listing\Filter\ManufacturerListingFilterHandler;
use Shopware\Core\Content\Product\SalesChannel\Listing\Filter\PriceListingFilterHandler;
use Shopware\Core\Content\Product\SalesChannel\Listing\Filter\PropertyListingFilterHandler;
use Shopware\Core\Content\Product\SalesChannel\Listing\Filter\RatingListingFilterHandler;
use Shopware\Core\Content\Product\SalesChannel\Listing\Filter\ShippingFreeListingFilterHandler;
use Shopware\Core\Content\Product\SalesChannel\Listing\ProductListingRouteResponse;
use Shopware\Core\Framework\DataAbstractionLayer\Search\Criteria;
use Shopware\Core\System\SalesChannel\SalesChannelContext;
use Symfony\Component\HttpFoundation\Request;

/**
 * Sets no-aggregations + disabled filters before CompositeListingProcessor runs
 * (BehaviorListingProcessor must run after AggregationListingProcessor).
 */
class ProductListingRouteOptimizer extends AbstractProductListingRoute
{
    /** @var list<string> */
    private const FILTER_PARAMS = [
        ManufacturerListingFilterHandler::FILTER_ENABLED_REQUEST_PARAM,
        PropertyListingFilterHandler::FILTER_ENABLED_REQUEST_PARAM,
        RatingListingFilterHandler::FILTER_ENABLED_REQUEST_PARAM,
        ShippingFreeListingFilterHandler::FILTER_ENABLED_REQUEST_PARAM,
        PriceListingFilterHandler::FILTER_ENABLED_REQUEST_PARAM,
    ];

    public function __construct(
        private readonly AbstractProductListingRoute $decorated,
    ) {
    }

    public function getDecorated(): AbstractProductListingRoute
    {
        return $this->decorated;
    }

    public function load(string $categoryId, Request $request, SalesChannelContext $context, Criteria $criteria): ProductListingRouteResponse
    {
        if ($this->shouldTrim($request)) {
            $request->query->set('no-aggregations', '1');
            $request->request->set('no-aggregations', '1');

            foreach (self::FILTER_PARAMS as $param) {
                $request->request->set($param, false);
            }
        }

        return $this->decorated->load($categoryId, $request, $context, $criteria);
    }

    private function shouldTrim(Request $request): bool
    {
        if ($request->query->has('order') || $request->query->has('reduce-aggregations')) {
            return false;
        }

        if ($request->query->has('properties') || $request->query->has('manufacturer')) {
            return false;
        }

        return true;
    }
}
