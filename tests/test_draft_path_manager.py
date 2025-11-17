#!/usr/bin/env python3
"""
测试草稿路径管理器
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.draft_path_manager import get_draft_path_manager
from app.config import get_config

def test_draft_path_manager():
    """测试草稿路径管理器功能"""
    print("=== 测试草稿路径管理器 ===\n")
    
    # 获取路径管理器实例
    manager = get_draft_path_manager()
    print(f"✓ 成功创建路径管理器实例")
    
    # 测试默认状态
    print(f"\n默认状态:")
    print(f"  - 传输启用: {manager.is_transfer_enabled()}")
    print(f"  - 草稿文件夹: {manager.get_draft_folder()}")
    print(f"  - 有效输出路径: {manager.get_effective_output_path()}")
    print(f"  - 有效素材路径: {manager.get_effective_assets_path('test_draft_id')}")
    print(f"  - 状态文本: {manager.get_status_text()}")
    
    # 测试设置草稿文件夹
    test_path = r"C:\Users\Test\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft"
    manager.set_draft_folder(test_path)
    print(f"\n设置草稿文件夹后:")
    print(f"  - 草稿文件夹: {manager.get_draft_folder()}")
    print(f"  - 有效输出路径: {manager.get_effective_output_path()}")
    print(f"  - 状态文本: {manager.get_status_text()}")
    
    # 测试启用传输
    manager.set_transfer_enabled(True)
    print(f"\n启用传输后:")
    print(f"  - 传输启用: {manager.is_transfer_enabled()}")
    print(f"  - 有效输出路径: {manager.get_effective_output_path()}")
    print(f"  - 有效素材路径: {manager.get_effective_assets_path('test_draft_id')}")
    print(f"  - 状态文本: {manager.get_status_text()}")
    
    # 测试禁用传输
    manager.set_transfer_enabled(False)
    print(f"\n禁用传输后:")
    print(f"  - 传输启用: {manager.is_transfer_enabled()}")
    print(f"  - 有效输出路径: {manager.get_effective_output_path()}")
    print(f"  - 有效素材路径: {manager.get_effective_assets_path('test_draft_id')}")
    print(f"  - 状态文本: {manager.get_status_text()}")
    
    # 测试单例模式
    manager2 = get_draft_path_manager()
    print(f"\n单例模式测试:")
    print(f"  - 两个实例是同一个: {manager is manager2}")
    print(f"  - 第二个实例的传输启用状态: {manager2.is_transfer_enabled()}")
    
    # 测试检测默认路径
    detected = manager.detect_default_draft_folder()
    print(f"\n自动检测剪映草稿文件夹:")
    print(f"  - 检测结果: {detected}")
    
    print(f"\n=== 测试完成 ===")
    return True

if __name__ == "__main__":
    try:
        success = test_draft_path_manager()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
