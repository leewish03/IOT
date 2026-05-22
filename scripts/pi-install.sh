#!/usr/bin/env bash
# Raspberry Pi one-shot install: Docker, env templates, systemd stack.
set -euo pipefail

IOT_INSTALL_DIR="${IOT_INSTALL_DIR:-/opt/iot-home}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root: sudo $0" >&2
  exit 1
fi

echo "==> Installing Docker (if missing)"
if ! command -v docker >/dev/null 2>&1; then
  apt-get update
  apt-get install -y ca-certificates curl
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
    $(. /etc/os-release && echo "${VERSION_CODENAME:-bookworm}") stable" \
    > /etc/apt/sources.list.d/docker.list
  apt-get update
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
fi
systemctl enable --now docker

DEPLOY_USER="${SUDO_USER:-${USER:-pi}}"
if id "$DEPLOY_USER" &>/dev/null; then
  usermod -aG docker "$DEPLOY_USER" || true
fi

echo "==> Syncing repo to ${IOT_INSTALL_DIR}"
install -d -m 0755 "$IOT_INSTALL_DIR"
if [[ "$(realpath "$REPO_ROOT")" != "$(realpath "$IOT_INSTALL_DIR")" ]]; then
  rsync -a --delete \
    --exclude .git \
    --exclude web/node_modules \
    --exclude web/.next \
    --exclude '__pycache__' \
    "$REPO_ROOT/" "$IOT_INSTALL_DIR/"
fi

ENV_DIR="$IOT_INSTALL_DIR/deploy/env"
echo "==> Env templates -> ${ENV_DIR}/*.env"
for example in backend.env.example web.env.example; do
  base="${example%.example}"
  if [[ ! -f "${ENV_DIR}/${base}" ]]; then
    cp "${ENV_DIR}/${example}" "${ENV_DIR}/${base}"
    echo "  created ${ENV_DIR}/${base} (edit before production)"
  else
    echo "  kept existing ${ENV_DIR}/${base}"
  fi
done

if grep -q '^ORCHESTRATOR_TOKEN=change-me' "${ENV_DIR}/web.env" 2>/dev/null; then
  token="$(grep '^BACKEND_API_TOKEN=' "${ENV_DIR}/backend.env" | cut -d= -f2- || true)"
  if [[ -n "$token" && "$token" != "change-me" ]]; then
    sed -i "s/^ORCHESTRATOR_TOKEN=.*/ORCHESTRATOR_TOKEN=${token}/" "${ENV_DIR}/web.env"
    echo "  synced ORCHESTRATOR_TOKEN from backend.env"
  fi
fi

echo "==> Installing systemd units"
for unit in iot-docker.service iot-orchestrator.service iot-web.service iot-stack.target; do
  install -m 0644 "$IOT_INSTALL_DIR/deploy/systemd/${unit}" "/etc/systemd/system/${unit}"
done
systemctl daemon-reload
systemctl enable iot-stack.target

echo "==> Done."
echo "    1. Edit ${ENV_DIR}/backend.env and ${ENV_DIR}/web.env"
echo "    2. sudo systemctl start iot-stack.target"
echo "    3. Dashboard: http://$(hostname -I | awk '{print $1}'):3000  Orchestrator: :8080"
echo "    Or: cd ${IOT_INSTALL_DIR}/deploy/docker-compose && docker compose up -d --build"
