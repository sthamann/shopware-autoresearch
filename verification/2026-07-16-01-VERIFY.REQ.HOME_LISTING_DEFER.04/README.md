# 2026-07-16-01 — VERIFY.REQ.HOME_LISTING_DEFER.04

> **Status: Planned.** Freeze the gates in `run.py` BEFORE implementing.

## Claim

Storefront home p95 on request bench <= 500 ms after deferring product-listing to ESI/async load at >= 100k; shell must still return HTTP 200; anti-pattern: remove listing element from CMS or skip corpus

## Acceptance gates (freeze a priori)

- [ ] gate 1: <metric> <op> <threshold>
- [ ] gate 2: ...

## Verdict

_Fill after the official run: what was measured, what passed/failed, and —
if Failed — the exact missing capability (honest negative)._
