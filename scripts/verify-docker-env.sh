#!/usr/bin/env bash
set -uo pipefail

STRICT=0
if [[ "${1:-}" == "--strict" ]]; then
  STRICT=1
  shift
fi

status=0

if ! command -v docker >/dev/null 2>&1; then
  echo "[x] Docker CLI nicht gefunden. Installationsanleitung: https://docs.docker.com/engine/install/" >&2
  status=1
else
  echo "[✓] Docker CLI gefunden: $(docker --version 2>/dev/null)"

  if docker info >/dev/null 2>&1; then
    echo "[✓] Docker-Daemon antwortet"
  else
    echo "[x] Docker-Daemon läuft nicht oder Berechtigungen fehlen. Starte den Dienst (z. B. 'sudo service docker start') oder prüfe deine Umgebung." >&2
    status=1
  fi

  if docker compose version >/dev/null 2>&1; then
    echo "[✓] Docker Compose v2 Plugin verfügbar"
  elif command -v docker-compose >/dev/null 2>&1; then
    if docker-compose version >/dev/null 2>&1; then
      short_version=$(docker-compose version --short 2>/dev/null || echo "unbekannt")
      echo "[!] Docker Compose v1 gefunden: ${short_version}"
    else
      echo "[!] Docker Compose v1 gefunden, konnte aber nicht ausgeführt werden (benötigt ggf. python3-distutils/PyYAML)." >&2
    fi
    echo "    Hinweis: Für dieses Projekt wird Compose v2 empfohlen. Installation: https://docs.docker.com/compose/install/" >&2
  else
    echo "[x] Weder Docker Compose v2 noch v1 gefunden. Installiere das Compose-Plugin oder docker-compose." >&2
    status=1
  fi
fi

if [[ $status -ne 0 ]]; then
  if [[ $STRICT -eq 1 ]]; then
    exit "$status"
  fi
  echo ""
  echo "[!] Warnung: Docker-Umgebung unvollständig. Führe das Skript mit '--strict' aus, um einen Fehlercode zu erhalten." >&2
  exit 0
fi

echo "[✓] Docker-Umgebung bereit."
