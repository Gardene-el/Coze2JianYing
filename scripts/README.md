# Scripts 目录

## 📦 概述

此目录包含项目的实用工具脚本，这些脚本可以独立运行，不依赖复杂的包管理结构。

## 🛠️ 可用脚本

### coze_json_formatter.py

**功能**: Coze JSON 格式化工具

将 Coze 输出的特殊格式（包含 output 字段的字符串 JSON）转换为标准 JSON 格式。

**使用方法**:

```bash
# 显示帮助信息
python scripts/coze_json_formatter.py --help

# 转换单个文件（自动生成输出文件名）
python scripts/coze_json_formatter.py coze_example_for_paste_context.json

# 指定输出文件名
python scripts/coze_json_formatter.py input.json output.json

# 批量转换当前目录下的所有匹配文件
python scripts/coze_json_formatter.py --batch

# 批量转换指定目录和模式
python scripts/coze_json_formatter.py --batch ./data "*coze*.json"
```

**作为 Python 模块使用**:

```python
import sys
from pathlib import Path

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from coze_json_formatter import convert_coze_to_standard_format

# 转换文件
output_file = convert_coze_to_standard_format('input.json')
print(f"转换完成: {output_file}")
```

**主要功能**:
- ✅ 自动提取并解析 output 字段
- ✅ 格式验证
- ✅ 批量转换
- ✅ 智能命名
- ✅ 详细日志
- ✅ UTF-8 编码支持

### test_coze_json_formatter.py

**功能**: 测试 coze_json_formatter.py 的功能

**使用方法**:

```bash
python scripts/test_coze_json_formatter.py
```

**测试内容**:
- 单文件转换
- 提取 output 字段
- 自定义输出文件名
- 与 DraftGenerator 集成

### test_api_demo.py

**功能**: DraftStateManager 和 SegmentManager 综合测试

完全仿照 pyJianYingDraft 的 demo.py 工作流，通过直接调用 API 函数（非 HTTP 请求）生成完整的视频草稿项目。使用 GitHub Pages 托管的网络素材 URL。

**使用方法**:

```bash
python scripts/test_api_demo.py
```

**测试流程**:
1. ✅ 创建草稿 (1920x1080, 30fps)
2. ✅ 添加音频、视频和文本轨道
3. ✅ 创建音频片段（带淡入效果）
4. ✅ 创建视频片段（带入场动画）
5. ✅ 创建贴纸片段（GIF，带模糊背景）
6. ✅ 添加转场效果
7. ✅ 创建文本片段（带气泡、花字、动画效果）
8. ✅ 将所有片段添加到相应轨道
9. ✅ 保存草稿
10. ✅ 查询草稿状态

**使用的素材 URL**:
- 音频: https://gardene-el.github.io/Coze2JianYing/assets/audio.mp3
- 视频: https://gardene-el.github.io/Coze2JianYing/assets/video.mp4
- 贴纸: https://gardene-el.github.io/Coze2JianYing/assets/sticker.gif
- 字幕: https://gardene-el.github.io/Coze2JianYing/assets/subtitles.srt

**主要功能**:
- ✅ 测试 DraftStateManager 所有核心功能
- ✅ 测试 SegmentManager 所有核心功能
- ✅ 验证草稿创建、轨道添加、片段创建、操作记录
- ✅ 验证状态管理和配置持久化
- ✅ 提供详细的测试日志和进度输出

### generate_tool_doc.py

**功能**: 工具文档生成器

从 Coze 插件工具的 handler.py 文件自动生成文档，包括工具名称、描述和输入参数。

**使用方法**:

```bash
# 显示帮助信息
python scripts/generate_tool_doc.py

# 为单个工具生成文档（自动生成输出文件名）
python scripts/generate_tool_doc.py coze_plugin/tools/create_draft/handler.py

# 指定输出文件名
python scripts/generate_tool_doc.py coze_plugin/tools/create_draft/handler.py output.md
```

**作为 Python 模块使用**:

```python
import sys
from pathlib import Path

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'scripts'))

from generate_tool_doc import generate_documentation, get_tool_name_from_path

# 生成文档
handler_path = "coze_plugin/tools/create_draft/handler.py"
doc_content = generate_documentation(handler_path)
print(doc_content)
```

**主要功能**:
- ✅ 从模块文档字符串提取工具描述
- ✅ 解析 Input 类获取参数定义
- ✅ 自动格式化工具名称
- ✅ 生成标准格式的 Markdown 文档
- ✅ 支持自定义输出路径

**生成的文档格式**:

```markdown
# 工具函数 Tool Name

工具名称：tool_name
工具描述：[从 handler.py 模块文档字符串提取]

## 输入参数

\`\`\`python
class Input(NamedTuple):
    param1: type = default_value  # 参数注释
    param2: type = default_value
\`\`\`
```

### scan_and_generate_docs.py

**功能**: 批量文档生成工具

扫描 `coze_plugin/tools/` 目录下的所有 handler.py 文件，并为每个工具自动生成文档。

**使用方法**:

```bash
# 显示帮助信息
python scripts/scan_and_generate_docs.py --help

# 扫描并生成所有工具的文档（默认输出到各工具目录）
python scripts/scan_and_generate_docs.py

# 指定工具目录
python scripts/scan_and_generate_docs.py coze_plugin/tools

# 指定输出目录（统一输出到一个目录）
python scripts/scan_and_generate_docs.py coze_plugin/tools /tmp/docs
```

**主要功能**:
- ✅ 自动扫描所有 handler.py 文件
- ✅ 批量生成工具文档
- ✅ 支持自定义输出目录
- ✅ 提供详细的处理进度和统计
- ✅ 错误处理和报告

**输出示例**:

```
🔍 Scanning for handler.py files in: coze_plugin/tools
================================================================================

📋 Found 13 handler.py files
================================================================================

📝 Generating documentation...
================================================================================
✅ create_draft         -> coze_plugin/tools/create_draft/create_draft_generated.md
✅ export_drafts        -> coze_plugin/tools/export_drafts/export_drafts_generated.md
...

================================================================================
📊 Summary
================================================================================
✅ Successfully generated: 13
❌ Failed: 0

✨ Documentation generation complete!
```

## 📊 输入输出格式

### 输入格式（Coze 特殊格式）

```json
{
  "output": "{\"format_version\":\"1.0\",\"drafts\":[...]}"
}
```

- `output` 字段是一个字符串
- 字符串内容是转义的 JSON

### 输出格式（标准格式）

```json
{
  "format_version": "1.0",
  "export_type": "single_draft",
  "draft_count": 1,
  "drafts": [...]
}
```

- 标准的 JSON 对象
- 可直接用于剪映草稿生成器

## ⚠️ 注意事项

- 所有脚本使用 UTF-8 编码
- 支持中文和特殊字符
- 转换不会修改原始文件
- 批量转换时自动跳过已转换的文件
- 建议在项目根目录运行命令

## 🔧 添加新脚本

如需添加新的工具脚本：

1. 在 `scripts/` 目录下创建新的 Python 文件
2. 添加详细的文档字符串说明功能
3. 提供 `--help` 选项显示使用方法
4. 更新此 README 文件
5. 创建对应的测试脚本（可选）

## 📚 相关文档

- [项目主 README](../README.md)
- [Coze 输出转换器详细指南](../docs/draft_generator/COZE_OUTPUT_CONVERTER_GUIDE.md)
