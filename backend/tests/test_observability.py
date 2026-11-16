import json
import logging

from fastapi.testclient import TestClient

from app.main import create_app


def test_alertmanager_webhook_accepts_alerts(tmp_path):
    test_client = TestClient(create_app(str(tmp_path / "alerts.db")))
    response = test_client.post(
        "/internal/alerts/alertmanager",
        json={"status": "firing", "alerts": [{"labels": {"alertname": "RedirectFailureRateHigh"}}]},
    )
    assert response.status_code == 202
    assert response.json() == {"accepted": 1}


def test_requests_return_shared_trace_id_and_redacted_structured_log(tmp_path, caplog):
    logger = logging.getLogger("pulselink")
    logger.propagate = True
    caplog.set_level(logging.INFO, logger="pulselink")
    test_client = TestClient(create_app(str(tmp_path / "trace.db")))
    response = test_client.post(
        "/api/urls",
        headers={"X-User-ID": "customer-123"},
        json={"original_url": "https://private.example/customer-secret"},
    )
    assert response.status_code == 201
    trace_id = response.headers["x-trace-id"]
    assert len(trace_id) == 32
    event = next(record for record in caplog.records if record.getMessage() == "http_request")
    assert event.trace_id == trace_id
    assert event.span_id
    assert event.route == "/api/urls"
    assert "private.example" not in json.dumps(event.__dict__)
    assert "customer-123" not in json.dumps(event.__dict__)
    logger.propagate = False


def test_traceparent_is_continued(tmp_path):
    test_client = TestClient(create_app(str(tmp_path / "parent.db")))
    parent_trace_id = "0123456789abcdef0123456789abcdef"
    traceparent = f"00-{parent_trace_id}-0123456789abcdef-01"
    response = test_client.get("/health", headers={"traceparent": traceparent})
    assert response.headers["x-trace-id"] == parent_trace_id


def test_responder_report_is_auditable(tmp_path):
    test_client = TestClient(create_app(str(tmp_path / "reports.db")))
    report = {
        "incident_id": "inc-1",
        "evidence": {"health": {"status_code": 200}},
        "diagnosis": {"confidence": "medium", "recommended_action": "inspect"},
        "agent": "pulselink-responder",
        "action_status": "proposed",
    }
    accepted = test_client.post("/internal/responder/reports", json=report)
    assert accepted.status_code == 202
    incidents = test_client.get("/api/incidents", headers={"X-User-ID": "operator"})
    assert incidents.json()[0]["incident_id"] == "inc-1"
