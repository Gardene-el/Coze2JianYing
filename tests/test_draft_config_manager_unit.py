"""
测试草稿配置管理器（不依赖外部库）
"""
import os
import sys
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.draft_config_manager import get_draft_config_manager
from app.config import get_config


def test_draft_config_manager():
    """测试草稿配置管理器的基本功能"""
    print("测试草稿配置管理器...\n")
    
    # 获取配置管理器
    config_mgr = get_draft_config_manager()
    app_config = get_config()
    
    print("1. 测试单例模式")
    config_mgr2 = get_draft_config_manager()
    assert config_mgr is config_mgr2, "应该返回同一个实例"
    print("   ✓ 单例模式正常工作\n")
    
    print("2. 测试默认值")
    assert config_mgr.draft_folder_path is None, "默认 draft_folder_path 应为 None"
    assert config_mgr.transfer_to_draft_folder is False, "默认 transfer_to_draft_folder 应为 False"
    print("   ✓ 默认值正确\n")
    
    print("3. 测试设置和获取路径")
    test_path = "/test/draft/folder"
    config_mgr.draft_folder_path = test_path
    assert config_mgr.draft_folder_path == test_path, "应该能正确设置和获取路径"
    print(f"   ✓ 路径设置成功: {test_path}\n")
    
    print("4. 测试传输选项")
    config_mgr.transfer_to_draft_folder = True
    assert config_mgr.transfer_to_draft_folder is True, "应该能正确设置传输选项"
    print("   ✓ 传输选项设置成功\n")
    
    print("5. 测试有效输出路径（传输模式）")
    effective_path = config_mgr.get_effective_output_path()
    assert effective_path == test_path, f"传输模式下应返回指定路径，实际: {effective_path}"
    print(f"   ✓ 传输模式输出路径: {effective_path}\n")
    
    print("6. 测试有效输出路径（非传输模式）")
    config_mgr.transfer_to_draft_folder = False
    effective_path = config_mgr.get_effective_output_path()
    assert effective_path == app_config.drafts_dir, f"非传输模式下应返回本地数据目录"
    print(f"   ✓ 非传输模式输出路径: {effective_path}\n")
    
    print("7. 测试路径验证")
    is_valid, msg = config_mgr.validate_draft_folder_path()
    assert is_valid is False, "不存在的路径应该验证失败"
    assert "不存在" in msg, f"错误消息应包含'不存在'，实际: {msg}"
    print(f"   ✓ 路径验证正常: {msg}\n")
    
    # 测试真实路径验证
    real_path = tempfile.mkdtemp()
    config_mgr.draft_folder_path = real_path
    is_valid, msg = config_mgr.validate_draft_folder_path()
    assert is_valid is True, f"存在的路径应该验证通过，实际: {msg}"
    print(f"   ✓ 真实路径验证通过: {real_path}\n")
    os.rmdir(real_path)
    
    print("8. 测试素材基础路径（传输模式）")
    test_folder = "/test/jianying/drafts"
    config_mgr.draft_folder_path = test_folder
    config_mgr.transfer_to_draft_folder = True
    assets_base = config_mgr.get_assets_base_path()
    assert assets_base == test_folder, f"传输模式下素材基础路径应该是草稿文件夹"
    print(f"   ✓ 传输模式素材路径: {assets_base}\n")
    
    print("9. 测试素材基础路径（非传输模式）")
    config_mgr.transfer_to_draft_folder = False
    assets_base = config_mgr.get_assets_base_path()
    assert assets_base == app_config.assets_dir, f"非传输模式下素材基础路径应该是本地 assets 目录"
    print(f"   ✓ 非传输模式素材路径: {assets_base}\n")
    
    print("10. 测试重置功能")
    config_mgr.reset()
    assert config_mgr.draft_folder_path is None, "重置后 draft_folder_path 应为 None"
    assert config_mgr.transfer_to_draft_folder is False, "重置后 transfer_to_draft_folder 应为 False"
    print("   ✓ 重置功能正常\n")
    
    print("✓ 所有测试通过!")


if __name__ == "__main__":
    test_draft_config_manager()
