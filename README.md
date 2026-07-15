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

## Pawl verification

```bash
TOOLS=pawl/tools

python3 $TOOLS/memory.py fronts
python3 $TOOLS/scan.py --audit
python3 $TOOLS/register.py VERIFY.INFRA.DOCKER_STACK.01 "..."
python3 $TOOLS/init_folder.py VERIFY.INFRA.DOCKER_STACK.01
python3 $TOOLS/run.py VERIFY.INFRA.DOCKER_STACK.01
```

See `AGENTS.md` for the full agent workflow.

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
