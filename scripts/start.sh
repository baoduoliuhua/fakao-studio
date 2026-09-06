#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ ! -d .venv ]; then
  echo "Missing .venv. Run scripts/setup.sh first."
  exit 1
fi

source .venv/bin/activate
PYTHONPATH=backend uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
trap 'kill "$BACKEND_PID" 2>/dev/null || true' EXIT

npm --prefix frontend run dev
