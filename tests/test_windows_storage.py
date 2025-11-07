#!/usr/bin/env python3
"""
测试 Windows 专用存储配置

验证：
1. 存储目录正确初始化
2. 三个子目录（cache, drafts, assets）正确创建
3. DraftStateManager 和 DraftSaver 正确集成
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.storage_config import get_storage_config, reset_storage_config
from app.utils.draft_state_manager import DraftStateManager
from app.utils.draft_saver import DraftSaver


def test_storage_config():
    """测试存储配置"""
    print("=== 测试 Windows 存储配置 ===\n")
    
    # 重置配置
    reset_storage_config()
    
    # 获取配置
    config = get_storage_config()
    
    # 打印配置摘要
    summary = config.get_summary()
    print("存储配置:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # 验证目录
    assert config.get_cache_dir().exists(), "cache 目录应该存在"
    assert config.get_drafts_dir().exists(), "drafts 目录应该存在"
    assert config.get_assets_dir().exists(), "assets 目录应该存在"
    
    print("\n✅ 存储配置测试通过")
    return True


def test_draft_state_manager_integration():
    """测试 DraftStateManager 集成"""
    print("\n=== 测试 DraftStateManager 集成 ===\n")
    
    # 创建管理器
    manager = DraftStateManager()
    print(f"状态目录: {manager.base_dir}")
    
    # 验证目录正确
    config = get_storage_config()
    assert str(manager.base_dir) == str(config.get_cache_dir()), "应该使用 cache 目录"
    
    # 创建测试草稿
    result = manager.create_draft(
        draft_name="测试项目",
        width=1920,
        height=1080,
        fps=30
    )
    
    assert result["success"], "创建草稿应该成功"
    print(f"草稿 ID: {result['draft_id']}")
    
    print("\n✅ DraftStateManager 集成测试通过")
    return True


def test_draft_saver_integration():
    """测试 DraftSaver 集成"""
    print("\n=== 测试 DraftSaver 集成 ===\n")
    
    # 创建保存器
    saver = DraftSaver()
    print(f"草稿输出目录: {saver.output_dir}")
    print(f"素材目录: {saver.assets_dir}")
    
    # 验证目录正确
    config = get_storage_config()
    assert str(saver.output_dir) == str(config.get_drafts_dir()), "应该使用 drafts 目录"
    assert str(saver.assets_dir) == str(config.get_assets_dir()), "应该使用 assets 目录"
    
    print("\n✅ DraftSaver 集成测试通过")
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("Windows 存储配置测试套件")
    print("="*60 + "\n")
    
    tests = [
        test_storage_config,
        test_draft_state_manager_integration,
        test_draft_saver_integration,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "="*60)
    print(f"测试总结: {sum(results)}/{len(results)} 通过")
    print("="*60)
    
    return all(results)


if __name__ == "__main__":
    success = run_all_tests()
    
    if success:
        print("\n🎉 所有测试通过！Windows 存储配置工作正常。")
    
    sys.exit(0 if success else 1)
