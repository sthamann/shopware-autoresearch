#!/usr/bin/env bash
# Fixed api-perf harness — stdout: one JSON object.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CONFIG="${HERE}/config.json"

exec python3 - "$CONFIG" <<'PY'
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = int(round((pct / 100.0) * (len(ordered) - 1)))
    return ordered[idx]


def post_json(url: str, body: dict, headers: dict[str, str]) -> tuple[int, float]:
    payload = json.dumps(body).encode("utf-8")
    req_headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        **headers,
    }
    request = urllib.request.Request(url, data=payload, headers=req_headers, method="POST")
    start = time.perf_counter()
    with urllib.request.urlopen(request, timeout=30) as resp:
        resp.read()
        status = resp.status
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return status, elapsed_ms


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


def fetch_storefront_access_key(base_url: str, token: str) -> str:
    url = base_url.rstrip("/") + "/api/search/sales-channel"
    body = {"limit": 5, "filter": [{"type": "equals", "field": "name", "value": "Storefront"}]}
    payload = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    rows = data.get("data") or []
    if not rows:
        raise RuntimeError("no sales channels returned")
    access_key = rows[0].get("accessKey") or (rows[0].get("attributes") or {}).get("accessKey")
    if not access_key:
        raise RuntimeError("storefront access key missing")
    return access_key


def main() -> int:
    config_path = Path(sys.argv[1])
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    base_url = cfg["base_url"]
    warmup = int(cfg.get("warmup", 3))
    iterations = int(cfg.get("iterations", 20))
    primary = cfg.get("primary", cfg["endpoints"][0]["name"])
    admin_cfg = cfg["admin"]

    token = fetch_admin_token(base_url, admin_cfg)
    access_key = fetch_storefront_access_key(base_url, token)

    per_endpoint: dict[str, list[float]] = {ep["name"]: [] for ep in cfg["endpoints"]}
    errors: list[str] = []

    def run_endpoint(ep: dict) -> float:
        url = base_url.rstrip("/") + ep["path"]
        headers: dict[str, str] = {}
        if ep.get("auth") == "bearer":
            headers["Authorization"] = f"Bearer {token}"
        if ep.get("family") == "storeapi":
            headers["sw-access-key"] = access_key
        status, elapsed_ms = post_json(url, ep.get("body", {}), headers)
        if status >= 400:
            raise RuntimeError(f"HTTP {status}")
        return elapsed_ms

    for _ in range(warmup):
        for ep in cfg["endpoints"]:
            try:
                run_endpoint(ep)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"warmup {ep['name']}: {exc}")

    for _ in range(iterations):
        for ep in cfg["endpoints"]:
            try:
                ms = run_endpoint(ep)
                per_endpoint[ep["name"]].append(ms)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{ep['name']}: {exc}")

    by_endpoint = {
        name: {
            "p50_ms": round(percentile(samples, 50), 2),
            "p95_ms": round(percentile(samples, 95), 2),
            "request_count": len(samples),
        }
        for name, samples in per_endpoint.items()
    }
    primary_samples = per_endpoint.get(primary, [])
    result = {
        "strand": "api",
        "base_url": base_url,
        "warmup": warmup,
        "iterations": iterations,
        "primary": primary,
        "p50_ms": round(percentile(primary_samples, 50), 2),
        "p95_ms": round(percentile(primary_samples, 95), 2),
        "request_count": len(primary_samples),
        "by_endpoint": by_endpoint,
        "errors": errors[:20],
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY
