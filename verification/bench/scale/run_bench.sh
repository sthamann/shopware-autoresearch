#!/usr/bin/env bash
# Fixed catalog-scale harness — stdout: one JSON object.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CONFIG="${HERE}/config.json"

exec python3 - "$CONFIG" <<'PY'
import json
import sys
import time
import urllib.request
from pathlib import Path


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = int(round((pct / 100.0) * (len(ordered) - 1)))
    return ordered[idx]


def post_json(url: str, body: dict, headers: dict[str, str]) -> tuple[int, bytes, float]:
    payload = json.dumps(body).encode("utf-8")
    req_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        **headers,
    }
    request = urllib.request.Request(url, data=payload, headers=req_headers, method="POST")
    start = time.perf_counter()
    with urllib.request.urlopen(request, timeout=60) as resp:
        raw = resp.read()
        status = resp.status
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return status, raw, elapsed_ms


def fetch_admin_token(base_url: str, admin_cfg: dict) -> str:
    url = base_url.rstrip("/") + "/api/oauth/token"
    body = {
        "grant_type": "password",
        "client_id": admin_cfg["client_id"],
        "username": admin_cfg["username"],
        "password": admin_cfg["password"],
    }
    payload = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    token = data.get("access_token")
    if not token:
        raise RuntimeError("admin oauth token missing")
    return token


def fetch_product_count(base_url: str, token: str) -> int:
    url = base_url.rstrip("/") + "/api/search/product"
    body = {"limit": 1, "total-count-mode": 1}
    status, raw, _ = post_json(url, body, {"Authorization": f"Bearer {token}"})
    if status >= 400:
        raise RuntimeError(f"product count query failed: HTTP {status}")
    data = json.loads(raw.decode("utf-8"))
    meta = data.get("meta") or {}
    total = meta.get("total", data.get("total", 0))
    return int(total or 0)


def main() -> int:
    config_path = Path(sys.argv[1])
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    base_url = cfg["base_url"]
    corpus_target = int(cfg.get("corpus_target", 100000))
    warmup = int(cfg.get("warmup", 3))
    iterations = int(cfg.get("iterations", 20))
    bench = cfg["bench"]
    admin_cfg = cfg["admin"]

    token = fetch_admin_token(base_url, admin_cfg)
    product_count = fetch_product_count(base_url, token)
    corpus_ready = product_count >= corpus_target

    samples: list[float] = []
    errors: list[str] = []
    url = base_url.rstrip("/") + bench["path"]
    headers = {"Authorization": f"Bearer {token}"}
    body = bench.get("body", {})

    def run_once() -> float:
        status, _, elapsed_ms = post_json(url, body, headers)
        if status >= 400:
            raise RuntimeError(f"HTTP {status}")
        return elapsed_ms

    for _ in range(warmup):
        try:
            run_once()
        except Exception as exc:  # noqa: BLE001
            errors.append(f"warmup: {exc}")

    for _ in range(iterations):
        try:
            samples.append(run_once())
        except Exception as exc:  # noqa: BLE001
            errors.append(f"bench: {exc}")

    result = {
        "strand": "scale",
        "base_url": base_url,
        "corpus_target": corpus_target,
        "product_count": product_count,
        "corpus_ready": corpus_ready,
        "bench": bench["name"],
        "warmup": warmup,
        "iterations": iterations,
        "p50_ms": round(percentile(samples, 50), 2),
        "p95_ms": round(percentile(samples, 95), 2),
        "request_count": len(samples),
        "errors": errors[:20],
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY
