#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Formatting code ==="

# Backend
cd "$ROOT_DIR/backend"
source .venv/bin/activate
black app/
isort app/

# Frontend
cd "$ROOT_DIR/frontend"
npx prettier --write "src/**/*.{ts,tsx,css,json}"

echo "=== Format complete ==="
