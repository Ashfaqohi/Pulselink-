# PulseLink database schema

The production database is PostgreSQL. All timestamps are stored as UTC
timezone-aware values.

## Tables

### users

| Column | Type | Constraints |
|---|---|---|
| id | UUID | primary key, generated |
| email | VARCHAR(320) | not null, unique |
| password_hash | TEXT | not null |
| created_at | TIMESTAMPTZ | not null, default now() |

### urls

| Column | Type | Constraints |
|---|---|---|
| id | UUID | primary key, generated |
| user_id | UUID | not null, FK users(id) |
| original_url | TEXT | not null |
| short_code | VARCHAR(32) | not null, unique |
| created_at | TIMESTAMPTZ | not null, default now() |
| is_active | BOOLEAN | not null, default true |

Indexes: `urls(user_id, created_at DESC)` and the unique index on
`short_code`.

### click_events

| Column | Type | Constraints |
|---|---|---|
| id | BIGINT | primary key, generated |
| url_id | UUID | not null, FK urls(id) |
| clicked_at | TIMESTAMPTZ | not null, default now() |
| response_status | SMALLINT | not null |
| response_time_ms | INTEGER | not null, non-negative |

Indexes: `click_events(url_id, clicked_at DESC)` and
`click_events(clicked_at)` for retention and metrics queries.

### incidents

| Column | Type | Constraints |
|---|---|---|
| id | UUID | primary key, generated |
| title | VARCHAR(255) | not null |
| severity | VARCHAR(16) | not null, constrained to info/warning/critical |
| status | VARCHAR(16) | not null, constrained to open/investigating/resolved |
| trigger_reason | TEXT | not null |
| started_at | TIMESTAMPTZ | not null |
| resolved_at | TIMESTAMPTZ | nullable |

Index `incidents(status, started_at DESC)` supports the incident dashboard.

### incident_actions

| Column | Type | Constraints |
|---|---|---|
| id | UUID | primary key, generated |
| incident_id | UUID | not null, FK incidents(id) |
| action_type | VARCHAR(64) | not null |
| action_description | TEXT | not null |
| execution_status | VARCHAR(16) | not null, constrained to proposed/approved/executed/rejected/failed |
| created_at | TIMESTAMPTZ | not null, default now() |

Index `incident_actions(incident_id, created_at)` supports the audit trail.

## Integrity and retention

- Foreign keys use restrictive deletion for users and incidents; URL click events
  may be removed with a URL only through an explicit service operation.
- URL aliases are unique case-insensitively; the service normalizes aliases before
  persistence.
- Click events are retained for the documented operational retention period and
  removed by a scheduled maintenance job.
- Secrets and password material never appear in this schema or in logs.
