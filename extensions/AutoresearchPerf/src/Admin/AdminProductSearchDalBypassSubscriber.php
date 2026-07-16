<?php declare(strict_types=1);

namespace AutoresearchPerf\Admin;

use Shopware\Core\Content\Product\ProductDefinition;
use Shopware\Core\Framework\Context;
use Shopware\Core\Framework\DataAbstractionLayer\Event\EntityIdSearchResultLoadedEvent;
use Shopware\Core\Framework\DataAbstractionLayer\Event\EntitySearchedEvent;
use Shopware\Elasticsearch\Framework\DataAbstractionLayer\ElasticsearchEntitySearcher;
use Symfony\Component\EventDispatcher\EventSubscriberInterface;

/**
 * Enables ES-only admin product search by caching ES hits and skipping DAL read.
 */
class AdminProductSearchDalBypassSubscriber implements EventSubscriberInterface
{
    public const BYPASS_STATE = 'autoresearch_admin_es_only_search';

    public function __construct(
        private readonly AdminProductEsSourceRegistry $registry,
    ) {
    }

    public static function getSubscribedEvents(): array
    {
        return [
            EntitySearchedEvent::class => 'onEntitySearch',
            EntityIdSearchResultLoadedEvent::class => 'onIdSearchResult',
        ];
    }

    public function onEntitySearch(EntitySearchedEvent $event): void
    {
        if ($event->getDefinition()->getEntityName() !== ProductDefinition::ENTITY_NAME) {
            return;
        }

        if ($event->getContext()->getScope() !== Context::CRUD_API_SCOPE) {
            return;
        }

        $criteria = $event->getCriteria();
        if ($criteria->getTerm() === null || $criteria->getTerm() === '') {
            return;
        }

        $this->registry->clear();
    }

    public function onIdSearchResult(EntityIdSearchResultLoadedEvent $event): void
    {
        if ($event->getDefinition()->getEntityName() !== ProductDefinition::ENTITY_NAME) {
            return;
        }

        $context = $event->getContext();
        if ($context->getScope() !== Context::CRUD_API_SCOPE) {
            return;
        }

        $criteria = $event->getResult()->getCriteria();
        if ($criteria->getTerm() === null || $criteria->getTerm() === '') {
            return;
        }

        if (!$event->getResult()->hasState(ElasticsearchEntitySearcher::RESULT_STATE)) {
            return;
        }

        $data = $event->getResult()->getData();
        if ($data === []) {
            return;
        }

        $this->registry->store($data);
        $context->addState(self::BYPASS_STATE);
    }
}
