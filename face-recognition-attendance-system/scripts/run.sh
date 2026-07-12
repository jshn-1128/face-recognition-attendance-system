#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

case "${1:-dev}" in
  dev)
    echo "=== Starting development environment ==="
    # Backend
    cd "$ROOT_DIR/backend"
    source .venv/bin/activate
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!

    # Frontend
    cd "$ROOT_DIR/frontend"
    npm run dev &
    FRONTEND_PID=$!

    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:5173"

    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
    wait
    ;;
  docker)
    echo "=== Starting Docker environment ==="
    cd "$ROOT_DIR"
    docker compose up --build
    ;;
  *)
    echo "Usage: $0 {dev|docker}"
    exit 1
    ;;
esac
