# 2026-07-15-12 — VERIFY.STOREAPI.FIELD_PROJECTION.02

> **Status: Planned.** Freeze the gates in `run.py` BEFORE implementing.

## Claim

Store API product list p95 <= 80 ms with explicit field projection decorator (baseline ~97 ms); anti-pattern: return empty elements or drop calculatedPrice

## Acceptance gates (freeze a priori)

- [ ] gate 1: <metric> <op> <threshold>
- [ ] gate 2: ...

## Verdict

_Fill after the official run: what was measured, what passed/failed, and —
if Failed — the exact missing capability (honest negative)._
