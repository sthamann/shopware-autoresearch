# Big Picture — Auto-Research Shopware

> **As of: 2026-07-15.** Agent-facing bird's-eye view for Shopware research
> with Pawl verification discipline.

---

## 0. The one sentence

> **A Shopware capability is implemented only when a frozen Pawl claim gate passes
> against the live Docker stack — a green CI run or a convincing agent summary
> without a registry Verified row is a failure.**

---

## 1. The core model

| Naive view | This project |
|---|---|
| One monorepo with everything | Meta-repo orchestrates sibling checkouts |
| Shopware platform = our code | `repos/shopware` is upstream trunk, read-mostly |
| Plugins mixed into platform tree | `extensions/*` are separate submodules, volume-mounted |
| Agent memory = chat history | `verification/registry.csv` is ground truth |

**Flow:** Agent registers claim → freezes gate → edits scoped paths (platform
or extension) → runs gate via `./scripts/dev-exec.sh` → official `run.py`
writes Verified/Failed.

---

## 2. Layers and roles

| Layer | May | Must not |
|---|---|---|
| Meta-repo (`auto-research-shopware`) | Orchestrate, verify, document, mount extensions | Fork Shopware core casually |
| `repos/shopware` | Platform dev, core contributions via PR upstream | Hold custom plugins permanently |
| `extensions/*` | Plugin/app code owned by claims | Replace platform services |
| `pawl/` | Registry, gates, autoresearch loop | Contain Shopware business logic |
| Docker stack | Run Shopware + deps consistently | Be edited per-experiment |

---

## 3. Anti-sprawl rules

1. **No extension without submodule + compose mount** — shadow copies in
   `repos/shopware/custom/plugins/` are forbidden.
2. **No claim without registry row** — `register.py` before any verification folder.
3. **Gates frozen before code** — `run.py` thresholds are a priori.
4. **Platform compose is upstream-owned** — customize only via `compose.override.yaml`.
5. **One claim, one scope** — declare `scope` paths in `register.py`.

---

## 4. Research fronts (tracks)

See `verification/tracks.json`:

- **platform** — Shopware core behavior, APIs, admin/storefront
- **extensions** — Custom plugins under `extensions/`
- **infra** — Docker stack, dev ergonomics, submodule hygiene
- **agentic** — UCP, AXP, WebMCP, sales-agent integrations

---

## 5. Key commands

```bash
./scripts/bootstrap.sh          # submodules + pawl init
./scripts/dev-up.sh             # start Docker
./scripts/dev-setup.sh          # first-time composer setup
./scripts/dev-exec.sh <cmd>     # run in web container
./scripts/add-extension.sh ...  # add plugin submodule + mount
```
