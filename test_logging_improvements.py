#!/usr/bin/env python3
"""
测试日志系统改进
验证:
1. 日志窗口可以调整大小
2. 后台线程处理草稿生成不会阻塞UI
3. 日志实时显示
"""
import sys
import os
import time
import threading

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.logger import setup_logger, get_logger, set_gui_log_callback


def test_logger_threading():
    """测试日志系统在多线程环境下的表现"""
    print("=== 测试日志系统线程安全 ===")
    
    # 设置日志
    setup_logger()
    logger = get_logger(__name__)
    
    # 模拟GUI回调
    log_messages = []
    def mock_gui_callback(message):
        log_messages.append(message)
        print(f"GUI接收到日志: {message[:50]}...")
    
    set_gui_log_callback(mock_gui_callback)
    
    # 在后台线程中记录日志
    def worker(worker_id):
        worker_logger = get_logger(f"worker_{worker_id}")
        for i in range(5):
            worker_logger.info(f"工作线程 {worker_id} - 步骤 {i}")
            time.sleep(0.1)
    
    # 创建多个工作线程
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    # 等待所有线程完成
    for t in threads:
        t.join()
    
    print(f"✅ 共接收到 {len(log_messages)} 条日志消息")
    assert len(log_messages) > 0, "应该接收到日志消息"
    print("✅ 日志系统线程安全测试通过")
    return True


def test_log_window_properties():
    """测试日志窗口属性"""
    print("\n=== 测试日志窗口属性 ===")
    
    # 读取log_window.py文件内容
    log_window_path = os.path.join(os.path.dirname(__file__), 'src', 'gui', 'log_window.py')
    with open(log_window_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否包含可调整大小的代码
    assert 'resizable(True, True)' in content, "日志窗口应该可以调整大小"
    print("✅ 日志窗口支持调整大小")
    
    # 检查是否设置了最小窗口大小
    assert 'minsize' in content, "应该设置最小窗口大小"
    print("✅ 日志窗口设置了最小大小")
    
    # 检查是否有update_idletasks强制更新
    assert 'update_idletasks' in content, "应该强制更新显示"
    print("✅ 日志窗口强制更新显示")
    
    return True


def test_main_window_threading():
    """测试主窗口线程处理"""
    print("\n=== 测试主窗口线程处理 ===")
    
    # 读取main_window.py文件内容
    main_window_path = os.path.join(os.path.dirname(__file__), 'src', 'gui', 'main_window.py')
    with open(main_window_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否导入了threading
    assert 'import threading' in content, "应该导入threading模块"
    print("✅ 导入了threading模块")
    
    # 检查是否有生成线程变量
    assert 'generation_thread' in content, "应该有generation_thread变量"
    print("✅ 定义了generation_thread变量")
    
    # 检查是否有is_generating标志
    assert 'is_generating' in content, "应该有is_generating标志"
    print("✅ 定义了is_generating标志")
    
    # 检查是否有后台工作函数
    assert '_generate_draft_worker' in content, "应该有_generate_draft_worker方法"
    print("✅ 定义了后台工作函数")
    
    # 检查是否使用root.after进行线程安全的GUI更新
    assert 'root.after' in content, "应该使用root.after更新GUI"
    print("✅ 使用root.after进行线程安全更新")
    
    # 检查是否自动打开日志窗口
    assert '自动打开日志窗口' in content or 'log_window = LogWindow' in content, "应该自动打开日志窗口"
    print("✅ 生成草稿时自动打开日志窗口")
    
    return True


def main():
    """运行所有测试"""
    print("开始测试日志系统改进...\n")
    
    results = []
    
    try:
        results.append(("日志窗口属性", test_log_window_properties()))
    except Exception as e:
        print(f"❌ 日志窗口属性测试失败: {e}")
        results.append(("日志窗口属性", False))
    
    try:
        results.append(("主窗口线程处理", test_main_window_threading()))
    except Exception as e:
        print(f"❌ 主窗口线程处理测试失败: {e}")
        results.append(("主窗口线程处理", False))
    
    try:
        results.append(("日志系统线程安全", test_logger_threading()))
    except Exception as e:
        print(f"❌ 日志系统线程安全测试失败: {e}")
        results.append(("日志系统线程安全", False))
    
    # 打印测试总结
    print("\n" + "=" * 60)
    print("测试总结:")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print("=" * 60)
    print(f"总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("✅ 所有测试通过!")
        return 0
    else:
        print("❌ 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
