"""
测试草稿配置管理器的集成
"""
import os
import tempfile
from app.utils.draft_config_manager import get_draft_config_manager
from app.utils.draft_saver import DraftSaver
from app.config import get_config


def test_draft_config_integration():
    """测试草稿配置管理器与 draft_saver 的集成"""
    print("测试草稿配置管理器集成...\n")
    
    # 获取配置管理器
    config_mgr = get_draft_config_manager()
    app_config = get_config()
    
    print("1. 测试默认配置（不传输到草稿文件夹）")
    config_mgr.transfer_to_draft_folder = False
    config_mgr.draft_folder_path = None
    
    saver = DraftSaver()
    print(f"   输出目录: {saver.output_dir}")
    print(f"   预期: {app_config.drafts_dir}")
    assert saver.output_dir == app_config.drafts_dir, "默认配置输出目录不正确"
    print("   ✓ 通过\n")
    
    print("2. 测试自定义路径配置（传输到草稿文件夹）")
    test_folder = tempfile.mkdtemp()
    config_mgr.draft_folder_path = test_folder
    config_mgr.transfer_to_draft_folder = True
    
    saver = DraftSaver()
    print(f"   输出目录: {saver.output_dir}")
    print(f"   预期: {test_folder}")
    assert saver.output_dir == test_folder, "自定义路径配置输出目录不正确"
    print("   ✓ 通过\n")
    
    print("3. 测试传输选项关闭时使用本地数据目录")
    config_mgr.transfer_to_draft_folder = False
    
    saver = DraftSaver()
    print(f"   输出目录: {saver.output_dir}")
    print(f"   预期: {app_config.drafts_dir}")
    assert saver.output_dir == app_config.drafts_dir, "传输关闭时应使用本地数据目录"
    print("   ✓ 通过\n")
    
    print("4. 测试显式传入 output_dir 参数覆盖全局配置")
    custom_dir = tempfile.mkdtemp()
    saver = DraftSaver(output_dir=custom_dir)
    print(f"   输出目录: {saver.output_dir}")
    print(f"   预期: {custom_dir}")
    assert saver.output_dir == custom_dir, "显式传入的 output_dir 应覆盖全局配置"
    print("   ✓ 通过\n")
    
    # 清理临时目录
    os.rmdir(test_folder)
    os.rmdir(custom_dir)
    
    # 重置配置
    config_mgr.reset()
    
    print("✓ 所有测试通过!")


if __name__ == "__main__":
    test_draft_config_integration()
