#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

docker compose up --build -d
trap 'rm -f "$TMP_RESPONSE"' EXIT
TMP_RESPONSE="$(mktemp)"

for _ in {1..30}; do
  curl --silent --fail http://127.0.0.1:5173/ >/dev/null && break
  sleep 2
done
curl --silent --fail http://127.0.0.1:5173/ >/dev/null

ALIAS="demo-$(date +%s)"
curl --silent --fail \
  -H 'Content-Type: application/json' \
  -H 'X-User-ID: demo-user' \
  -d "{\"original_url\":\"https://example.com/pulselink-demo\",\"custom_alias\":\"$ALIAS\"}" \
  http://127.0.0.1:5173/api/urls > "$TMP_RESPONSE"

SHORT_URL="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["short_url"])' "$TMP_RESPONSE")"
curl --silent --show-error --fail --max-redirs 0 "$SHORT_URL" >/dev/null 2>&1 && STATUS=$? || STATUS=$?
if [[ "$STATUS" != "0" && "$STATUS" != "47" ]]; then
  echo "Redirect smoke check failed with curl status $STATUS" >&2
  exit 1
fi

echo "Demo is running at http://127.0.0.1:5173"
echo "Created and verified: $SHORT_URL"
echo "Stop it with: docker compose down"
