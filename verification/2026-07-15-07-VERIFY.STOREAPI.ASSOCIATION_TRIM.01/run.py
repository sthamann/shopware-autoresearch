#!/usr/bin/env python3
"""Gate for VERIFY.STOREAPI.ASSOCIATION_TRIM.01."""

from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BENCH = ROOT / "verification" / "bench" / "api" / "run_bench.sh"
CONFIG = ROOT / "verification" / "bench" / "api" / "config.json"
P95_THRESHOLD_MS = 85.0
BASELINE_MS = 97.0


def product_count_from_api(base_url: str, admin_cfg: dict) -> int:
    token_url = base_url.rstrip("/") + "/api/oauth/token"
    body = json.dumps(
        {
            "grant_type": "password",
            "client_id": admin_cfg["client_id"],
            "username": admin_cfg["username"],
            "password": admin_cfg["password"],
        }
    ).encode()
    req = urllib.request.Request(
        token_url, data=body, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        token = json.loads(resp.read())["access_token"]

    sc_url = base_url.rstrip("/") + "/api/search/sales-channel"
    sc_body = json.dumps(
        {"limit": 5, "filter": [{"type": "equals", "field": "name", "value": "Storefront"}]}
    ).encode()
    sc_req = urllib.request.Request(
        sc_url,
        data=sc_body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    with urllib.request.urlopen(sc_req, timeout=30) as resp:
        rows = json.loads(resp.read())["data"]
    access_key = rows[0].get("accessKey") or rows[0]["attributes"]["accessKey"]

    prod_url = base_url.rstrip("/") + "/store-api/product"
    prod_body = json.dumps({"limit": 25}).encode()
    prod_req = urllib.request.Request(
        prod_url,
        data=prod_body,
        headers={"Content-Type": "application/json", "sw-access-key": access_key},
        method="POST",
    )
    with urllib.request.urlopen(prod_req, timeout=30) as resp:
        data = json.loads(resp.read())
    return len(data.get("elements") or [])


def main() -> int:
    proc = subprocess.run(
        [str(BENCH)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout, file=sys.stderr)
        return 1

    bench = json.loads(proc.stdout)
    p95_ms = float(bench.get("p95_ms", 0))
    request_count = int(bench.get("request_count", 0))

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    try:
        products_returned = product_count_from_api(cfg["base_url"], cfg["admin"])
    except (urllib.error.URLError, KeyError, json.JSONDecodeError) as exc:
        print(f"product count check failed: {exc}", file=sys.stderr)
        products_returned = 0

    gates = {
        "bench_ran": proc.returncode == 0,
        "samples_collected": request_count >= 10,
        "store_api_p95_within_threshold": p95_ms <= P95_THRESHOLD_MS,
        "response_has_products": products_returned >= 1,
    }
    metrics = {
        "p95_ms": p95_ms,
        "p50_ms": bench.get("p50_ms"),
        "baseline_ms": BASELINE_MS,
        "threshold_ms": P95_THRESHOLD_MS,
        "request_count": request_count,
        "products_returned": products_returned,
        "by_endpoint": bench.get("by_endpoint"),
    }

    ok = all(gates.values())
    report = {
        "claim_id": "VERIFY.STOREAPI.ASSOCIATION_TRIM.01",
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "verdict": "pass" if ok else "fail",
        "gates": gates,
        "metrics": metrics,
    }
    (HERE / "last_run.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    for name, value in gates.items():
        print(f"  gate {name}: {'PASS' if value else 'FAIL'}")
    print(f"VERIFY.STOREAPI.ASSOCIATION_TRIM.01: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
