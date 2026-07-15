#!/usr/bin/env bash
# Seed the scale harness catalog (>= corpus_target products) via Sync API.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "${HERE}/../../.." && pwd)"
CONFIG="${HERE}/config.json"
DEV_EXEC="${ROOT}/scripts/dev-exec.sh"

exec python3 - "$CONFIG" "$DEV_EXEC" <<'PY'
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

CONFIG_PATH = Path(sys.argv[1])
DEV_EXEC = sys.argv[2]

BATCH_SIZE = 1000
PRODUCT_PREFIX = "SCALE-BENCH-"
MANUFACTURER_ID = uuid.uuid5(uuid.NAMESPACE_DNS, "scale-bench-manufacturer").hex
NAMESPACE_PRODUCT = uuid.NAMESPACE_DNS


def post_json(
    url: str, body: dict | list, headers: dict[str, str], timeout: float = 120
) -> tuple[int, dict | list]:
    payload = json.dumps(body).encode("utf-8")
    req_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        **headers,
    }
    request = urllib.request.Request(
        url, data=payload, headers=req_headers, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} for {url}: {detail[:500]}") from exc


def fetch_token(base_url: str, admin_cfg: dict) -> str:
    url = base_url.rstrip("/") + "/api/oauth/token"
    body = {
        "grant_type": "password",
        "client_id": admin_cfg["client_id"],
        "username": admin_cfg["username"],
        "password": admin_cfg["password"],
    }
    _, data = post_json(url, body, {})
    token = data.get("access_token")
    if not token:
        raise RuntimeError("admin oauth token missing")
    return token


def search_one(base_url: str, token: str, entity: str, body: dict) -> dict | None:
    url = base_url.rstrip("/") + f"/api/search/{entity}"
    _, data = post_json(url, body, {"Authorization": f"Bearer {token}"})
    items = data.get("data") or []
    return items[0] if items else None


def product_count(base_url: str, token: str) -> int:
    url = base_url.rstrip("/") + "/api/search/product"
    body = {"limit": 1, "total-count-mode": 1}
    _, data = post_json(url, body, {"Authorization": f"Bearer {token}"})
    meta = data.get("meta") or {}
    total = meta.get("total", data.get("total", 0))
    return int(total or 0)


def bench_product_count(base_url: str, token: str) -> int:
    url = base_url.rstrip("/") + "/api/search/product"
    body = {
        "limit": 1,
        "total-count-mode": 1,
        "filter": [
            {
                "type": "prefix",
                "field": "productNumber",
                "value": PRODUCT_PREFIX,
            }
        ],
    }
    _, data = post_json(url, body, {"Authorization": f"Bearer {token}"})
    meta = data.get("meta") or {}
    total = meta.get("total", data.get("total", 0))
    return int(total or 0)


def resolve_fixtures(base_url: str, token: str) -> dict[str, str]:
    auth = {"Authorization": f"Bearer {token}"}

    currency = search_one(
        base_url,
        token,
        "currency",
        {"filter": [{"type": "equals", "field": "isoCode", "value": "EUR"}], "limit": 1},
    )
    tax = search_one(
        base_url,
        token,
        "tax",
        {"filter": [{"type": "equals", "field": "taxRate", "value": 19}], "limit": 1},
    )
    category = search_one(
        base_url,
        token,
        "category",
        {"filter": [{"type": "equals", "field": "level", "value": 1}], "limit": 1},
    )
    channel = search_one(
        base_url,
        token,
        "sales-channel",
        {"filter": [{"type": "equals", "field": "name", "value": "Storefront"}], "limit": 1},
    )

    missing = [
        name
        for name, row in (
            ("currency(EUR)", currency),
            ("tax(19%)", tax),
            ("category(level=1)", category),
            ("sales-channel(Storefront)", channel),
        )
        if row is None
    ]
    if missing:
        raise RuntimeError(f"fixture lookup failed: {', '.join(missing)}")

    return {
        "currency_id": currency["id"],
        "tax_id": tax["id"],
        "category_id": category["id"],
        "sales_channel_id": channel["id"],
    }


def ensure_manufacturer(base_url: str, token: str) -> None:
    payload = [
        {
            "action": "upsert",
            "entity": "product_manufacturer",
            "payload": [
                {
                    "id": MANUFACTURER_ID,
                    "name": "Scale Bench Manufacturer",
                }
            ],
        }
    ]
    post_json(
        base_url.rstrip("/") + "/api/_action/sync",
        payload,
        {"Authorization": f"Bearer {token}"},
    )


