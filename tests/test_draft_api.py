"""测试草稿 API（新响应契约）。"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from app.backend.api_main import app

# 创建测试客户端
client = TestClient(app)


def _assert_success_body(body: dict) -> dict:
    assert body.get("code") == 0
    assert "message" in body
    assert "data" in body
    return body["data"]


def test_root_endpoint():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    data = _assert_success_body(response.json())
    assert "message" in data


def test_draft_create_endpoint():
    """测试草稿创建端点"""
    response = client.post(
        "/api/draft/create",
        json={"draft_name": "api_test", "width": 1920, "height": 1080, "fps": 30},
    )
    assert response.status_code == 200
    data = _assert_success_body(response.json())
    assert "draft_id" in data


def test_create_draft_invalid_payload():
    """参数校验错误也应返回 HTTP 200 + 失败结构。"""
    response = client.post(
        "/api/draft/create",
        json={
            "draft_name": "bad",
            "width": "invalid_width",
            "height": 1080,
            "fps": 30,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body.get("code") == 1400
    assert "message" in body


def test_draft_status_not_found():
    """查询不存在草稿应返回中间件映射错误码。"""
    response = client.get(
        "/api/draft/not-exists/status",
        headers={"Accept-Language": "zh"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body.get("code") == 1001
    assert "草稿不存在" in body.get("message", "")


def test_api_docs_available():
    """测试 API 文档是否可用"""
    response = client.get("/docs")
    assert response.status_code == 200

    response = client.get("/redoc")
    assert response.status_code == 200

    response = client.get("/openapi.json")
    assert response.status_code == 200
    openapi_wrapped = response.json()
    openapi_spec = openapi_wrapped.get("data", openapi_wrapped)
    assert "paths" in openapi_spec
    assert "/api/draft/create" in openapi_spec["paths"]


def main():
    """运行所有测试。"""
    try:
        test_root_endpoint()
        test_draft_create_endpoint()
        test_create_draft_invalid_payload()
        test_draft_status_not_found()
        test_api_docs_available()
        return 0
    except AssertionError:
        return 1
    except Exception:
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
