"""
测试统一存储方式

验证 DraftGenerator 的 use_local_storage 参数功能
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_draft_generator_storage_modes():
    """测试 DraftGenerator 的两种存储模式"""
    print("=== 测试草稿生成器存储模式 ===\n")
    
    # 检查 DraftGenerator 的方法签名
    from app.utils.draft_generator import DraftGenerator
    import inspect
    
    print("测试 1: 检查 generate() 方法签名")
    sig = inspect.signature(DraftGenerator.generate)
    params = list(sig.parameters.keys())
    print(f"参数列表: {params}")
    assert 'use_local_storage' in params, "generate() 应该有 use_local_storage 参数"
    print("✓ generate() 有 use_local_storage 参数\n")
    
    print("测试 2: 检查 generate_from_file() 方法签名")
    sig = inspect.signature(DraftGenerator.generate_from_file)
    params = list(sig.parameters.keys())
    print(f"参数列表: {params}")
    assert 'use_local_storage' in params, "generate_from_file() 应该有 use_local_storage 参数"
    print("✓ generate_from_file() 有 use_local_storage 参数\n")
    
    print("测试 3: 检查 _convert_drafts() 方法签名")
    sig = inspect.signature(DraftGenerator._convert_drafts)
    params = list(sig.parameters.keys())
    print(f"参数列表: {params}")
    assert 'use_local_storage' in params, "_convert_drafts() 应该有 use_local_storage 参数"
    print("✓ _convert_drafts() 有 use_local_storage 参数\n")
    
    print("测试 4: 检查 _convert_single_draft() 方法签名")
    sig = inspect.signature(DraftGenerator._convert_single_draft)
    params = list(sig.parameters.keys())
    print(f"参数列表: {params}")
    assert 'use_local_storage' in params, "_convert_single_draft() 应该有 use_local_storage 参数"
    print("✓ _convert_single_draft() 有 use_local_storage 参数\n")
    
    print("测试 5: 验证默认参数值")
    sig = inspect.signature(DraftGenerator.generate)
    default = sig.parameters['use_local_storage'].default
    print(f"use_local_storage 默认值: {default}")
    assert default == False, "use_local_storage 默认应为 False"
    print("✓ 默认值正确（False = 使用指定文件夹模式）\n")
    
    print("=== 所有存储模式测试通过！ ===")
    return True


def test_draft_generator_tab_integration():
    """测试 draft_generator_tab 的集成"""
    print("\n=== 测试标签页集成 ===\n")
    
    # 检查 draft_generator_tab.py 文件中的关键代码
    tab_file = project_root / "app" / "gui" / "draft_generator_tab.py"
    
    print("测试 1: 检查文件存在")
    assert tab_file.exists(), f"文件不存在: {tab_file}"
    print(f"✓ 文件存在: {tab_file}\n")
    
    print("测试 2: 检查是否使用 use_local_storage")
    with open(tab_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'use_local_storage' in content, "标签页应该使用 use_local_storage 参数"
    print("✓ 标签页使用了 use_local_storage 参数\n")
    
    print("测试 3: 检查是否根据 enable_transfer 设置存储模式")
    assert 'folder_manager.enable_transfer' in content, "应该读取 folder_manager.enable_transfer"
    print("✓ 标签页根据 enable_transfer 设置存储模式\n")
    
    print("=== 标签页集成测试通过！ ===")
    return True


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("统一存储方式测试")
    print("="*60 + "\n")
    
    try:
        # 测试 DraftGenerator 的存储模式
        test_draft_generator_storage_modes()
        print()
        
        # 测试标签页集成
        test_draft_generator_tab_integration()
        print()
        
        print("="*60)
        print("所有测试通过！ ✓")
        print("="*60)
        
        print("\n📋 存储模式说明:")
        print("  • use_local_storage=True:  草稿存config.drafts_dir, 素材存config.assets_dir/{draft_id}/")
        print("  • use_local_storage=False: 草稿存指定文件夹, 素材存CozeJianYingAssistantAssets/{draft_id}/")
        print("\n💡 标签页行为:")
        print("  • 不勾选传输: use_local_storage=True  (not enable_transfer)")
        print("  • 勾选传输:   use_local_storage=False (enable_transfer)")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
