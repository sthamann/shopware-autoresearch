<?php declare(strict_types=1);

namespace AutoresearchPerf\StoreApi;

use Shopware\Core\Checkout\Customer\CustomerEntity;
use Shopware\Core\Framework\Adapter\Cache\Event\HttpCacheCookieEvent;
use Shopware\Core\PlatformRequest;
use Shopware\Core\System\SalesChannel\SalesChannelContext;
use Symfony\Component\EventDispatcher\EventSubscriberInterface;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Session\Session;
use Symfony\Component\HttpFoundation\Session\Storage\MockArraySessionStorage;
use Symfony\Component\HttpKernel\Event\RequestEvent;
use Symfony\Component\HttpKernel\Event\ResponseEvent;
use Symfony\Component\HttpKernel\KernelEvents;

/**
 * Anonymous cacheable storefront GET: fixed context token header + cache policy, no session cookie.
 */
class SessionCachePolicySubscriber implements EventSubscriberInterface
{
    public const ANONYMOUS_CONTEXT_TOKEN = 'autoresearch-anonymous-cache-token';
    public const POLICY_ATTRIBUTE = 'autoresearch_cache_policy';

    /** @var list<string> */
    private const CACHEABLE_ROUTES = [
        'frontend.home.page',
        'frontend.cms.page',
        'frontend.cms.page.full',
        'frontend.navigation.page',
    ];

    public static function getSubscribedEvents(): array
    {
        return [
            KernelEvents::REQUEST => [
                ['applyCachePolicy', 35],
                ['prepareHeaderContextToken', 38],
            ],
            KernelEvents::RESPONSE => ['finalizeCachePolicyResponse', \PHP_INT_MAX - 10],
            HttpCacheCookieEvent::class => 'onCacheCookie',
        ];
    }

    public function applyCachePolicy(RequestEvent $event): void
    {
        if (!$event->isMainRequest()) {
            return;
        }

        $request = $event->getRequest();
        if (!$this->isAnonymousCacheableGet($request)) {
            return;
        }

        $request->attributes->set(self::POLICY_ATTRIBUTE, true);
    }

    public function prepareHeaderContextToken(RequestEvent $event): void
    {
        if (!$event->isMainRequest()) {
            return;
        }

        $request = $event->getRequest();
        if (!$request->attributes->getBoolean(self::POLICY_ATTRIBUTE)) {
            return;
        }

        $token = $request->headers->get(PlatformRequest::HEADER_CONTEXT_TOKEN);
        if (!\is_string($token) || $token === '') {
            $request->headers->set(PlatformRequest::HEADER_CONTEXT_TOKEN, self::ANONYMOUS_CONTEXT_TOKEN);
        }

        if ($request->hasSession()) {
            $session = $request->getSession();
            if ($session->isStarted()) {
                $session->save();
            }
        }

        $request->setSession(new Session(new MockArraySessionStorage()));
        $request->attributes->set('_stateless', true);
    }

    public function finalizeCachePolicyResponse(ResponseEvent $event): void
    {
        if (!$event->isMainRequest()) {
            return;
        }

        $request = $event->getRequest();
        if (!$request->attributes->getBoolean(self::POLICY_ATTRIBUTE)) {
            return;
        }

        $response = $event->getResponse();
        foreach ($response->headers->getCookies() as $cookie) {
            if (str_starts_with($cookie->getName(), 'session')) {
                $response->headers->removeCookie(
                    $cookie->getName(),
                    $cookie->getPath(),
                    $cookie->getDomain(),
                );
            }
        }

        $response->headers->set('X-Autoresearch-Cache-Policy', 'anonymous-header-token');
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

        $context = $request->attributes->get(PlatformRequest::ATTRIBUTE_SALES_CHANNEL_CONTEXT_OBJECT);
        if ($context instanceof SalesChannelContext && $context->getCustomer() instanceof CustomerEntity) {
            return false;
        }

        if (!$request->attributes->get(PlatformRequest::ATTRIBUTE_HTTP_CACHE)) {
            return false;
        }

        return true;
    }
}
