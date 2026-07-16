# 2026-07-16-07 — VERIFY.SCALE.ADMIN_SEARCH_DAL_BYPASS.05

## Claim

Admin product search p95 <= 260 ms at >= 100k via dedicated ES-only search path bypassing DAL hydration; anti-pattern: shrink limit

## Acceptance gates

- bench_ran
- corpus_at_least_100k
- admin_search_p95_dal_bypass (<= 260 ms)
- improved_vs_wave4 (< 303 ms)

## Verdict

**Failed (honest negative).** `AdminProductEntityReaderDecorator` builds grid rows from cached ES `_source`, but admin search p95 **316 ms** (Wave 4: 303 ms). DAL read was not the dominant cost; ES query + API serialization floor persists at ~315 ms.
