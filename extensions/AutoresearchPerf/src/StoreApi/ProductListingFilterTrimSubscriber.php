<?php declare(strict_types=1);

namespace AutoresearchPerf\StoreApi;

use Shopware\Core\Content\Product\Events\ProductListingCollectFilterEvent;
use Symfony\Component\EventDispatcher\EventSubscriberInterface;

/**
 * Drops facet filter handlers on default navigation listing requests.
 */
class ProductListingFilterTrimSubscriber implements EventSubscriberInterface
{
    public static function getSubscribedEvents(): array
    {
        return [
            ProductListingCollectFilterEvent::class => 'onCollectFilters',
        ];
    }

    public function onCollectFilters(ProductListingCollectFilterEvent $event): void
    {
        $request = $event->getRequest();

        if ($request->query->has('order') || $request->query->has('reduce-aggregations')) {
            return;
        }

        if ($request->query->has('properties') || $request->query->has('manufacturer')) {
            return;
        }

        $event->getFilters()->clear();
    }
}
