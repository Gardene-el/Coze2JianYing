"""
测试 EffectSegment 和 FilterSegment API 端点
验证特效片段和滤镜片段的创建功能
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


def test_effect_filter_routes_registered():
    """测试 effect 和 filter 路由是否正确注册"""
    print("测试 effect 和 filter 路由注册...")
    
    # 获取所有路由
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append(route.path)
    
    # 检查新端点
    required_endpoints = [
        "/api/segment/effect/create",
        "/api/segment/filter/create",
    ]
    
    for endpoint in required_endpoints:
        assert endpoint in routes, f"端点 {endpoint} 未注册"
        print(f"  ✅ {endpoint}")
    
    print("✅ effect 和 filter 路由注册测试通过\n")
    return True


def test_create_effect_segment():
    """测试创建特效片段端点"""
    print("测试创建特效片段端点...")
    
    response = client.post(
        "/api/segment/effect/create",
        json={
            "effect_type": "VideoSceneEffectType.XXX",
            "target_timerange": {
                "start": 0,
                "duration": 5000000
            },
            "params": [50.0, 75.0]
        }
    )
    
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 201, f"期望状态码 201，实际 {response.status_code}"
    
    data = response.json()
    print(f"  响应: {data}")
    
    assert "segment_id" in data, "响应中缺少 segment_id"
    assert data["success"] == True, "success 应为 True"
    assert len(data["segment_id"]) > 0, "segment_id 不应为空"
    assert "片段创建成功" in data["message"], "消息中应包含'片段创建成功'"
    
    print("✅ 创建特效片段测试通过\n")
    return data["segment_id"]


def test_create_effect_segment_without_params():
    """测试创建特效片段端点（不带参数）"""
    print("测试创建特效片段端点（不带参数）...")
    
    response = client.post(
        "/api/segment/effect/create",
        json={
            "effect_type": "VideoSceneEffectType.YYY",
            "target_timerange": {
                "start": 1000000,
                "duration": 3000000
            }
        }
    )
    
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 201, f"期望状态码 201，实际 {response.status_code}"
    
    data = response.json()
    print(f"  响应: {data}")
    
    assert "segment_id" in data, "响应中缺少 segment_id"
    assert data["success"] == True, "success 应为 True"
    
    print("✅ 创建特效片段（不带参数）测试通过\n")
    return data["segment_id"]


def test_create_filter_segment():
    """测试创建滤镜片段端点"""
    print("测试创建滤镜片段端点...")
    
    response = client.post(
        "/api/segment/filter/create",
        json={
            "filter_type": "FilterType.XXX",
            "target_timerange": {
                "start": 0,
                "duration": 5000000
            },
            "intensity": 100.0
        }
    )
    
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 201, f"期望状态码 201，实际 {response.status_code}"
    
    data = response.json()
    print(f"  响应: {data}")
    
    assert "segment_id" in data, "响应中缺少 segment_id"
    assert data["success"] == True, "success 应为 True"
    assert len(data["segment_id"]) > 0, "segment_id 不应为空"
    assert "片段创建成功" in data["message"], "消息中应包含'片段创建成功'"
    
    print("✅ 创建滤镜片段测试通过\n")
    return data["segment_id"]


def test_create_filter_segment_with_different_intensity():
    """测试创建滤镜片段端点（不同强度）"""
    print("测试创建滤镜片段端点（不同强度）...")
    
    response = client.post(
        "/api/segment/filter/create",
        json={
            "filter_type": "FilterType.YYY",
            "target_timerange": {
                "start": 2000000,
                "duration": 4000000
            },
            "intensity": 50.0
        }
    )
    
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 201, f"期望状态码 201，实际 {response.status_code}"
    
    data = response.json()
    print(f"  响应: {data}")
    
    assert "segment_id" in data, "响应中缺少 segment_id"
    assert data["success"] == True, "success 应为 True"
    
    print("✅ 创建滤镜片段（不同强度）测试通过\n")
    return data["segment_id"]


def test_get_effect_segment_detail():
    """测试查询特效片段详情"""
    print("测试查询特效片段详情...")
    
    # 先创建一个特效片段
    segment_id = test_create_effect_segment()
    
    # 查询片段详情
    response = client.get(f"/api/segment/effect/{segment_id}")
    
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 200, f"期望状态码 200，实际 {response.status_code}"
    
    data = response.json()
    print(f"  响应: {data}")
    
    assert data["segment_id"] == segment_id, "segment_id 不匹配"
    assert data["segment_type"] == "effect", "segment_type 应为 effect"
    assert "properties" in data, "响应中缺少 properties"
    
    print("✅ 查询特效片段详情测试通过\n")
    return True


def test_get_filter_segment_detail():
    """测试查询滤镜片段详情"""
    print("测试查询滤镜片段详情...")
    
    # 先创建一个滤镜片段
    segment_id = test_create_filter_segment()
    
    # 查询片段详情
    response = client.get(f"/api/segment/filter/{segment_id}")
    
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 200, f"期望状态码 200，实际 {response.status_code}"
    
    data = response.json()
    print(f"  响应: {data}")
    
    assert data["segment_id"] == segment_id, "segment_id 不匹配"
    assert data["segment_type"] == "filter", "segment_type 应为 filter"
    assert "properties" in data, "响应中缺少 properties"
    
    print("✅ 查询滤镜片段详情测试通过\n")
    return True


def test_validation_intensity_out_of_range():
    """测试滤镜强度超出范围的验证"""
    print("测试滤镜强度超出范围的验证...")
    
    # 测试强度超过 100
    response = client.post(
        "/api/segment/filter/create",
        json={
            "filter_type": "FilterType.XXX",
            "target_timerange": {
                "start": 0,
                "duration": 5000000
            },
            "intensity": 150.0  # 超过 100
        }
    )
    
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 422, f"期望状态码 422，实际 {response.status_code}"
    
    # 测试强度小于 0
    response = client.post(
        "/api/segment/filter/create",
        json={
            "filter_type": "FilterType.XXX",
            "target_timerange": {
                "start": 0,
                "duration": 5000000
            },
            "intensity": -10.0  # 小于 0
        }
    )
    
    print(f"  状态码: {response.status_code}")
    assert response.status_code == 422, f"期望状态码 422，实际 {response.status_code}"
    
    print("✅ 滤镜强度超出范围的验证测试通过\n")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("开始测试 EffectSegment 和 FilterSegment API 端点")
    print("=" * 60 + "\n")
    
    test_results = []
    
    # 运行所有测试
    try:
        test_effect_filter_routes_registered()
        test_results.append(True)
    except Exception as e:
        print(f"❌ 路由注册测试失败: {e}")
        test_results.append(False)
    
    try:
        test_create_effect_segment()
        test_results.append(True)
    except Exception as e:
        print(f"❌ 创建特效片段测试失败: {e}")
        test_results.append(False)
    
    try:
        test_create_effect_segment_without_params()
        test_results.append(True)
    except Exception as e:
        print(f"❌ 创建特效片段（不带参数）测试失败: {e}")
        test_results.append(False)
    
    try:
        test_create_filter_segment()
        test_results.append(True)
    except Exception as e:
        print(f"❌ 创建滤镜片段测试失败: {e}")
        test_results.append(False)
    
    try:
        test_create_filter_segment_with_different_intensity()
        test_results.append(True)
    except Exception as e:
        print(f"❌ 创建滤镜片段（不同强度）测试失败: {e}")
        test_results.append(False)
    
    try:
        test_get_effect_segment_detail()
        test_results.append(True)
    except Exception as e:
        print(f"❌ 查询特效片段详情测试失败: {e}")
        test_results.append(False)
    
    try:
        test_get_filter_segment_detail()
        test_results.append(True)
    except Exception as e:
        print(f"❌ 查询滤镜片段详情测试失败: {e}")
        test_results.append(False)
    
    try:
        test_validation_intensity_out_of_range()
        test_results.append(True)
    except Exception as e:
        print(f"❌ 滤镜强度验证测试失败: {e}")
        test_results.append(False)
    
    print("\n" + "=" * 60)
    print(f"测试总结: {sum(test_results)}/{len(test_results)} 测试通过")
    print("=" * 60)
    
    if all(test_results):
        print("✅ 所有测试通过！")
        exit(0)
    else:
        print("❌ 有测试失败")
        exit(1)
