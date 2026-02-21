"""测试 effect/filter 端点与统一响应格式。"""

from fastapi.testclient import TestClient

from app.backend.api_main import app


client = TestClient(app)


def test_effect_filter_routes_registered():
    routes = [getattr(route, "path", None) for route in app.routes]
    assert "/api/segment/effect/create" in routes
    assert "/api/segment/filter/create" in routes


def test_create_effect_segment_invalid_type_returns_standard_error():
    response = client.post(
        "/api/segment/effect/create",
        json={
            "effect_type": "VideoSceneEffectType.XXX",
            "target_timerange": {"start": 0, "duration": 5000000},
            "params": [50.0, 75.0],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert "code" in body
    assert "message" in body
    assert body["code"] != 0


def test_create_filter_segment_invalid_intensity_returns_1400():
    response = client.post(
        "/api/segment/filter/create",
        json={
            "filter_type": "FilterType.XXX",
            "target_timerange": {"start": 0, "duration": 5000000},
            "intensity": 150.0,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["code"] == 1400
    assert "message" in body


def test_get_nonexistent_effect_detail_returns_standard_error():
    response = client.get("/api/segment/effect/not-exists")

    assert response.status_code == 200
    body = response.json()
    assert "code" in body
    assert "message" in body
    assert body["code"] != 0
