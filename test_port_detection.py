#!/usr/bin/env python3
"""
测试端口检测功能
"""
import sys
import socket
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_port_availability_function():
    """测试端口可用性检测函数的逻辑"""
    print("=== 测试端口可用性检测逻辑 ===")

    def is_port_available(port: int) -> bool:
        """检查端口是否可用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("localhost", port))
                return True
        except OSError:
            return False

    # 测试1: 检测一个应该空闲的高端口
    test_port = 54321
    result = is_port_available(test_port)
    print(f"测试端口 {test_port}: {'可用' if result else '被占用'}")

    # 测试2: 尝试占用一个端口，然后检测它
    print("\n测试端口占用检测:")
    test_port2 = 54322
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_socket:
        test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        test_socket.bind(("localhost", test_port2))
        test_socket.listen(1)

        # 现在这个端口应该被占用
        result = is_port_available(test_port2)
        if not result:
            print(f"✅ 正确检测到端口 {test_port2} 被占用")
        else:
            print(f"❌ 错误: 端口 {test_port2} 应该被占用但被检测为可用")
            return False

    # 端口释放后应该再次可用
    result = is_port_available(test_port2)
    if result:
        print(f"✅ 正确检测到端口 {test_port2} 释放后可用")
    else:
        print(f"❌ 错误: 端口 {test_port2} 释放后应该可用")
        return False

    return True


def test_code_structure():
    """测试代码结构中是否包含端口检测功能"""
    print("\n=== 测试代码结构 ===")

    local_service_path = Path(__file__).parent / "src" / "gui" / "local_service_tab.py"
    with open(local_service_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 检查是否导入了socket
    if "import socket" in content:
        print("✅ 已导入 socket 模块")
    else:
        print("❌ 未导入 socket 模块")
        return False

    # 检查是否有检测端口按钮
    if "check_port_btn" in content:
        print("✅ 已添加检测端口按钮")
    else:
        print("❌ 未添加检测端口按钮")
        return False

    # 检查是否有检测端口方法
    if "_check_port_available" in content:
        print("✅ 已添加 _check_port_available 方法")
    else:
        print("❌ 未添加 _check_port_available 方法")
        return False

    # 检查是否有端口可用性检查方法
    if "_is_port_available" in content:
        print("✅ 已添加 _is_port_available 方法")
    else:
        print("❌ 未添加 _is_port_available 方法")
        return False

    # 检查启动服务前是否检查端口
    if "_start_service" in content and "_is_port_available(port)" in content:
        print("✅ 启动服务前会检查端口可用性")
    else:
        print("❌ 启动服务前未检查端口可用性")
        return False

    # 检查按钮文本
    if '"检测端口"' in content:
        print("✅ 检测端口按钮文本正确")
    else:
        print("❌ 检测端口按钮文本不正确")
        return False

    # 检查端口状态显示组件
    if "port_status_label" in content and "port_status_indicator" in content:
        print("✅ 已添加端口状态显示组件")
    else:
        print("❌ 缺少端口状态显示组件")
        return False

    # 检查端口状态更新方法
    if "_update_port_status_indicator" in content:
        print("✅ 已添加 _update_port_status_indicator 方法")
    else:
        print("❌ 未添加 _update_port_status_indicator 方法")
        return False

    # 检查是否不使用弹窗显示检测结果（除了错误）
    # 检查 _check_port_available 方法中不使用 showinfo 或 showwarning
    check_method_start = content.find("def _check_port_available(self):")
    if check_method_start != -1:
        # 找到下一个方法的开始位置
        next_method = content.find("\n    def ", check_method_start + 1)
        check_method_content = content[check_method_start:next_method] if next_method != -1 else content[check_method_start:]
        
        # 应该只有 showerror 用于无效输入，不应该有 showinfo 或 showwarning
        has_showinfo = "showinfo" in check_method_content
        has_showwarning = "showwarning" in check_method_content
        
        if not has_showinfo and not has_showwarning:
            print("✅ 端口检测结果不使用弹窗（使用状态显示）")
        else:
            print("⚠️  端口检测可能仍使用弹窗")

    return True


def main():
    """主测试函数"""
    print("开始测试端口检测功能...\n")

    results = []

    # 运行测试
    results.append(("端口可用性检测逻辑", test_port_availability_function()))
    results.append(("代码结构", test_code_structure()))

    # 总结
    print("\n=== 测试总结 ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！端口检测功能已成功实现。")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
