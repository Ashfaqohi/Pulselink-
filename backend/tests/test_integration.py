from fastapi.testclient import TestClient

from app.main import create_app


def test_url_lifecycle_and_database_persistence(tmp_path):
    db_path = str(tmp_path / "integration.db")
    first = TestClient(create_app(db_path))
    headers = {"X-User-ID": "integration-user"}
    created = first.post("/api/urls", headers=headers, json={"original_url": "https://example.org", "custom_alias": "launch"})
    assert created.status_code == 201
    assert first.get("/api/urls", headers=headers).json()[0]["short_code"] == "launch"
    assert first.delete(f"/api/urls/{created.json()['id']}", headers=headers).status_code == 204
    assert first.get("/launch", follow_redirects=False).status_code == 404

    second = TestClient(create_app(db_path))
    assert second.get("/api/urls", headers=headers).json()[0]["is_active"] is False


def test_health_readiness_and_metrics(tmp_path):
    test_client = TestClient(create_app(str(tmp_path / "ops.db")))
    assert test_client.get("/health").json() == {"status": "ok"}
    assert test_client.get("/ready").status_code == 200
    assert "redirect_requests_total" in test_client.get("/metrics").text
