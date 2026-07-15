#!/usr/bin/env bash
# Profile home vs category vs root listing API — stdout: JSON breakdown.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

exec python3 - "$ROOT" <<'PY'
import json
import sys
import time
import urllib.request
from pathlib import Path


def timed(url: str, headers: dict | None = None) -> float:
    req = urllib.request.Request(url, method="GET", headers=headers or {"Accept": "text/html"})
    start = time.perf_counter()
    with urllib.request.urlopen(req, timeout=60) as resp:
        resp.read()
    return round((time.perf_counter() - start) * 1000.0, 2)


def post_json(url: str, body: dict, headers: dict) -> tuple[dict, float]:
    payload = json.dumps(body).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={**headers, "Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    start = time.perf_counter()
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read()
    elapsed = round((time.perf_counter() - start) * 1000.0, 2)
    return json.loads(raw.decode()), elapsed


def main() -> int:
    root = Path(sys.argv[1])
    cfg = json.loads((root / "verification/bench/request/config.json").read_text(encoding="utf-8"))
    base = cfg["base_url"].rstrip("/")
    category = next(r for r in cfg["requests"] if r["name"] == "category")

    home_ms = timed(base + "/")
    category_ms = timed(base + category["path"])
    esi_header_ms = timed(base + "/_esi/global/header")
    esi_footer_ms = timed(base + "/_esi/global/footer")

    listing_ms = None
    listing_error = None
    try:
        token_data, _ = post_json(
            base + "/api/oauth/token",
            {"grant_type": "password", "client_id": "administration", "username": "admin", "password": "shopware"},
            {},
        )
        token = token_data["access_token"]
        sc_data, _ = post_json(base + "/api/search/sales-channel", {"limit": 1}, {"Authorization": f"Bearer {token}"})
        sc = sc_data["data"][0]
        ctx_req = urllib.request.Request(
            base + "/store-api/context",
            headers={"Accept": "application/json", "sw-access-key": sc["accessKey"]},
        )
        with urllib.request.urlopen(ctx_req, timeout=30) as resp:
            ctx_token = resp.headers.get("sw-context-token")
        _, listing_ms = post_json(
            f"{base}/store-api/product-listing/{sc['navigationCategoryId']}",
            {"no-aggregations": True},
            {"sw-access-key": sc["accessKey"], "sw-context-token": ctx_token},
        )
    except Exception as exc:  # noqa: BLE001
        listing_error = str(exc)

    result = {
        "home_ms": home_ms,
        "category_ms": category_ms,
        "esi_header_ms": esi_header_ms,
        "esi_footer_ms": esi_footer_ms,
        "root_listing_api_ms": listing_ms,
        "listing_error": listing_error,
        "home_cms_note": "Default listing layout — product-listing at root nav (100k)",
        "category_cms_note": "Contact form layout — no product listing element",
        "home_to_category_ratio": round(home_ms / category_ms, 2) if category_ms else 0,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY
