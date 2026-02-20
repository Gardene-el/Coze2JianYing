#!/usr/bin/env python3
"""
测试 README 生成功能
验证 pyJianYingDraft docstring 解析和 README 格式
"""

from pathlib import Path
import sys

# 添加 handler_generator 到 path
sys.path.insert(0, str(Path(__file__).parent))

from handler_generator import FolderCreator, SchemaExtractor, APIEndpointInfo


def test_docstring_parsing():
    """测试 docstring 解析功能"""
    print("=" * 60)
    print("测试 pyJianYingDraft Docstring 解析")
    print("=" * 60)
    
    # 测试用例 1: 完整的 docstring
    docstring1 = """
    对应 pyJianYingDraft 代码：
    ```python
    audio_segment = draft.AudioSegment("audio.mp3", trange("0s", "5s"))
    ```
    对应 pyJianYingDraft 注释：
    ```
        创建音频片段, 并指定其时间信息、音量等设置
        片段创建完成后, 可通过add_segment方法将其添加到轨道中
        
        Args:
            material (`AudioMaterial` or `str`): 素材实例或素材路径, 若为路径则自动构造素材实例
            target_timerange (`Timerange`): 片段在轨道上的目标时间范围
            speed (`float`, optional): 播放速度, 默认为1.0
            volume (`float`, optional): 音量, 默认为1.0
        
        Raises:
            `ValueError`: 指定的或计算出的source_timerange超出了素材的时长范围
    ```
    """
    
    creator = FolderCreator("/tmp/test")
    result = creator._parse_pyjianying_docstring(docstring1)
    
    print("\n测试用例 1: 完整的 docstring")
    print(f"Description: {result['description']}")
    print(f"Args 数量: {len(result['args'])}")
    for arg in result['args']:
        print(f"  - {arg['name']} ({arg['type']}): {arg['description'][:50]}... [Required: {arg['required']}]")
    print(f"Raises 数量: {len(result['raises'])}")
    for exc in result['raises']:
        print(f"  - {exc['type']}: {exc['description'][:50]}...")
    
    # 测试用例 2: 只有 Args 的 docstring
    docstring2 = """
    对应 pyJianYingDraft 注释：
    ```
        Args:
            draft_name (`str`): 草稿名称, 即相应文件夹名称
            width (`int`): 视频宽度, 单位为像素
            height (`int`): 视频高度, 单位为像素
            fps (`int`, optional): 视频帧率. 默认为30.
        
        Raises:
            `FileExistsError`: 已存在与draft_name重名的草稿
    ```
    """
    
    result2 = creator._parse_pyjianying_docstring(docstring2)
    
    print("\n测试用例 2: 只有 Args 的 docstring")
    print(f"Description: {result2['description']}")
    print(f"Args 数量: {len(result2['args'])}")
    for arg in result2['args']:
        print(f"  - {arg['name']} ({arg['type']}): Required={arg['required']}")
    print(f"Raises 数量: {len(result2['raises'])}")
    
    # 测试用例 3: 空 docstring
    result3 = creator._parse_pyjianying_docstring(None)
    
    print("\n测试用例 3: 空 docstring")
    print(f"Description: {result3['description']}")
    print(f"Args 数量: {len(result3['args'])}")
    print(f"Raises 数量: {len(result3['raises'])}")
    
    print("\n✅ Docstring 解析测试完成!")
    return True


def test_readme_format():
    """测试 README 格式生成"""
    print("\n" + "=" * 60)
    print("测试 README 格式生成")
    print("=" * 60)
    
    # 加载 schema
    project_root = Path(__file__).parent.parent
    schema_file = project_root / "app" / "schemas" / "general_schemas.py"
    schema_extractor = SchemaExtractor(str(schema_file))
    
    # 创建测试 endpoint
    endpoint = APIEndpointInfo(
        func_name="create_test_segment",
        path="/test/create",
        has_draft_id=False,
        has_segment_id=False,
        request_model="CreateAudioSegmentRequest",
        response_model="CreateSegmentResponse",
        path_params=[],
        source_file="test.py",
        docstring="""
        对应 pyJianYingDraft 注释：
        ```
            测试片段创建功能
            
            Args:
                material (`str`): 素材路径
                timerange (`Timerange`): 时间范围
            
            Raises:
                `ValueError`: 参数错误
        ```
        """
    )
    
    creator = FolderCreator("/tmp/test", schema_extractor)
    readme = creator.generate_readme(endpoint)
    
    print("\n生成的 README 预览:")
    print("-" * 60)
    print(readme[:1000] + "...")
    print("-" * 60)
    
    # 验证关键部分
    assert "## 工具名称" in readme
    assert "## 工具介绍" in readme
    # Description 标签已移除，但描述内容应该存在
    assert "测试片段创建功能" in readme
    # Args 和 Raises 标签已移除
    assert "**Args:**" not in readme
    assert "**Raises:**" not in readme
    assert "## 输入参数" in readme
    assert "## 输出参数" in readme
    assert "| 参数名称 | 参数描述 | 参数类型 | 是否必填 |" in readme
    
    print("\n✅ README 格式测试通过!")
    return True


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Handler Generator README 测试套件")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(test_docstring_parsing())
    except Exception as e:
        print(f"\n❌ Docstring 解析测试失败: {e}")
        import traceback
        traceback.print_exc()
        results.append(False)
    
    try:
        results.append(test_readme_format())
    except Exception as e:
        print(f"\n❌ README 格式测试失败: {e}")
        import traceback
        traceback.print_exc()
        results.append(False)
    
    print("\n" + "=" * 60)
    print(f"测试结果: {sum(results)}/{len(results)} 通过")
    print("=" * 60)
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
