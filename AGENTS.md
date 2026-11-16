# Agent instructions

This repository uses modular project guidance. Read the relevant documents
before changing the system:

- [Agent team and operating process](docs/agent-team.md) — roles, ownership,
  handoffs, review gates, and escalation.
- [Task tracker](docs/task-tracker.md) — task status, acceptance criteria,
  dependencies, and evidence.
- [Agent activity log](docs/agent-activity.md) — required durable record for
  consulted, changed, and verified tasks.
- [Local development](docs/local-development.md) — service startup and tests.
- [Deployment and observability](docs/deployment.md) — containers, CI/CD,
  rollback, and user-impact alerts.

## Required process

For every change, identify the tracker task, preserve the acceptance criteria,
run the relevant verification commands, and update the tracker and activity
log with repository evidence. Never claim a test, deployment, or public URL
that was not actually verified.
