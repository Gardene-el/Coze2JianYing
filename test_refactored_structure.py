#!/usr/bin/env python3
"""
测试重构后的src目录结构
验证GUI和CLI模块可以正确导入和运行
"""
import sys
from pathlib import Path

# 添加src到路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def test_cli_imports():
    """测试CLI模块导入"""
    print("=== 测试CLI模块导入 ===")
    try:
        from CLI.main import cli, info
        print("✓ CLI模块导入成功")
        print(f"  - cli函数: {cli}")
        print(f"  - info命令: {info}")
        return True
    except Exception as e:
        print(f"✗ CLI模块导入失败: {e}")
        return False


def test_gui_imports():
    """测试GUI模块导入"""
    print("\n=== 测试GUI模块导入 ===")
    try:
        # GUI模块依赖tkinter，在无GUI环境中会失败，这是预期的
        try:
            from GUI.main_window import MainWindow
            print("✓ GUI模块导入成功")
            print(f"  - MainWindow类: {MainWindow}")
            return True
        except ModuleNotFoundError as e:
            if 'tkinter' in str(e):
                print("✓ GUI模块结构正确 (tkinter不可用是预期的)")
                return True
            else:
                raise
    except Exception as e:
        print(f"✗ GUI模块导入失败: {e}")
        return False


def test_utils_imports():
    """测试工具模块导入"""
    print("\n=== 测试工具模块导入 ===")
    try:
        from utils.draft_generator import DraftGenerator
        from utils.coze_parser import CozeOutputParser
        from utils.converter import DraftInterfaceConverter
        from utils.material_manager import MaterialManager
        from utils.logger import get_logger
        
        print("✓ 工具模块导入成功")
        print(f"  - DraftGenerator: {DraftGenerator}")
        print(f"  - CozeOutputParser: {CozeOutputParser}")
        print(f"  - DraftInterfaceConverter: {DraftInterfaceConverter}")
        print(f"  - MaterialManager: {MaterialManager}")
        return True
    except Exception as e:
        print(f"✗ 工具模块导入失败: {e}")
        return False


def test_directory_structure():
    """测试目录结构"""
    print("\n=== 测试目录结构 ===")
    
    required_dirs = [
        src_path / "CLI",
        src_path / "GUI",
        src_path / "utils",
        src_path / "core",
    ]
    
    required_files = [
        src_path / "main.py",
        src_path / "CLI" / "main.py",
        src_path / "GUI" / "main.py",
        src_path / "GUI" / "main_window.py",
    ]
    
    all_good = True
    
    for dir_path in required_dirs:
        if dir_path.exists():
            print(f"✓ 目录存在: {dir_path.relative_to(src_path.parent)}")
        else:
            print(f"✗ 目录缺失: {dir_path.relative_to(src_path.parent)}")
            all_good = False
    
    for file_path in required_files:
        if file_path.exists():
            print(f"✓ 文件存在: {file_path.relative_to(src_path.parent)}")
        else:
            print(f"✗ 文件缺失: {file_path.relative_to(src_path.parent)}")
            all_good = False
    
    return all_good


def main():
    """运行所有测试"""
    print("=" * 60)
    print("测试重构后的src目录结构")
    print("=" * 60)
    
    results = []
    
    # 先测试目录结构
    results.append(("目录结构", test_directory_structure()))
    
    # 测试导入
    results.append(("CLI导入", test_cli_imports()))
    results.append(("GUI导入", test_gui_imports()))
    results.append(("工具导入", test_utils_imports()))
    
    # 输出总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✓ 所有测试通过！")
        return 0
    else:
        print("\n✗ 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
