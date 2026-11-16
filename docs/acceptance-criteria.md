# PulseLink acceptance criteria

This document is the Phase 1 gate for the PulseLink implementation. The
criteria are written as observable behaviors so they can be converted into
automated tests in later phases.

## URL creation and redirects

- A valid absolute HTTP(S) URL can be shortened by an authenticated user.
- Every generated short code is unique.
- Invalid URLs are rejected with a useful 4xx response.
- Custom aliases are validated and duplicate aliases are rejected.
- A short URL redirects to its active original destination.
- Disabled or deleted URLs do not redirect.
- Every redirect records its outcome and response latency.

## URL management and ownership

- An authenticated user can list only URLs they own.
- An owner can retrieve, inspect statistics for, and disable their own URL.
- An owner can delete or disable their own URL according to the API contract.
- A user cannot read, modify, or delete another user's URL.
- Click statistics are available for each owned URL.

## Reliability and security

- API endpoints return meaningful HTTP status codes and safe error messages.
- Database failures are handled gracefully without exposing internals.
- Passwords are stored only as secure hashes; plaintext passwords are never stored.
- Secrets come from environment or managed secret configuration and are not committed.
- `/health` reports process liveness.
- `/ready` reports required dependency readiness.
- Redirect metrics distinguish successful and failed outcomes.
- Prometheus labels remain bounded and do not contain full URLs, user IDs, or short codes.
- The redirect journey emits metrics, OpenTelemetry traces, and structured JSON logs
  correlated by a trace ID.
- Telemetry excludes request bodies, credentials, user IDs, and full customer URLs.
- Prometheus, Tempo, and Loki data is retained by the local observability stack and
  viewable through the provisioned Grafana dashboard.

## Incident response

- Redirect failure rate is measured continuously.
- An incident is created when failure rate exceeds 5%, at least 20 requests occur
  in the evaluation window, and the condition persists for five minutes.
- Alertmanager webhook payloads are authenticated and validated.
- Incident evidence includes metrics, relevant logs, health/readiness status, and
  recent deployment metadata when available.
- Responder output distinguishes evidence from hypotheses and includes a confidence
  level and recommended remediation.
- Production-changing actions, including rollback, require human approval.
- Incident actions and outcomes are auditable and idempotent where practical.

## Performance targets

These are targets to validate under a documented load test, not assumed results:

- Redirect p95 latency is below 300 ms.
- Redirect success rate is at least 99.5% under normal operating conditions.
- Metrics support calculation of redirect success rate, failure rate, p95/p99
  latency, degradation duration, and active incidents.

## Phase 1 exit gate

Phase 1 is complete when the problem statement, user journeys, acceptance criteria,
and measurable performance targets have been reviewed. Implementation proceeds next
to the database schema and API contract.
