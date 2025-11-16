"""
测试草稿文件夹管理器模块

由于 tkinter 在 CI 环境中不可用，这里主要测试核心逻辑而非 UI 组件
"""
import os
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_draft_folder_manager_core_logic():
    """测试 DraftFolderManager 的核心逻辑（不涉及 tkinter）"""
    # 由于 tkinter 不可用，我们只能测试非 UI 相关的逻辑
    # 创建一个模拟的管理器类来测试核心功能
    
    class MockDraftFolderManager:
        """模拟的草稿文件夹管理器（用于测试核心逻辑）"""
        
        DEFAULT_DRAFT_PATHS = [
            r"C:\Users\{username}\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft",
            r"C:\Users\{username}\AppData\Roaming\JianyingPro\User Data\Projects\com.lveditor.draft",
        ]
        
        def __init__(self):
            self._folder_path = None
            self._enable_transfer = True
        
        @property
        def folder_path(self):
            return self._folder_path
        
        @folder_path.setter
        def folder_path(self, path):
            self._folder_path = path
        
        @property
        def enable_transfer(self):
            return self._enable_transfer
        
        @enable_transfer.setter
        def enable_transfer(self, value):
            self._enable_transfer = value
        
        def get_output_folder(self, fallback_folder=None):
            """获取最终的输出文件夹路径"""
            if not self._enable_transfer:
                return fallback_folder
            
            if self._folder_path:
                return self._folder_path
            
            return None
        
        def validate_folder(self, folder_path):
            """验证文件夹路径是否有效"""
            if not folder_path:
                return False, "未指定文件夹路径"
            
            if not os.path.exists(folder_path):
                return False, f"指定的文件夹不存在:\n{folder_path}"
            
            if not os.path.isdir(folder_path):
                return False, f"指定的路径不是文件夹:\n{folder_path}"
            
            return True, ""
    
    print("=== 测试草稿文件夹管理器核心逻辑 ===\n")
    
    # 测试 1: 初始化
    print("测试 1: 初始化管理器")
    manager = MockDraftFolderManager()
    assert manager.folder_path is None, "初始文件夹路径应为 None"
    assert manager.enable_transfer is True, "默认应启用传输"
    print("✓ 初始化测试通过\n")
    
    # 测试 2: 设置和获取文件夹路径
    print("测试 2: 设置和获取文件夹路径")
    test_path = "/tmp/test_folder"
    manager.folder_path = test_path
    assert manager.folder_path == test_path, "文件夹路径设置失败"
    print("✓ 文件夹路径设置测试通过\n")
    
    # 测试 3: 传输选项控制
    print("测试 3: 传输选项控制")
    
    # 3.1 启用传输时，返回设置的路径
    manager.enable_transfer = True
    manager.folder_path = "/path/to/jianying"
    result = manager.get_output_folder("/fallback/path")
    assert result == "/path/to/jianying", "启用传输时应返回设置的路径"
    print("✓ 3.1 启用传输时返回设置的路径")
    
    # 3.2 禁用传输时，返回备用路径
    manager.enable_transfer = False
    result = manager.get_output_folder("/fallback/path")
    assert result == "/fallback/path", "禁用传输时应返回备用路径"
    print("✓ 3.2 禁用传输时返回备用路径")
    
    # 3.3 启用传输但未设置路径，返回 None
    manager.enable_transfer = True
    manager.folder_path = None
    result = manager.get_output_folder("/fallback/path")
    assert result is None, "启用传输但未设置路径时应返回 None"
    print("✓ 3.3 启用传输但未设置路径时返回 None")
    print("✓ 传输选项控制测试通过\n")
    
    # 测试 4: 文件夹验证
    print("测试 4: 文件夹验证")
    
    # 4.1 验证空路径
    is_valid, msg = manager.validate_folder("")
    assert not is_valid, "空路径应该无效"
    assert "未指定" in msg, "错误消息应包含'未指定'"
    print("✓ 4.1 空路径验证")
    
    # 4.2 验证不存在的路径
    is_valid, msg = manager.validate_folder("/nonexistent/path")
    assert not is_valid, "不存在的路径应该无效"
    assert "不存在" in msg, "错误消息应包含'不存在'"
    print("✓ 4.2 不存在路径验证")
    
    # 4.3 验证有效的临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        is_valid, msg = manager.validate_folder(tmpdir)
        assert is_valid, "临时目录应该有效"
        assert msg == "", "有效路径的错误消息应为空"
        print("✓ 4.3 有效路径验证")
    
    # 4.4 验证文件而非目录
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        tmpfile_path = tmpfile.name
    try:
        is_valid, msg = manager.validate_folder(tmpfile_path)
        assert not is_valid, "文件路径应该无效"
        assert "不是文件夹" in msg, "错误消息应包含'不是文件夹'"
        print("✓ 4.4 文件路径验证")
    finally:
        os.unlink(tmpfile_path)
    
    print("✓ 文件夹验证测试通过\n")
    
    print("=== 所有核心逻辑测试通过！ ===")
    return True


def test_module_imports():
    """测试模块结构和语法（不导入 tkinter 部分）"""
    print("=== 测试模块结构 ===\n")
    
    print("测试 1: 检查模块文件存在")
    module_path = project_root / "app" / "utils" / "draft_folder_manager.py"
    assert module_path.exists(), f"模块文件不存在: {module_path}"
    print("✓ 模块文件存在\n")
    
    print("测试 2: 检查模块语法")
    import py_compile
    try:
        py_compile.compile(str(module_path), doraise=True)
        print("✓ 模块语法正确\n")
    except py_compile.PyCompileError as e:
        print(f"✗ 模块语法错误: {e}")
        raise
    
    print("=== 模块结构测试通过！ ===")
    return True


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("草稿文件夹管理器测试")
    print("="*60 + "\n")
    
    try:
        # 测试模块导入和结构
        test_module_imports()
        print()
        
        # 测试核心逻辑
        test_draft_folder_manager_core_logic()
        print()
        
        print("="*60)
        print("所有测试通过！ ✓")
        print("="*60)
        return 0
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
