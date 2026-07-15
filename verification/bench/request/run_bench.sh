#!/usr/bin/env bash
# Fixed request-perf harness — stdout: one JSON object.
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


def timed_request(base_url: str, req: dict) -> float:
    url = base_url.rstrip("/") + req["path"]
    method = req.get("method", "GET").upper()
    start = time.perf_counter()
    request = urllib.request.Request(url, method=method)
    with urllib.request.urlopen(request, timeout=30) as resp:
        resp.read()
        if resp.status >= 400:
            raise urllib.error.HTTPError(url, resp.status, "bad status", resp.headers, None)
    return (time.perf_counter() - start) * 1000.0


def main() -> int:
    config_path = Path(sys.argv[1])
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    base_url = cfg["base_url"]
    warmup = int(cfg.get("warmup", 3))
    iterations = int(cfg.get("iterations", 20))
    requests = cfg["requests"]
    primary = cfg.get("primary", requests[0]["name"])

    per_request: dict[str, list[float]] = {r["name"]: [] for r in requests}
    errors: list[str] = []

    for _ in range(warmup):
        for req in requests:
            try:
                timed_request(base_url, req)
            except Exception as exc:  # noqa: BLE001 — bench reports, does not crash
                errors.append(f"warmup {req['name']}: {exc}")

    for _ in range(iterations):
        for req in requests:
            try:
                ms = timed_request(base_url, req)
                per_request[req["name"]].append(ms)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{req['name']}: {exc}")

    all_samples = [v for samples in per_request.values() for v in samples]
    by_request = {
        name: {
            "p50_ms": round(percentile(samples, 50), 2),
            "p95_ms": round(percentile(samples, 95), 2),
            "request_count": len(samples),
        }
        for name, samples in per_request.items()
    }
    primary_samples = per_request.get(primary, [])
    result = {
        "strand": "request",
        "base_url": base_url,
        "warmup": warmup,
        "iterations": iterations,
        "primary": primary,
        "p50_ms": round(percentile(primary_samples, 50), 2),
        "p95_ms": round(percentile(primary_samples, 95), 2),
        "request_count": len(primary_samples),
        "by_request": by_request,
        "all_p50_ms": round(percentile(all_samples, 50), 2),
        "all_p95_ms": round(percentile(all_samples, 95), 2),
        "errors": errors[:20],
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY
