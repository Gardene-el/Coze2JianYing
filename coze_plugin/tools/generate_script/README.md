# generate_script 工具文档

## 功能描述

从草稿配置生成完整的可执行 Python 脚本，用户可以直接运行该脚本来自动调用 API 生成剪映草稿。

这是手动 JSON 导入和完全自动化云端 API 之间的一个中间方案，适合以下场景：
- 用户希望有一定的自动化程度，但不想配置云端服务
- 用户希望审查和自定义脚本内容
- 用户希望保存脚本以便后续重复使用

## 工作流程

```
Coze 工作流 → 创建草稿 → generate_script → 生成 Python 脚本 → 用户复制并执行脚本 → 自动调用 API → 生成剪映草稿
```

## Input 参数

### draft_ids (必需)
- **类型**: `string` 或 `array[string]`
- **描述**: 要生成脚本的草稿 ID（UUID）
- **示例**: 
  - 单个: `"12345678-1234-1234-1234-123456789abc"`
  - 多个: `["uuid1", "uuid2", "uuid3"]`

### api_base_url (可选)
- **类型**: `string`
- **描述**: API 服务的基础 URL
- **默认值**: `"http://127.0.0.1:8000"`
- **示例**: 
  - 本地: `"http://127.0.0.1:8000"`
  - 远程: `"https://your-server.com"`

### output_folder (可选)
- **类型**: `string` 或 `null`
- **描述**: 剪映草稿输出文件夹路径
- **默认值**: `null` (使用默认路径)
- **示例**: 
  - Windows: `"C:\\Users\\YourName\\AppData\\Local\\JianyingPro\\User Data\\Projects\\com.lveditor.draft"`
  - 默认: `null`

## Output 结果

### success
- **类型**: `boolean`
- **描述**: 脚本生成是否成功
- **示例**: `true`

### message
- **类型**: `string`
- **描述**: 结果摘要信息
- **示例**: `"成功生成 1 个脚本"`

### scripts
- **类型**: `array[object]`
- **描述**: 生成的脚本列表，每个对象包含：
  - `draft_id` (string): 草稿 ID
  - `draft_name` (string): 草稿名称
  - `script` (string): 完整的 Python 脚本内容
- **示例**:
```json
[
  {
    "draft_id": "uuid-here",
    "draft_name": "我的视频项目",
    "script": "#!/usr/bin/env python3\\n..."
  }
]
```

### errors (可选)
- **类型**: `array[string]` 或 `null`
- **描述**: 错误信息列表（如果有）
- **示例**: `["草稿 xxx 不存在", "配置文件读取失败"]`

## 使用示例

### 示例 1: 生成单个脚本

**输入**:
```json
{
  "draft_ids": "12345678-1234-1234-1234-123456789abc",
  "api_base_url": "http://127.0.0.1:8000",
  "output_folder": null
}
```

**输出**:
```json
{
  "success": true,
  "message": "成功生成 1 个脚本",
  "scripts": [
    {
      "draft_id": "12345678-1234-1234-1234-123456789abc",
      "draft_name": "我的视频项目",
      "script": "#!/usr/bin/env python3\n\"\"\"Coze2JianYing 自动草稿生成脚本...\"\"\"\n\nimport requests\n..."
    }
  ],
  "errors": null
}
```

### 示例 2: 批量生成多个脚本

**输入**:
```json
{
  "draft_ids": ["uuid1", "uuid2", "uuid3"],
  "api_base_url": "http://127.0.0.1:8000"
}
```

**输出**:
```json
{
  "success": true,
  "message": "成功生成 3 个脚本",
  "scripts": [
    {"draft_id": "uuid1", "draft_name": "项目1", "script": "..."},
    {"draft_id": "uuid2", "draft_name": "项目2", "script": "..."},
    {"draft_id": "uuid3", "draft_name": "项目3", "script": "..."}
  ],
  "errors": null
}
```

### 示例 3: 自定义输出路径

**输入**:
```json
{
  "draft_ids": "uuid-here",
  "api_base_url": "http://127.0.0.1:8000",
  "output_folder": "C:\\MyProjects\\JianyingDrafts"
}
```

## 在 Coze 工作流中的使用

### 典型工作流

```
1. [create_draft] 创建草稿
   ↓ (返回 draft_id)
2. [add_images/add_audios/add_captions] 添加内容
   ↓
3. [generate_script] 生成脚本
   ↓ (返回 script)
4. [输出节点] 显示脚本给用户
```

### 配置示例

在工作流的最后一步：

1. **添加 generate_script 工具节点**
2. **配置输入**：
   - `draft_ids`: 使用前面步骤的 `draft_id` 变量
   - `api_base_url`: 使用默认值或让用户输入
   - `output_folder`: 使用 `null` 或让用户输入

