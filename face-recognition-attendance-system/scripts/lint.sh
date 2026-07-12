#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
EXIT_CODE=0

echo "=== Linting backend ==="
cd "$ROOT_DIR/backend"
source .venv/bin/activate
echo ">>> ruff..."
ruff check app/ || EXIT_CODE=$?
echo ">>> mypy..."
mypy app/ || EXIT_CODE=$?

echo ""
echo "=== Linting frontend ==="
cd "$ROOT_DIR/frontend"
echo ">>> ESLint..."
npm run lint || EXIT_CODE=$?
echo ">>> TypeScript..."
npm run typecheck || EXIT_CODE=$?

exit $EXIT_CODE
