# Agent activity log

This append-only log records how agents used the task tracker. Each entry names
the tracker tasks consulted or updated and points to repository evidence.

| Timestamp (UTC) | Agent | Action | Tracker references | Evidence |
|---|---|---|---|---|
| 2026-11-17 | Codex | Inspected the repository for a specification, acceptance criteria, public tracker, and prior agent-use evidence. | PL-001–PL-010 | Initial inspection found the specification and criteria but no tracker or activity log. |
| 2026-11-17 | Codex | Added the repository-backed public task tracker and this activity log; linked tasks to acceptance criteria and evidence. | PL-001–PL-010 | [task-tracker.md](task-tracker.md), [acceptance-criteria.md](acceptance-criteria.md), [README_Pulse.md](../README_Pulse.md) |
| 2026-11-17 | Codex | Defined the agent team, ownership boundaries, lifecycle, handoffs, review gates, and incident-response collaboration process. | PL-011 | [agent-team.md](agent-team.md), [README_Pulse.md](../README_Pulse.md#17-project-tracking-and-agent-evidence) |
| 2026-11-17 | Codex | Implemented the SQLite-backed FastAPI backend, React frontend, backend unit/integration tests, frontend tests, and build verification. | PL-005–PL-007 | [local-development.md](local-development.md), [backend](../backend), [frontend](../frontend) |
| 2026-11-17 | Codex | Added the single-command local launcher and browser end-to-end test; verified frontend creation, API persistence, and redirect behavior. | PL-012 | [run-local.sh](../scripts/run-local.sh), [pulselink.spec.ts](../frontend/e2e/pulselink.spec.ts) |
| 2026-11-17 | Codex | Added Dockerfiles, Compose observability services, user-impact Prometheus alerts, Alertmanager intake, GitHub CI/deploy/rollback workflows, and deployment documentation. | PL-008–PL-010 | [deployment.md](deployment.md), [docker-compose.yml](../docker-compose.yml), [workflows](../.github/workflows) |
| 2026-11-17 | Codex | Added root agent guidance, one-command verification, and a reproducible Docker demo with explicit public-deployment prerequisites. | PL-013 | [AGENTS.md](../AGENTS.md), [demo.md](demo.md), [test-all.sh](../scripts/test-all.sh) |
| 2026-11-17 | Codex | Split CI/CD into automatic development deployment on `main` and a manual, protected production promotion workflow; removed automatic production deployment. | PL-009 | [deploy-dev.yml](../.github/workflows/deploy-dev.yml), [deploy-production.yml](../.github/workflows/deploy-production.yml), [deployment.md](deployment.md) |
| 2026-11-17 | Codex | Added OpenTelemetry traces, traceparent/X-Trace-ID correlation, redacted structured JSON logs, Tempo/Loki storage, Grafana provisioning, and observability redaction/correlation tests. | PL-010 | [observability.py](../backend/app/observability.py), [Grafana dashboard](../observability/grafana/dashboards/pulselink.json), [observability tests](../backend/tests/test_observability.py) |
| 2026-11-17 | Codex | Added the Alertmanager-woken responder service, deterministic evidence-based diagnosis, auditable responder reports, and safe recovery verification; production changes remain approval-gated. | PL-010 | [responder](../responder), [responder tests](../responder/tests/test_responder.py), [deployment.md](deployment.md) |

## Evidence policy

Agents must add an entry when they consult, create, update, or verify a task.
Entries must identify the task ID, the action taken, and a durable repository
link or test artifact supporting the claim. This log records repository changes;
Git hosting history supplies author, timestamp, and review metadata after
publication.
