# 2026-07-16-04 — VERIFY.REQ.SESSION_CACHE_BYPASS.04

> **Status: Planned.** Freeze the gates in `run.py` BEFORE implementing.

## Claim

Anonymous storefront GET without Cookie header on category bench achieves X-Symfony-Cache hit after warmup and p95 <= 120 ms; anti-pattern: send session cookie or measure cold-only

## Acceptance gates (freeze a priori)

- [ ] gate 1: <metric> <op> <threshold>
- [ ] gate 2: ...

## Verdict

_Fill after the official run: what was measured, what passed/failed, and —
if Failed — the exact missing capability (honest negative)._
