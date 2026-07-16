#!/usr/bin/env python3
"""Gate for VERIFY.SCALE.STOREFRONT_LISTING_TRUE_CMS.04."""

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
REQUEST_CONFIG = ROOT / "verification" / "bench" / "request" / "config.json"
LISTING_CMS_PATH = "/page/cms/019f64c64cf77058b8bc452c37f90ca8"
CORPUS_TARGET = 100_000
P95_THRESHOLD_MS = 2500.0
WARMUP = 3
ITERATIONS = 20


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = int(round((pct / 100.0) * (len(ordered) - 1)))
    return ordered[idx]


def timed_get(url: str) -> float:
    start = time.perf_counter()
    req = urllib.request.Request(url, method="GET", headers={"Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        resp.read()
        if resp.status >= 400:
            raise RuntimeError(f"HTTP {resp.status}")
    return (time.perf_counter() - start) * 1000.0


def main() -> int:
    scale_proc = subprocess.run(
        [str(SCALE_BENCH)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if scale_proc.returncode != 0:
        print(scale_proc.stderr or scale_proc.stdout, file=sys.stderr)
        return 1

    scale = json.loads(scale_proc.stdout)
    product_count = int(scale.get("product_count", 0))

    req_cfg = json.loads(REQUEST_CONFIG.read_text(encoding="utf-8"))
    base_url = req_cfg["base_url"].rstrip("/")
    url = base_url + LISTING_CMS_PATH

    samples: list[float] = []
    errors: list[str] = []
    for _ in range(WARMUP):
        try:
            timed_get(url)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"warmup: {exc}")

    for _ in range(ITERATIONS):
        try:
            samples.append(timed_get(url))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"bench: {exc}")

    p95_ms = percentile(samples, 95)
    p50_ms = percentile(samples, 50)

    gates = {
        "corpus_at_least_100k": product_count >= CORPUS_TARGET,
        "samples_collected": len(samples) >= 10,
        "true_listing_cms_p95_within_threshold": p95_ms <= P95_THRESHOLD_MS,
    }
    metrics = {
        "p95_ms": round(p95_ms, 2),
        "p50_ms": round(p50_ms, 2),
        "threshold_ms": P95_THRESHOLD_MS,
        "request_count": len(samples),
        "product_count": product_count,
        "listing_cms_path": LISTING_CMS_PATH,
        "bench_category_path": next(
            r["path"] for r in req_cfg["requests"] if r["name"] == "category"
        ),
        "errors": errors[:10],
    }

    ok = all(gates.values())
    report = {
        "claim_id": "VERIFY.SCALE.STOREFRONT_LISTING_TRUE_CMS.04",
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
    print(f"VERIFY.SCALE.STOREFRONT_LISTING_TRUE_CMS.04: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
