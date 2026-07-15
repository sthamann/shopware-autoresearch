# 2026-07-15-09 — VERIFY.SCALE.ADMIN_SEARCH_ES_TUNING.01

> **Status: Planned.** Freeze the gates in `run.py` BEFORE implementing.

## Claim

Admin product search p95 <= 250 ms at >= 100k products on scale bench (baseline ~301 ms); anti-pattern: reduce search limit below bench or skip corpus gate

## Acceptance gates (freeze a priori)

- [ ] gate 1: <metric> <op> <threshold>
- [ ] gate 2: ...

## Verdict

**Failed (2026-07-15).** Admin search p95 **308 ms** at 100k (gate 250 ms; baseline ~301 ms).
Opensearch 768m heap alone did not improve search latency. Index refresh command initially
wrong (`dal:refresh:index product`); fixed to `--only product` for Wave 2.
