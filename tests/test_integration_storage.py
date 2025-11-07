#!/usr/bin/env python3
"""
集成测试：验证存储配置系统与所有组件的集成

测试场景：
1. 存储配置的初始化和检测
2. DraftGenerator 集成
3. DraftStateManager 集成
4. 配置持久化和重载
"""
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.storage_config import StorageConfig, reset_storage_config
from app.utils.draft_generator import DraftGenerator
from app.utils.draft_state_manager import DraftStateManager


def test_full_integration():
    """完整集成测试"""
    print("\n" + "="*60)
    print("存储配置系统 - 完整集成测试")
    print("="*60 + "\n")
    
    success = True
    
    try:
        # 1. 测试配置初始化
        print("1️⃣ 测试配置初始化...")
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "config.json"
            config = StorageConfig(config_file=config_file)
            
            print(f"   ✅ 草稿目录: {config.drafts_base_dir}")
            print(f"   ✅ 状态目录: {config.state_base_dir}")
            print(f"   ✅ 素材目录: {config.assets_base_dir}")
            print(f"   ✅ 临时目录: {config.temp_dir}")
        
        # 2. 测试 DraftGenerator 集成
        print("\n2️⃣ 测试 DraftGenerator 集成...")
        reset_storage_config()  # 重置全局配置
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # 使用默认配置
            gen1 = DraftGenerator()
            print(f"   ✅ 默认输出: {gen1.output_base_dir}")
            
            # 使用自定义路径
            custom_path = Path(tmpdir) / "custom"
            gen2 = DraftGenerator(output_base_dir=str(custom_path))
            print(f"   ✅ 自定义输出: {gen2.output_base_dir}")
            
            # 测试检测功能
            detected = gen2.detect_default_draft_folder()
            print(f"   ✅ 剪映检测: {detected if detected else '未检测到（正常）'}")
        
        # 3. 测试 DraftStateManager 集成
        print("\n3️⃣ 测试 DraftStateManager 集成...")
        with tempfile.TemporaryDirectory() as tmpdir:
            # 使用默认配置
            manager1 = DraftStateManager()
            print(f"   ✅ 默认状态目录: {manager1.base_dir}")
            
            # 使用自定义路径
            custom_path = Path(tmpdir) / "state"
            manager2 = DraftStateManager(base_dir=str(custom_path))
            print(f"   ✅ 自定义状态目录: {manager2.base_dir}")
            
            # 测试创建草稿
            result = manager2.create_draft(
                draft_name="集成测试项目",
                width=1920,
                height=1080,
                fps=30
            )
            assert result["success"], "创建草稿失败"
            print(f"   ✅ 创建草稿: {result['draft_id'][:8]}...")
            
            # 验证草稿文件存在
            draft_path = manager2.base_dir / result['draft_id'] / "draft_config.json"
            assert draft_path.exists(), "草稿配置文件不存在"
            print(f"   ✅ 配置文件已创建")
        
        # 4. 测试配置持久化
        print("\n4️⃣ 测试配置持久化...")
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test_config.json"
            
            # 创建并设置配置
            config1 = StorageConfig(config_file=config_file)
            custom_draft_dir = Path(tmpdir) / "my_drafts"
            config1.set_drafts_dir(str(custom_draft_dir))
            print(f"   ✅ 设置草稿目录: {custom_draft_dir}")
            
            # 重新加载配置
            config2 = StorageConfig(config_file=config_file)
            assert str(config2.drafts_base_dir) == str(custom_draft_dir), "配置未持久化"
            print(f"   ✅ 配置已持久化")
        
        # 5. 测试配置摘要
        print("\n5️⃣ 测试配置摘要...")
        reset_storage_config()
        from app.core.storage_config import get_storage_config
        config = get_storage_config()
        
        summary = config.get_config_summary()
        print("   配置摘要:")
        for key, value in summary.items():
            print(f"     • {key}: {value}")
        
        print("\n" + "="*60)
        print("✅ 所有集成测试通过！")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_full_integration()
    
    if success:
        print("\n🎉 存储配置系统已成功集成到所有组件！")
        print("📚 详细文档: docs/STORAGE_CONFIG_GUIDE.md")
        print("📊 重构总结: STORAGE_REFACTORING_SUMMARY.md")
    
    sys.exit(0 if success else 1)
