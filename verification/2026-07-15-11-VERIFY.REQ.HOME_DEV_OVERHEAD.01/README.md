# 2026-07-15-11 — VERIFY.REQ.HOME_DEV_OVERHEAD.01

> **Status: Planned.** Freeze the gates in `run.py` BEFORE implementing.

## Claim

Storefront home p95 on request bench <= 500 ms when dev-only overhead (Vite/session) is isolated; category p95 must stay <= 250 ms; anti-pattern: disable storefront dev pipeline globally

## Acceptance gates (freeze a priori)

- [ ] gate 1: <metric> <op> <threshold>
- [ ] gate 2: ...

## Verdict

_Fill after the official run: what was measured, what passed/failed, and —
if Failed — the exact missing capability (honest negative)._
