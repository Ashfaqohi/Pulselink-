# PulseLink API contract

Unless noted otherwise, JSON responses use `Content-Type: application/json`,
errors use the shape `{ "detail": "safe human-readable message" }`, and
authenticated endpoints require the current user's authentication context.

## URL endpoints

### `POST /api/urls`

Request:

```json
{ "original_url": "https://example.com/article", "custom_alias": "article" }
```

`custom_alias` is optional. Response `201`:

```json
{
  "id": "uuid",
  "original_url": "https://example.com/article",
  "short_code": "article",
  "short_url": "https://short.example/article",
  "created_at": "2026-01-01T00:00:00Z",
  "is_active": true
}
```

Invalid URLs return `422`; duplicate aliases return `409`.

### `GET /api/urls`

Returns `200` with an array of URLs owned by the current user. It never returns
another user's URLs.

### `GET /api/urls/{id}`

Returns `200` with URL details, or `404` when the URL is missing or not owned by
the current user.

### `DELETE /api/urls/{id}`

Disables the URL and prevents future redirects. Returns `204`, or `404` when the
URL is missing or not owned by the current user. The operation is idempotent.

### `GET /api/urls/{id}/stats`

Returns `200` with click totals, success/failure counts, and latency summary for
an owned URL. Returns `404` for a missing or unauthorized URL.

## Redirect and operations endpoints

- `GET /{short_code}`: returns `302` to an active destination; inactive or unknown
  codes return `404`. The request outcome and latency are recorded.
- `GET /health`: process liveness; returns `200` when the process is running.
- `GET /ready`: dependency readiness; returns `200` when required dependencies are
  available, otherwise `503`.
- `GET /metrics`: Prometheus exposition format.

## Incident endpoints

- `GET /api/incidents`: list incidents, newest first.
- `GET /api/incidents/{id}`: retrieve incident details, evidence, findings, and
  action history.
- `POST /api/incidents/{id}/resolve`: resolve an incident after recovery checks;
  returns `409` if it is already resolved.
- `POST /internal/alerts/alertmanager`: authenticated Alertmanager intake endpoint;
  validates the alert and creates or updates an incident.

## Security rules

- Authentication and authorization are enforced before URL data is returned.
- Error responses do not expose SQL, stack traces, secrets, or internal URLs.
- Redirect destinations are validated as HTTP(S) URLs.
- Alert intake requires a configured shared secret or equivalent request
  authentication and rejects malformed payloads.
