# 文档生成工具演示和测试指令

## 概述

根据 Issue 要求，为 coze_plugin 创建了两个文档生成脚本：

1. **generate_tool_doc.py** - 根据 handler.py 生成文档的脚本
2. **scan_and_generate_docs.py** - 自动扫描文件有哪些 handler.py 并触发生成脚本的脚本

## 生成文档格式示例（以 create_draft 为例）

生成的文档格式如下：

```markdown
# 工具函数 Create Draft

工具名称：create_draft
工具描述：Create Draft Tool Handler
Creates a new draft with basic project settings and returns a UUID for future reference.
The draft data is stored in /tmp directory with UUID as folder name.

## 输入参数

\`\`\`python
class Input(NamedTuple):
    draft_name: str = 'Coze剪映项目'
    width: int = 1920
    height: int = 1080
    fps: int = 30
\`\`\`
```

### 格式说明

1. **标题**: `# 工具函数 {工具名称}` - 工具名称自动从文件夹名转换为标题格式
2. **工具名称**: 从文件夹名提取（如 `create_draft`）
3. **工具描述**: 从 handler.py 文件开头的 `""" """` 文档字符串提取
4. **输入参数**: 通过读取 handler.py 里的 `class Input(NamedTuple):` 实现，包含：
   - 参数名称
   - 参数类型
   - 默认值
   - 行内注释（如果有）

## 测试效果指令

### 测试 1: 运行完整测试脚本

```bash
python test_doc_generation.py
```

**预期输出**：
```
🧪 Testing Documentation Generation Scripts
================================================================================
Working directory: /home/runner/work/Coze2JianYing/Coze2JianYing
================================================================================
Test 1: Testing create_draft tool documentation generation
================================================================================

📁 Handler path: coze_plugin/tools/create_draft/handler.py

1️⃣ Testing tool name extraction...
   Tool name: create_draft
   ✅ Correct! Expected: create_draft

2️⃣ Testing docstring extraction...
   Docstring: Create Draft Tool Handler...
   ✅ Docstring extracted successfully

3️⃣ Testing input parameters extraction...
   Found 4 parameters:
     - draft_name: str = 'Coze剪映项目'
     - width: int = 1920
     - height: int = 1080
     - fps: int = 30
   ✅ All expected parameters found

4️⃣ Testing full documentation generation...
   ✅ Title with 'Create Draft'
   ✅ Tool name line
   ✅ Tool description
   ✅ Input parameters section
   ✅ Input class definition
   ✅ draft_name parameter
   ✅ width parameter
   ✅ height parameter
   ✅ fps parameter

5️⃣ Testing file writing...
   ✅ File write/read successful

✅ All tests passed for create_draft tool!

[... 更多测试输出 ...]

📊 Test Summary
================================================================================
✅ PASSED     create_draft tool
✅ PASSED     export_drafts tool

🎉 All tests passed!

📚 Usage Instructions
================================================================================
[详细使用说明]
```

### 测试 2: 为单个工具生成文档

```bash
python scripts/generate_tool_doc.py coze_plugin/tools/create_draft/handler.py /tmp/create_draft_doc.md
```

**预期输出**：
```
✅ Documentation generated successfully!
📄 Output file: /tmp/create_draft_doc.md

============================================================
Preview:
============================================================
# 工具函数 Create Draft

工具名称：create_draft
工具描述：Create Draft Tool Handler
Creates a new draft with basic project settings and returns a UUID for future reference.
The draft data is stored in /tmp directory with UUID as folder name.

## 输入参数

\`\`\`python
class Input(NamedTuple):
    draft_name: str = 'Coze剪映项目'
    width: int = 1920
    height: int = 1080
    fps: int = 30
\`\`\`
```

**查看生成的文件**：
```bash
cat /tmp/create_draft_doc.md
```

### 测试 3: 批量扫描并生成所有工具的文档

```bash
python scripts/scan_and_generate_docs.py coze_plugin/tools /tmp/all_tool_docs
```