def build_product(index: int, fixtures: dict[str, str]) -> dict:
    product_id = uuid.uuid5(NAMESPACE_PRODUCT, f"scale-bench-product-{index}").hex
    return {
        "id": product_id,
        "productNumber": f"{PRODUCT_PREFIX}{index:08d}",
        "name": f"Scale Bench Product {index}",
        "stock": 100,
        "active": True,
        "taxId": fixtures["tax_id"],
        "manufacturerId": MANUFACTURER_ID,
        "categories": [{"id": fixtures["category_id"]}],
        "price": [
            {
                "currencyId": fixtures["currency_id"],
                "gross": 19.99,
                "net": 16.80,
                "linked": False,
            }
        ],
        "visibilities": [
            {
                "salesChannelId": fixtures["sales_channel_id"],
                "visibility": 30,
            }
        ],
    }


def sync_batch(
    base_url: str, token: str, products: list[dict], skip_indexing: bool
) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    if skip_indexing:
        headers["indexing-skip"] = "product"
    payload = [{"action": "upsert", "entity": "product", "payload": products}]
    post_json(
        base_url.rstrip("/") + "/api/_action/sync",
        payload,
        headers,
        timeout=600,
    )


def refresh_indexes(dev_exec: str) -> None:
    for cmd in (
        ["bin/console", "dal:refresh:index", "--no-progress"],
        ["bin/console", "es:admin:index", "--no-progress"],
    ):
        proc = subprocess.run(
            [dev_exec, *cmd],
            check=False,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            detail = proc.stderr or proc.stdout
            raise RuntimeError(f"{' '.join(cmd)} failed: {detail[:500]}")


def log_progress(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def main() -> int:
    started = time.perf_counter()
    cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    base_url = cfg["base_url"]
    corpus_target = int(cfg.get("corpus_target", 100000))

    token = fetch_token(base_url, cfg["admin"])
    existing_total = product_count(base_url, token)
    existing_bench = bench_product_count(base_url, token)

    if existing_total >= corpus_target:
        result = {
            "action": "skipped",
            "corpus_target": corpus_target,
            "product_count": existing_total,
            "bench_product_count": existing_bench,
            "corpus_ready": True,
            "batches": 0,
            "seeded": 0,
            "elapsed_s": round(time.perf_counter() - started, 2),
        }
        print(json.dumps(result, indent=2))
        return 0

    fixtures = resolve_fixtures(base_url, token)
    ensure_manufacturer(base_url, token)

    start_index = existing_bench
    batches = 0
    seeded = 0
    token_refreshed_at = time.perf_counter()

    log_progress(
        f"Seeding scale corpus: {start_index} -> {corpus_target - 1} "
        f"(batch_size={BATCH_SIZE}, existing_total={existing_total})"
    )

    index = start_index
    while index < corpus_target:
        if time.perf_counter() - token_refreshed_at > 240:
            token = fetch_token(base_url, cfg["admin"])
            token_refreshed_at = time.perf_counter()
        batch_end = min(index + BATCH_SIZE, corpus_target)
        products = [build_product(i, fixtures) for i in range(index, batch_end)]
        sync_batch(base_url, token, products, skip_indexing=True)
        batch_count = batch_end - index
        batches += 1
        seeded += batch_count
        index = batch_end
        log_progress(
            f"  batch {batches}: upserted {batch_count} products "
            f"({index}/{corpus_target})"
        )

    log_progress("Refreshing DAL + admin search indexes...")
    refresh_indexes(DEV_EXEC)

    token = fetch_token(base_url, cfg["admin"])
    final_total = product_count(base_url, token)
    final_bench = bench_product_count(base_url, token)
    corpus_ready = final_total >= corpus_target

    result = {
        "action": "seeded",
        "corpus_target": corpus_target,
        "product_count": final_total,
        "bench_product_count": final_bench,
        "corpus_ready": corpus_ready,
        "batches": batches,
        "seeded": seeded,
        "batch_size": BATCH_SIZE,
        "elapsed_s": round(time.perf_counter() - started, 2),
    }
    print(json.dumps(result, indent=2))
    return 0 if corpus_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
PY
