#!/usr/bin/env python3
"""Gate for VERIFY.INFRA.DOCKER_STACK.01.

Exit 0 = all gates green (claim becomes Verified).
Exit 1 = any gate red (claim becomes Failed — an honest negative, not an error).
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COMPOSE_BASE = ROOT / "repos" / "shopware" / "compose.yaml"
COMPOSE_OVERRIDE = ROOT / "compose.override.yaml"
STOREFRONT_URL = "http://localhost:8000/"
STARTUP_TIMEOUT_S = 120


def run_compose(args: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    cmd = [
        "docker",
        "compose",
        "-f",
        str(COMPOSE_BASE),
        "-f",
        str(COMPOSE_OVERRIDE),
        *args,
    ]
    return subprocess.run(
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def docker_daemon_running() -> bool:
    result = subprocess.run(
        ["docker", "info"],
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    return result.returncode == 0


def services_running() -> bool:
    result = run_compose(["ps", "--status", "running", "--format", "json"])
    if result.returncode != 0:
        return False
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    return len(lines) >= 2


def database_healthy() -> bool:
    result = run_compose(["ps", "database", "--format", "{{.Health}}"])
    return result.returncode == 0 and "healthy" in result.stdout.lower()


def storefront_http_ok() -> tuple[bool, int | None]:
    deadline = time.time() + STARTUP_TIMEOUT_S
    last_status: int | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(STOREFRONT_URL, timeout=5) as resp:
                last_status = resp.status
                if 200 <= resp.status < 400:
                    return True, last_status
        except urllib.error.HTTPError as exc:
            last_status = exc.code
            if 200 <= exc.code < 400:
                return True, last_status
        except (urllib.error.URLError, TimeoutError):
            pass
        time.sleep(3)
    return False, last_status


def main() -> int:
    metrics: dict[str, object] = {}

    compose_files_exist = COMPOSE_BASE.is_file() and COMPOSE_OVERRIDE.is_file()
    metrics["compose_base"] = str(COMPOSE_BASE)
    metrics["compose_override"] = str(COMPOSE_OVERRIDE)

    daemon_ok = docker_daemon_running()
    metrics["docker_daemon"] = daemon_ok

    if daemon_ok and compose_files_exist:
        up = run_compose(["up", "-d"], timeout=180)
        metrics["compose_up_exit"] = up.returncode
        running = services_running()
        metrics["services_running"] = running
        db_ok = database_healthy()
        metrics["database_healthy"] = db_ok
        http_ok, status = storefront_http_ok()
        metrics["storefront_status"] = status
        metrics["storefront_ok"] = http_ok
    else:
        metrics["compose_up_exit"] = None
        metrics["services_running"] = False
        metrics["database_healthy"] = False
        metrics["storefront_status"] = None
        metrics["storefront_ok"] = False
        http_ok = False
        db_ok = False
        running = False

    gates = {
        "compose_files_exist": compose_files_exist,
        "docker_daemon_running": daemon_ok,
        "services_running": running,
        "database_healthy": db_ok,
        "storefront_http_ok": http_ok,
    }

    ok = all(gates.values())
    report = {
        "claim_id": "VERIFY.INFRA.DOCKER_STACK.01",
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "verdict": "pass" if ok else "fail",
        "gates": gates,
        "metrics": metrics,
    }
    (HERE / "last_run.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    for name, value in gates.items():
        print(f"  gate {name}: {'PASS' if value else 'FAIL'}")
    print(f"VERIFY.INFRA.DOCKER_STACK.01: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