**预期输出**：
```
🔍 Scanning for handler.py files in: coze_plugin/tools
================================================================================

📋 Found 13 handler.py files
================================================================================

📝 Generating documentation...
================================================================================
✅ add_audios           -> /tmp/all_tool_docs/add_audios_generated.md
✅ add_captions         -> /tmp/all_tool_docs/add_captions_generated.md
✅ add_effects          -> /tmp/all_tool_docs/add_effects_generated.md
✅ add_images           -> /tmp/all_tool_docs/add_images_generated.md
✅ add_videos           -> /tmp/all_tool_docs/add_videos_generated.md
✅ create_draft         -> /tmp/all_tool_docs/create_draft_generated.md
✅ export_drafts        -> /tmp/all_tool_docs/export_drafts_generated.md
✅ get_media_duration   -> /tmp/all_tool_docs/get_media_duration_generated.md
✅ make_audio_info      -> /tmp/all_tool_docs/make_audio_info_generated.md
✅ make_caption_info    -> /tmp/all_tool_docs/make_caption_info_generated.md
✅ make_effect_info     -> /tmp/all_tool_docs/make_effect_info_generated.md
✅ make_image_info      -> /tmp/all_tool_docs/make_image_info_generated.md
✅ make_video_info      -> /tmp/all_tool_docs/make_video_info_generated.md

================================================================================
📊 Summary
================================================================================
✅ Successfully generated: 13
❌ Failed: 0

✨ Documentation generation complete!
```

**查看生成的所有文档**：
```bash
ls -la /tmp/all_tool_docs/
cat /tmp/all_tool_docs/create_draft_generated.md
```

### 测试 4: 查看其他工具的生成示例

```bash
# 生成 export_drafts 工具的文档
python scripts/generate_tool_doc.py coze_plugin/tools/export_drafts/handler.py /tmp/export_drafts_doc.md

# 查看生成的文档
cat /tmp/export_drafts_doc.md
```

**预期输出的文档内容**：
```markdown
# 工具函数 Export Drafts

工具名称：export_drafts
工具描述：Export Drafts Tool Handler
Exports draft data from /tmp storage for use by the draft generator.
Supports single draft or batch export, with optional cleanup of temporary files.

## 输入参数

\`\`\`python
class Input(NamedTuple):
    draft_ids: Union[str, List[str], None] = None  # Single UUID string, list of UUIDs, or None for export_all
    remove_temp_files: bool = False  # Whether to remove temp files after export
    export_all: bool = False  # Whether to export all drafts in the directory
\`\`\`
```

## 功能特点

### ✅ 已实现的功能

1. **从 handler.py 提取信息**：
   - 工具名称（从文件夹名）
   - 工具描述（从模块级文档字符串）
   - 输入参数（从 Input 类）

2. **格式化输出**：
   - 标题格式：`# 工具函数 {Title Case Name}`
   - 工具名称：`工具名称：{snake_case_name}`
   - 工具描述：直接使用文档字符串内容
   - 参数格式：保留类型注解、默认值和注释

3. **批量处理**：
   - 自动扫描所有 handler.py 文件
   - 批量生成文档
   - 提供详细的进度和统计

4. **错误处理**：
   - 文件不存在检查
   - 解析错误处理
   - 详细的错误信息

### ⚠️ 重要说明

1. **不修改原文件**: 脚本只读取 handler.py，不会修改任何现有文件
2. **生成文件位置**: 
   - 默认生成在 handler.py 所在目录，文件名为 `{tool_name}_generated.md`
   - 可以通过参数指定输出路径
3. **测试输出**: 为了测试效果，示例中将文档输出到 `/tmp` 目录

## 相关文件

- `scripts/generate_tool_doc.py` - 核心文档生成脚本
- `scripts/scan_and_generate_docs.py` - 批量扫描和生成脚本
- `test_doc_generation.py` - 测试脚本
- `TEST_DOC_GENERATION_GUIDE.md` - 详细使用指南
- `scripts/README.md` - 脚本目录文档（已更新）

## 快速开始

```bash
# 1. 运行测试验证功能
python test_doc_generation.py

# 2. 为单个工具生成文档
python scripts/generate_tool_doc.py coze_plugin/tools/create_draft/handler.py

# 3. 为所有工具生成文档
python scripts/scan_and_generate_docs.py
```

所有测试都使用 `/tmp` 目录输出，不会修改项目文件！
