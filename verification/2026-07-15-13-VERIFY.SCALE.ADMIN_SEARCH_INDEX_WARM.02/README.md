# 2026-07-15-13 — VERIFY.SCALE.ADMIN_SEARCH_INDEX_WARM.02

> **Status: Planned.** Freeze the gates in `run.py` BEFORE implementing.

## Claim

Admin product search p95 <= 260 ms at >= 100k after full dal:refresh:index --only product; anti-pattern: skip corpus gate or shrink limit

## Acceptance gates (freeze a priori)

- [ ] gate 1: <metric> <op> <threshold>
- [ ] gate 2: ...

## Verdict

_Fill after the official run: what was measured, what passed/failed, and —
if Failed — the exact missing capability (honest negative)._
