"""集成测试：验证 API 统一返回 code/message/data。"""

from fastapi.testclient import TestClient

from app.backend.api_main import app


client = TestClient(app)


def _assert_standard_body(body: dict):
    assert "code" in body
    assert "message" in body


def test_create_draft_success_format():
    response = client.post(
        "/api/draft/create",
        json={
            "draft_name": "format_test",
            "width": 1920,
            "height": 1080,
            "fps": 30,
        },
    )

    assert response.status_code == 200
    body = response.json()
    _assert_standard_body(body)
    assert body["code"] == 0
    assert "draft_id" in body["data"]


def test_create_draft_validation_error_format():
    response = client.post(
        "/api/draft/create",
        json={"draft_name": "invalid_test", "width": -100, "height": 1080, "fps": 30},
    )

    assert response.status_code == 200
    body = response.json()
    _assert_standard_body(body)
    assert body["code"] == 1400


def test_get_nonexistent_draft_format():
    response = client.get("/api/draft/nonexistent-id")
    assert response.status_code == 200
    body = response.json()
    _assert_standard_body(body)
    assert body["code"] != 0


def test_response_contains_required_fields():
    endpoints = ["/", "/api/version", "/api/draft/nonexistent/status"]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200
        body = response.json()
        _assert_standard_body(body)


def test_error_code_consistency():
    response = client.get("/api/draft/nonexistent/status")
    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 1001
