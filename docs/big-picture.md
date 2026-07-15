# Big Picture — Shopware Autoresearch

> **As of: 2026-07-15.** Agent-facing bird's-eye view for Shopware
> **performance research** with Pawl verification discipline.
>
> Living numbers (current p95, verified wins, honest negatives) live in
> `verification/registry.csv` — not here.

---

## 0. The one sentence

> **A performance improvement counts only when it lowers latency or resource
> cost on the fixed benchmark harness at the declared corpus size — a faster
> response that skips work, serves stale data, or only wins on a toy catalog
> is a failure, even if the dashboard looks green.**

The failure mode we reject: optimizing the measurement instead of the system.

---

## 1. Mission

Systematically find, verify, and document **real** Shopware performance gains
across three research strands. Each gain is a Pawl claim with frozen gates;
each dead end is an honest negative that blocks re-exploration.

This is not a feature backlog. It is a **performance research program** on
`repos/shopware` (trunk) with reproducible benches and a registry that
survives agent session boundaries.

| Naive view | This project |
|---|---|
| "Make Shopware faster" (vague) | Three strands with fixed harnesses and corpus sizes |
| One global benchmark score | Per-strand authoritative scalars + per-claim gates |
| Agent says "done" | Registry row `Verified` after official `run.py` |
| Re-try known failures every session | `Failed` claims name the missing capability |
| 10 products in dev = scale proof | Strang 3 requires 100k+ product corpus on the bench |

---

## 2. The three research strands

### Forschungsstrang 1 — Request-Performance (`request-perf`)

**Question:** Wie bekommt man **einzelne HTTP-Requests** schneller?

Scope: End-to-end latency of one request through the Shopware stack — not
API surface area (Strang 2), not catalog cardinality (Strang 3).

| Area | Examples |
|---|---|
| Request lifecycle | Kernel bootstrap, routing, middleware chain, session handling |
| Backend work per request | SQL query count & duration, ES round-trips, event subscribers |
| Caching | HTTP cache, Redis/object cache, config/route warmup |
| Rendering | Twig compilation, storefront/admin asset pipeline, serialization overhead |
| Infrastructure | PHP opcache, connection pooling, container I/O |

**Authoritative scalar:** p95 **total response time** (or TTFB where
declared) on a **fixed request set** at a **reference catalog size**
(documented in the harness; default: Shopware demo data until Strang 3 corpus
is ready).

**Claim families:** `REQ`, `HTTP`, `TTFB`, `PIPELINE`, `CACHE`

**Anti-patterns:** cache only benchmark URLs; disable middleware for the
bench; measure only warm-cache when claiming cold-start wins.

---

### Forschungsstrang 2 — API-Performance (`api-perf`)

**Question:** Wie optimiert man die **verschiedenen Shopware-APIs**?

Scope: API-layer performance — endpoints, payloads, pagination, bulk
operations. A Strang-2 claim must name the API surface (Store API, Admin API,
Sync API, …).

| API surface | Typical pressure points |
|---|---|
| **Store API** | Product listing, search, cart, checkout, filtering, includes/associations |
| **Admin API** | CRUD, search, bulk sync, media, indexing triggers |
| **Sync API** | Bulk import/export throughput, memory per batch |
| **Cross-cutting** | JSON:API serialization, pagination defaults, N+1 in hydrators, search queries |

**Authoritative scalar:** p95 latency per **API family** on a **fixed API
bench** (same endpoints, payloads, concurrency, and auth — harness-owned).

**Claim families:** `API`, `STOREAPI`, `ADMINAPI`, `SYNCAPI`, `GRAPHQL`

**Anti-patterns:** smaller `limit` to pass gates; strip required associations
from responses; benchmark only localhost without containerized stack.

---

### Forschungsstrang 3 — Katalog-Skalierung (`catalog-scale`)

**Question:** Wie bleibt Shopware performant bei **hunderttausenden Produkten**
— im **Storefront** und im **Admin**?

Scope: Behaviour at scale. Strang-3 claims **must** declare corpus size
(≥ 100 000 products unless the claim explicitly tests a lower floor with
justification). Both surfaces matter:

| Surface | Examples |
|---|---|
| **Storefront** | Category navigation, listing pages, search & suggest, filters/facets, PDP |
| **Administration** | Product grid, admin search, filters, bulk actions, media browser, indexing UI |
| **Platform** | DB indexes, OpenSearch indexing & query plans, message queue backpressure, warmup |

**Authoritative scalar:** p95 on **representative storefront + admin flows**
at **≥ 100k products** on the fixed scale corpus (seed script harness-owned).

