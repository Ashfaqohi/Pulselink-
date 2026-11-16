# PulseLink --- Production-Ready URL Shortener with an Incident Responder

> One application taken from specification to production: build it, test
> it, containerize it, deploy it, monitor real user impact, and
> implement an automated incident responder.

## 1. Project overview

**PulseLink** is a URL-shortening service with built-in reliability
monitoring and incident response.

Users can create short URLs, share them, and view click statistics. The
system monitors redirect success and latency. When users experience
degraded service, it triggers an incident, gathers diagnostic evidence,
and asks a responder agent to investigate and recommend recovery.

### Core user journey

1.  A user submits a long URL.
2.  The backend generates a unique short URL.
3.  A visitor opens the short URL.
4.  The backend redirects the visitor to the original URL.
5.  The application records the click and response outcome.
6.  Monitoring measures redirect success and latency.

### Incident journey

1.  Redirect failures increase.
2.  Monitoring detects sustained user-impacting degradation.
3.  An alert creates an incident.
4.  The responder gathers metrics, logs, health status, and deployment
    information.
5.  The responder identifies a likely cause and recommends remediation.
6.  A human approves production-changing actions such as rollback.
7.  Recovery is verified and the incident is recorded.

## 2. Technology stack

  Component               Technology
  ----------------------- ------------------------------------
  Frontend                React, TypeScript, Vite
  Styling                 Tailwind CSS
  Backend                 Python, FastAPI
  Database                PostgreSQL
  ORM and migrations      SQLAlchemy, Alembic
  Validation              Pydantic
  Backend tests           Pytest
  Frontend tests          Vitest, React Testing Library
  API integration tests   Pytest, HTTPX
  End-to-end tests        Playwright
  Containers              Docker, Docker Compose
  CI/CD                   GitHub Actions
  Container registry      Amazon ECR
  Deployment              AWS ECS Fargate
  Managed database        AWS RDS PostgreSQL
  Observability           OpenTelemetry, Prometheus, Grafana
  Alerting                Prometheus Alertmanager

Start with a deterministic, rules-based responder. An LLM can later be
added for log summarization and assisted root-cause analysis.

## 3. Problem statement

URL-shortening services must do more than generate links: they must
reliably redirect visitors. A service can appear healthy at the
infrastructure level while users experience broken redirects, HTTP 500
errors, slow responses, or failures introduced by a deployment.

PulseLink addresses this by combining URL management with user-impact
monitoring and controlled incident response.

## 4. Functional requirements

### 4.1 Frontend

Build these pages:

**Dashboard** - Total shortened URLs and clicks. - Redirect success and
failure counts. - Recent URL activity.

**Create URL** - Original URL input. - Optional custom alias. - Generate
and copy the short URL. - Show validation errors clearly.

**URL management** - List URLs owned by the user. - View original and
shortened URLs. - Delete or disable a URL. - View click statistics.

**Incident dashboard** - Active incidents and severity. - Affected
requests and observed errors. - Responder findings and
recommendations. - Incident and recovery history.

### 4.2 Backend API

  Method   Endpoint                        Purpose
  -------- ------------------------------- ------------------------------
  POST     `/api/urls`                     Create a shortened URL
  GET      `/api/urls`                     List the current user's URLs
  GET      `/api/urls/{id}`                Retrieve URL details
  DELETE   `/api/urls/{id}`                Delete or disable a URL
  GET      `/api/urls/{id}/stats`          Retrieve click statistics
  GET      `/health`                       Process liveness
  GET      `/ready`                        Dependency readiness
  GET      `/metrics`                      Prometheus metrics
  GET      `/api/incidents`                List incidents
  GET      `/api/incidents/{id}`           Retrieve incident details
  POST     `/api/incidents/{id}/resolve`   Resolve an incident

The redirect route is `GET /{short_code}` and returns an HTTP redirect
to the original destination.

### 4.3 Database schema

Use PostgreSQL and Alembic migrations.

**users** - `id` - `email` - `password_hash` - `created_at`

**urls** - `id` - `user_id` - `original_url` - `short_code` -
`created_at` - `is_active`

**click_events** - `id` - `url_id` - `clicked_at` - `response_status` -
`response_time_ms`

