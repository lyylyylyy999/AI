from fastapi.testclient import TestClient

from app.main import create_app


def test_app_starts_without_model_configuration(monkeypatch):
    for key in ("DEEPSEEK_API_KEY", "DEEPSEEK_MODEL", "DATABASE_URL"):
        monkeypatch.delenv(key, raising=False)
    with TestClient(create_app()) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        assert "/api/v1/datasets" not in client.get("/openapi.json").json()["paths"]
