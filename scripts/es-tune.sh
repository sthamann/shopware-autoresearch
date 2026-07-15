#!/usr/bin/env bash
# Refresh product index and warm admin search queries before scale bench.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="${ROOT}/verification/bench/scale/config.json"

"${ROOT}/scripts/dev-exec.sh" bin/console dal:refresh:index --only product --no-interaction >/dev/null

exec python3 - "$CONFIG" <<'PY'
import json
import sys
import urllib.request
from pathlib import Path

config_path = Path(sys.argv[1])
cfg = json.loads(config_path.read_text(encoding="utf-8"))
base_url = cfg["base_url"].rstrip("/")
admin = cfg["admin"]
bench = cfg["bench"]

token_url = base_url + "/api/oauth/token"
body = json.dumps(
    {
        "grant_type": "password",
        "client_id": admin["client_id"],
        "username": admin["username"],
        "password": admin["password"],
    }
).encode()
req = urllib.request.Request(
    token_url, data=body, headers={"Content-Type": "application/json"}, method="POST"
)
with urllib.request.urlopen(req, timeout=30) as resp:
    token = json.loads(resp.read())["access_token"]

url = base_url + bench["path"]
payload = json.dumps(bench.get("body", {})).encode()
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {token}",
}

for _ in range(10):
    warm = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(warm, timeout=60):
        pass

print("Product index refreshed and admin search warmed")
PY