**incidents** - `id` - `title` - `severity` - `status` -
`trigger_reason` - `started_at` - `resolved_at`

**incident_actions** - `id` - `incident_id` - `action_type` -
`action_description` - `execution_status` - `created_at`

Add foreign keys, indexes, uniqueness constraints, and appropriate
retention policies. Store password hashes, never plaintext passwords.
Scope URL access to the authenticated owner.

## 5. Acceptance criteria

Write and review these criteria before implementation.

### URL creation and redirects

-   A valid URL can be shortened.
-   Every generated short code is unique.
-   Invalid URLs are rejected with a useful client error.
-   Duplicate custom aliases are rejected.
-   A short URL redirects to the correct destination.
-   Disabled or deleted URLs do not redirect.
-   Redirect outcomes and latency are recorded.

### URL management

-   An authenticated user can list only their own URLs.
-   A user can retrieve and disable their own URL.
-   A user cannot read, modify, or delete another user's URL.
-   Click statistics are available for each URL.

### Reliability and security

-   API endpoints return meaningful HTTP status codes.
-   Database failures are handled gracefully.
-   Sensitive exception details and secrets are not exposed.
-   `/health` reports process liveness.
-   `/ready` reports whether required dependencies are available.
-   Secrets are supplied through environment configuration, not
    committed to Git.

### Initial performance targets

-   Redirect p95 latency below 300 ms under a documented test load.
-   Redirect success rate at or above 99.5% under normal operating
    conditions.
-   Metrics distinguish successful redirects from failed redirects.

These are target values to validate under a defined load, not assumed
production results.

## 6. Testing strategy

Use a testing pyramid and run tests automatically in CI.

### 6.1 Backend unit tests

Test: - Short-code generation and collision handling. - URL
validation. - Custom alias validation. - Redirect business logic. -
Click-event recording. - Error handling.

### 6.2 Frontend tests

Test: - URL submission and form validation. - Loading and error
states. - Copy-to-clipboard behavior. - URL list rendering. - Dashboard
statistics. - Incident dashboard rendering.

### 6.3 Integration tests

Use a real PostgreSQL test service or an isolated test database.

Test: - API-to-database communication. - URL creation and retrieval. -
Redirect and click-event persistence. - Ownership and authorization
boundaries. - Database failure handling. - Incident creation and
resolution.

### 6.4 End-to-end tests

Use Playwright to simulate: 1. Open the application and authenticate. 2.
Create a shortened URL. 3. Copy and visit the short URL. 4. Verify the
redirect destination. 5. Verify click statistics. 6. Simulate a service
failure. 7. Verify that an incident appears.

## 7. Containerization

Create separate Dockerfiles for the frontend, backend, and responder.
Use Docker Compose to run:

-   Frontend.
-   Backend API.
-   Responder service.
-   PostgreSQL.
-   Prometheus.
-   Grafana.
-   Alertmanager.

Start the local environment with:

``` bash
docker compose up --build
```

Document database migrations and seed data. Persist PostgreSQL data
using a Docker volume. Provide health checks and avoid running
production containers as root where practical.

## 8. CI/CD

Use GitHub Actions.

### Continuous integration

On every pull request: 1. Install dependencies. 2. Run backend unit
tests. 3. Run frontend tests. 4. Run integration tests. 5. Run linting
and type checks. 6. Build the frontend. 7. Build backend and responder
images.

Only passing changes should be eligible for merge.

### Continuous deployment

On merge to `main`: 1. Build production images. 2. Tag images with the
Git commit SHA. 3. Push images to Amazon ECR. 4. Deploy to AWS ECS
Fargate. 5. Run health and smoke checks. 6. Mark deployment successful
or initiate rollback.

### Rollback strategy

-   Retain the last known-good image and ECS task definition.
-   If deployment health checks fail, stop or revert the deployment.
-   Restore the previous task definition/image.
-   Verify readiness and a synthetic redirect.
-   Record the rollback event.

Do not delete previous images immediately. Use least-privilege IAM roles
and protect production deployment credentials.

## 9. Observability: measure user impact

Do not rely only on CPU, memory, or server uptime. Instrument the user
journey.

