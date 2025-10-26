#!/usr/bin/env python3
"""
验证脚本 - 验证草稿生成器迁移是否成功
Migration Verification Script
"""
import sys
from pathlib import Path

def check_directories():
    """检查必要的目录是否存在"""
    print("=== 检查目录结构 ===")
    required_dirs = [
        'coze_plugin',
        'src',
        'src/gui',
        'src/utils',
        'test_utils',
        'test_utils/converters',
        'resources',
        'docs/draft_generator',
        '.github/workflows'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        exists = Path(dir_path).exists()
        status = "✅" if exists else "❌"
        print(f"{status} {dir_path}")
        if not exists:
            all_exist = False
    
    return all_exist

def check_files():
    """检查关键文件是否存在"""
    print("\n=== 检查关键文件 ===")
    required_files = [
        'build.py',
        '.github/workflows/build.yml',
        'src/main.py',
        'src/utils/draft_generator.py',
        'src/utils/coze_parser.py',
        'src/utils/converter.py',
        'src/utils/material_manager.py',
        'test_utils/converters/coze_output_converter.py',
        'resources/README.md'
    ]
    
    all_exist = True
    for file_path in required_files:
        exists = Path(file_path).exists()
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")
        if not exists:
            all_exist = False
    
    return all_exist

def check_imports():
    """检查关键模块是否可以导入"""
    print("\n=== 检查模块导入 ===")
    imports_to_test = [
        ("Coze Plugin Main", "from coze_plugin.main import Coze2JianYing"),
        ("Draft Generator", "import sys; sys.path.insert(0, 'src'); from utils.draft_generator import DraftGenerator"),
        ("Coze Parser", "import sys; sys.path.insert(0, 'src'); from utils.coze_parser import CozeOutputParser"),
        ("Converter", "import sys; sys.path.insert(0, 'src'); from utils.converter import DraftInterfaceConverter"),
        ("Material Manager", "import sys; sys.path.insert(0, 'src'); from utils.material_manager import MaterialManager"),
        ("Output Converter", "from test_utils.converters.coze_output_converter import convert_coze_to_standard_format"),
        ("Build Script", "import build"),
    ]
    
    all_success = True
    for name, import_stmt in imports_to_test:
        try:
            exec(import_stmt)
            print(f"✅ {name}")
        except Exception as e:
            print(f"❌ {name}: {e}")
            all_success = False
    
    return all_success

def check_dependencies():
    """检查依赖是否安装"""
    print("\n=== 检查依赖包 ===")
    dependencies = [
        ('pyJianYingDraft', 'pyJianYingDraft'),
        ('requests', 'requests'),
        ('pytest', 'pytest'),
        ('black', 'black'),
        ('flake8', 'flake8'),
        ('PyInstaller', 'PyInstaller')
    ]
    
    all_installed = True
    for dep_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {dep_name}")
        except ImportError:
            print(f"❌ {dep_name} - 未安装")
            all_installed = False
    
    return all_installed

def main():
    """主验证函数"""
    print("=" * 60)
    print("Coze2JianYing 项目迁移验证")
    print("=" * 60)
    print()
    
    results = {
        '目录结构': check_directories(),
        '关键文件': check_files(),
        '依赖包': check_dependencies(),
        '模块导入': check_imports(),
    }
    
    print("\n" + "=" * 60)
    print("验证结果汇总")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 所有验证通过！迁移成功！")
        return 0
    else:
        print("⚠️  部分验证失败，请检查上述错误")
        return 1

if __name__ == '__main__':
    sys.exit(main())
