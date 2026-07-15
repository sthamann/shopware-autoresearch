# 2026-07-15-15 — VERIFY.REQ.HOME_DEV_OVERHEAD.02

## Claim

Storefront home p95 on request bench <= 500 ms after root listing CMS trim (profiled: Default listing layout at 100k); category p95 <= 250 ms.

## Verdict

**Failed.** Home p95 **3199 ms** (Wave 2: 3087 ms). Profile shows ~1570 ms root listing API floor + ~1590 ms CMS/render. Plugin DI path fixed (`src/Resources/config/services.xml`) but home gate not met. Missing capability: deferred/lazy home listing or non-listing home CMS layout.
