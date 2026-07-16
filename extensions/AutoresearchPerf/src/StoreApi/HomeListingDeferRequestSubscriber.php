<?php declare(strict_types=1);

namespace AutoresearchPerf\StoreApi;

use Symfony\Component\EventDispatcher\EventSubscriberInterface;
use Symfony\Component\HttpKernel\Event\ControllerEvent;
use Symfony\Component\HttpKernel\Event\RequestEvent;
use Symfony\Component\HttpKernel\KernelEvents;

/**
 * Marks home page main requests for deferred product-listing load.
 */
class HomeListingDeferRequestSubscriber implements EventSubscriberInterface
{
    public static function getSubscribedEvents(): array
    {
        return [
            KernelEvents::REQUEST => ['onRequest', 5],
            KernelEvents::CONTROLLER => ['onController', 100],
        ];
    }

    public function onRequest(RequestEvent $event): void
    {
        $this->markDefer($event->getRequest(), $event->isMainRequest());
    }

    public function onController(ControllerEvent $event): void
    {
        $this->markDefer($event->getRequest(), $event->isMainRequest());
    }

    private function markDefer(\Symfony\Component\HttpFoundation\Request $request, bool $main): void
    {
        if (!$main) {
            return;
        }

        $route = $request->attributes->get('_route');
        if (!\in_array($route, ['frontend.home.page', 'frontend.cms.page.full'], true)) {
            return;
        }

        if ($request->attributes->getBoolean('_esi')) {
            return;
        }

        $request->attributes->set(DeferredProductListingCmsElementResolver::DEFER_ATTRIBUTE, true);
    }
}
