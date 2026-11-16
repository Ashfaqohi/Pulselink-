#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

if [[ ! -x "$BACKEND_DIR/.venv/bin/uvicorn" ]]; then
  echo "Preparing backend environment..."
  python3 -m venv "$BACKEND_DIR/.venv"
  "$BACKEND_DIR/.venv/bin/pip" install -r "$BACKEND_DIR/requirements.txt"
fi

if [[ ! -x "$FRONTEND_DIR/node_modules/.bin/vite" ]]; then
  echo "Preparing frontend environment..."
  npm --prefix "$FRONTEND_DIR" install
fi

cleanup() {
  trap - EXIT INT TERM
  [[ -n "${BACKEND_PID:-}" ]] && kill "$BACKEND_PID" 2>/dev/null || true
  [[ -n "${FRONTEND_PID:-}" ]] && kill "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

PULSELINK_DB_PATH="${PULSELINK_DB_PATH:-$BACKEND_DIR/pulselink.db}" \
  "$BACKEND_DIR/.venv/bin/uvicorn" app.main:app --app-dir "$BACKEND_DIR" --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

for _ in {1..50}; do
  curl --silent --fail http://127.0.0.1:8000/health >/dev/null && break
  sleep 0.2
done
curl --silent --fail http://127.0.0.1:8000/health >/dev/null

npm --prefix "$FRONTEND_DIR" run dev -- --host 127.0.0.1 --port 5173 &
FRONTEND_PID=$!

for _ in {1..50}; do
  curl --silent --fail http://127.0.0.1:5173 >/dev/null && break
  sleep 0.2
done
curl --silent --fail http://127.0.0.1:5173 >/dev/null

echo "PulseLink is running: frontend http://127.0.0.1:5173, API http://127.0.0.1:8000"
echo "Press Ctrl-C to stop both services."
wait "$BACKEND_PID" "$FRONTEND_PID"
