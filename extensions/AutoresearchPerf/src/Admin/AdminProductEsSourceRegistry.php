<?php declare(strict_types=1);

namespace AutoresearchPerf\Admin;

use Symfony\Component\HttpFoundation\RequestStack;

/**
 * Request-scoped cache of Elasticsearch hit data for admin product search bypass.
 */
class AdminProductEsSourceRegistry
{
    private const ATTRIBUTE = 'autoresearch_admin_es_sources';

    public function __construct(
        private readonly RequestStack $requestStack,
    ) {
    }

    /**
     * @param array<string, array{primaryKey: string|array<string, string>, data: array<string, mixed>}> $sources
     */
    public function store(array $sources): void
    {
        $request = $this->requestStack->getCurrentRequest();
        if ($request === null) {
            return;
        }

        $request->attributes->set(self::ATTRIBUTE, $sources);
    }

    /**
     * @return array<string, array{primaryKey: string, data: array<string, mixed>}>|null
     */
    public function getSources(): ?array
    {
        $request = $this->requestStack->getCurrentRequest();
        if ($request === null) {
            return null;
        }

        $sources = $request->attributes->get(self::ATTRIBUTE);
        if (!\is_array($sources)) {
            return null;
        }

        return $sources;
    }

    public function clear(): void
    {
        $request = $this->requestStack->getCurrentRequest();
        if ($request === null) {
            return;
        }

        $request->attributes->remove(self::ATTRIBUTE);
    }
}
