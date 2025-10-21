#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"

# Determine where the stack definition is located (source) and where it should
# be executed from (runtime). When the launcher is called from the AppImage we
# copy the stack definition to a persistent location under the user's home.
STACK_SOURCE_DIR="${WEBOWIE_STACK_SOURCE_DIR:-}"
if [[ -z "$STACK_SOURCE_DIR" ]]; then
  if [[ -n "${APPDIR:-}" && -d "${APPDIR}/usr/share/webowie-stack" ]]; then
    STACK_SOURCE_DIR="${APPDIR}/usr/share/webowie-stack"
  elif [[ -f "$PROJECT_ROOT/docker-compose.yml" ]]; then
    STACK_SOURCE_DIR="$PROJECT_ROOT"
  else
    echo "[WebOwie] Konnte die Stack-Definition nicht finden." >&2
    exit 1
  fi
fi

DEFAULT_RUNTIME_DIR="$STACK_SOURCE_DIR"
if [[ "$STACK_SOURCE_DIR" == *".AppDir"* ]]; then
  DEFAULT_RUNTIME_DIR="${WEBOWIE_RUNTIME_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/webowie-stack}"
fi

RUNTIME_DIR="${WEBOWIE_RUNTIME_DIR:-$DEFAULT_RUNTIME_DIR}"
mkdir -p "$RUNTIME_DIR"

# Copy stack artefacts on first run when we are executed from an AppImage.
if [[ "$RUNTIME_DIR" != "$STACK_SOURCE_DIR" ]]; then
  for item in docker-compose.yml .env.example docs branding; do
    if [[ -e "$STACK_SOURCE_DIR/$item" ]]; then
      if [[ -d "$STACK_SOURCE_DIR/$item" ]]; then
        if command -v rsync >/dev/null 2>&1; then
          rsync -a --ignore-errors "$STACK_SOURCE_DIR/$item" "$RUNTIME_DIR/" 2>/dev/null || true
        else
          cp -a "$STACK_SOURCE_DIR/$item" "$RUNTIME_DIR/"
        fi
      else
        cp -n "$STACK_SOURCE_DIR/$item" "$RUNTIME_DIR/$item" 2>/dev/null || true
      fi
    fi
  done
fi

COMPOSE_FILE="$RUNTIME_DIR/docker-compose.yml"
if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "[WebOwie] docker-compose.yml wurde nicht gefunden in $RUNTIME_DIR" >&2
  exit 1
fi

ENV_FILE="${WEBOWIE_ENV_FILE:-$RUNTIME_DIR/.env}"
if [[ ! -f "$ENV_FILE" ]]; then
  if [[ -f "$RUNTIME_DIR/.env.example" ]]; then
    cp "$RUNTIME_DIR/.env.example" "$ENV_FILE"
    echo "[WebOwie] Erste Konfiguration: .env aus .env.example erzeugt." >&2
  else
    touch "$ENV_FILE"
  fi
fi

resolve_compose() {
  if [[ -n "${DOCKER_COMPOSE_BIN:-}" ]]; then
    echo "$DOCKER_COMPOSE_BIN"
    return 0
  fi
  if command -v docker >/dev/null 2>&1; then
    if docker compose version >/dev/null 2>&1; then
      echo "docker compose"
      return 0
    fi
  fi
  if command -v docker-compose >/dev/null 2>&1; then
    echo "docker-compose"
    return 0
  fi
  return 1
}

COMPOSE_CLI=""

ensure_compose() {
  if [[ -n "$COMPOSE_CLI" ]]; then
    return 0
  fi
  local resolved
  resolved="$(resolve_compose || true)"
  if [[ -z "$resolved" ]]; then
    cat <<'MSG' >&2
[WebOwie] Docker Compose konnte nicht gefunden werden.
Bitte installiere entweder Docker Compose v2 ("docker compose") oder das klassische "docker-compose"-Binary.
MSG
    return 1
  fi
  COMPOSE_CLI="$resolved"
}

compose() {
  ensure_compose || exit 1
  if [[ "$COMPOSE_CLI" == "docker compose" ]]; then
    docker compose --project-name webowie --file "$COMPOSE_FILE" --env-file "$ENV_FILE" "$@"
  else
    (cd "$RUNTIME_DIR" && docker-compose --project-name webowie --file "$COMPOSE_FILE" "$@")
  fi
}

open_urls() {
  local urls=(
    "http://localhost:8085" # Appsmith
    "http://localhost:4000"  # Matomo
    "http://localhost:5678"  # n8n
  )
  if command -v xdg-open >/dev/null 2>&1; then
    for url in "${urls[@]}"; do
      xdg-open "$url" >/dev/null 2>&1 || true
    done
  fi
}

print_usage() {
  cat <<'USAGE'
WebOwie Stack Launcher
======================

Verwendung: webowie-launcher <Befehl> [Optionen]

Befehle:
  start [services]   Docker-Stack im Hintergrund starten
  stop [services]    Dienste stoppen (alias: down)
  restart            Stack neu starten
  status             Aktuellen Status (docker compose ps)
  logs [services]    Logs streamen
  open               Öffnet zentrale Web-Oberflächen im Browser
  exec <args...>     Beliebigen docker compose-Befehl durchreichen
  help               Diese Hilfe anzeigen

Beispiele:
  webowie-launcher start
  webowie-launcher logs n8n
  webowie-launcher exec run --rm n8n npm test
USAGE
}

ACTION="${1:-help}"
if [[ $# -gt 0 ]]; then
  shift || true
fi

case "$ACTION" in
  start)
    ensure_compose || exit 1
    compose up -d "$@"
    open_urls
    ;;
  stop|down)
    ensure_compose || exit 1
    compose down "$@"
    ;;
  restart)
    ensure_compose || exit 1
    compose down
    compose up -d "$@"
    open_urls
    ;;
  status|ps)
    ensure_compose || exit 1
    compose ps "$@"
    ;;
  logs)
    ensure_compose || exit 1
    compose logs -f "$@"
    ;;
  open)
    open_urls
    ;;
  exec)
    ensure_compose || exit 1
    compose "$@"
    ;;
  help|--help|-h)
    print_usage
    ;;
  *)
    echo "[WebOwie] Unbekannter Befehl: $ACTION" >&2
    print_usage
    exit 1
    ;;
esac
