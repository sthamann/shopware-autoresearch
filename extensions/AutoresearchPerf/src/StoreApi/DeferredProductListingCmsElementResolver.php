<?php declare(strict_types=1);

namespace AutoresearchPerf\StoreApi;

use Shopware\Core\Content\Cms\Aggregate\CmsSlot\CmsSlotEntity;
use Shopware\Core\Content\Cms\DataResolver\CriteriaCollection;
use Shopware\Core\Content\Cms\DataResolver\Element\CmsElementResolverInterface;
use Shopware\Core\Content\Cms\DataResolver\Element\ElementDataCollection;
use Shopware\Core\Content\Cms\DataResolver\ResolverContext\ResolverContext;
use Shopware\Core\Content\Cms\SalesChannel\Struct\ProductListingStruct;

/**
 * Skips synchronous listing load on home when defer flag is set (ESI/async path).
 */
class DeferredProductListingCmsElementResolver implements CmsElementResolverInterface
{
    public const DEFER_ATTRIBUTE = 'autoresearch_defer_home_listing';

    public function __construct(
        private readonly CmsElementResolverInterface $decorated,
    ) {
    }

    public function getType(): string
    {
        return $this->decorated->getType();
    }

    public function collect(CmsSlotEntity $slot, ResolverContext $resolverContext): ?CriteriaCollection
    {
        if ($this->shouldDefer($resolverContext)) {
            return null;
        }

        return $this->decorated->collect($slot, $resolverContext);
    }

    public function enrich(CmsSlotEntity $slot, ResolverContext $resolverContext, ElementDataCollection $result): void
    {
        if ($this->shouldDefer($resolverContext)) {
            $data = new ProductListingStruct();
            $data->addArrayExtension(self::DEFER_ATTRIBUTE, ['deferred' => true]);
            $slot->setData($data);

            return;
        }

        $this->decorated->enrich($slot, $resolverContext, $result);
    }

    /** @var list<string> */
    private const DEFERABLE_ROUTES = [
        'frontend.home.page',
        'frontend.cms.page.full',
    ];

    private function shouldDefer(ResolverContext $resolverContext): bool
    {
        $request = $resolverContext->getRequest();

        if ($request->attributes->getBoolean('_esi')) {
            return false;
        }

        if ($request->attributes->getBoolean(self::DEFER_ATTRIBUTE)) {
            return true;
        }

        $route = $request->attributes->get('_route');

        return \is_string($route) && \in_array($route, self::DEFERABLE_ROUTES, true);
    }
}
