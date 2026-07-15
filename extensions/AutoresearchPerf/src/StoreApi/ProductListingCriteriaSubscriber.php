<?php declare(strict_types=1);

namespace AutoresearchPerf\StoreApi;

use Shopware\Core\Content\Product\Events\ProductListingCriteriaEvent;
use Symfony\Component\EventDispatcher\EventSubscriberInterface;

/**
 * Storefront listing at scale: skip aggregations on category pages unless requested.
 */
class ProductListingCriteriaSubscriber implements EventSubscriberInterface
{
    public static function getSubscribedEvents(): array
    {
        return [
            ProductListingCriteriaEvent::class => 'onListingCriteria',
        ];
    }

    public function onListingCriteria(ProductListingCriteriaEvent $event): void
    {
        $criteria = $event->getCriteria();
        $request = $event->getRequest();

        if ($request->query->has('order') || $request->query->has('reduce-aggregations')) {
            return;
        }

        if ($criteria->getAggregations() === []) {
            return;
        }

        // Drop facet aggregations on default navigation listing — major ES cost at 100k+.
        $criteria->resetAggregations();
        $criteria->resetAssociations();
    }
}
