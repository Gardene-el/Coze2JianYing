#!/usr/bin/env python3
"""
测试 generate_script 工具

验证脚本生成功能是否正常工作
"""
import sys
import os
import json
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 模拟 Coze runtime
class MockArgs:
    class Logger:
        def info(self, msg):
            print(f"[INFO] {msg}")
        
        def error(self, msg):
            print(f"[ERROR] {msg}")
    
    def __init__(self, input_data):
        self.input = input_data
        self.logger = self.Logger()


def test_generate_script_basic():
    """测试基本的脚本生成功能"""
    print("=" * 60)
    print("测试 generate_script 工具 - 基本功能")
    print("=" * 60)
    
    # 创建测试草稿
    print("\n步骤 1: 创建测试草稿配置...")
    
    import uuid
    draft_id = str(uuid.uuid4())
    draft_folder = Path("/tmp/jianying_assistant/drafts") / draft_id
    draft_folder.mkdir(parents=True, exist_ok=True)
    
    test_config = {
        "draft_name": "测试项目",
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "tracks": [
            {
                "track_type": "video",
                "segments": [
                    {
                        "segment_type": "image",
                        "material_url": "https://example.com/test.jpg",
                        "time_range": {"start": 0, "duration": 3000000}
                    }
                ]
            },
            {
                "track_type": "audio",
                "segments": [
                    {
                        "segment_type": "audio",
                        "material_url": "https://example.com/test.mp3",
                        "time_range": {"start": 0, "duration": 5000000},
                        "volume": 0.8
                    }
                ]
            }
        ]
    }
    
    # 保存配置
    config_file = draft_folder / "draft_config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(test_config, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 测试配置已保存到: {config_file}")
    
    # 导入工具（需要先模拟 runtime 模块）
    print("\n步骤 2: 导入 generate_script 工具...")
    
    # 创建模拟的 runtime 模块
    import types
    from typing import Generic, TypeVar
    
    runtime = types.ModuleType('runtime')
    
    T = TypeVar('T')
    
    class Args(Generic[T]):
        def __init__(self, input_data):
            self.input = input_data
            self.logger = MockArgs.Logger()
    
    runtime.Args = Args
    sys.modules['runtime'] = runtime
    
    sys.path.insert(0, str(project_root / "coze_plugin" / "tools" / "generate_script"))
    from handler import handler, Input
    
    print("✓ 工具导入成功")
    
    # 准备输入
    print("\n步骤 3: 准备输入参数...")
    input_data = Input(
        draft_ids=draft_id,
        api_base_url="http://127.0.0.1:8000",
        output_folder=None
    )
    
    args = MockArgs(input_data)
    print(f"✓ 输入参数: draft_ids={draft_id}")
    
    # 调用工具
    print("\n步骤 4: 调用 generate_script 工具...")
    result = handler(args)
    
    # 验证结果
    print("\n步骤 5: 验证结果...")
    
    assert result["success"], "脚本生成应该成功"
    print("✓ success = True")
    
    assert len(result["scripts"]) == 1, "应该生成 1 个脚本"
    print(f"✓ 生成了 {len(result['scripts'])} 个脚本")
    
    script_data = result["scripts"][0]
    assert script_data["draft_id"] == draft_id
    print(f"✓ draft_id 匹配: {script_data['draft_id']}")
    
    assert script_data["draft_name"] == "测试项目"
    print(f"✓ draft_name 匹配: {script_data['draft_name']}")
    
    script_content = script_data["script"]
    assert "#!/usr/bin/env python3" in script_content
    print("✓ 脚本包含 shebang")
    
    assert "import requests" in script_content
    print("✓ 脚本导入 requests")
    
    assert "API_BASE_URL" in script_content
    print("✓ 脚本包含 API_BASE_URL")
    
    assert "DRAFT_CONFIG" in script_content
    print("✓ 脚本包含 DRAFT_CONFIG")
    
    assert "DRAFT_CONTENT" in script_content
    print("✓ 脚本包含 DRAFT_CONTENT")
    
    assert "def create_draft():" in script_content
    print("✓ 脚本包含 create_draft 函数")
    
    assert "def main():" in script_content
    print("✓ 脚本包含 main 函数")
    
    # 保存生成的脚本到文件（用于人工检查）
    output_file = Path("/tmp/generated_test_script.py")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"\n✓ 生成的脚本已保存到: {output_file}")
    print(f"  你可以查看这个文件来验证脚本内容")
    
    # 清理测试文件
    print("\n步骤 6: 清理测试文件...")
    import shutil
    if draft_folder.exists():
        shutil.rmtree(draft_folder.parent.parent)
    print("✓ 测试文件已清理")
    
    print("\n" + "=" * 60)
    print("✅ 测试通过！generate_script 工具工作正常")
    print("=" * 60)
    
    return True


