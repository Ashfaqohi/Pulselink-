#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== backend unit and integration tests =="
(cd "$ROOT_DIR/backend" && .venv/bin/pytest -q)

echo "== frontend unit tests =="
npm --prefix "$ROOT_DIR/frontend" test

echo "== frontend production build =="
npm --prefix "$ROOT_DIR/frontend" run build

if [[ "${SKIP_E2E:-0}" != "1" ]]; then
  echo "== browser end-to-end test =="
  npm --prefix "$ROOT_DIR/frontend" run test:e2e
else
  echo "== browser end-to-end test skipped (SKIP_E2E=1) =="
fi

echo "All verification suites passed."
