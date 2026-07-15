# 2026-07-15-18 — VERIFY.REQ.HOME_LISTING_PROFILE.03

## Claim

Home route profiling artifact documents >= 3 timing breakdown buckets with measured ms.

## Verdict

**Verified.** Five buckets measured: home 3133 ms, category 183 ms, ESI header 142 ms, ESI footer 118 ms, root listing API 1577 ms. Home slowness is root-category product-listing CMS at 100k, not Vite/session overhead.
