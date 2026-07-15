#!/usr/bin/env python3
"""Gate for VERIFY.REQ.CATEGORY_HTTP_CACHE.01."""

from __future__ import annotations

import http.cookiejar
import json
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WARMUP = ROOT / "scripts" / "warmup-http-cache.sh"
CONFIG = ROOT / "verification" / "bench" / "request" / "config.json"
P95_THRESHOLD_MS = 120.0
WARMUP_ITERS = 5
BENCH_ITERS = 25


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = int(round((pct / 100.0) * (len(ordered) - 1)))
    return ordered[idx]


def main() -> int:
    subprocess.run([str(WARMUP)], cwd=ROOT, check=False)

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    base_url = cfg["base_url"].rstrip("/")
    category = next(r for r in cfg["requests"] if r["name"] == "category")
    url = base_url + category["path"]

    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

    cache_hit = False
    for _ in range(3):
        req = urllib.request.Request(url, method="GET", headers={"Accept": "text/html"})
        with opener.open(req, timeout=60) as resp:
            hdr = resp.headers.get("X-Symfony-Cache", "")
            if " hit" in hdr.lower():
                cache_hit = True

    samples: list[float] = []
    for _ in range(WARMUP_ITERS):
        req = urllib.request.Request(url, method="GET", headers={"Accept": "text/html"})
        with opener.open(req, timeout=60) as resp:
            resp.read()
    for _ in range(BENCH_ITERS):
        start = time.perf_counter()
        req = urllib.request.Request(url, method="GET", headers={"Accept": "text/html"})
        with opener.open(req, timeout=60) as resp:
            resp.read()
        samples.append((time.perf_counter() - start) * 1000.0)

    p95_ms = percentile(samples, 95)

    gates = {
        "samples_collected": len(samples) >= 10,
        "category_p95_cached": p95_ms <= P95_THRESHOLD_MS,
        "http_cache_hit_with_session_jar": cache_hit,
    }
    metrics = {
        "p95_ms": round(p95_ms, 2),
        "threshold_ms": P95_THRESHOLD_MS,
        "cache_hit": cache_hit,
        "request_count": len(samples),
        "category_path": category["path"],
    }

    ok = all(gates.values())
    report = {
        "claim_id": "VERIFY.REQ.CATEGORY_HTTP_CACHE.01",
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "verdict": "pass" if ok else "fail",
        "gates": gates,
        "metrics": metrics,
    }
    (HERE / "last_run.json").write_text(json.dumps(report, indent=2) + "\n")
    for name, value in gates.items():
        print(f"  gate {name}: {'PASS' if value else 'FAIL'}")
    print(f"VERIFY.REQ.CATEGORY_HTTP_CACHE.01: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
