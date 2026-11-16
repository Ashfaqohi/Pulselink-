from __future__ import annotations

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from logging import LogRecord
from pathlib import Path

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


LOGGER = logging.getLogger("pulselink")
_TRACER: trace.Tracer | None = None


class JsonFormatter(logging.Formatter):
    def format(self, record: LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "service": "pulselink-api",
            "trace_id": getattr(record, "trace_id", None),
            "span_id": getattr(record, "span_id", None),
        }
        for key in ("method", "route", "status_code", "duration_ms"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, separators=(",", ":"))


def configure_logging() -> None:
    if LOGGER.handlers:
        return
    LOGGER.setLevel(logging.INFO)
    formatter = JsonFormatter()
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    LOGGER.addHandler(stdout_handler)
    log_path = os.getenv("PULSELINK_LOG_PATH")
    if log_path:
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        LOGGER.addHandler(file_handler)
    LOGGER.propagate = False


def configure_tracing() -> trace.Tracer:
    global _TRACER
    if _TRACER is not None:
        return _TRACER
    provider = TracerProvider(resource=Resource.create({"service.name": "pulselink-api"}))
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if endpoint:
        provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(endpoint=f"{endpoint.rstrip('/')}/v1/traces")
            )
        )
    trace.set_tracer_provider(provider)
    _TRACER = trace.get_tracer("pulselink.http")
    return _TRACER


def trace_identifiers() -> tuple[str | None, str | None]:
    span = trace.get_current_span()
    context = span.get_span_context()
    if not context.is_valid:
        return None, None
    return f"{context.trace_id:032x}", f"{context.span_id:016x}"


def safe_route(path: str) -> str:
    if path == "/health":
        return "/health"
    if path == "/ready":
        return "/ready"
    if path == "/metrics":
        return "/metrics"
    if path.startswith("/api/urls/"):
        return "/api/urls/{id}"
    if path == "/api/urls":
        return "/api/urls"
    if path.startswith("/internal/alerts/"):
        return "/internal/alerts/{provider}"
    if path.startswith("/") and path.count("/") == 1:
        return "/{short_code}"
    return "/other"


def elapsed_ms(start: float) -> int:
    return max(0, round((time.perf_counter() - start) * 1000))
