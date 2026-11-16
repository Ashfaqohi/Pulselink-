from fastapi.testclient import TestClient

from app import app


def test_responder_rejects_malformed_alert():
    assert TestClient(app).post("/alerts", json={}).status_code == 422


def test_health():
    assert TestClient(app).get("/health").json() == {"status": "ok"}