### Metrics

  Metric                          Meaning
  ------------------------------- ---------------------------------------
  `redirect_requests_total`       Redirect requests, labeled by outcome
  `redirect_failures_total`       Failed redirect requests
  `redirect_latency_seconds`      Redirect response latency histogram
  `url_creation_failures_total`   Failed URL creation requests
  `database_errors_total`         Database-related errors
  `active_incidents`              Current active incidents

Use bounded labels such as `status` and `route`. Never use full URLs,
user IDs, or short codes as Prometheus labels; high-cardinality labels
can damage monitoring performance.

### User-impact indicators

Track: - Redirect failure percentage. - Number of failed redirect
requests. - p95 and p99 redirect latency. - Duration of degradation. -
Affected users, only where reliably measurable and privacy-safe.

Create Grafana panels for: 1. Redirect success rate. 2. Redirect failure
rate. 3. p95 redirect latency. 4. URL creation success rate. 5. Active
incidents. 6. Recent deployment events.

Use structured logs with request IDs so a failed request can be traced
across services.

## 10. Alert trigger

Create a primary Prometheus alert named `HighRedirectFailureRate`.

**Trigger condition** - Redirect failure rate exceeds 5%. - At least 20
redirect requests were observed in the evaluation window. - The
condition persists for five minutes.

Example PromQL expression:

``` promql
(
  sum(rate(redirect_requests_total{status="error"}[5m]))
  /
  clamp_min(sum(rate(redirect_requests_total[5m])), 0.000001)
) > 0.05
and
sum(increase(redirect_requests_total[5m])) >= 20
```

Configure `for: 5m` in the Prometheus alert rule. Ensure the metric
labels and outcome values match the application's instrumentation.

When the alert fires: 1. Alertmanager sends a webhook to the incident
intake endpoint. 2. The backend creates or updates an incident. 3. The
system captures relevant metrics and timestamps. 4. The responder is
notified. 5. The incident and alert state are recorded.

Also implement a synthetic redirect check. A traffic-based ratio cannot
detect every outage when request volume is low or zero.

## 11. Incident responder agent

Build a Python responder service that receives incident events, gathers
evidence, applies diagnostic rules, and recommends remediation.

### Workflow

**Step 1 --- Receive alert**

Receive the Alertmanager webhook and validate its payload and
authenticity.

**Step 2 --- Collect evidence**

Gather: - Redirect failure rate. - Redirect latency. - Database error
metrics. - Relevant application logs. - Health and readiness status. -
Recent deployment metadata.

**Step 3 --- Diagnose**

Start with transparent, deterministic rules:

  -----------------------------------------------------------------------
  Observation                         Possible diagnosis
  ----------------------------------- -----------------------------------
  Database errors rise with redirect  Database connectivity or
  failures                            availability

  Failures begin immediately after    Possible deployment regression
  deployment                          

  Latency rises while database        Application or dependency
  metrics remain normal               performance issue

  Readiness check fails               Service or dependency unavailable
  -----------------------------------------------------------------------

The agent must distinguish evidence from hypotheses. It should report a
likely cause, not claim certainty without proof.

**Step 4 --- Recommend**

Produce a structured report containing: - Incident ID and severity. -
User impact and time window. - Observed symptoms. - Probable cause and
confidence. - Supporting evidence. - Recommended remediation.

**Step 5 --- Recover**

For the first release: - Collect evidence automatically. - Generate
recommendations. - Require human approval for rollback.

For a later release: - Permit rollback through a narrowly scoped
deployment interface. - Verify recovery using health checks and redirect
success metrics. - Record the action and outcome.

### Agent safety requirements

-   No unrestricted shell execution.
-   No direct database modification.
-   No unrestricted AWS credentials.
-   Use least-privilege IAM permissions.
-   Require approval for production-changing actions.
-   Make actions idempotent where possible.
-   Maintain an auditable record of agent decisions and actions.
-   Protect webhook endpoints and validate incoming events.

## 12. Deployment architecture

``` text
                       Users
                         |
                         v
                  React Frontend
                         |
                         v
                   FastAPI API
                    /       \
                   v         v
              PostgreSQL   Redirect API
                   |         |
                   v         v
               Click Events and Metrics
                         |
                         v
                   OpenTelemetry
                         |
                         v
                     Prometheus
                         |
                         v
                      Grafana
                         |
                    Alertmanager
                         |
                         v
                 Incident Responder
                         |
                         v
                Diagnosis / Approval
                         |
                         v
                 Controlled Rollback
```

