# 2026-07-15-06 — VERIFY.CACHE.OPCACHE_WARMUP.01

> **Status: Planned.** Freeze the gates in `run.py` BEFORE implementing.

## Claim

After bin/console cache:warmup, storefront home p95 on request bench <= 180 ms (baseline ~195 ms); anti-pattern: skip warmup or measure only opcache status without latency gate

## Acceptance gates (freeze a priori)

- [ ] gate 1: <metric> <op> <threshold>
- [ ] gate 2: ...

## Verdict

**Failed (2026-07-15).** After `bin/console cache:warmup`, home p95 **3082 ms** (gate 180 ms).
Category ~182 ms. Warmup does not address the home-specific dev overhead.
