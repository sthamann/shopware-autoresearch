<?php declare(strict_types=1);

namespace AutoresearchPerf\Admin;

use Shopware\Core\Content\Product\ProductCollection;
use Shopware\Core\Content\Product\ProductDefinition;
use Shopware\Core\Content\Product\ProductEntity;
use Shopware\Core\Framework\Context;
use Shopware\Core\Framework\DataAbstractionLayer\EntityCollection;
use Shopware\Core\Framework\DataAbstractionLayer\EntityDefinition;
use Shopware\Core\Framework\DataAbstractionLayer\Pricing\Price;
use Shopware\Core\Framework\DataAbstractionLayer\Pricing\PriceCollection;
use Shopware\Core\Framework\DataAbstractionLayer\Read\EntityReaderInterface;
use Shopware\Core\Framework\DataAbstractionLayer\Search\Criteria;

/**
 * Builds admin grid products from cached Elasticsearch _source instead of DAL read.
 */
class AdminProductEntityReaderDecorator implements EntityReaderInterface
{
    public function __construct(
        private readonly EntityReaderInterface $decorated,
        private readonly AdminProductEsSourceRegistry $registry,
    ) {
    }

    public function read(EntityDefinition $definition, Criteria $criteria, Context $context): EntityCollection
    {
        if (!$this->canBypass($definition, $criteria, $context)) {
            return $this->decorated->read($definition, $criteria, $context);
        }

        $sources = $this->registry->getSources();
        if ($sources === null) {
            return $this->decorated->read($definition, $criteria, $context);
        }

        /** @var ProductCollection $collection */
        $collection = new ProductCollection();

        foreach ($criteria->getIds() as $id) {
            if (\is_array($id)) {
                continue;
            }

            $hit = $sources[$id]['data'] ?? null;
            if (!\is_array($hit)) {
                continue;
            }

            $collection->add($this->buildProduct($id, $hit));
        }

        return $collection;
    }

    private function canBypass(EntityDefinition $definition, Criteria $criteria, Context $context): bool
    {
        if ($definition->getEntityName() !== ProductDefinition::ENTITY_NAME) {
            return false;
        }

        if (!$context->hasState(AdminProductSearchDalBypassSubscriber::BYPASS_STATE)) {
            return false;
        }

        if ($criteria->getIds() === []) {
            return false;
        }

        return $this->registry->getSources() !== null;
    }

    /**
     * @param array<string, mixed> $source
     */
    private function buildProduct(string $id, array $source): ProductEntity
    {
        $product = new ProductEntity();
        $product->setUniqueIdentifier($id);
        $product->setId($id);

        if (isset($source['name']) && \is_string($source['name'])) {
            $product->setName($source['name']);
        }

        if (isset($source['productNumber']) && \is_string($source['productNumber'])) {
            $product->setProductNumber($source['productNumber']);
        }

        if (\array_key_exists('active', $source)) {
            $product->setActive((bool) $source['active']);
        }

        if (isset($source['stock'])) {
            $product->setStock((int) $source['stock']);
        }

        if (isset($source['manufacturerId']) && \is_string($source['manufacturerId'])) {
            $product->setManufacturerId($source['manufacturerId']);
        }

        if (isset($source['coverId']) && \is_string($source['coverId'])) {
            $product->setCoverId($source['coverId']);
        }

        if (isset($source['autoIncrement'])) {
            $product->setAutoIncrement((int) $source['autoIncrement']);
        }

        $price = $this->buildPriceCollection($source['price'] ?? null);
        if ($price !== null) {
            $product->setPrice($price);
        }

        return $product;
    }

    /**
     * @param mixed $raw
     */
    private function buildPriceCollection($raw): ?PriceCollection
    {
        if (!\is_array($raw) || $raw === []) {
            return null;
        }

        $prices = [];
        foreach ($raw as $entry) {
            if (!\is_array($entry)) {
                continue;
            }

            $gross = isset($entry['gross']) ? (float) $entry['gross'] : 0.0;
            $net = isset($entry['net']) ? (float) $entry['net'] : $gross;
            $currencyId = isset($entry['currencyId']) && \is_string($entry['currencyId'])
                ? $entry['currencyId']
                : 'b7d2554b0ce847cd82f3ac9bd1c0dfca';

            $prices[] = new Price($currencyId, $net, $gross, isset($entry['linked']) ? (bool) $entry['linked'] : true);
        }

        return $prices === [] ? null : new PriceCollection($prices);
    }
}