### Production infrastructure

-   AWS ECS Fargate: application containers.
-   Amazon ECR: container image registry.
-   Amazon RDS: PostgreSQL.
-   GitHub Actions: CI/CD.
-   OpenTelemetry: instrumentation and telemetry export.
-   Prometheus: metrics and alert evaluation.
-   Grafana: dashboards.
-   Alertmanager: alert routing.

Keep development and production environments separate. Store production
secrets in an appropriate secrets manager and use secure network access
to the database.

## 13. Suggested repository structure

``` text
pulselink/
├── frontend/
│   ├── src/
│   ├── tests/
│   ├── Dockerfile
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── database/
│   │   └── main.py
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   ├── Dockerfile
│   └── requirements.txt
├── responder/
│   ├── agent/
│   ├── diagnostics/
│   ├── remediation/
│   ├── tests/
│   └── Dockerfile
├── monitoring/
│   ├── prometheus.yml
│   ├── alert_rules.yml
│   ├── alertmanager.yml
│   └── grafana/
├── infrastructure/
│   ├── docker-compose.yml
│   └── aws/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
├── docs/
│   ├── architecture.md
│   ├── api.md
│   └── incident-response.md
├── README.md
└── .gitignore
```

## 14. Development milestones

Complete the project in this order. Do not move forward until the
current phase meets its acceptance criteria.

  Phase   Deliverable
  ------- ---------------------------------------------
  1       Problem definition and acceptance criteria
  2       Database schema and API contract
  3       FastAPI backend
  4       React frontend
  5       Unit, frontend, and integration tests
  6       Docker and Docker Compose
  7       GitHub Actions CI
  8       AWS deployment and CD
  9       Observability dashboards
  10      Alert trigger and incident creation
  11      Incident responder
  12      Approved rollback and recovery verification

## 15. Definition of done

-   [ ] Users can create and manage shortened URLs.
-   [ ] Redirects work correctly.
-   [ ] Click statistics are stored in PostgreSQL.
-   [ ] Frontend and backend are integrated.
-   [ ] Backend unit tests pass.
-   [ ] Frontend tests pass.
-   [ ] Integration tests pass.
-   [ ] End-to-end tests pass.
-   [ ] Application runs through Docker Compose.
-   [ ] CI runs automatically on pull requests.
-   [ ] Application is deployed to AWS.
-   [ ] CD deploys new versions.
-   [ ] Previous versions can be restored.
-   [ ] Grafana displays user-impact metrics.
-   [ ] Alert triggers under the defined failure condition.
-   [ ] Incident responder receives and investigates alerts.
-   [ ] Responder produces a diagnosis and recommendation.
-   [ ] Approved rollback can be executed and verified.
-   [ ] Incident history and agent actions are auditable.

## 16. Production-readiness exercises

After deployment, deliberately introduce these failures in a safe test
environment.

### Scenario A --- Database failure

Stop or isolate the PostgreSQL test service.

Expected result: - URL creation and redirects fail gracefully. -
Database errors are recorded. - An incident is generated when alert
conditions are met. - The responder identifies database connectivity as
a likely cause.

### Scenario B --- Deployment regression

Deploy a test version that intentionally introduces redirect failures.

Expected result: - Redirect success rate decreases. - Monitoring
triggers an alert. - The responder identifies the recent deployment as a
possible cause. - A human approves rollback. - The previous deployment
is restored and verified.

### Scenario C --- Increased redirect latency

Introduce an artificial delay in the redirect service.

Expected result: - p95 latency increases. - The dashboard reflects user
degradation. - The responder identifies the latency problem. - The
incident remains open until recovery is verified.

Run failure exercises only in an isolated environment or during an
explicitly approved test window.

## 17. Final engineering principle

Build it like a real production service. Break it deliberately, observe
its failures, investigate the evidence, and engineer its recovery.

The objective is not merely to demonstrate that PulseLink runs on a
developer's machine. The objective is to demonstrate that it can detect,
diagnose, and recover safely from realistic production failures.
