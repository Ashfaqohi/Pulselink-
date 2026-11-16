from __future__ import annotations

import os
import re
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated
from urllib.parse import urlparse

from opentelemetry import propagate
from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from .database import connect, initialize
from .observability import configure_logging, configure_tracing, elapsed_ms, safe_route, trace_identifiers, LOGGER


DB_PATH = os.getenv("PULSELINK_DB_PATH", str(Path(__file__).resolve().parents[1] / "pulselink.db"))
ALIAS_PATTERN = re.compile(r"^[A-Za-z0-9_-]{3,32}$")


class Metrics:
    def __init__(self) -> None:
        self.redirect_total = {"success": 0, "failure": 0}
        self.redirect_latency_ms: list[int] = []

    def observe_redirect(self, outcome: str, latency_ms: int) -> None:
        self.redirect_total[outcome] += 1
        self.redirect_latency_ms.append(latency_ms)
        self.redirect_latency_ms = self.redirect_latency_ms[-10_000:]

    def exposition(self) -> str:
        lines = [
            "# HELP redirect_requests_total Redirect requests by user-visible outcome",
            "# TYPE redirect_requests_total counter",
        ]
        for outcome, value in self.redirect_total.items():
            lines.append(f'redirect_requests_total{{outcome="{outcome}"}} {value}')
        lines += [
            "# HELP redirect_request_duration_seconds Redirect latency in seconds",
            "# TYPE redirect_request_duration_seconds summary",
        ]
        if self.redirect_latency_ms:
            ordered = sorted(self.redirect_latency_ms)
            p95 = ordered[min(len(ordered) - 1, round(len(ordered) * 0.95))] / 1000
            lines.append(f'redirect_request_duration_seconds{{quantile="0.95"}} {p95:.6f}')
            lines.append(f'redirect_request_duration_seconds_sum {sum(ordered) / 1000:.6f}')
            lines.append(f'redirect_request_duration_seconds_count {len(ordered)}')
        else:
            lines += [
                'redirect_request_duration_seconds{quantile="0.95"} 0',
                "redirect_request_duration_seconds_sum 0",
                "redirect_request_duration_seconds_count 0",
            ]
        return "\n".join(lines) + "\n"


