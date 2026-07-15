#!/usr/bin/env bash
# Add a Shopware extension repo as a git submodule and mount it in compose.override.yaml
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <plugin-name> <git-url> [branch]" >&2
  echo "Example: $0 SwagUcp https://github.com/shopware/SwagUcp.git" >&2
  exit 1
fi

PLUGIN_NAME="$1"
REPO_URL="$2"
BRANCH="${3:-}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${ROOT}/extensions/${PLUGIN_NAME}"
OVERRIDE="${ROOT}/compose.override.yaml"
MOUNT_LINE="      - ./extensions/${PLUGIN_NAME}:/var/www/html/custom/plugins/${PLUGIN_NAME}"

cd "${ROOT}"

if [[ -d "${TARGET}" ]]; then
  echo "Extension already exists: ${TARGET}" >&2
  exit 1
fi

if [[ -n "${BRANCH}" ]]; then
  git submodule add -b "${BRANCH}" "${REPO_URL}" "extensions/${PLUGIN_NAME}"
else
  git submodule add "${REPO_URL}" "extensions/${PLUGIN_NAME}"
fi

if ! grep -Fq "${MOUNT_LINE}" "${OVERRIDE}"; then
  awk -v mount="${MOUNT_LINE}" '
    /# - \.\/extensions\// && !inserted { print mount; inserted=1 }
    { print }
  ' "${OVERRIDE}" > "${OVERRIDE}.tmp" && mv "${OVERRIDE}.tmp" "${OVERRIDE}"
  echo "Added volume mount to compose.override.yaml"
fi

echo "Extension added: extensions/${PLUGIN_NAME}"
echo "Restart stack: ./scripts/dev-up.sh"
