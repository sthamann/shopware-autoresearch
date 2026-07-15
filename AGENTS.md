# Auto-Research Shopware — Agent Entry

> **Agents: start here.** Verification workflow managed with
> [Pawl](https://github.com/agentic-commerce-lab/pawl) (tools under `pawl/tools/`).

## 1. Doc index

| Priority | Doc |
|---|---|
| **First** | `docs/big-picture.md` — three performance strands, one-sentence law |
| Strang 1 | Request-Performance — single HTTP request latency (`REQ`, `HTTP`, …) |
| Strang 2 | API-Performance — Store/Admin/Sync API (`STOREAPI`, `ADMINAPI`, …) |
| Strang 3 | Katalog-Skalierung — ≥ 100k products, storefront + admin (`SCALE`, …) |
| Platform | `repos/shopware/` — Shopware trunk checkout (Docker dev stack) |
| Status | `verification/registry.csv` — claim status ground truth |
| Proposals | `docs/plans/` — plans (proposals, NOT ground truth) |

## 2. Rules and skills

- Guard rails: `.cursor/rules/verification-framework.mdc`
- Before substantive edits: `.cursor/rules/project-startup.mdc`
- Skills: `.cursor/skills/` (`claim-lifecycle`, `verification-memory`, …)

## 3. The verification loop (mandatory for features)

```text
memory.py query (duplicates?) -> register.py -> init_folder.py
  -> freeze gates -> implement -> tools/run.py -> Verified | Failed
```

```bash
python3 pawl/tools/memory.py fronts
python3 pawl/tools/scan.py --audit
python3 pawl/tools/run.py <CLAIM_ID>
```

## 4. Fixed harness

Primary metrics (per strand, fixed harness):

| Strand | Scalar |
|---|---|
| 1 Request | p95 response time on fixed request set |
| 2 API | p95 per API family on fixed endpoints |
| 3 Scale | p95 storefront + admin flows at ≥ 100k products |

Measured by `verification/bench/<strand>/` (harness-owned). Experiments may
never edit the harness or `repos/shopware/compose.yaml`.

## 5. Project audits (before merge)

```bash
./scripts/dev-exec.sh bin/console -V
python3 pawl/tools/scan.py --audit
```

## 6. Hard laws

- Plans are proposals; the registry is ground truth.
- No green verification → feature is not implemented.
- Freeze measurable gates **before** implementation.
- Failed is a result: name the missing capability, sweep dependent claims.
- One canonical implementation per concern — no shadow systems.
- Smallest correct diff; update README of touched modules.

## Learned project facts

- Shopware runs in Docker via `repos/shopware/compose.yaml` + root `compose.override.yaml`.
- Dev commands: `./scripts/dev-up.sh`, `./scripts/dev-exec.sh <cmd>`, `./scripts/dev-setup.sh`.
- Extension repos live in `extensions/` and mount to `custom/plugins/<Name>`.
- Platform submodule tracks `trunk` (6.7-dev); image `ghcr.io/shopware/docker-dev:php8.4-node24-caddy`.
