"""
测试批量片段 API 路由

测试所有批量操作 API 端点的基本功能
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.router import api_router


@pytest.fixture
def app():
    """创建 FastAPI 应用"""
    app = FastAPI()
    app.include_router(api_router)
    return app


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return TestClient(app)


def test_batch_routes_registered(app):
    """测试所有批量路由都已注册"""
    routes = [route.path for route in app.routes if hasattr(route, 'path')]
    
    expected_routes = [
        "/api/batch/add_audios",
        "/api/batch/add_captions",
        "/api/batch/add_effects",
        "/api/batch/add_images",
        "/api/batch/add_videos",
        "/api/batch/add_sticker",
        "/api/batch/add_keyframes",
        "/api/batch/add_masks",
    ]
    
    for route in expected_routes:
        assert route in routes, f"Route {route} not registered"
    
    print(f"✓ All {len(expected_routes)} batch routes registered")


def test_add_audios_endpoint_exists(client):
    """测试 add_audios 端点存在"""
    # 发送一个无效请求来检查端点是否存在
    response = client.post("/api/batch/add_audios", json={})
    # 应该返回 422（验证错误）而不是 404
    assert response.status_code in [422, 200], f"Unexpected status: {response.status_code}"
    print("✓ add_audios endpoint exists")


def test_add_captions_endpoint_exists(client):
    """测试 add_captions 端点存在"""
    response = client.post("/api/batch/add_captions", json={})
    assert response.status_code in [422, 200], f"Unexpected status: {response.status_code}"
    print("✓ add_captions endpoint exists")


def test_add_effects_endpoint_exists(client):
    """测试 add_effects 端点存在"""
    response = client.post("/api/batch/add_effects", json={})
    assert response.status_code in [422, 200], f"Unexpected status: {response.status_code}"
    print("✓ add_effects endpoint exists")


def test_add_images_endpoint_exists(client):
    """测试 add_images 端点存在"""
    response = client.post("/api/batch/add_images", json={})
    assert response.status_code in [422, 200], f"Unexpected status: {response.status_code}"
    print("✓ add_images endpoint exists")


def test_add_videos_endpoint_exists(client):
    """测试 add_videos 端点存在"""
    response = client.post("/api/batch/add_videos", json={})
    assert response.status_code in [422, 200], f"Unexpected status: {response.status_code}"
    print("✓ add_videos endpoint exists")


def test_add_sticker_endpoint_exists(client):
    """测试 add_sticker 端点存在"""
    response = client.post("/api/batch/add_sticker", json={})
    assert response.status_code in [422, 200], f"Unexpected status: {response.status_code}"
    print("✓ add_sticker endpoint exists")


def test_add_keyframes_endpoint_exists(client):
    """测试 add_keyframes 端点存在"""
    response = client.post("/api/batch/add_keyframes", json={})
    assert response.status_code in [422, 200], f"Unexpected status: {response.status_code}"
    print("✓ add_keyframes endpoint exists")


def test_add_masks_endpoint_exists(client):
    """测试 add_masks 端点存在"""
    response = client.post("/api/batch/add_masks", json={})
    assert response.status_code in [422, 200], f"Unexpected status: {response.status_code}"
    print("✓ add_masks endpoint exists")


def test_all_endpoints_have_post_method(app):
    """测试所有批量端点都使用 POST 方法"""
    batch_routes = [r for r in app.routes if hasattr(r, 'path') and '/batch/' in r.path]
    
    for route in batch_routes:
        if hasattr(route, 'methods'):
            assert 'POST' in route.methods, f"Route {route.path} should use POST method"
    
    print(f"✓ All {len(batch_routes)} batch routes use POST method")


if __name__ == "__main__":
    # 运行简单的端点检查
    print("=" * 60)
    print("Testing Batch Routes Registration")
    print("=" * 60)
    
    from fastapi import FastAPI
    from app.api.router import api_router
    
    app = FastAPI()
    app.include_router(api_router)
    
    # 检查所有路由
    batch_routes = [r for r in app.routes if hasattr(r, 'path') and '/batch/' in r.path]
    
    print(f"\n✓ Found {len(batch_routes)} batch routes:")
    for route in batch_routes:
        methods = list(route.methods) if hasattr(route, 'methods') and route.methods else ['GET']
        print(f"  {methods[0]:6} {route.path}")
    
    print("\n✓ All batch routes registered successfully!")
    print("=" * 60)
