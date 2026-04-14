#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

COMPOSE_FILES=(-f docker-compose.yml -f docker-compose.prod.yml)

echo "[deploy] Validating compose config..."
docker compose "${COMPOSE_FILES[@]}" config -q

echo "[deploy] Building images..."
docker compose "${COMPOSE_FILES[@]}" build

echo "[deploy] Starting services..."
docker compose "${COMPOSE_FILES[@]}" up -d

echo "[deploy] Waiting for healthchecks..."
deadline=$((SECONDS + 180))
while (( SECONDS < deadline )); do
  core="$(docker inspect --format '{{json .State.Health.Status}}' d-lite-core-backend 2>/dev/null || true)"
  rt="$(docker inspect --format '{{json .State.Health.Status}}' d-lite-realtime-service 2>/dev/null || true)"
  if [[ "$core" == "\"healthy\"" && "$rt" == "\"healthy\"" ]]; then
    echo "[deploy] OK: core-backend + realtime-service healthy"
    docker compose "${COMPOSE_FILES[@]}" ps
    exit 0
  fi
  sleep 3
done

echo "[deploy] ERROR: healthchecks did not become healthy in time"
docker compose "${COMPOSE_FILES[@]}" ps || true
exit 1

