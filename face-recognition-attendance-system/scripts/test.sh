#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Running backend tests ==="
cd "$ROOT_DIR/backend"
source .venv/bin/activate
pytest --cov=app --cov-report=term-missing -v

echo ""
echo "=== Running frontend tests ==="
cd "$ROOT_DIR/frontend"
npm run test -- --run
