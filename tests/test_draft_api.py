"""
测试草稿生成 API
快速验证 API 端点是否正常工作
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi.testclient import TestClient
from app.backend.api_main import app

# 创建测试客户端
client = TestClient(app)


def test_root_endpoint():
    """测试根路径"""
    print("测试根路径...")
    response = client.get("/")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    assert response.status_code == 200
    assert "message" in response.json()
    print("✅ 根路径测试通过\n")


def test_draft_create_endpoint():
    """测试草稿创建端点"""
    print("测试草稿创建端点...")
    response = client.post(
        "/api/draft/create",
        json={"draft_name": "api_test", "width": 1920, "height": 1080, "fps": 30},
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert "draft_id" in data
    assert data.get("success") is True
    print("✅ 草稿创建端点测试通过\n")


def test_create_draft_invalid_payload():
    """测试创建草稿参数校验（FastAPI/Pydantic）"""
    print("测试创建草稿参数校验...")
    response = client.post(
        "/api/draft/create",
        json={
            "draft_name": "bad",
            "width": "invalid_width",
            "height": 1080,
            "fps": 30,
        },
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    assert response.status_code == 422
    print("✅ 参数校验测试通过\n")


def test_draft_status_not_found():
    """测试查询不存在草稿状态"""
    print("测试查询不存在草稿状态...")
    response = client.get("/api/draft/not-exists/status")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    assert response.status_code == 404
    print("✅ 不存在草稿状态测试通过\n")


def test_api_docs_available():
    """测试 API 文档是否可用"""
    print("测试 API 文档...")
    
    # Swagger UI
    response = client.get("/docs")
    print(f"Swagger UI 状态码: {response.status_code}")
    assert response.status_code == 200
    
    # ReDoc
    response = client.get("/redoc")
    print(f"ReDoc 状态码: {response.status_code}")
    assert response.status_code == 200
    
    # OpenAPI JSON
    response = client.get("/openapi.json")
    print(f"OpenAPI JSON 状态码: {response.status_code}")
    assert response.status_code == 200
    openapi_spec = response.json()
    assert "paths" in openapi_spec
    assert "/api/draft/create" in openapi_spec["paths"]
    print("✅ API 文档测试通过\n")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("开始测试草稿生成 API")
    print("=" * 60 + "\n")
    
    try:
        test_root_endpoint()
        test_draft_create_endpoint()
        test_create_draft_invalid_payload()
        test_draft_status_not_found()
        test_api_docs_available()
        
        print("=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 测试错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
