"""
端插件服务测试

测试 LocalPluginService 的基本功能
"""

import json
from unittest.mock import Mock, patch, MagicMock

# 测试是否可以导入模块
def test_import_module():
    """测试模块导入"""
    try:
        from app.services.local_plugin_service import (
            LocalPluginService,
            create_draft_tool_handler,
            is_cozepy_available,
            PluginMode
        )
        print("✓ 模块导入成功")
        return True
    except ImportError as e:
        print(f"✗ 模块导入失败: {e}")
        return False


def test_cozepy_availability():
    """测试 cozepy 可用性检查"""
    from app.services.local_plugin_service import is_cozepy_available
    
    available = is_cozepy_available()
    print(f"cozepy 可用性: {available}")
    
    if available:
        print("✓ cozepy 可用")
    else:
        print("⚠ cozepy 不可用，部分功能将受限")
    
    return True


def test_plugin_mode_enum():
    """测试插件模式枚举"""
    from app.services.local_plugin_service import PluginMode
    
    assert PluginMode.BOT == "bot"
    assert PluginMode.WORKFLOW == "workflow"
    print("✓ 插件模式枚举正常")
    return True


def test_draft_tool_handler_creation():
    """测试草稿工具处理函数创建"""
    from app.services.local_plugin_service import create_draft_tool_handler
    
    # 创建模拟的 DraftGenerator
    mock_generator = Mock()
    mock_generator.generate.return_value = ["draft_id_1", "draft_id_2"]
    
    # 创建处理函数
    handler = create_draft_tool_handler(mock_generator)
    
    # 测试成功场景
    result = handler({"content": '{"test": "data"}'})
    result_dict = json.loads(result)
    
    assert result_dict["status"] == "success"
    assert len(result_dict["draft_ids"]) == 2
    print("✓ 草稿工具处理函数创建成功")
    
    # 测试缺少参数场景
    result = handler({})
    result_dict = json.loads(result)
    assert result_dict["status"] == "error"
    print("✓ 参数验证正常")
    
    return True


def test_service_initialization():
    """测试服务初始化（需要 cozepy）"""
    from app.services.local_plugin_service import LocalPluginService, is_cozepy_available
    
    if not is_cozepy_available():
        print("⚠ 跳过测试：cozepy 不可用")
        return True
    
    try:
        # 使用测试 token 初始化
        service = LocalPluginService(
            coze_token="test_token",
            base_url="https://api.coze.cn"
        )
        
        assert service.coze is not None
        assert service.is_running is False
        assert len(service.tool_handlers) == 0
        
        print("✓ 服务初始化成功")
        return True
    
    except Exception as e:
        print(f"✗ 服务初始化失败: {e}")
        return False


def test_tool_registration():
    """测试工具注册"""
    from app.services.local_plugin_service import LocalPluginService, is_cozepy_available
    
    if not is_cozepy_available():
        print("⚠ 跳过测试：cozepy 不可用")
        return True
    
    service = LocalPluginService(coze_token="test_token")
    
    # 注册测试工具
    def test_tool(args: dict) -> str:
        return json.dumps({"result": "ok"})
    
    service.register_tool("test_tool", test_tool)
    
    assert "test_tool" in service.tool_handlers
    print("✓ 工具注册成功")
    
    # 测试执行工具
    result = service._execute_tool("test_tool", '{}')
    result_dict = json.loads(result)
    assert result_dict["result"] == "ok"
    print("✓ 工具执行成功")
    
    return True


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("端插件服务测试")
    print("=" * 60)
    
    tests = [
        ("模块导入", test_import_module),
        ("cozepy 可用性", test_cozepy_availability),
        ("插件模式枚举", test_plugin_mode_enum),
        ("草稿工具处理函数", test_draft_tool_handler_creation),
    ]
    
    # 如果 cozepy 可用，添加更多测试
    try:
        from app.services.local_plugin_service import is_cozepy_available
        if is_cozepy_available():
            tests.extend([
                ("服务初始化", test_service_initialization),
                ("工具注册", test_tool_registration),
            ])
    except:
        pass
    
    results = []
    for name, test_func in tests:
        print(f"\n测试: {name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            results.append((name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"通过: {passed}/{total}")
    
    for name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {name}")
    
    return passed == total


if __name__ == "__main__":
    import sys
    sys.path.insert(0, '/home/runner/work/Coze2JianYing/Coze2JianYing')
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
