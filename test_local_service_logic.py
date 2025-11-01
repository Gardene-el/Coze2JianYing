#!/usr/bin/env python3
"""
验证本地服务标签页的代码逻辑（不需要GUI）
"""
import ast
import sys
from pathlib import Path

def analyze_python_file(filepath):
    """分析Python文件的AST结构"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return ast.parse(content, filename=str(filepath))

def test_local_service_tab_structure():
    """测试LocalServiceTab的代码结构"""
    print("=== 测试 LocalServiceTab 结构 ===")
    
    filepath = Path(__file__).parent / "src" / "gui" / "local_service_tab.py"
    tree = analyze_python_file(filepath)
    
    # 查找LocalServiceTab类
    local_service_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "LocalServiceTab":
            local_service_class = node
            break
    
    if not local_service_class:
        print("❌ 未找到LocalServiceTab类")
        return False
    
    print("✅ 找到LocalServiceTab类")
    
    # 检查方法
    methods = {node.name for node in local_service_class.body if isinstance(node, ast.FunctionDef)}
    
    required_methods = {
        '__init__',
        '_create_widgets',
        '_setup_layout',
        'cleanup',
        '_select_output_folder',
        '_auto_detect_folder',
        '_start_service',
        '_stop_service',
        '_run_service',
        '_update_status_indicator',
        '_append_to_info',
        '_on_service_error'
    }
    
    missing_methods = required_methods - methods
    if missing_methods:
        print(f"❌ 缺少方法: {missing_methods}")
        return False
    
    print(f"✅ 包含所有必需的方法 ({len(required_methods)} 个)")
    
    # 检查继承
    if local_service_class.bases:
        base_name = None
        for base in local_service_class.bases:
            if isinstance(base, ast.Name):
                base_name = base.id
                break
        
        if base_name == "BaseTab":
            print("✅ 正确继承自 BaseTab")
        else:
            print(f"❌ 继承自 {base_name}，应该继承自 BaseTab")
            return False
    else:
        print("❌ 没有继承任何基类")
        return False
    
    return True

def test_main_window_integration():
    """测试MainWindow中的集成"""
    print("\n=== 测试 MainWindow 集成 ===")
    
    filepath = Path(__file__).parent / "src" / "gui" / "main_window.py"
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查导入
    if "from gui.local_service_tab import LocalServiceTab" in content:
        print("✅ 已导入 LocalServiceTab")
    else:
        print("❌ 未导入 LocalServiceTab")
        return False
    
    # 检查实例化
    if "LocalServiceTab(self.notebook, log_callback=self._on_log_message)" in content:
        print("✅ 已创建 LocalServiceTab 实例")
    else:
        print("❌ 未创建 LocalServiceTab 实例")
        return False
    
    # 检查注释
    if "# 创建本地服务标签页" in content or "本地服务标签页" in content:
        print("✅ 已添加本地服务标签页的注释")
    else:
        print("⚠️  缺少本地服务标签页的注释")
    
    return True

def test_draft_generator_tab_rename():
    """测试DraftGeneratorTab的重命名"""
    print("\n=== 测试 DraftGeneratorTab 重命名 ===")
    
    filepath = Path(__file__).parent / "src" / "gui" / "draft_generator_tab.py"
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '"手动草稿生成"' in content:
        print('✅ 标签页名称已更改为 "手动草稿生成"')
    else:
        print('❌ 标签页名称未更改')
        return False
    
    # 确保不再使用旧名称
    if 'super().__init__(parent, "草稿生成")' in content:
        print('❌ 仍使用旧名称 "草稿生成"')
        return False
    
    return True

def test_folder_detection_logic():
    """测试文件夹检测逻辑"""
    print("\n=== 测试文件夹检测逻辑 ===")
    
    filepath = Path(__file__).parent / "src" / "gui" / "local_service_tab.py"
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否使用DraftGenerator
    if "self.draft_generator = DraftGenerator()" in content:
        print("✅ 使用 DraftGenerator 进行文件夹检测")
    else:
        print("❌ 未使用 DraftGenerator")
        return False
    
    # 检查自动检测方法
    if "detect_default_draft_folder" in content:
        print("✅ 调用 detect_default_draft_folder 方法")
    else:
        print("❌ 未调用 detect_default_draft_folder 方法")
        return False
    
    # 检查选择文件夹功能
    if "filedialog.askdirectory" in content:
        print("✅ 支持手动选择文件夹")
    else:
        print("❌ 不支持手动选择文件夹")
        return False
    
    return True

def test_service_management_logic():
    """测试服务管理逻辑"""
    print("\n=== 测试服务管理逻辑 ===")
    
    filepath = Path(__file__).parent / "src" / "gui" / "local_service_tab.py"
    tree = analyze_python_file(filepath)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查服务状态管理
    if "self.service_running" in content:
        print("✅ 有服务运行状态标志")
    else:
        print("❌ 缺少服务运行状态标志")
        return False
    
    # 检查线程管理
    if "threading.Thread" in content:
        print("✅ 使用线程运行服务")
    else:
        print("❌ 未使用线程运行服务")
        return False
    
    # 检查占位符说明
    if "占位符" in content or "placeholder" in content.lower():
        print("✅ 包含占位符说明")
    else:
        print("⚠️  缺少占位符说明")
    
    # 检查端口配置
    if "self.service_port" in content or "port" in content:
        print("✅ 支持端口配置")
    else:
        print("❌ 不支持端口配置")
        return False
    
    # 检查端口检测功能
    if "_is_port_available" in content:
        print("✅ 包含端口可用性检测方法")
    else:
        print("❌ 缺少端口可用性检测方法")
        return False
    
    # 检查socket导入
    if "import socket" in content:
        print("✅ 导入 socket 模块用于端口检测")
    else:
        print("❌ 未导入 socket 模块")
        return False
    
    return True

def test_ui_components():
    """测试UI组件"""
    print("\n=== 测试UI组件 ===")
    
    filepath = Path(__file__).parent / "src" / "gui" / "local_service_tab.py"
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_components = [
        "folder_frame",
        "service_frame",
        "start_service_btn",
        "stop_service_btn",
        "check_port_btn",
        "port_status_label",
        "port_status_indicator",
        "service_status_label",
        "service_status_indicator",
        "info_text",
        "port_entry"
    ]
    
    missing_components = []
    for component in required_components:
        if f"self.{component}" in content:
            print(f"✅ 包含组件: {component}")
        else:
            print(f"❌ 缺少组件: {component}")
            missing_components.append(component)
    
    if missing_components:
        return False
    
    return True

def main():
    """主测试函数"""
    print("开始验证本地服务标签页的代码逻辑...\n")
    
    tests = [
        ("LocalServiceTab结构", test_local_service_tab_structure),
        ("MainWindow集成", test_main_window_integration),
        ("DraftGeneratorTab重命名", test_draft_generator_tab_rename),
        ("文件夹检测逻辑", test_folder_detection_logic),
        ("服务管理逻辑", test_service_management_logic),
        ("UI组件", test_ui_components),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试 {test_name} 出错: {e}")
            results.append((test_name, False))
    
    # 总结
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
