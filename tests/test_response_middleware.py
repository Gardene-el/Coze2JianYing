"""测试统一响应中间件基础契约。"""

from fastapi.testclient import TestClient

from app.backend.api_main import app


client = TestClient(app)


def test_success_payload_wrapped():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert "message" in body
    assert isinstance(body.get("data"), dict)


def test_validation_error_is_http_200():
    response = client.post(
        "/api/draft/create",
        json={"draft_name": "x", "width": 0, "height": 1080, "fps": 30},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 1400
    assert "message" in body


def test_not_found_error_shape():
    response = client.get("/api/draft/not-exists/status")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 1001
    assert "message" in body
