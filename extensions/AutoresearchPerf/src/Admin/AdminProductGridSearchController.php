<?php declare(strict_types=1);

namespace AutoresearchPerf\Admin;

use Shopware\Core\Framework\Context;
use Shopware\Core\Framework\Routing\ApiRouteScope;
use Shopware\Core\PlatformRequest;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route(defaults: [PlatformRequest::ATTRIBUTE_ROUTE_SCOPE => [ApiRouteScope::ID]])]
class AdminProductGridSearchController
{
    public function __construct(
        private readonly AdminProductGridSearchService $gridSearchService,
    ) {
    }

    #[Route(
        path: '/api/_action/autoresearch/admin-product-grid-search',
        name: 'api.action.autoresearch.admin-product-grid-search',
        methods: ['POST'],
    )]
    public function search(Request $request, Context $context): Response
    {
        $term = (string) ($request->request->get('term') ?? 'product');
        $limit = $request->request->getInt('limit', 25);

        return new JsonResponse($this->gridSearchService->search($term, $limit, $context));
    }
}
