# PulseLink agent team and operating process

This document defines the agents responsible for delivering and operating
PulseLink. Agents work from the public task tracker and must leave durable
repository evidence for completed work.

## Team

| Agent | Primary ownership | Responsibilities | Required handoff |
|---|---|---|---|
| Product and planning agent | Scope and sequencing | Break the specification into tasks, clarify acceptance criteria, maintain priorities, and identify dependencies | Assigns implementation tasks with acceptance criteria and dependencies recorded in `docs/task-tracker.md` |
| Backend and data agent | FastAPI and PostgreSQL | Implement URL, redirect, ownership, statistics, health/readiness, metrics, migrations, and API behavior | Provides API/schema notes and passing backend tests to the integration agent |
| Frontend agent | React application | Implement dashboard, URL creation/management, statistics, and incident views; handle loading and error states | Provides UI behavior notes and passing frontend tests to the integration agent |
| Reliability and responder agent | Observability and incident response | Implement metrics, alerts, evidence collection, diagnostic rules, recommendations, recovery verification, and audit records | Provides incident scenarios, responder findings, and operational runbooks |
| Quality and release agent | Verification and delivery | Run unit, integration, end-to-end, security, performance, container, and CI checks; review release readiness | Reports failures with reproduction evidence and approves only when gates pass |

One agent may perform more than one role in a small change, but the change
must still identify each role performed and satisfy the same review gates.

## Work lifecycle

1. The product and planning agent creates or updates one tracker row per
   deliverable. Each row names an owner, dependencies, acceptance criteria,
   and expected evidence.
2. The owning implementation agent reviews the relevant specification,
   acceptance criteria, schema, and API contract before changing code.
3. The owner implements the smallest coherent change and adds or updates
   automated tests. Cross-cutting changes must identify affected agents in
   the task notes.
4. The owner updates the tracker and records an entry in
   `docs/agent-activity.md`, linking to the changed files and test output.
5. The quality and release agent verifies the acceptance criteria and runs
   the checks appropriate to the change. A failed check returns to the owner
   with a reproducible failure and evidence.
6. The change is complete only when the acceptance criteria pass, evidence is
   linked, and the tracker status is updated in the same change.

## Coordination and handoffs

- The task tracker is the source of truth for status, ownership, dependencies,
  and evidence; chat or local notes do not replace it.
- Handoffs must state: current status, work completed, remaining work,
  affected interfaces, known risks, and the exact verification command or
  artifact.
- API, schema, metric, and event changes require the owning agents to review
  compatibility before implementation is marked complete.
- Shared files are changed in one coordinated task where possible. If two
  agents need the same file, the planning agent establishes the order and
  the later agent rebases or reconciles deliberately rather than overwriting
  the earlier work.
- The quality and release agent is independent of the implementation owner
  for release approval whenever staffing permits.

## Incident-response collaboration

The reliability and responder agent owns automated evidence collection and
diagnosis. It may propose remediation but cannot perform production-changing
actions on its own. The human operator approves rollback or other production
changes. The backend/deployment owner executes the approved action, while
the reliability agent verifies recovery using health, readiness, redirect
success, and latency signals. The quality and release agent records the
final outcome and ensures the incident and action history are auditable.

For every incident, the handoff must distinguish evidence, hypotheses,
confidence, recommended action, approval status, execution result, and
recovery evidence.

## Decision and escalation rules

- Acceptance-criteria conflicts are escalated to the product and planning
  agent; security or data-integrity concerns take precedence over schedule.
- API or schema conflicts are resolved jointly by the backend/data and
  frontend agents, with the contract documented before implementation
  continues.
- Failed tests, unsafe changes, missing evidence, or unverifiable claims
  block release until corrected or explicitly accepted by a human owner.
- Production incidents and production-changing actions always require a
  human decision and an auditable record.
- Agents must not hide failures, claim tests they did not run, expose secrets,
  or use unrestricted shell, database, or cloud access.

## Required task evidence

Each completed task must include:

- the task ID and responsible agent;
- links to implementation, contract, or documentation changes;
- tests or verification commands and their results;
- unresolved risks or follow-up tasks;
- a corresponding entry in `docs/agent-activity.md`.

