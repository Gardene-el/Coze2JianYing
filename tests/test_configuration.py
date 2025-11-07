#!/usr/bin/env python3
"""
配置系统集成测试

测试应用配置和 Coze 插件配置的各种场景
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
    print("Test 1: 应用配置系统")
    print("=" * 60)
    
    from app.config import get_config, reset_config
    
    # 测试默认配置
    print("\n1.1 测试默认配置")
    reset_config()
    config = get_config()
    print(f"  Platform: {config.to_dict()['platform']}")
    print(f"  Data root: {config.data_root}")
    print(f"  Drafts dir: {config.drafts_dir}")
    print(f"  ✅ 默认配置测试通过")
    
    # 测试自定义配置
    print("\n1.2 测试自定义配置")
    os.environ["JIANYING_DATA_ROOT"] = "/tmp/test_custom"
    reset_config()
    config = get_config()
    assert config.data_root == "/tmp/test_custom", "自定义根目录失败"
    assert config.drafts_dir == "/tmp/test_custom/drafts", "自定义草稿目录失败"
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
    
    from app.utils.draft_state_manager import get_draft_state_manager
    from app.config import reset_config
    
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
    
    from app.utils.segment_manager import get_segment_manager
    from app.config import reset_config
    
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


def test_coze_configuration():
    """测试 Coze 插件配置"""
    print("\n" + "=" * 60)
    print("Test 4: Coze 插件配置")
    print("=" * 60)
    
    # 添加 Coze base_tools 到路径
    base_tools_path = project_root / "coze_plugin" / "base_tools"
    if str(base_tools_path) not in sys.path:
        sys.path.insert(0, str(base_tools_path))
    
    import coze_config
    from coze_config import get_coze_base_dir, get_coze_drafts_dir
    
    print("\n4.1 测试默认配置")
    base_dir = get_coze_base_dir()
    drafts_dir = get_coze_drafts_dir()
    print(f"  Base dir: {base_dir}")
    print(f"  Drafts dir: {drafts_dir}")
    # 验证路径结构而不是具体值
    assert drafts_dir.endswith("drafts"), "草稿目录应该以 'drafts' 结尾"
    assert drafts_dir.startswith(base_dir), "草稿目录应该在基础目录下"
    print(f"  ✅ 默认配置正确")
    
    print("\n4.2 测试自定义配置")
    os.environ["JIANYING_COZE_DATA_DIR"] = "/tmp/coze_custom"
    # 需要重新导入以获取新的环境变量
    import importlib
    importlib.reload(coze_config)
    from coze_config import get_coze_base_dir, get_coze_drafts_dir
    
    base_dir = get_coze_base_dir()
    drafts_dir = get_coze_drafts_dir()
    print(f"  Custom base dir: {base_dir}")
    print(f"  Custom drafts dir: {drafts_dir}")
    assert base_dir == "/tmp/coze_custom", "自定义基础目录不正确"
    assert drafts_dir == "/tmp/coze_custom/drafts", "自定义草稿目录不正确"
    print(f"  ✅ 自定义配置正确")
    
    # 清理环境变量
    del os.environ["JIANYING_COZE_DATA_DIR"]
    
    print("\n✅ Coze 插件配置测试全部通过")


def test_api_config_endpoint():
    """测试 API 配置端点"""
    print("\n" + "=" * 60)
    print("Test 5: API 配置端点")
    print("=" * 60)
    
    from app.config import get_config, reset_config
    
    print("\n5.1 获取配置信息")
    reset_config()
    config = get_config()
    config_dict = config.to_dict()
    
    print(f"  配置信息:")
    for key, value in config_dict.items():
        print(f"    {key}: {value}")
    
    assert "platform" in config_dict, "配置缺少 platform 字段"
    assert "data_root" in config_dict, "配置缺少 data_root 字段"
    print(f"  ✅ 配置端点测试通过")
    
    print("\n✅ API 配置端点测试全部通过")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始运行配置系统集成测试")
    print("=" * 60)
    
    try:
        test_app_configuration()
        test_draft_state_manager()
        test_segment_manager()
        test_coze_configuration()
        test_api_config_endpoint()
        
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
