#!/usr/bin/env python3
"""
测试存储配置模块

验证：
1. 平台无关的路径检测
2. 配置持久化
3. 与各组件的集成
"""
import os
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.storage_config import StorageConfig, reset_storage_config
from app.utils.draft_generator import DraftGenerator
from app.utils.draft_state_manager import DraftStateManager


def test_storage_config_initialization():
    """测试存储配置初始化"""
    print("=== 测试1: 存储配置初始化 ===")
    
    # 创建临时配置文件
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test_config.json"
        
        # 创建配置实例
        config = StorageConfig(config_file=config_file)
        
        # 验证所有路径都已设置
        assert config.drafts_base_dir is not None
        assert config.state_base_dir is not None
        assert config.assets_base_dir is not None
        assert config.temp_dir is not None
        
        print(f"✅ 草稿目录: {config.drafts_base_dir}")
        print(f"✅ 状态目录: {config.state_base_dir}")
        print(f"✅ 素材目录: {config.assets_base_dir}")
        print(f"✅ 临时目录: {config.temp_dir}")
    
    print("✅ 测试通过\n")
    return True


def test_config_persistence():
    """测试配置持久化"""
    print("=== 测试2: 配置持久化 ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test_config.json"
        
        # 创建配置并设置自定义路径
        config1 = StorageConfig(config_file=config_file)
        custom_path = Path(tmpdir) / "custom_drafts"
        config1.set_drafts_dir(str(custom_path))
        
        print(f"设置自定义路径: {custom_path}")
        
        # 重新加载配置
        config2 = StorageConfig(config_file=config_file)
        
        # 验证路径已持久化
        assert str(config2.drafts_base_dir) == str(custom_path)
        print(f"✅ 配置已持久化: {config2.drafts_base_dir}")
    
    print("✅ 测试通过\n")
    return True


def test_platform_detection():
    """测试平台检测功能"""
    print("=== 测试3: 平台检测 ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test_config.json"
        config = StorageConfig(config_file=config_file)
        
        # 尝试检测剪映路径（可能为 None）
        detected = config.detect_jianying_draft_folder()
        
        import platform
        system = platform.system()
        
        if system == "Linux":
            # Linux 不支持剪映，应该返回 None
            assert detected is None
            print(f"✅ Linux 平台检测正确: {detected}")
        else:
            # Windows/macOS 可能检测到或未检测到
            print(f"✅ {system} 平台检测结果: {detected}")
    
    print("✅ 测试通过\n")
    return True


def test_draft_generator_integration():
    """测试与 DraftGenerator 的集成"""
    print("=== 测试4: DraftGenerator 集成 ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 重置全局配置
        reset_storage_config()
        
        # 测试默认配置
        generator1 = DraftGenerator()
        print(f"✅ 默认输出目录: {generator1.output_base_dir}")
        
        # 测试自定义路径
        custom_path = Path(tmpdir) / "custom_output"
        generator2 = DraftGenerator(output_base_dir=str(custom_path))
        assert str(generator2.output_base_dir) == str(custom_path)
        print(f"✅ 自定义输出目录: {generator2.output_base_dir}")
        
        # 测试检测功能
        detected = generator2.detect_default_draft_folder()
        print(f"✅ 检测结果: {detected}")
    
    print("✅ 测试通过\n")
    return True


def test_draft_state_manager_integration():
    """测试与 DraftStateManager 的集成"""
    print("=== 测试5: DraftStateManager 集成 ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 测试默认配置
        manager1 = DraftStateManager()
        print(f"✅ 默认状态目录: {manager1.base_dir}")
        
        # 测试自定义路径
        custom_path = Path(tmpdir) / "custom_state"
        manager2 = DraftStateManager(base_dir=str(custom_path))
        assert str(manager2.base_dir) == str(custom_path)
        print(f"✅ 自定义状态目录: {manager2.base_dir}")
        
        # 测试创建草稿
        result = manager2.create_draft(
            draft_name="测试项目",
            width=1920,
            height=1080,
            fps=30
        )
        
        assert result["success"] is True
        draft_id = result["draft_id"]
        print(f"✅ 创建草稿成功: {draft_id}")
        
        # 验证草稿文件已创建
        draft_path = manager2.base_dir / draft_id / "draft_config.json"
        assert draft_path.exists()
        print(f"✅ 草稿配置文件已创建: {draft_path}")
    
    print("✅ 测试通过\n")
    return True


def test_config_summary():
    """测试配置摘要功能"""
    print("=== 测试6: 配置摘要 ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test_config.json"
        config = StorageConfig(config_file=config_file)
        
        summary = config.get_config_summary()
        
        # 验证摘要包含所有必要信息
        required_keys = ["草稿目录", "状态目录", "素材目录", "临时目录", "自动检测", "配置文件"]
        for key in required_keys:
            assert key in summary
            print(f"✅ {key}: {summary[key]}")
    
    print("✅ 测试通过\n")
    return True


def test_reset_config():
    """测试配置重置功能"""
    print("=== 测试7: 配置重置 ===")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test_config.json"
        config = StorageConfig(config_file=config_file)
        
        # 设置自定义路径
        custom_path = Path(tmpdir) / "custom_drafts"
        config.set_drafts_dir(str(custom_path))
        config.enable_auto_detect(False)
        
        print(f"设置自定义路径: {custom_path}")
        print(f"自动检测: {'禁用' if not config.config.get('auto_detect_jianying') else '启用'}")
        
        # 重置配置
        config.reset_to_defaults()
        
        # 验证已重置
        assert config.config.get("auto_detect_jianying") is True
        print(f"✅ 配置已重置")
        print(f"自动检测: {'启用' if config.config.get('auto_detect_jianying') else '禁用'}")
    
    print("✅ 测试通过\n")
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("存储配置模块测试套件")
    print("="*60 + "\n")
    
    tests = [
        test_storage_config_initialization,
        test_config_persistence,
        test_platform_detection,
        test_draft_generator_integration,
        test_draft_state_manager_integration,
        test_config_summary,
        test_reset_config,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("="*60)
    print(f"测试总结: {sum(results)}/{len(results)} 通过")
    print("="*60)
    
    return all(results)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
