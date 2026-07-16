<?php declare(strict_types=1);

namespace AutoresearchPerf\StoreApi;

use Symfony\Component\EventDispatcher\EventSubscriberInterface;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpKernel\Event\ResponseEvent;
use Symfony\Component\HttpKernel\KernelEvents;

/**
 * Injects async listing placeholder + fetch script on deferred home responses.
 */
class HomeListingDeferResponseSubscriber implements EventSubscriberInterface
{
    public static function getSubscribedEvents(): array
    {
        return [
            KernelEvents::RESPONSE => ['onResponse', -100],
        ];
    }

    public function onResponse(ResponseEvent $event): void
    {
        if (!$event->isMainRequest()) {
            return;
        }

        $request = $event->getRequest();
        if (!$request->attributes->getBoolean(DeferredProductListingCmsElementResolver::DEFER_ATTRIBUTE)) {
            return;
        }

        if ($request->getMethod() !== Request::METHOD_GET) {
            return;
        }

        $response = $event->getResponse();
        $content = $response->getContent();
        if (!\is_string($content) || $content === '') {
            return;
        }

        $placeholder = <<<'HTML'
<div class="cms-element-product-listing" data-autoresearch-deferred-listing="1">
    <div class="text-center py-5">
        <div class="spinner-border text-primary" role="status" aria-label="Loading products"></div>
        <p class="mt-3 text-muted">Loading products…</p>
    </div>
</div>
HTML;

        $pattern = '/<div class="cms-element-product-listing-wrapper"[\s\S]*?<\/div>\s*<\/div>\s*<\/div>/';
        $updated = preg_replace($pattern, $placeholder, $content, 1);
        if (!\is_string($updated) || $updated === $content) {
            return;
        }

        $script = <<<'HTML'
<script>
(function () {
  var host = document.querySelector('[data-autoresearch-deferred-listing="1"]');
  if (!host) { return; }
  var navId = window.activeNavigationId || '';
  if (!navId) { return; }
  fetch('/widgets/cms/navigation/' + navId, {
    credentials: 'same-origin',
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
    .then(function (response) { return response.text(); })
    .then(function (html) {
      var doc = new DOMParser().parseFromString(html, 'text/html');
      var listing = doc.querySelector('.cms-element-product-listing');
      if (!listing) { return; }
      host.replaceWith(listing);
    })
    .catch(function () {});
})();
</script>
HTML;

        if (str_contains($updated, '</body>')) {
            $updated = str_replace('</body>', $script . '</body>', $updated);
        }

        $response->setContent($updated);
    }
}
