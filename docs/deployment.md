# Deployment, rollback, and user-impact observability

## Containers

Run the full local stack with:

```bash
docker compose up --build
```

Services:

- Frontend/API: `http://localhost:5173`
- Prometheus: `http://localhost:9090`
- Alertmanager: `http://localhost:9093`
- Grafana: `http://localhost:3000` (pre-provisioned Prometheus, Tempo, Loki,
  and the PulseLink user-impact dashboard)
- Tempo traces: collected privately by Grafana at `tempo:3200`
- Loki logs: collected privately by Grafana at `loki:3100`

The API stores its local SQLite database in the `pulselink-data` volume.

## CI/CD

`.github/workflows/ci.yml` runs backend tests, frontend tests/builds, Compose
validation, and container builds on pull requests and `main`.

`.github/workflows/deploy-dev.yml` publishes immutable SHA-tagged images to GHCR
and automatically deploys them to ECS behind the `development` environment on
`main`, then performs health/readiness/metrics verification. Configure the
`DEV_*` AWS, ECS, and health-check secrets before enabling the workflow.

`.github/workflows/deploy-production.yml` is manual-only. It promotes an
immutable image tag that has already passed development, uses the protected
`production` environment for approval, waits for ECS stability, and performs
the same user-impact checks. It has no push trigger.

## Rollback

Use the manually triggered `Rollback` workflow with a known-good ECS task
definition revision, or run:

```bash
ECS_CLUSTER=... ECS_SERVICE=... ROLLBACK_TASK_DEFINITION=... ./scripts/rollback.sh
```

Rollback is explicit and approval-gated by the GitHub production environment.

## User-impact alerts

Prometheus records redirect outcomes and p95 redirect latency. Alert rules
fire on:

- redirect failure rate above 5% with at least 20 requests in five minutes;
- p95 redirect latency above 300ms for five minutes;
- missing redirect telemetry for ten minutes.

These signals measure actual redirect experience. CPU and memory are not used
as the incident trigger. Alertmanager sends firing/resolved alerts to the
responder service, which validates the event, gathers evidence, diagnoses the
likely cause, and records an auditable report in the backend.

The responder agent is woken by Alertmanager, collects API health/readiness and
metrics evidence, classifies the likely cause, records confidence and a safe
action, and publishes an auditable report to `GET /api/incidents`. It performs
safe diagnosis and recovery verification automatically. Rollbacks, restarts,
and other production-changing actions remain proposed until a human approves
them.

## Trace and log correlation

Every API request creates an OpenTelemetry span. The API accepts and continues
the W3C `traceparent` header, returns `X-Trace-ID`, and emits a JSON request
log containing the same `trace_id` and `span_id`. Logs contain only method,
route template, status, and latency; request bodies, full URLs, user IDs, and
credentials are excluded. Promtail stores the JSON logs in Loki, while OTLP
stores spans in Tempo. Grafana links logs to traces using the shared IDs.
