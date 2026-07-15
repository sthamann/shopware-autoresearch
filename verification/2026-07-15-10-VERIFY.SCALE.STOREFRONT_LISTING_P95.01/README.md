# 2026-07-15-10 — VERIFY.SCALE.STOREFRONT_LISTING_P95.01

> **Status: Planned.** Freeze the gates in `run.py` BEFORE implementing.

## Claim

Storefront category listing p95 <= 2500 ms at >= 100k products (measured in claim gate, not harness); anti-pattern: measure demo catalog only or skip corpus gate

## Acceptance gates (freeze a priori)

- [ ] gate 1: <metric> <op> <threshold>
- [ ] gate 2: ...

## Verdict

**Verified (2026-07-15).** Category listing p95 **184 ms** at 100k products (gate 2500 ms).
`ProductListingCriteriaSubscriber` dropping facet aggregations on default navigation listing
is a real scale win.
