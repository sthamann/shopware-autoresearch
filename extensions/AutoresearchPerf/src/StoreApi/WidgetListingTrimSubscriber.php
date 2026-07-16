<?php declare(strict_types=1);

namespace AutoresearchPerf\StoreApi;

use Shopware\Core\Content\Product\Events\ProductListingCriteriaEvent;
use Shopware\Core\Content\Product\SalesChannel\Listing\Filter\ManufacturerListingFilterHandler;
use Shopware\Core\Content\Product\SalesChannel\Listing\Filter\PriceListingFilterHandler;
use Shopware\Core\Content\Product\SalesChannel\Listing\Filter\PropertyListingFilterHandler;
use Shopware\Core\Content\Product\SalesChannel\Listing\Filter\RatingListingFilterHandler;
use Shopware\Core\Content\Product\SalesChannel\Listing\Filter\ShippingFreeListingFilterHandler;
use Shopware\Core\Content\Product\ProductDefinition;
use Shopware\Elasticsearch\Framework\DataAbstractionLayer\Event\ElasticsearchEntitySearcherSearchEvent;
use Symfony\Component\EventDispatcher\EventSubscriberInterface;
use Symfony\Component\HttpFoundation\RequestStack;
use Symfony\Component\HttpKernel\Event\RequestEvent;
use Symfony\Component\HttpKernel\KernelEvents;

/**
 * Aggressive ES/listing trim for deferred widget route at 100k scale.
 */
class WidgetListingTrimSubscriber implements EventSubscriberInterface
{
    public function __construct(
        private readonly RequestStack $requestStack,
    ) {
    }

    /** @var list<string> */
    private const FILTER_PARAMS = [
        ManufacturerListingFilterHandler::FILTER_ENABLED_REQUEST_PARAM,
        PropertyListingFilterHandler::FILTER_ENABLED_REQUEST_PARAM,
        RatingListingFilterHandler::FILTER_ENABLED_REQUEST_PARAM,
        ShippingFreeListingFilterHandler::FILTER_ENABLED_REQUEST_PARAM,
        PriceListingFilterHandler::FILTER_ENABLED_REQUEST_PARAM,
    ];

    /** @var list<string> */
    private const WIDGET_SOURCE_INCLUDES = [
        'id',
        'name',
        'productNumber',
        'active',
        'stock',
        'available',
        'coverId',
        'manufacturerId',
        'calculatedPrice',
        'ratingAverage',
    ];

    public static function getSubscribedEvents(): array
    {
        return [
            KernelEvents::REQUEST => ['onWidgetRequest', 99],
            ProductListingCriteriaEvent::class => 'onListingCriteria',
            ElasticsearchEntitySearcherSearchEvent::class => 'onEsSearch',
        ];
    }

    public function onWidgetRequest(RequestEvent $event): void
    {
        if (!$event->isMainRequest()) {
            return;
        }

        $request = $event->getRequest();
        if ($request->attributes->get('_route') !== 'frontend.cms.navigation.page') {
            return;
        }

        if ($request->query->has('order') || $request->query->has('reduce-aggregations')) {
            return;
        }

        $request->query->set('no-aggregations', '1');
        $request->request->set('no-aggregations', '1');

        foreach (self::FILTER_PARAMS as $param) {
            $request->request->set($param, false);
        }

        $request->attributes->set('autoresearch_widget_listing_trim', true);
    }

    public function onListingCriteria(ProductListingCriteriaEvent $event): void
    {
        if (!$event->getRequest()->attributes->getBoolean('autoresearch_widget_listing_trim')) {
            return;
        }

        $criteria = $event->getCriteria();
        $criteria->resetAggregations();
        $criteria->resetAssociations();
        $criteria->setLimit(min($criteria->getLimit() ?? 24, 24));
    }

    public function onEsSearch(ElasticsearchEntitySearcherSearchEvent $event): void
    {
        if (!$this->isWidgetTrimActive()) {
            return;
        }

        if ($event->getDefinition()->getEntityName() !== ProductDefinition::ENTITY_NAME) {
            return;
        }

        $event->getSearch()->setSource(['includes' => self::WIDGET_SOURCE_INCLUDES]);
    }

    private function isWidgetTrimActive(): bool
    {
        $request = $this->requestStack->getCurrentRequest();

        return $request !== null && $request->attributes->getBoolean('autoresearch_widget_listing_trim');
    }
}
