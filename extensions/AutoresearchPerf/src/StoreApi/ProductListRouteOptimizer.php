<?php declare(strict_types=1);

namespace AutoresearchPerf\StoreApi;

use Shopware\Core\Content\Product\SalesChannel\AbstractProductListRoute;
use Shopware\Core\Content\Product\SalesChannel\ProductListResponse;
use Shopware\Core\Framework\DataAbstractionLayer\Search\Criteria;
use Shopware\Core\System\SalesChannel\SalesChannelContext;

/**
 * Trims default associations and sets lightweight includes for bare product list
 * requests (no explicit associations in POST body).
 */
class ProductListRouteOptimizer extends AbstractProductListRoute
{
    /** @var list<string> */
    private const LIGHT_INCLUDES = [
        'id',
        'name',
        'productNumber',
        'stock',
        'available',
        'coverId',
    ];

    public function __construct(
        private readonly AbstractProductListRoute $decorated,
    ) {
    }

    public function getDecorated(): AbstractProductListRoute
    {
        return $this->decorated;
    }

    public function load(Criteria $criteria, SalesChannelContext $context): ProductListResponse
    {
        if ($this->shouldOptimize($criteria)) {
            $this->applyLightweightDefaults($criteria);
        }

        return $this->decorated->load($criteria, $context);
    }

    private function shouldOptimize(Criteria $criteria): bool
    {
        return $criteria->getAssociations() === [];
    }

    private function applyLightweightDefaults(Criteria $criteria): void
    {
        $criteria->resetAssociations();

        if ($criteria->getIncludes() === []) {
            $criteria->setIncludes(['product' => self::LIGHT_INCLUDES]);
        }
    }
}
