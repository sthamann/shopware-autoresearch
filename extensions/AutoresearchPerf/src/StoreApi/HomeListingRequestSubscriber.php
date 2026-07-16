<?php declare(strict_types=1);

namespace AutoresearchPerf\StoreApi;

use Shopware\Core\Content\Product\SalesChannel\Listing\Filter\ManufacturerListingFilterHandler;
use Shopware\Core\Content\Product\SalesChannel\Listing\Filter\PriceListingFilterHandler;
use Shopware\Core\Content\Product\SalesChannel\Listing\Filter\PropertyListingFilterHandler;
use Shopware\Core\Content\Product\SalesChannel\Listing\Filter\RatingListingFilterHandler;
use Shopware\Core\Content\Product\SalesChannel\Listing\Filter\ShippingFreeListingFilterHandler;
use Symfony\Component\EventDispatcher\EventSubscriberInterface;
use Symfony\Component\HttpKernel\Event\RequestEvent;
use Symfony\Component\HttpKernel\KernelEvents;

/**
 * Sets listing trim request params before CompositeListingProcessor runs.
 */
class HomeListingRequestSubscriber implements EventSubscriberInterface
{
    /** @var list<string> */
    private const FILTER_PARAMS = [
        ManufacturerListingFilterHandler::FILTER_ENABLED_REQUEST_PARAM,
        PropertyListingFilterHandler::FILTER_ENABLED_REQUEST_PARAM,
        RatingListingFilterHandler::FILTER_ENABLED_REQUEST_PARAM,
        ShippingFreeListingFilterHandler::FILTER_ENABLED_REQUEST_PARAM,
        PriceListingFilterHandler::FILTER_ENABLED_REQUEST_PARAM,
    ];

    public static function getSubscribedEvents(): array
    {
        return [
            KernelEvents::REQUEST => ['onRequest', 100],
        ];
    }

    public function onRequest(RequestEvent $event): void
    {
        if (!$event->isMainRequest()) {
            return;
        }

        $request = $event->getRequest();
        $route = $request->attributes->get('_route');
        if (!\is_string($route)) {
            return;
        }

        if (!\in_array($route, ['frontend.home.page', 'frontend.cms.page.full', 'frontend.navigation.page'], true)) {
            return;
        }

        if (
            \in_array($route, ['frontend.home.page', 'frontend.cms.page.full'], true)
            && !$request->attributes->getBoolean('_esi')
        ) {
            $request->attributes->set(DeferredProductListingCmsElementResolver::DEFER_ATTRIBUTE, true);
        }

        if ($request->query->has('order') || $request->query->has('reduce-aggregations')) {
            return;
        }

        $request->query->set('no-aggregations', '1');
        $request->request->set('no-aggregations', '1');

        foreach (self::FILTER_PARAMS as $param) {
            $request->request->set($param, false);
        }
    }
}
