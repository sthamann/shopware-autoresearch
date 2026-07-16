# 2026-07-16-03 — VERIFY.SCALE.ADMIN_SEARCH_ES_SOURCE.03

> **Status: Planned.** Freeze the gates in `run.py` BEFORE implementing.

## Claim

Admin product search p95 <= 260 ms at >= 100k with OpenSearch _source includes limited to admin grid columns; anti-pattern: shrink limit below bench or disable ES

## Acceptance gates (freeze a priori)

- [ ] gate 1: <metric> <op> <threshold>
- [ ] gate 2: ...

## Verdict

_Fill after the official run: what was measured, what passed/failed, and —
if Failed — the exact missing capability (honest negative)._
