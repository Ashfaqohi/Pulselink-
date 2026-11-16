#!/usr/bin/env bash
set -Eeuo pipefail

: "${ECS_CLUSTER:?Set ECS_CLUSTER}"
: "${ECS_SERVICE:?Set ECS_SERVICE}"
: "${ROLLBACK_TASK_DEFINITION:?Set ROLLBACK_TASK_DEFINITION to a known-good revision}"

aws ecs update-service \
  --cluster "$ECS_CLUSTER" \
  --service "$ECS_SERVICE" \
  --task-definition "$ROLLBACK_TASK_DEFINITION" \
  --force-new-deployment
aws ecs wait services-stable --cluster "$ECS_CLUSTER" --services "$ECS_SERVICE"
echo "Rollback completed: $ROLLBACK_TASK_DEFINITION"
