# 2026-07-15-01 — VERIFY.INFRA.DOCKER_STACK.01

> **Status: Planned.** Freeze the gates in `run.py` BEFORE implementing.

## Claim

Shopware Docker stack from repos/shopware/compose.yaml starts healthy; web container responds HTTP 200 on / within 120s after up; database healthcheck passes; anti-pattern: do not patch upstream compose.yaml

## Acceptance gates (freeze a priori)

- [ ] gate 1: <metric> <op> <threshold>
- [ ] gate 2: ...

## Verdict

_Fill after the official run: what was measured, what passed/failed, and —
if Failed — the exact missing capability (honest negative)._
