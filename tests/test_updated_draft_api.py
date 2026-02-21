"""测试更新后的 Draft API 响应契约。"""

from fastapi.testclient import TestClient

from app.backend.api_main import app


client = TestClient(app)


def test_create_draft_success():
    response = client.post(
        "/api/draft/create",
        json={"draft_name": "测试草稿_success", "width": 1920, "height": 1080, "fps": 30},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 0
    assert "message" in body
    assert "data" in body
    assert "draft_id" in body["data"]


def test_create_draft_validation_error_is_200():
    response = client.post(
        "/api/draft/create",
        json={"draft_name": "测试草稿_error", "width": 1920, "height": 1080, "fps": 0},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 1400
    assert "message" in body


def test_response_structure():
    response = client.post(
        "/api/draft/create",
        json={"draft_name": "测试草稿_structure", "width": 1920, "height": 1080, "fps": 30},
    )

    assert response.status_code == 200
    body = response.json()
    assert set(["code", "message", "data"]).issubset(body.keys())
