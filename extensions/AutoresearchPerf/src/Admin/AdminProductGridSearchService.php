<?php declare(strict_types=1);

namespace AutoresearchPerf\Admin;

use Doctrine\DBAL\Connection;
use OpenSearch\Client;
use Shopware\Core\Content\Product\ProductDefinition;
use Shopware\Core\Framework\Context;
use Shopware\Core\Framework\Uuid\Uuid;
use Shopware\Elasticsearch\Framework\ElasticsearchHelper;

/**
 * Query-only admin product grid search — OpenSearch direct with DBAL fallback.
 */
class AdminProductGridSearchService
{
    /** @var list<string> */
    private const SOURCE_INCLUDES = [
        'id',
        'name',
        'productNumber',
        'active',
        'stock',
        'manufacturerId',
        'coverId',
        'autoIncrement',
    ];

    public function __construct(
        private readonly Client $openSearchClient,
        private readonly ElasticsearchHelper $elasticsearchHelper,
        private readonly ProductDefinition $productDefinition,
        private readonly Connection $connection,
    ) {
    }

    /**
     * @return array{data: list<array<string, mixed>>, total: int, meta: array<string, mixed>}
     */
    public function search(string $term, int $limit, Context $context): array
    {
        $limit = max(1, min($limit, 100));

        if ($this->canUseElasticsearch()) {
            try {
                return $this->searchElasticsearch($term, $limit);
            } catch (\Throwable) {
                // Fall through to DBAL query-only path when ES index is unavailable.
            }
        }

        return $this->searchDatabase($term, $limit, $context);
    }

    /**
     * @return array{data: list<array<string, mixed>>, total: int, meta: array<string, mixed>}
     */
    private function searchElasticsearch(string $term, int $limit): array
    {
        $params = [
            'index' => $this->elasticsearchHelper->getIndexName($this->productDefinition),
            'body' => [
                'size' => $limit,
                'track_total_hits' => false,
                '_source' => ['includes' => self::SOURCE_INCLUDES],
                'query' => [
                    'multi_match' => [
                        'query' => $term,
                        'fields' => ['name^3', 'productNumber^2', 'ean', 'manufacturerNumber'],
                        'type' => 'best_fields',
                        'fuzziness' => 'AUTO',
                    ],
                ],
            ],
        ];

        $response = $this->openSearchClient->search($params);
        $hits = $response['hits']['hits'] ?? [];

        $rows = [];
        foreach ($hits as $hit) {
            if (!\is_array($hit)) {
                continue;
            }

            $source = $hit['_source'] ?? [];
            if (!\is_array($source)) {
                continue;
            }

            $id = $hit['_id'] ?? ($source['id'] ?? null);
            if (!\is_string($id) || $id === '') {
                continue;
            }

            $rows[] = [
                'id' => $id,
                'name' => $source['name'] ?? null,
                'productNumber' => $source['productNumber'] ?? null,
                'active' => (bool) ($source['active'] ?? false),
                'stock' => isset($source['stock']) ? (int) $source['stock'] : null,
                'manufacturerId' => $source['manufacturerId'] ?? null,
                'coverId' => $source['coverId'] ?? null,
                'autoIncrement' => isset($source['autoIncrement']) ? (int) $source['autoIncrement'] : null,
            ];
        }

        return [
            'data' => $rows,
            'total' => \count($rows),
            'meta' => [
                'queryOnly' => true,
                'source' => 'autoresearch-admin-grid-es',
            ],
        ];
    }

    /**
     * @return array{data: list<array<string, mixed>>, total: int, meta: array<string, mixed>}
     */
    private function searchDatabase(string $term, int $limit, Context $context): array
    {
        $languageId = Uuid::fromHexToBytes($context->getLanguageId());
        $versionId = Uuid::fromHexToBytes($context->getVersionId());
        $like = '%' . addcslashes($term, '%_\\') . '%';

        $sql = <<<'SQL'
SELECT
    LOWER(HEX(p.id)) AS id,
    pt.name AS name,
    p.product_number AS productNumber,
    p.active AS active,
    p.stock AS stock,
    LOWER(HEX(p.product_manufacturer_id)) AS manufacturerId,
    LOWER(HEX(p.product_media_id)) AS coverId,
    p.auto_increment AS autoIncrement
FROM product p
INNER JOIN product_translation pt
    ON pt.product_id = p.id
    AND pt.product_version_id = p.version_id
    AND pt.language_id = :languageId
WHERE p.version_id = :versionId
  AND p.parent_id IS NULL
  AND (pt.name LIKE :term OR p.product_number LIKE :term)
ORDER BY p.auto_increment DESC
LIMIT :limit
SQL;

        /** @var list<array<string, mixed>> $rows */
        $rows = $this->connection->fetchAllAssociative(
            $sql,
            [
                'languageId' => $languageId,
                'versionId' => $versionId,
                'term' => $like,
                'limit' => $limit,
            ],
            [
                'languageId' => 'binary',
                'versionId' => 'binary',
                'term' => 'string',
                'limit' => 'integer',
            ],
        );

        $data = [];
        foreach ($rows as $row) {
            $data[] = [
                'id' => (string) $row['id'],
                'name' => $row['name'] ?? null,
                'productNumber' => $row['productNumber'] ?? null,
                'active' => (bool) ($row['active'] ?? false),
                'stock' => isset($row['stock']) ? (int) $row['stock'] : null,
                'manufacturerId' => $row['manufacturerId'] ?? null,
                'coverId' => $row['coverId'] ?? null,
                'autoIncrement' => isset($row['autoIncrement']) ? (int) $row['autoIncrement'] : null,
            ];
        }

        return [
            'data' => $data,
            'total' => \count($data),
            'meta' => [
                'queryOnly' => true,
                'source' => 'autoresearch-admin-grid-dbal',
            ],
        ];
    }

    private function canUseElasticsearch(): bool
    {
        if (!$this->elasticsearchHelper->allowIndexing()) {
            return false;
        }

        try {
            $index = $this->elasticsearchHelper->getIndexName($this->productDefinition);

            return (bool) $this->openSearchClient->indices()->exists(['index' => $index]);
        } catch (\Throwable) {
            return false;
        }
    }
}