class CreateURL(BaseModel):
    original_url: str = Field(min_length=1, max_length=2048)
    custom_alias: str | None = Field(default=None, max_length=32)

    @field_validator("original_url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("original_url must be an absolute HTTP(S) URL")
        return value

    @field_validator("custom_alias")
    @classmethod
    def validate_alias(cls, value: str | None) -> str | None:
        if value is not None and not ALIAS_PATTERN.fullmatch(value):
            raise ValueError("custom_alias must be 3-32 letters, numbers, hyphens, or underscores")
        return value


class URLResponse(BaseModel):
    id: str
    original_url: str
    short_code: str
    short_url: str
    created_at: str
    is_active: bool


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_app(db_path: str = DB_PATH) -> FastAPI:
    initialize(db_path)
    configure_logging()
    tracer = configure_tracing()
    app = FastAPI(title="PulseLink API", version="1.0.0")
    app.state.db_path = db_path
    app.state.metrics = Metrics()
    app.state.alerts: list[dict[str, object]] = []
    app.state.responder_reports: list[dict[str, object]] = []
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def trace_request(request: Request, call_next):
        route = safe_route(request.url.path)
        started = time.perf_counter()
        parent_context = propagate.extract(dict(request.headers))
        with tracer.start_as_current_span(
            f"HTTP {request.method} {route}",
            attributes={"http.request.method": request.method, "url.route": route},
            context=parent_context,
        ) as span:
            try:
                response = await call_next(request)
            except Exception as exc:
                span.record_exception(exc)
                raise
            duration = elapsed_ms(started)
            span.set_attribute("http.response.status_code", response.status_code)
            trace_id, span_id = trace_identifiers()
            if trace_id:
                response.headers["X-Trace-ID"] = trace_id
            LOGGER.info(
                "http_request",
                extra={
                    "trace_id": trace_id,
                    "span_id": span_id,
                    "method": request.method,
                    "route": route,
                    "status_code": response.status_code,
                    "duration_ms": duration,
                },
            )
            return response

    def db() -> sqlite3.Connection:
        return connect(app.state.db_path)

    def current_user(x_user_id: Annotated[str | None, Header()] = None) -> str:
        if not x_user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        return x_user_id

    def ensure_user(connection: sqlite3.Connection, user_id: str) -> None:
        connection.execute(
            "INSERT OR IGNORE INTO users (id, email) VALUES (?, ?)",
            (user_id, f"{user_id}@local.pulselink"),
        )

    def as_response(row: sqlite3.Row, request: Request) -> URLResponse:
        return URLResponse(
            id=row["id"],
            original_url=row["original_url"],
            short_code=row["short_code"],
            short_url=f"{str(request.base_url).rstrip('/')}/{row['short_code']}",
            created_at=row["created_at"],
            is_active=bool(row["is_active"]),
        )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    def ready() -> dict[str, str]:
        try:
            connection = db()
            connection.execute("SELECT 1")
            connection.close()
            return {"status": "ready"}
        except sqlite3.Error as exc:
            raise HTTPException(status_code=503, detail="Database unavailable") from exc

    @app.get("/metrics")
    def metrics() -> Response:
        connection = db()
        try:
            total = connection.execute("SELECT COUNT(*) FROM click_events").fetchone()[0]
            successes = connection.execute(
                "SELECT COUNT(*) FROM click_events WHERE response_status BETWEEN 300 AND 399"
            ).fetchone()[0]
        finally:
            connection.close()
        body = app.state.metrics.exposition()
        body += f'redirect_requests_persisted_total{{outcome="all"}} {total}\n'
        body += f'redirect_requests_persisted_total{{outcome="success"}} {successes}\n'
        return Response(content=body, media_type="text/plain")

    @app.post("/internal/alerts/alertmanager", status_code=status.HTTP_202_ACCEPTED)
    async def alertmanager_webhook(request: Request) -> dict[str, object]:
        expected_secret = os.getenv("ALERTMANAGER_SHARED_SECRET")
        if expected_secret and request.headers.get("x-alertmanager-secret") != expected_secret:
            raise HTTPException(status_code=401, detail="Invalid alert authentication")
        try:
            payload = await request.json()
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Malformed alert payload") from exc
        alerts = payload.get("alerts") if isinstance(payload, dict) else None
        if not isinstance(alerts, list):
            raise HTTPException(status_code=422, detail="Alert payload must contain alerts")
        for alert in alerts:
            if isinstance(alert, dict):
                app.state.alerts.append({
                    "status": payload.get("status", "firing"),
                    "labels": alert.get("labels", {}),
                    "annotations": alert.get("annotations", {}),
                    "received_at": now(),
                })
        app.state.alerts[:] = app.state.alerts[-100:]
        return {"accepted": len(alerts)}

    @app.post("/internal/responder/reports", status_code=status.HTTP_202_ACCEPTED)
    async def responder_report(request: Request) -> dict[str, object]:
        expected_secret = os.getenv("RESPONDER_SHARED_SECRET")
        if expected_secret and request.headers.get("x-responder-secret") != expected_secret:
            raise HTTPException(status_code=401, detail="Invalid responder authentication")
        report = await request.json()
        required = {"incident_id", "evidence", "diagnosis", "agent", "action_status"}
        if not isinstance(report, dict) or not required.issubset(report):
            raise HTTPException(status_code=422, detail="Incomplete responder report")
        app.state.responder_reports.append(report)
        app.state.responder_reports[:] = app.state.responder_reports[-100:]
        return {"accepted": True, "incident_id": report["incident_id"]}

    @app.get("/api/incidents")
    def incidents(user_id: str = Depends(current_user)) -> list[dict[str, object]]:
        return list(reversed(app.state.responder_reports))

    @app.post("/api/urls", response_model=URLResponse, status_code=status.HTTP_201_CREATED)
    def create_url(payload: CreateURL, request: Request, user_id: str = Depends(current_user)) -> URLResponse:
        connection = db()
        try:
            ensure_user(connection, user_id)
            short_code = payload.custom_alias or uuid.uuid4().hex[:8]
            if not payload.custom_alias:
                while connection.execute("SELECT 1 FROM urls WHERE short_code = ?", (short_code,)).fetchone():
                    short_code = uuid.uuid4().hex[:8]
            try:
                url_id = str(uuid.uuid4())
                created_at = now()
                connection.execute(
                    "INSERT INTO urls (id, user_id, original_url, short_code, created_at) VALUES (?, ?, ?, ?, ?)",
                    (url_id, user_id, payload.original_url, short_code, created_at),
                )
                connection.commit()
            except sqlite3.IntegrityError as exc:
                raise HTTPException(status_code=409, detail="Short alias already exists") from exc
            row = connection.execute("SELECT * FROM urls WHERE id = ?", (url_id,)).fetchone()
            return as_response(row, request)
        finally:
            connection.close()

    @app.get("/api/urls", response_model=list[URLResponse])
    def list_urls(request: Request, user_id: str = Depends(current_user)) -> list[URLResponse]:
        connection = db()
        try:
            rows = connection.execute(
                "SELECT * FROM urls WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
            ).fetchall()
            return [as_response(row, request) for row in rows]
        finally:
            connection.close()

    def owned_url(connection: sqlite3.Connection, url_id: str, user_id: str) -> sqlite3.Row:
        row = connection.execute(
            "SELECT * FROM urls WHERE id = ? AND user_id = ?", (url_id, user_id)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="URL not found")
        return row

    @app.get("/api/urls/{url_id}", response_model=URLResponse)
    def get_url(url_id: str, request: Request, user_id: str = Depends(current_user)) -> URLResponse:
        connection = db()
        try:
            return as_response(owned_url(connection, url_id, user_id), request)
        finally:
            connection.close()

    @app.delete("/api/urls/{url_id}", status_code=status.HTTP_204_NO_CONTENT)
    def disable_url(url_id: str, user_id: str = Depends(current_user)) -> Response:
        connection = db()
        try:
            owned_url(connection, url_id, user_id)
            connection.execute("UPDATE urls SET is_active = 0 WHERE id = ?", (url_id,))
            connection.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        finally:
            connection.close()

    @app.get("/api/urls/{url_id}/stats")
    def stats(url_id: str, user_id: str = Depends(current_user)) -> dict[str, int]:
        connection = db()
        try:
            owned_url(connection, url_id, user_id)
            row = connection.execute(
                "SELECT COUNT(*) AS total, SUM(CASE WHEN response_status BETWEEN 300 AND 399 THEN 1 ELSE 0 END) AS successes, "
                "SUM(CASE WHEN response_status >= 400 THEN 1 ELSE 0 END) AS failures, "
                "COALESCE(ROUND(AVG(response_time_ms)), 0) AS avg_latency_ms FROM click_events WHERE url_id = ?",
                (url_id,),
            ).fetchone()
            return {"total_clicks": row["total"], "successes": row["successes"] or 0, "failures": row["failures"] or 0, "avg_latency_ms": row["avg_latency_ms"]}
        finally:
            connection.close()

    @app.get("/{short_code}")
    def redirect(short_code: str, request: Request) -> Response:
        started = time.perf_counter()
        connection = db()
        try:
            row = connection.execute("SELECT * FROM urls WHERE short_code = ?", (short_code,)).fetchone()
            response_status = 302 if row and row["is_active"] else 404
            if row and row["is_active"]:
                response = Response(status_code=302, headers={"location": row["original_url"]})
            else:
                response = Response(status_code=404, content="Short URL not found")
            elapsed_ms = max(0, round((time.perf_counter() - started) * 1000))
            app.state.metrics.observe_redirect("success" if response_status == 302 else "failure", elapsed_ms)
            if row:
                connection.execute(
                    "INSERT INTO click_events (url_id, clicked_at, response_status, response_time_ms) VALUES (?, ?, ?, ?)",
                    (row["id"], now(), response_status, elapsed_ms),
                )
                connection.commit()
            return response
        finally:
            connection.close()

    return app


app = create_app()
