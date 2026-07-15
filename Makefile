.PHONY: bootstrap up down setup exec logs ps audit

bootstrap:
	./scripts/bootstrap.sh

up:
	./scripts/dev-up.sh

down:
	./scripts/dev-down.sh

setup:
	./scripts/dev-setup.sh

logs:
	./scripts/dev-compose.sh
	docker compose -f "$$COMPOSE_BASE" -f "$$COMPOSE_OVERRIDE" logs -f

ps:
	./scripts/dev-compose.sh
	docker compose -f "$$COMPOSE_BASE" -f "$$COMPOSE_OVERRIDE" ps

exec:
	./scripts/dev-exec.sh $(CMD)

audit:
	python3 pawl/tools/scan.py --audit

memory:
	python3 pawl/tools/memory.py fronts
