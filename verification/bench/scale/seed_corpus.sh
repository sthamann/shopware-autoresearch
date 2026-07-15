#!/usr/bin/env bash
# Stub: 100k product corpus seeding for the scale harness.
#
# Planned approach (not implemented):
#   1. Use Shopware Sync API bulk import with batched product payloads
#      (e.g. 500 products per request) generated from a deterministic fixture.
#   2. Assign products to the Storefront sales channel + root category.
#   3. Run `bin/console dal:refresh:index` and wait for OpenSearch green.
#   4. Verify count via Admin API before marking corpus_ready.
#
# Until this script is implemented, scale gates that require >= 100k products
# will honestly fail with corpus_ready=false.
set -euo pipefail

echo "seed_corpus.sh: not implemented — scale bench runs on current corpus size." >&2
echo "See verification/bench/scale/README.md for the planned seeding approach." >&2
exit 1
