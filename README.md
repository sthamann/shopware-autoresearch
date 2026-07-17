# Auto-Research Shopware

Multirepo workspace for **agent-driven Shopware research** with [Pawl](https://github.com/agentic-commerce-lab/pawl) verification and a Docker-based Shopware platform checkout.

## Layout

```
auto-research-shopware/          # Meta-repo (Pawl + orchestration)
├── pawl/                        # Submodule: agentic-commerce-lab/pawl
├── repos/shopware/              # Submodule: shopware/shopware (trunk, latest)
├── extensions/                  # Optional plugin/app submodules (mounted into Shopware)
├── verification/                # Pawl registry + claim folders
├── docs/                        # Big picture, plans
├── compose.override.yaml        # Multirepo volume mounts for extensions
└── scripts/                     # Dev helpers
```

| Repo | Role |
|------|------|
| `pawl/` | Verification framework (registry, gates, autoresearch) |
| `repos/shopware/` | Shopware platform source (trunk, 6.7-dev) |
| `extensions/*` | Custom plugins/apps as separate git submodules |

## Prerequisites

- Docker Desktop (Compose v2)
- Python 3.9+
- Git

## Quick start

```bash
# 1. Clone with submodules
git clone --recurse-submodules <this-repo-url>
cd auto-research-shopware

# Or if already cloned:
./scripts/bootstrap.sh

# 2. Start Shopware Docker stack (uses repos/shopware/compose.yaml)
./scripts/dev-up.sh

# 3. First-time Shopware install inside container
./scripts/dev-setup.sh

# 4. Run commands in the web container
./scripts/dev-exec.sh bin/console cache:clear
./scripts/dev-exec.sh composer watch:admin
```

### URLs

| Service | URL |
|---------|-----|
| Storefront / Admin | http://localhost:8000 |
| Admin login | `admin` / `shopware` |
| Adminer (DB) | http://localhost:9080 |
| Mailpit | http://localhost:8025 |

## Multirepo: add an extension

```bash
./scripts/add-extension.sh MyPlugin https://github.com/org/MyPlugin.git
./scripts/dev-up.sh
./scripts/dev-exec.sh bin/console plugin:refresh
./scripts/dev-exec.sh bin/console plugin:install --activate MyPlugin
```

Or add a volume manually in `compose.override.yaml`:

```yaml
services:
  web:
    volumes:
      - ./extensions/MyPlugin:/var/www/html/custom/plugins/MyPlugin
```

## Research program

Three performance strands — see `docs/big-picture.md`:

| # | Strand | Focus |
|---|--------|-------|
| 1 | **Request performance** | Single HTTP requests faster (TTFB, pipeline, caching) |
| 2 | **API performance** | Store API, Admin API, Sync API optimization |
| 3 | **Catalog scaling** | ≥ 100k products — storefront + admin |

```bash
python3 pawl/tools/memory.py fronts    # status per strand
./verification/bench/request/run_bench.sh
./verification/bench/api/run_bench.sh
./verification/bench/scale/seed_corpus.sh   # ≥100k products (scale strand)
./verification/bench/scale/run_bench.sh
```

Fixed harnesses live under `verification/bench/<strand>/` — sacred, harness-owned;
see `verification/bench/README.md`.

See `AGENTS.md` for the full agent workflow.

## Current progress

> **As of 2026-07-16** — Bootstrap + Waves 1–6 complete. Full write-up:
> [`RESEARCH_RESULTS.md`](RESEARCH_RESULTS.md) · [`RESEARCH_RESULTS.pdf`](RESEARCH_RESULTS.pdf)

All measurements are from official Pawl gates against a **100,000-product** catalog.

| Metric | Value |
|--------|------:|
| Experiments (claims) | **33** |
| Verified | **12** |
| Failed (honest negatives) | **18** |
| Planned (Wave 7) | **3** |
| Completed waves | **6** (+ bootstrap) |

**Biggest breakthroughs**

| Route | Before | After | Change | Mechanism |
|-------|-------:|------:|-------:|-----------|
| Home `/` | 3,199 ms | **199 ms** | −94 % | Deferred product listing |
| Listing CMS | 1,681 ms | **200 ms** | −88 % | Deferred product listing (CMS pages) |
| Admin search | 316 ms | **71 ms** | −78 % | Query-only grid endpoint (DBAL) |

**Per-strand state @ 100k**

- **Strand 1 (Request):** home **199 ms** (deferred), category **186 ms**, widget async **1,598 ms**; HTTP cache blocked by session cookie.
- **Strand 2 (API):** Store API product list **96 ms** (baseline); association/field trims plateau at ~109 ms.
- **Strand 3 (Scale):** category listing **184 ms**, listing CMS deferred **200 ms**, admin grid query-only **71 ms**; standard admin search floor ~316 ms.

Optimizations ship in [`extensions/AutoresearchPerf/`](extensions/AutoresearchPerf/); results
are reproducible via `docs/assets/gen_charts.py` and `docs/build_pdf.py`.

**Open (Wave 7):** wire the query-only admin grid into the standard search path,
CACHE_REWORK policies for cookie-less GETs, and a listing-only widget partial.

## Docker compose model

- **Base**: `repos/shopware/compose.yaml` — managed by upstream Shopware (trunk)
- **Override**: `compose.override.yaml` — only extension mounts; never edit the base file
- **Run from root**: all `scripts/dev-*.sh` merge both files automatically

This keeps the platform checkout updatable via `git submodule update` while extensions live in sibling repos under `extensions/`.

## Updating submodules

```bash
git submodule update --remote repos/shopware   # pull latest trunk
git submodule update --remote pawl             # pull latest Pawl
```

## Makefile shortcuts

```bash
make bootstrap   # init submodules + pawl
make up          # docker compose up
make down        # docker compose down
make setup       # composer setup in container
make exec CMD="bin/console -V"
```
