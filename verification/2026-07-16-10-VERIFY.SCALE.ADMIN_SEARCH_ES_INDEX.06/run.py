#!/usr/bin/env python3
"""Gate for VERIFY.SCALE.ADMIN_SEARCH_ES_INDEX.06."""

from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCALE_BENCH = ROOT / "verification" / "bench" / "scale" / "run_bench.sh"
CONFIG = ROOT / "verification" / "bench" / "scale" / "config.json"
CORPUS_TARGET = 100_000
P95_THRESHOLD_MS = 260.0
WAVE5_BASELINE_MS = 316.0
GRID_PATH = "/api/_action/autoresearch/admin-product-grid-search"
WARMUP = 3
ITERATIONS = 20


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = int(round((pct / 100.0) * (len(ordered) - 1)))
    return ordered[idx]


def fetch_admin_token(base_url: str, admin_cfg: dict) -> str:
    url = base_url.rstrip("/") + "/api/oauth/token"
    body = json.dumps(
        {
            "grant_type": "password",
            "client_id": admin_cfg["client_id"],
            "username": admin_cfg["username"],
            "password": admin_cfg["password"],
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    token = data.get("access_token")
    if not token:
        raise RuntimeError("admin oauth token missing")
    return token


def post_grid(url: str, body: dict, token: str) -> tuple[int, dict, float]:
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
    start = time.perf_counter()
    with urllib.request.urlopen(request, timeout=60) as resp:
        raw = resp.read().decode("utf-8")
        status = resp.status
    elapsed_ms = (time.perf_counter() - start) * 1000.0
    return status, json.loads(raw), elapsed_ms


def main() -> int:
    scale_proc = subprocess.run(
        [str(SCALE_BENCH)], cwd=ROOT, capture_output=True, text=True, check=False
    )
    scale = json.loads(scale_proc.stdout) if scale_proc.returncode == 0 else {}
    product_count = int(scale.get("product_count", 0))

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    base_url = cfg["base_url"].rstrip("/")
    admin_cfg = cfg["admin"]
    token = fetch_admin_token(base_url, admin_cfg)
    grid_url = base_url + GRID_PATH
    body = {"limit": 25, "term": "product"}

    samples: list[float] = []
    errors: list[str] = []
    grid_response: dict = {}

    for _ in range(WARMUP):
        try:
            post_grid(grid_url, body, token)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"warmup: {exc}")

    for _ in range(ITERATIONS):
        try:
            status, data, elapsed = post_grid(grid_url, body, token)
            if status >= 400:
                errors.append(f"bench: HTTP {status}")
                continue
            samples.append(elapsed)
            grid_response = data
        except Exception as exc:  # noqa: BLE001
            errors.append(f"bench: {exc}")

    p95_ms = percentile(samples, 95)
    total = int(grid_response.get("total", 0))
    rows = grid_response.get("data") or []
    query_only = bool(grid_response.get("meta", {}).get("queryOnly"))

    gates = {
        "corpus_at_least_100k": product_count >= CORPUS_TARGET,
        "grid_endpoint_responds": len(rows) > 0,
        "grid_query_only_path": query_only,
        "admin_grid_search_p95": p95_ms <= P95_THRESHOLD_MS,
        "improved_vs_wave5": p95_ms < WAVE5_BASELINE_MS,
    }
    metrics = {
        "p95_ms": round(p95_ms, 2),
        "p50_ms": round(percentile(samples, 50), 2),
        "wave5_baseline_ms": WAVE5_BASELINE_MS,
        "delta_ms": round(p95_ms - WAVE5_BASELINE_MS, 2),
        "threshold_ms": P95_THRESHOLD_MS,
        "product_count": product_count,
        "grid_total": total,
        "grid_rows": len(rows),
        "grid_path": GRID_PATH,
        "errors": errors[:10],
    }

    ok = all(gates.values())
    report = {
        "claim_id": "VERIFY.SCALE.ADMIN_SEARCH_ES_INDEX.06",
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "verdict": "pass" if ok else "fail",
        "gates": gates,
        "metrics": metrics,
    }
    (HERE / "last_run.json").write_text(json.dumps(report, indent=2) + "\n")
    for name, value in gates.items():
        print(f"  gate {name}: {'PASS' if value else 'FAIL'}")
    print(f"VERIFY.SCALE.ADMIN_SEARCH_ES_INDEX.06: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
