# Local development

## One-command startup

From the repository root, run:

```bash
./scripts/run-local.sh
```

The script bootstraps missing dependencies, starts the API and frontend,
waits for both health checks, and stops both services together with Ctrl-C.
The SQLite database persists at `backend/pulselink.db` by default.

## Backend

The backend uses SQLite by default for local development and tests. Set
`PULSELINK_DB_PATH` to choose another SQLite file. The API currently uses the
`X-User-ID` header as a lightweight development authentication boundary.

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`; interactive documentation is
at `/docs`.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend uses `VITE_API_URL` when set, otherwise it calls
`http://localhost:8000`.

## Verification

```bash
cd backend && .venv/bin/pytest -q
cd frontend && npm test
cd frontend && npm run build
cd frontend && npm run test:e2e
```

The backend integration tests create a temporary SQLite database, so they do
not require a running database service.

Container deployment, CI/CD, rollback, and user-impact alerting are documented
in [deployment.md](deployment.md).
The complete Docker-backed demo is documented in [demo.md](demo.md).
Run all local verification with one command using `./scripts/test-all.sh`;
set `SKIP_E2E=1` only when browser execution is unavailable.
