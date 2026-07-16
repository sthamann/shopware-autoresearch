<?php declare(strict_types=1);

namespace AutoresearchPerf\StoreApi;

use Shopware\Core\Checkout\Customer\CustomerEntity;
use Shopware\Core\Framework\Adapter\Cache\Event\HttpCacheCookieEvent;
use Shopware\Core\PlatformRequest;
use Symfony\Component\EventDispatcher\EventSubscriberInterface;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Session\Storage\MockArraySessionStorage;
use Symfony\Component\HttpKernel\Event\RequestEvent;
use Symfony\Component\HttpKernel\Event\ResponseEvent;
use Symfony\Component\HttpKernel\KernelEvents;

/**
 * Anonymous cookie-less GET on cacheable storefront routes: skip persistent session cookie.
 */
class AnonymousSessionBypassSubscriber implements EventSubscriberInterface
{
    /** @var list<string> */
    private const CACHEABLE_ROUTES = [
        'frontend.home.page',
        'frontend.cms.page',
        'frontend.navigation.page',
    ];

    public static function getSubscribedEvents(): array
    {
        return [
            KernelEvents::REQUEST => ['onRequest', 35],
            KernelEvents::RESPONSE => ['onResponse', 1600],
            HttpCacheCookieEvent::class => 'onCacheCookie',
        ];
    }

    public function onRequest(RequestEvent $event): void
    {
        if (!$event->isMainRequest()) {
            return;
        }

        $request = $event->getRequest();
        if (!$this->isAnonymousCacheableGet($request)) {
            return;
        }

        if (!$request->hasSession()) {
            return;
        }

        $session = $request->getSession();
        if ($session->isStarted()) {
            $session->save();
        }

        $request->setSession(new \Symfony\Component\HttpFoundation\Session\Session(new MockArraySessionStorage()));
        $request->attributes->set('autoresearch_anonymous_cache', true);
    }

    public function onResponse(ResponseEvent $event): void
    {
        if (!$event->isMainRequest()) {
            return;
        }

        $request = $event->getRequest();
        if (!$request->attributes->getBoolean('autoresearch_anonymous_cache')) {
            return;
        }

        $response = $event->getResponse();
        $response->headers->removeCookie('session-');
        foreach ($response->headers->getCookies() as $cookie) {
            if (str_starts_with($cookie->getName(), 'session')) {
                $response->headers->removeCookie($cookie->getName(), $cookie->getPath(), $cookie->getDomain());
            }
        }
    }

    public function onCacheCookie(HttpCacheCookieEvent $event): void
    {
        if (!$this->isAnonymousCacheableGet($event->request)) {
            return;
        }

        if ($event->context->getCustomer() instanceof CustomerEntity) {
            return;
        }

        $event->isCacheable = true;
        $event->doNotStore = false;
    }

    private function isAnonymousCacheableGet(Request $request): bool
    {
        if ($request->getMethod() !== Request::METHOD_GET) {
            return false;
        }

        if ($request->cookies->count() > 0) {
            return false;
        }

        if ($request->attributes->getBoolean('_esi')) {
            return false;
        }

        $route = $request->attributes->get('_route');
        if (!\is_string($route) || !\in_array($route, self::CACHEABLE_ROUTES, true)) {
            return false;
        }

        if (!$request->attributes->get(PlatformRequest::ATTRIBUTE_HTTP_CACHE)) {
            return false;
        }

        return true;
    }
}
