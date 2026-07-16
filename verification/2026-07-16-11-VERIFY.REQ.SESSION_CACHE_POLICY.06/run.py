#!/usr/bin/env python3
"""Gate for VERIFY.REQ.SESSION_CACHE_POLICY.06."""

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
WARMUP = ROOT / "scripts" / "warmup-http-cache.sh"
CONFIG = ROOT / "verification" / "bench" / "request" / "config.json"
P95_THRESHOLD_MS = 120.0
ANONYMOUS_CONTEXT_TOKEN = "autoresearch-anonymous-cache-token"
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

    headers = {
        "Accept": "text/html",
        "sw-context-token": ANONYMOUS_CONTEXT_TOKEN,
    }

    cache_hit = False
    session_cookie_set = False
    cache_policy_marker = False
    for _ in range(3):
        req = urllib.request.Request(url, method="GET", headers=headers)
        with urllib.request.urlopen(req, timeout=60) as resp:
            hdr = resp.headers.get("X-Symfony-Cache", "")
            if " hit" in hdr.lower():
                cache_hit = True
            set_cookie = resp.headers.get("Set-Cookie", "")
            if "session-" in set_cookie.lower():
                session_cookie_set = True
            if resp.headers.get("X-Autoresearch-Cache-Policy"):
                cache_policy_marker = True

    samples: list[float] = []
    for _ in range(WARMUP_ITERS):
        req = urllib.request.Request(url, method="GET", headers=headers)
        with urllib.request.urlopen(req, timeout=60) as resp:
            resp.read()
    for _ in range(BENCH_ITERS):
        start = time.perf_counter()
        req = urllib.request.Request(url, method="GET", headers=headers)
        with urllib.request.urlopen(req, timeout=60) as resp:
            resp.read()
        samples.append((time.perf_counter() - start) * 1000.0)

    p95_ms = percentile(samples, 95)

    gates = {
        "samples_collected": len(samples) >= 10,
        "anonymous_no_session_cookie": not session_cookie_set,
        "category_p95_cached": p95_ms <= P95_THRESHOLD_MS,
        "http_cache_hit_with_context_token": cache_hit,
        "cache_policy_marker_present": cache_policy_marker,
    }
    metrics = {
        "p95_ms": round(p95_ms, 2),
        "threshold_ms": P95_THRESHOLD_MS,
        "cache_hit": cache_hit,
        "session_cookie_set": session_cookie_set,
        "cache_policy_marker": cache_policy_marker,
        "context_token_header": ANONYMOUS_CONTEXT_TOKEN,
        "request_count": len(samples),
        "category_path": category["path"],
    }

    ok = all(gates.values())
    report = {
        "claim_id": "VERIFY.REQ.SESSION_CACHE_POLICY.06",
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "verdict": "pass" if ok else "fail",
        "gates": gates,
        "metrics": metrics,
    }
    (HERE / "last_run.json").write_text(json.dumps(report, indent=2) + "\n")
    for name, value in gates.items():
        print(f"  gate {name}: {'PASS' if value else 'FAIL'}")
    print(f"VERIFY.REQ.SESSION_CACHE_POLICY.06: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
