# PulseLink public task tracker

This file is the repository-backed task tracker. It is intentionally plain
Markdown so it remains publicly readable in GitHub, GitLab, or any static
repository browser.

## Public location

When this repository is published, expose this file at:

`https://github.com/<owner>/<repository>/blob/main/docs/task-tracker.md`

Until `<owner>/<repository>` is replaced with the real public repository, the
tracker is not yet publicly accessible. Do not replace the placeholder with an
invented URL.

## How to use this tracker

- Keep one row per deliverable.
- Link each task to observable acceptance criteria.
- Update status and evidence links in the same change that advances a task.
- Record agent activity in [agent-activity.md](agent-activity.md).
- A task is complete only when its acceptance criteria and evidence links are
  satisfied.

## Task board

| ID | Task | Acceptance criteria | Status | Evidence |
|---|---|---|---|---|
| PL-001 | Review problem statement and user journeys | [Phase 1 criteria](acceptance-criteria.md#phase-1-exit-gate) reviewed | Done | [README](../README_Pulse.md#3-problem-statement) |
| PL-002 | Finalize acceptance criteria | URL, ownership, reliability/security, incident response, and performance criteria are observable and testable | Done | [Acceptance criteria](acceptance-criteria.md) |
| PL-003 | Finalize database schema | PostgreSQL tables, keys, indexes, constraints, and retention rules are documented | Done | [Schema](schema.md) |
| PL-004 | Finalize API contract | Endpoint behavior, status codes, authorization, and safe errors are documented | Done | [API contract](api.md) |
| PL-005 | Implement FastAPI backend | URL creation, redirect, ownership, statistics, health, readiness, and metrics criteria pass | Done | [Backend app](../backend/app/main.py), [backend tests](../backend/tests/test_backend.py) |
| PL-006 | Implement React frontend | Dashboard, URL creation/management, and incident dashboard criteria pass | In progress | [Frontend app](../frontend/src/App.tsx), [frontend tests](../frontend/src/App.test.tsx) |
| PL-007 | Add automated tests | Unit, frontend, integration, and end-to-end criteria pass in CI | In progress | [Backend integration tests](../backend/tests/test_integration.py), [frontend tests](../frontend/src/App.test.tsx) |
| PL-008 | Containerize local environment | Compose runs frontend, backend, database volume, and observability services | Done | [Compose stack](../docker-compose.yml), [deployment guide](deployment.md) |
| PL-009 | Add CI/CD | Pull requests run required checks; development deploys on main; production deployment is manual and rollback is documented | In progress | [CI](../.github/workflows/ci.yml), [dev deploy](../.github/workflows/deploy-dev.yml), [production deploy](../.github/workflows/deploy-production.yml), [rollback](../.github/workflows/rollback.yml) |
| PL-010 | Add observability and incident response | User-impact metrics, alerts, webhook intake, traces, structured logs, redaction, Grafana views, and an alert-woken responder with auditable findings are configured | Done | [Observability stack](../observability), [responder](../responder), [deployment guide](deployment.md) |
| PL-011 | Define agent team and operating process | Roles, ownership, handoffs, review gates, escalation, and incident-response collaboration are documented | Done | [Agent team charter](agent-team.md) |
| PL-012 | Verify complete local full-stack flow | One command starts frontend and backend; browser creates a URL; data persists; redirect is verified end to end | Done | [Run-local launcher](../scripts/run-local.sh), [Playwright test](../frontend/e2e/pulselink.spec.ts) |
| PL-013 | Add repository guidance and reproducible demo | `AGENTS.md` points to modular docs; one command runs verification; Docker demo creates and verifies a deployed local link | Done | [AGENTS.md](../AGENTS.md), [test-all.sh](../scripts/test-all.sh), [demo.md](demo.md) |

## Acceptance-criteria source of truth

The detailed criteria live in [docs/acceptance-criteria.md](acceptance-criteria.md).
The broader project specification and milestone order live in
[README_Pulse.md](../README_Pulse.md).
