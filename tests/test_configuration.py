#!/usr/bin/env python3
"""
配置系统集成测试

测试应用配置系统（仅 Windows）
"""
import os
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def test_app_configuration():
    """测试应用配置系统"""
    print("=" * 60)
    print("Test 1: 应用配置系统 (Windows)")
    print("=" * 60)
    
    from app.backend.config import get_config, reset_config
    
    # 测试默认配置
    print("\n1.1 测试默认配置")
    reset_config()
    config = get_config()
    print(f"  Platform: {config.to_dict()['platform']}")
    print(f"  Data root: {config.data_root}")
    print(f"  Cache dir: {config.cache_dir}")
    print(f"  Drafts dir: {config.drafts_dir}")
    print(f"  Assets dir: {config.assets_dir}")
    
    # 验证目录结构
    assert "coze2jianying_data" in config.data_root, "数据根目录应包含 coze2jianying_data"
    assert config.cache_dir.endswith("cache"), "cache 目录应以 cache 结尾"
    assert config.drafts_dir.endswith("drafts"), "drafts 目录应以 drafts 结尾"
    assert config.assets_dir.endswith("assets"), "assets 目录应以 assets 结尾"
    
    print(f"  ✅ 默认配置测试通过")
    
    # 测试自定义配置
    print("\n1.2 测试自定义配置")
    test_root = os.path.join(tempfile.gettempdir(), "test_custom_coze")
    os.environ["JIANYING_DATA_ROOT"] = test_root
    reset_config()
    config = get_config()
    assert config.data_root == test_root, "自定义根目录失败"
    assert config.cache_dir == os.path.join(test_root, "cache"), "自定义 cache 目录失败"
    assert config.drafts_dir == os.path.join(test_root, "drafts"), "自定义 drafts 目录失败"
    assert config.assets_dir == os.path.join(test_root, "assets"), "自定义 assets 目录失败"
    print(f"  Custom data root: {config.data_root}")
    print(f"  ✅ 自定义配置测试通过")
    
    # 清理环境变量
    del os.environ["JIANYING_DATA_ROOT"]
    reset_config()
    
    print("\n✅ 应用配置系统测试全部通过")


def test_draft_state_manager():
    """测试草稿状态管理器"""
    print("\n" + "=" * 60)
    print("Test 2: 草稿状态管理器")
    print("=" * 60)
    
    from app.backend.core.draft_state_manager import get_draft_state_manager
    from app.backend.config import reset_config
    
    # 重置配置使用默认路径
    reset_config()
    
    print("\n2.1 创建草稿")
    draft_mgr = get_draft_state_manager()
    print(f"  草稿存储位置: {draft_mgr.base_dir}")
    
    result = draft_mgr.create_draft("测试项目", 1920, 1080, 30)
    assert result["success"], "创建草稿失败"
    draft_id = result["draft_id"]
    print(f"  创建草稿成功: {draft_id}")
    
    print("\n2.2 读取草稿配置")
    config = draft_mgr.get_draft_config(draft_id)
    assert config is not None, "读取草稿配置失败"
    assert config["project"]["name"] == "测试项目", "草稿名称不匹配"
    print(f"  读取草稿配置成功")
    print(f"  项目名称: {config['project']['name']}")
    
    print("\n2.3 列出所有草稿")
    draft_ids = draft_mgr.list_all_drafts()
    assert draft_id in draft_ids, "草稿未在列表中"
    print(f"  找到 {len(draft_ids)} 个草稿")
    
    print("\n2.4 删除草稿")
    success = draft_mgr.delete_draft(draft_id)
    assert success, "删除草稿失败"
    print(f"  删除草稿成功")
    
    print("\n✅ 草稿状态管理器测试全部通过")


def test_segment_manager():
    """测试片段管理器"""
    print("\n" + "=" * 60)
    print("Test 3: 片段管理器")
    print("=" * 60)
    
    from app.backend.core.segment_manager import get_segment_manager
    from app.backend.config import reset_config
    
    # 重置配置使用默认路径
    reset_config()
    
    print("\n3.1 创建音频片段")
    seg_mgr = get_segment_manager()
    print(f"  片段存储位置: {seg_mgr.base_dir}")
    
    result = seg_mgr.create_segment("audio", {
        "material_url": "http://example.com/audio.mp3",
        "timerange": {"start": "0s", "end": "5s"}
    })
    assert result["success"], "创建音频片段失败"
    segment_id = result["segment_id"]
    print(f"  创建片段成功: {segment_id}")
    
    print("\n3.2 读取片段")
    segment = seg_mgr.get_segment(segment_id)
    assert segment is not None, "读取片段失败"
    assert segment["segment_type"] == "audio", "片段类型不匹配"
    print(f"  读取片段成功")
    print(f"  片段类型: {segment['segment_type']}")
    
    print("\n3.3 添加操作")
    success = seg_mgr.add_operation(segment_id, "add_fade", {
        "fade_in": "1s",
        "fade_out": "1s"
    })
    assert success, "添加操作失败"
    print(f"  添加操作成功")
    
    print("\n3.4 删除片段")
    success = seg_mgr.delete_segment(segment_id)
    assert success, "删除片段失败"
    print(f"  删除片段成功")
    
    print("\n✅ 片段管理器测试全部通过")


def test_config_dict():
    """测试配置字典输出"""
    print("\n" + "=" * 60)
    print("Test 4: 配置字典输出")
    print("=" * 60)
    
    from app.backend.config import get_config, reset_config
    
    print("\n4.1 获取配置信息")
    reset_config()
    config = get_config()
    config_dict = config.to_dict()
    
    print(f"  配置信息:")
    for key, value in config_dict.items():
        print(f"    {key}: {value}")
    
    assert "platform" in config_dict, "配置缺少 platform 字段"
    assert "data_root" in config_dict, "配置缺少 data_root 字段"
    assert "cache_dir" in config_dict, "配置缺少 cache_dir 字段"
    assert "drafts_dir" in config_dict, "配置缺少 drafts_dir 字段"
    assert "assets_dir" in config_dict, "配置缺少 assets_dir 字段"
    print(f"  ✅ 配置字典测试通过")
    
    print("\n✅ 配置字典输出测试全部通过")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始运行配置系统集成测试")
    print("=" * 60)
    
    try:
        test_app_configuration()
        test_draft_state_manager()
        test_segment_manager()
        test_config_dict()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过!")
        print("=" * 60)
        return True
    
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
