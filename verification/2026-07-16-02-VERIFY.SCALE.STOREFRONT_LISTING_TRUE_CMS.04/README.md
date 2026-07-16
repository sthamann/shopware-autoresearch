# 2026-07-16-02 — VERIFY.SCALE.STOREFRONT_LISTING_TRUE_CMS.04

> **Status: Planned.** Freeze the gates in `run.py` BEFORE implementing.

## Claim

True listing CMS page p95 <= 2500 ms at >= 100k with aggregation trim active (path /page/cms/019f64c64cf77058b8bc452c37f90ca8); anti-pattern: measure contact-form CMS bench page without listing element

## Acceptance gates (freeze a priori)

- [ ] gate 1: <metric> <op> <threshold>
- [ ] gate 2: ...

## Verdict

_Fill after the official run: what was measured, what passed/failed, and —
if Failed — the exact missing capability (honest negative)._
