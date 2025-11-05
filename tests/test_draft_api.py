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
from app.api_main import app

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


def test_draft_health_check():
    """测试草稿服务健康检查"""
    print("测试草稿服务健康检查...")
    response = client.get("/api/draft/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "services" in data
    print("✅ 健康检查测试通过\n")


def test_list_drafts_empty():
    """测试列出草稿（空列表）"""
    print("测试列出草稿（空列表）...")
    response = client.get("/api/draft/list")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "drafts" in data
    assert isinstance(data["drafts"], list)
    print("✅ 列出草稿测试通过\n")


def test_generate_draft_invalid_json():
    """测试生成草稿（无效JSON）"""
    print("测试生成草稿（无效JSON）...")
    response = client.post(
        "/api/draft/generate",
        json={
            "content": "这不是有效的JSON",
            "output_folder": None
        }
    )
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    assert response.status_code == 400  # Bad Request
    print("✅ 无效JSON测试通过\n")


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
    assert "/api/draft/generate" in openapi_spec["paths"]
    print("✅ API 文档测试通过\n")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("开始测试草稿生成 API")
    print("=" * 60 + "\n")
    
    try:
        test_root_endpoint()
        test_draft_health_check()
        test_list_drafts_empty()
        test_generate_draft_invalid_json()
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
