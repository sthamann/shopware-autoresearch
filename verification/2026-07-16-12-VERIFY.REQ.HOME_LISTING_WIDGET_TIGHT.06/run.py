#!/usr/bin/env python3
"""Gate for VERIFY.REQ.HOME_LISTING_WIDGET_TIGHT.06."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCALE_BENCH = ROOT / "verification" / "bench" / "scale" / "run_bench.sh"
CONFIG = ROOT / "verification" / "bench" / "request" / "config.json"
CORPUS_TARGET = 100_000
WIDGET_P95_THRESHOLD_MS = 1000.0
WAVE5_BASELINE_MS = 1620.0
MIN_PRODUCTS = 20
WARMUP = 2
ITERATIONS = 10


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = int(round((pct / 100.0) * (len(ordered) - 1)))
    return ordered[idx]


def fetch(url: str, headers: dict[str, str] | None = None) -> tuple[str, float]:
    start = time.perf_counter()
    req = urllib.request.Request(url, method="GET", headers=headers or {"Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        if resp.status >= 400:
            raise RuntimeError(f"HTTP {resp.status}")
    return body, (time.perf_counter() - start) * 1000.0


def extract_navigation_id(home_html: str) -> str | None:
    match = re.search(r"window\.activeNavigationId\s*=\s*'([^']+)'", home_html)
    if match:
        return match.group(1)
    return None


def count_products(html: str) -> int:
    return len(re.findall(r'class="[^"]*product-box', html))


def main() -> int:
    scale_proc = subprocess.run(
        [str(SCALE_BENCH)], cwd=ROOT, capture_output=True, text=True, check=False
    )
    scale = json.loads(scale_proc.stdout) if scale_proc.returncode == 0 else {}
    product_count = int(scale.get("product_count", 0))

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    base_url = cfg["base_url"].rstrip("/")
    home_url = base_url + "/"

    home_html, _ = fetch(home_url)
    has_deferred_marker = 'data-autoresearch-deferred-listing="1"' in home_html
    nav_id = extract_navigation_id(home_html) or ""

    widget_url = base_url + f"/widgets/cms/navigation/{nav_id}"
    widget_headers = {
        "Accept": "text/html",
        "X-Requested-With": "XMLHttpRequest",
    }

    samples: list[float] = []
    product_counts: list[int] = []
    errors: list[str] = []

    for _ in range(WARMUP):
        try:
            html, _ = fetch(widget_url, widget_headers)
            product_counts.append(count_products(html))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"warmup: {exc}")

    for _ in range(ITERATIONS):
        try:
            html, elapsed = fetch(widget_url, widget_headers)
            samples.append(elapsed)
            product_counts.append(count_products(html))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"bench: {exc}")

    widget_p95 = percentile(samples, 95)
    max_products = max(product_counts) if product_counts else 0

    gates = {
        "corpus_at_least_100k": product_count >= CORPUS_TARGET,
        "home_has_deferred_marker": has_deferred_marker,
        "widget_samples_collected": len(samples) >= 5,
        "widget_p95_within_threshold": widget_p95 <= WIDGET_P95_THRESHOLD_MS,
        "widget_loads_min_products": max_products >= MIN_PRODUCTS,
        "improved_vs_wave5": widget_p95 < WAVE5_BASELINE_MS,
    }
    metrics = {
        "widget_p95_ms": round(widget_p95, 2),
        "widget_p50_ms": round(percentile(samples, 50), 2),
        "wave5_baseline_ms": WAVE5_BASELINE_MS,
        "delta_ms": round(widget_p95 - WAVE5_BASELINE_MS, 2),
        "threshold_ms": WIDGET_P95_THRESHOLD_MS,
        "max_product_boxes": max_products,
        "min_products_required": MIN_PRODUCTS,
        "navigation_id": nav_id,
        "product_count": product_count,
        "errors": errors[:10],
    }

    ok = all(gates.values())
    report = {
        "claim_id": "VERIFY.REQ.HOME_LISTING_WIDGET_TIGHT.06",
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "verdict": "pass" if ok else "fail",
        "gates": gates,
        "metrics": metrics,
    }
    (HERE / "last_run.json").write_text(json.dumps(report, indent=2) + "\n")
    for name, value in gates.items():
        print(f"  gate {name}: {'PASS' if value else 'FAIL'}")
    print(f"VERIFY.REQ.HOME_LISTING_WIDGET_TIGHT.06: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