3. **输出脚本**：
   - 在输出节点中显示 `scripts[0].script`
   - 用户复制脚本内容
   - 保存为 `.py` 文件并执行

## 生成的脚本特性

### 包含的功能
- ✅ API 服务连接检查
- ✅ 草稿创建
- ✅ 轨道和片段添加
- ✅ 错误处理和友好提示
- ✅ 进度反馈
- ✅ 详细的使用说明

### 脚本依赖
- Python 3.7+
- requests 库: `pip install requests`

### 执行方式
```bash
# 方式 1: 直接执行
python generated_script.py

# 方式 2: 作为模块执行
python -m generated_script

# 方式 3: 在 Python 中
>>> import generated_script
>>> generated_script.main()
```

## 优势与适用场景

### 优势
1. ✅ **半自动化**: 比手动 JSON 粘贴更方便
2. ✅ **可审查**: 用户可以查看和修改脚本
3. ✅ **可复用**: 脚本可以保存并重复执行
4. ✅ **灵活性**: 可以自定义脚本逻辑
5. ✅ **离线工作**: 脚本生成后可离线执行

### 适用场景
- 不想配置云端服务（ngrok 等）
- 需要审查自动化流程
- 想要保存和重复使用脚本
- 需要对脚本进行自定义修改

### 不适用场景
- 需要完全自动化（推荐使用云端 API）
- 频繁使用（推荐使用云端 API）
- 对脚本执行不熟悉（推荐使用手动 JSON）

## 与其他方案对比

| 特性 | 手动 JSON | 脚本方案 | 云端 API |
|------|----------|----------|----------|
| 自动化程度 | ❌ 低 | ⚠️ 中 | ✅ 高 |
| 使用复杂度 | 简单 | 中等 | 简单 |
| 配置成本 | 低 | 低 | 中 |
| 可审查性 | ✅ | ✅ | ❌ |
| 可复用性 | ❌ | ✅ | ✅ |
| 网络需求 | 无 | 无 | 需要 |

## 注意事项

### 安全提醒
⚠️ **执行脚本前请仔细审查内容**，确保：
1. 脚本来源可信（由你自己的 Coze 工作流生成）
2. 没有恶意代码或危险操作
3. API 地址正确且可信

### 使用提示
1. **保存脚本**: 建议将生成的脚本保存为文件，便于后续使用
2. **命名规范**: 使用有意义的文件名，如 `generate_draft_myproject.py`
3. **版本管理**: 如果需要修改脚本，建议使用版本控制
4. **环境检查**: 执行前确保 API 服务正在运行

### 常见问题

**Q: 脚本执行失败怎么办？**

A: 检查以下几点：
1. API 服务是否正在运行
2. API 地址是否正确
3. 是否安装了 requests 库
4. 网络连接是否正常

**Q: 如何修改脚本？**

A: 脚本是纯文本文件，可以使用任何文本编辑器打开并修改：
- 修改 `API_BASE_URL` 改变服务地址
- 修改 `OUTPUT_FOLDER` 改变输出路径
- 修改 `DRAFT_CONTENT` 改变草稿内容

**Q: 脚本可以重复执行吗？**

A: 可以。每次执行都会创建新的草稿项目。

**Q: 支持批量生成吗？**

A: 支持。可以传入多个 draft_ids，工具会为每个草稿生成独立的脚本。

## 技术细节

### 脚本模板

工具使用 Python 字符串模板生成脚本，包含：
1. Shebang 行: `#!/usr/bin/env python3`
2. 文档字符串: 项目信息和使用说明
3. 导入语句: requests, json, sys
4. 配置变量: API_BASE_URL, DRAFT_CONFIG, DRAFT_CONTENT
5. 辅助函数: check_api_server, create_draft, add_track, add_segment, add_content, save_draft
6. 主函数: main() 包含完整流程和错误处理

### 数据格式

生成的脚本中的 `DRAFT_CONTENT` 使用标准的 Draft Generator Interface 格式，与手动 JSON 导入完全兼容。

### 错误处理

脚本包含多层错误处理：
1. **连接错误**: 无法连接到 API 服务
2. **HTTP 错误**: API 返回错误状态码
3. **超时错误**: 请求超时
4. **用户中断**: Ctrl+C 中断
5. **未知错误**: 其他异常情况

## 总结

`generate_script` 工具为用户提供了一个介于完全手动和完全自动之间的灵活方案：
- 比手动 JSON 粘贴更自动化
- 比云端 API 更可控和可审查
- 适合对自动化有一定需求但不想配置复杂服务的用户

建议根据实际使用场景选择最合适的方案：
- **偶尔使用**: 手动 JSON
- **需要审查**: 脚本方案
- **频繁使用**: 云端 API
