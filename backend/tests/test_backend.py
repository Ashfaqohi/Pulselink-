from fastapi.testclient import TestClient

from app.main import create_app


def client(tmp_path):
    return TestClient(create_app(str(tmp_path / "test.db")))


def test_create_url_rejects_invalid_url(tmp_path):
    response = client(tmp_path).post("/api/urls", headers={"X-User-ID": "alice"}, json={"original_url": "not-a-url"})
    assert response.status_code == 422


def test_custom_alias_is_unique(tmp_path):
    test_client = client(tmp_path)
    payload = {"original_url": "https://example.com", "custom_alias": "docs"}
    assert test_client.post("/api/urls", headers={"X-User-ID": "alice"}, json=payload).status_code == 201
    duplicate = test_client.post("/api/urls", headers={"X-User-ID": "bob"}, json=payload)
    assert duplicate.status_code == 409


def test_ownership_is_enforced(tmp_path):
    test_client = client(tmp_path)
    created = test_client.post("/api/urls", headers={"X-User-ID": "alice"}, json={"original_url": "https://example.com"}).json()
    response = test_client.get(f"/api/urls/{created['id']}", headers={"X-User-ID": "bob"})
    assert response.status_code == 404


def test_redirect_records_click_and_stats(tmp_path):
    test_client = client(tmp_path)
    created = test_client.post("/api/urls", headers={"X-User-ID": "alice"}, json={"original_url": "https://example.com"}).json()
    redirected = test_client.get(f"/{created['short_code']}", follow_redirects=False)
    assert redirected.status_code == 302
    assert redirected.headers["location"] == "https://example.com"
    stats = test_client.get(f"/api/urls/{created['id']}/stats", headers={"X-User-ID": "alice"})
    assert stats.json()["total_clicks"] == 1
    assert stats.json()["successes"] == 1
