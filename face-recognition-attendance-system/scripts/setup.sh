#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Setting up Face Recognition Attendance System ==="

# Backend setup
echo ">>> Setting up Python virtual environment..."
cd "$ROOT_DIR/backend"
python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements/dev.txt

if [ ! -f .env ]; then
    cp .env.example .env
    echo ">>> Created .env from .env.example - update credentials!"
fi

# Frontend setup
echo ">>> Installing frontend dependencies..."
cd "$ROOT_DIR/frontend"
npm install

echo ">>> Setup complete!"
echo "  1. Update backend/.env with your credentials"
echo "  2. Run './scripts/run.sh' to start services"
