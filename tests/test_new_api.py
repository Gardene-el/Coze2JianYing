"""
测试新版 API 端点
验证 segment 创建和 draft 操作端点正常工作
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


def test_segment_routes_registered():
    """测试 segment 路由是否正确注册"""
    print("测试 segment 路由注册...")
    
    # 获取所有路由
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append(route.path)
    
    # 检查关键端点
    required_endpoints = [
        "/api/segment/audio/create",
        "/api/segment/video/create",
        "/api/segment/text/create",
        "/api/segment/sticker/create",
        "/api/draft/{draft_id}/add_segment",
        "/api/draft/{draft_id}/add_track",
    ]
    
    for endpoint in required_endpoints:
        assert endpoint in routes, f"端点 {endpoint} 未注册"
        print(f"  ✅ {endpoint}")
    
    print("✅ segment 路由注册测试通过\n")
    return True


def test_old_routes_removed():
    """测试旧路由是否已移除"""
    print("测试旧路由移除...")
    
    # 获取所有路由
    routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            routes.append(route.path)
    
    # 检查旧端点是否不存在
    old_endpoints = [
        "/api/draft/{draft_id}/add-videos",
        "/api/draft/{draft_id}/add-audios",
        "/api/draft/{draft_id}/add-images",
        "/api/draft/{draft_id}/add-captions",
    ]
    
    for endpoint in old_endpoints:
        assert endpoint not in routes, f"旧端点 {endpoint} 仍然存在"
        print(f"  ✅ {endpoint} 已移除")
    
    print("✅ 旧路由移除测试通过\n")
    return True


def test_create_draft():
    """测试创建草稿端点"""
    print("测试创建草稿端点...")
    
    response = client.post(
        "/api/draft/create",
        json={
            "draft_name": "测试项目",
            "width": 1920,
            "height": 1080,
            "fps": 30
        }
    )
    
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 201, f"期望状态码 201，实际 {response.status_code}"
    
    data = response.json()
    print(f"  响应: {data}")
    
    assert "draft_id" in data, "响应中缺少 draft_id"
    assert data["success"] == True, "success 应为 True"
    assert len(data["draft_id"]) > 0, "draft_id 不应为空"
    
    print("✅ 创建草稿测试通过\n")
    return data["draft_id"]


def test_create_audio_segment():
    """测试创建音频片段端点"""
    print("测试创建音频片段端点...")
    
    response = client.post(
        "/api/segment/audio/create",
        json={
            "material_url": "https://example.com/audio.mp3",
            "target_timerange": {
                "start": 0,
                "duration": 5000000
            },
            "volume": 1.0
        }
    )
    
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 201, f"期望状态码 201，实际 {response.status_code}"
    
    data = response.json()
    print(f"  响应: {data}")
    
    assert "segment_id" in data, "响应中缺少 segment_id"
    assert data["success"] == True, "success 应为 True"
    assert len(data["segment_id"]) > 0, "segment_id 不应为空"
    
    print("✅ 创建音频片段测试通过\n")
    return data["segment_id"]


def test_create_video_segment():
    """测试创建视频片段端点"""
    print("测试创建视频片段端点...")
    
    response = client.post(
        "/api/segment/video/create",
        json={
            "material_url": "https://example.com/video.mp4",
            "target_timerange": {
                "start": 0,
                "duration": 10000000
            }
        }
    )
    
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 201, f"期望状态码 201，实际 {response.status_code}"
    
    data = response.json()
    assert "segment_id" in data, "响应中缺少 segment_id"
    
    print("✅ 创建视频片段测试通过\n")
    return data["segment_id"]


def test_create_text_segment():
    """测试创建文本片段端点"""
    print("测试创建文本片段端点...")
    
    response = client.post(
        "/api/segment/text/create",
        json={
            "text_content": "Hello World",
            "target_timerange": {
                "start": 0,
                "duration": 3000000
            }
        }
    )
    
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 201, f"期望状态码 201，实际 {response.status_code}"
    
    data = response.json()
    assert "segment_id" in data, "响应中缺少 segment_id"
    
    print("✅ 创建文本片段测试通过\n")
    return data["segment_id"]


def test_add_track():
    """测试添加轨道端点"""
    print("测试添加轨道端点...")
    
    # 先创建草稿
    draft_id = test_create_draft()
    
    # 添加轨道
    response = client.post(
        f"/api/draft/{draft_id}/add_track",
        json={
            "track_type": "audio",
            "track_name": "背景音乐"
        }
    )
    
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 200, f"期望状态码 200，实际 {response.status_code}"
    
    data = response.json()
    print(f"  响应: {data}")
    
    assert data["success"] == True, "success 应为 True"
    assert "track_index" in data, "响应中缺少 track_index"
    
    print("✅ 添加轨道测试通过\n")
    return draft_id


def test_add_segment_to_draft():
    """测试将片段添加到草稿"""
    print("测试将片段添加到草稿...")
    
    # 创建草稿
    draft_id = test_create_draft()
    
    # 创建音频片段
    segment_id = test_create_audio_segment()
    
    # 添加片段到草稿
    response = client.post(
        f"/api/draft/{draft_id}/add_segment",
        json={
            "segment_id": segment_id
        }
    )
    
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 200, f"期望状态码 200，实际 {response.status_code}"
    
    data = response.json()
    print(f"  响应: {data}")
    
    assert data["success"] == True, "success 应为 True"
    
    print("✅ 添加片段到草稿测试通过\n")
    return True


def test_get_draft_status():
    """测试查询草稿状态"""
    print("测试查询草稿状态...")
    
    # 创建草稿和片段
    draft_id = test_create_draft()
    segment_id = test_create_audio_segment()
    
    # 添加片段
    client.post(
        f"/api/draft/{draft_id}/add_segment",
        json={"segment_id": segment_id}
    )
    
    # 查询状态
    response = client.get(f"/api/draft/{draft_id}/status")
    
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 200, f"期望状态码 200，实际 {response.status_code}"
    
    data = response.json()
    print(f"  响应: {data}")
    
    assert "draft_id" in data, "响应中缺少 draft_id"
    assert "tracks" in data, "响应中缺少 tracks"
    assert "segments" in data, "响应中缺少 segments"
    assert "download_status" in data, "响应中缺少 download_status"
    
    print("✅ 查询草稿状态测试通过\n")
    return True


def test_segment_operations():
    """测试片段操作端点"""
    print("测试片段操作端点...")
    
    # 创建音频片段
    audio_seg_id = test_create_audio_segment()
    
    # 测试添加淡入淡出
    response = client.post(
        f"/api/segment/audio/{audio_seg_id}/add_fade",
        json={
            "in_duration": "1s",
            "out_duration": "1s"
        }
    )
    assert response.status_code == 200, "添加淡入淡出失败"
    print("  ✅ 添加淡入淡出成功")
    
    # 测试添加关键帧
    response = client.post(
        f"/api/segment/audio/{audio_seg_id}/add_keyframe",
        json={
            "time_offset": "2s",
            "value": 0.8
        }
    )
    assert response.status_code == 200, "添加关键帧失败"
    print("  ✅ 添加关键帧成功")
    
    print("✅ 片段操作测试通过\n")
    return True


def test_api_documentation():
    """测试 API 文档可用性"""
    print("测试 API 文档...")
    
    # 测试 Swagger UI
    response = client.get("/docs")
    assert response.status_code == 200, "Swagger UI 不可用"
    print("  ✅ Swagger UI 可用")
    
    # 测试 ReDoc
    response = client.get("/redoc")
    assert response.status_code == 200, "ReDoc 不可用"
    print("  ✅ ReDoc 可用")
    
    # 测试 OpenAPI JSON
    response = client.get("/openapi.json")
    assert response.status_code == 200, "OpenAPI JSON 不可用"
    data = response.json()
    assert "paths" in data, "OpenAPI JSON 格式错误"
    
    # 验证新端点在 OpenAPI 中
    assert "/api/segment/audio/create" in data["paths"], "新端点未在 OpenAPI 中"
    assert "/api/draft/{draft_id}/add_segment" in data["paths"], "新端点未在 OpenAPI 中"
    
    print("  ✅ OpenAPI JSON 可用")
    print("✅ API 文档测试通过\n")
    return True


def main():
    """运行所有测试"""
    print("=" * 60)
    print("开始测试新版 API 端点")
    print("=" * 60)
    print()
    
    tests = [
        ("路由注册", test_segment_routes_registered),
        ("旧路由移除", test_old_routes_removed),
        ("创建草稿", lambda: test_create_draft() and True),
        ("创建音频片段", lambda: test_create_audio_segment() and True),
        ("创建视频片段", lambda: test_create_video_segment() and True),
        ("创建文本片段", lambda: test_create_text_segment() and True),
        ("添加轨道", lambda: test_add_track() and True),
        ("添加片段到草稿", test_add_segment_to_draft),
        ("查询草稿状态", test_get_draft_status),
        ("片段操作", test_segment_operations),
        ("API 文档", test_api_documentation),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, True, None))
        except Exception as e:
            print(f"❌ {name} 测试失败: {e}\n")
            results.append((name, False, str(e)))
    
    print("=" * 60)
    print("测试摘要")
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for name, success, error in results:
        status = "✅ 通过" if success else f"❌ 失败: {error}"
        print(f"{name}: {status}")
    
    print()
    print(f"总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    exit(main())