def test_generate_script_multiple():
    """测试批量生成多个脚本"""
    print("\n" + "=" * 60)
    print("测试 generate_script 工具 - 批量生成")
    print("=" * 60)
    
    # 创建多个测试草稿
    print("\n步骤 1: 创建多个测试草稿配置...")
    
    import uuid
    draft_ids = [str(uuid.uuid4()) for _ in range(3)]
    
    for draft_id in draft_ids:
        draft_folder = Path("/tmp/jianying_assistant/drafts") / draft_id
        draft_folder.mkdir(parents=True, exist_ok=True)
        
        test_config = {
            "draft_name": f"测试项目-{draft_id}",
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "tracks": []
        }
        
        config_file = draft_folder / "draft_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(test_config, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 创建了 {len(draft_ids)} 个测试配置")
    
    # 导入工具（runtime 模块已在第一个测试中模拟）
    sys.path.insert(0, str(project_root / "coze_plugin" / "tools" / "generate_script"))
    from handler import handler, Input
    
    # 准备输入（传入列表）
    print("\n步骤 2: 准备批量输入参数...")
    input_data = Input(
        draft_ids=draft_ids,
        api_base_url="http://127.0.0.1:8000"
    )
    
    args = MockArgs(input_data)
    
    # 调用工具
    print("\n步骤 3: 调用 generate_script 工具...")
    result = handler(args)
    
    # 验证结果
    print("\n步骤 4: 验证结果...")
    
    assert result["success"], "批量脚本生成应该成功"
    print("✓ success = True")
    
    assert len(result["scripts"]) == 3, "应该生成 3 个脚本"
    print(f"✓ 生成了 {len(result['scripts'])} 个脚本")
    
    for i, script_data in enumerate(result["scripts"]):
        assert script_data["draft_id"] in draft_ids
        print(f"✓ 脚本 {i+1}: draft_id = {script_data['draft_id']}")
    
    # 清理
    print("\n步骤 5: 清理测试文件...")
    import shutil
    test_folder = Path("/tmp/jianying_assistant")
    if test_folder.exists():
        shutil.rmtree(test_folder)
    print("✓ 测试文件已清理")
    
    print("\n" + "=" * 60)
    print("✅ 批量测试通过！")
    print("=" * 60)
    
    return True


def main():
    """运行所有测试"""
    print("\n" + "🧪" * 30)
    print("  generate_script 工具测试套件")
    print("🧪" * 30)
    
    results = []
    
    try:
        # 测试 1: 基本功能
        results.append(("基本功能测试", test_generate_script_basic()))
    except Exception as e:
        print(f"\n❌ 基本功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        results.append(("基本功能测试", False))
    
    try:
        # 测试 2: 批量生成
        results.append(("批量生成测试", test_generate_script_multiple()))
    except Exception as e:
        print(f"\n❌ 批量生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        results.append(("批量生成测试", False))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {test_name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\n通过: {passed_count}/{total_count}")
    
    if passed_count == total_count:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
