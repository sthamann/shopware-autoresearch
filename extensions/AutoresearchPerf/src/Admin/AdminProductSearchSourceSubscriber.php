<?php declare(strict_types=1);

namespace AutoresearchPerf\Admin;

use Shopware\Core\Content\Product\ProductDefinition;
use Shopware\Core\Framework\Context;use Shopware\Elasticsearch\Framework\DataAbstractionLayer\Event\ElasticsearchEntitySearcherSearchEvent;
use Symfony\Component\EventDispatcher\EventSubscriberInterface;

/**
 * Limits OpenSearch _source to admin grid columns on CRUD product search at scale.
 */
class AdminProductSearchSourceSubscriber implements EventSubscriberInterface
{
    /** @var list<string> */
    private const SOURCE_INCLUDES = [
        'id',
        'name',
        'productNumber',
        'active',
        'stock',
        'price',
        'manufacturerId',
        'coverId',
        'autoIncrement',
    ];

    public static function getSubscribedEvents(): array
    {
        return [
            ElasticsearchEntitySearcherSearchEvent::class => 'onSearch',
        ];
    }

    public function onSearch(ElasticsearchEntitySearcherSearchEvent $event): void
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

        $event->getSearch()->setSource(['includes' => self::SOURCE_INCLUDES]);
    }
}