**Claim families:** `SCALE`, `CATALOG`, `ADMIN`, `STORE`, `SEARCH`, `INDEX`

**Anti-patterns:** extrapolate from 1k products; test only ES-bypass paths;
optimize admin grid by hiding columns that production needs.

---

## 3. How the strands relate

```text
Strang 1 (Request)     → one HTTP request through the stack
Strang 2 (API)         → named API endpoints & payloads
Strang 3 (Scale)       → same flows, but corpus ≥ 100k products

```

A change may touch multiple strands — register **one claim per strand** it
claims to improve, or one claim with explicit multi-gate `run.py` sections.
Never blur strands in a single vague claim ("made Shopware faster").

Dependency rule: Strang-3 gates may depend on Strang-1/2 infrastructure
(e.g. a new index), but a Strang-1 win on demo data does **not** imply a
Strang-3 win — scale must be measured separately.

---

## 4. Layers and roles

| Layer | May | Must not |
|---|---|---|
| Meta-repo (`shopware-autoresearch`) | Orchestrate benches, verify, document | Patch Shopware core without scoped claim |
| `repos/shopware` | Platform changes scoped to claims | Hold permanent custom plugins |
| `extensions/*` | Bench helpers, profiling plugins (scoped) | Replace core perf paths silently |
| `pawl/` | Registry, gates, autoresearch | Contain Shopware business logic |
| **Fixed harness** (`verification/bench/`) | Define corpus, endpoints, concurrency | Be edited by experiment claims |
| Docker stack | Reproducible runtime | Be customized per experiment (only `compose.override.yaml`) |

---

## 5. Anti-sprawl rules

1. **No claim without registry row** — `register.py` before any folder.
2. **Gates frozen before implementation** — thresholds in `run.py` are a priori.
3. **Harness is sacred** — experiments may not edit the fixed bench; propose a
   harness change as its own `VERIFY.META.*` claim first.
4. **Corpus size is declared** — Strang 3 claims state product count in the
   claim text and gate.
5. **No benchmark gaming** — see `pawl/docs/metric-integrity.md`; reject wins
   that narrow the workload.
6. **One canonical fix per bottleneck** — no shadow optimizers behind feature flags.
7. **Platform compose is upstream-owned** — only `compose.override.yaml` at root.

---

## 6. What is measured — and what counts

| Strand | Primary scalar | Fixed harness |
|---|---|---|
| 1 Request | p95 response time on fixed request set | `verification/bench/request/` |
| 2 API | p95 per API family on fixed endpoints | `verification/bench/api/` |
| 3 Scale | p95 storefront + admin flows at ≥ 100k products | `verification/bench/scale/` |

**Ground truth for status:** `verification/registry.csv`. No green
verification → improvement is not implemented.

**Progress reporting:** only numbers from the official harness under honest
conditions (same corpus, same concurrency, same container stack).

---

## 7. Claim naming convention

```
VERIFY.<FAMILY>.<NAME>.<NN>
```

Examples:

| Claim id | Strand |
|---|---|
| `VERIFY.REQ.TTFB_STOREFRONT_HOME.01` | 1 |
| `VERIFY.STOREAPI.PRODUCT_LIST_P95.01` | 2 |
| `VERIFY.SCALE.ADMIN_PRODUCT_GRID_100K.01` | 3 |

Track assignment: `verification/tracks.json` + `python3 pawl/tools/memory.py fronts`.

---

## 8. Repo map

| Path | Role |
|---|---|
| `docs/big-picture.md` | This file — stable research framing |
| `docs/plans/` | Proposals (not ground truth) |
| `verification/registry.csv` | Claim statuses |
| `verification/bench/` | Fixed harnesses (per strand) |
| `repos/shopware/` | Shopware trunk checkout |
| `pawl/tools/` | Registry tooling |
| `scripts/` | Docker & dev helpers |

---

## 9. Reading order for agents

1. This file — §0, §2 (three strands), §5 (anti-sprawl).
2. `AGENTS.md` — entry point and hard laws.
3. `python3 pawl/tools/memory.py fronts` — live status per strand.
4. `verification/registry.csv` — before registering duplicates.
5. Harness README in `verification/bench/<strand>/` before running experiments.

---

## 10. Key commands

```bash
./scripts/bootstrap.sh
./scripts/dev-up.sh
./scripts/dev-exec.sh bin/console -V

python3 pawl/tools/memory.py fronts
python3 pawl/tools/register.py VERIFY.REQ.<NAME>.01 "..."
python3 pawl/tools/run.py <CLAIM_ID>
```
