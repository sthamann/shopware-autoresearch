<?php declare(strict_types=1);

namespace AutoresearchPerf\Admin;

use Shopware\Core\Content\Product\ProductDefinition;
use Shopware\Core\Framework\Context;
use Shopware\Core\Framework\DataAbstractionLayer\Event\EntitySearchedEvent;
use Shopware\Core\Framework\DataAbstractionLayer\Search\Criteria;
use Symfony\Component\EventDispatcher\EventSubscriberInterface;

/**
 * Trims admin CRUD product search criteria at scale (aggregations + heavy associations).
 */
class AdminProductSearchCriteriaSubscriber implements EventSubscriberInterface
{
    /** @var list<string> */
    private const ADMIN_LIST_INCLUDES = [
        'id',
        'name',
        'productNumber',
        'active',
        'stock',
        'price',
        'manufacturerId',
        'coverId',
    ];

    public static function getSubscribedEvents(): array
    {
        return [
            EntitySearchedEvent::class => 'onEntitySearch',
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

        $criteria->resetAggregations();
        $criteria->resetAssociations();
        $criteria->setTotalCountMode(Criteria::TOTAL_COUNT_MODE_NEXT_PAGES);

        if ($criteria->getIncludes() === []) {
            $criteria->setIncludes([ProductDefinition::ENTITY_NAME => self::ADMIN_LIST_INCLUDES]);
        }
    }
}
