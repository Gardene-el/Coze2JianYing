# Coze2JianYing 端插件示例

本目录包含端插件（Local Plugin）功能的示例脚本。

## 📁 文件说明

### Bot 模式示例
- **文件**: `local_plugin_bot_example.py`
- **功能**: 演示如何在 Bot 对话中使用端插件
- **适用场景**: 交互式对话、个人助手

### Workflow 模式示例
- **文件**: `local_plugin_workflow_example.py`
- **功能**: 演示如何在 Workflow 中使用端插件
- **适用场景**: 自动化任务、批量处理

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install cozepy>=0.20.0
```

### 2. 获取 Coze 凭证

#### 获取 API Token
1. 访问 [Coze Personal Access Tokens](https://www.coze.cn/open/oauth/pats)
2. 点击"创建 Personal Access Token"
3. 复制生成的 Token

#### 获取 Bot ID（Bot 模式）
1. 在 Coze 平台打开你的 Bot
2. 在 URL 中找到 Bot ID，例如：
   ```
   https://www.coze.cn/space/xxx/bot/7356789012345678901
                                      ^^^^^^^^^^^^^^^^^^^
                                      这是 Bot ID
   ```

#### 获取 Workflow ID（Workflow 模式）
1. 在 Coze 平台打开你的 Workflow
2. 在 URL 中找到 Workflow ID，例如：
   ```
   https://www.coze.cn/space/xxx/workflow/7356789012345678901
                                            ^^^^^^^^^^^^^^^^^^^
                                            这是 Workflow ID
   ```

### 3. 配置环境变量

```bash
# 必需配置
export COZE_API_TOKEN="your-token-here"

# Bot 模式需要
export COZE_BOT_ID="your-bot-id-here"

# Workflow 模式需要
export COZE_WORKFLOW_ID="your-workflow-id-here"

# 可选配置（默认为国内版）
export COZE_BASE_URL="https://api.coze.cn"  # 国内版
# export COZE_BASE_URL="https://api.coze.com"  # 国际版
```

### 4. 运行示例

#### Bot 模式
```bash
python examples/local_plugin_bot_example.py
```

然后在 Coze 平台与你的 Bot 对话，当 Bot 调用端插件时，本地应用会自动执行。

#### Workflow 模式
```bash
python examples/local_plugin_workflow_example.py
```

Workflow 将自动运行，本地应用监听并处理端插件调用。

## 📖 配置 Coze 平台

### 在 Coze 平台创建端插件

1. **进入资源库** → 点击 **"+ 资源"**
2. 选择 **"插件工具"** → **"端插件"**
3. 填写插件信息
4. 添加工具 `generate_draft`（参考下方配置）

### 工具配置：generate_draft

**输入参数**：
```json
{
  "type": "object",
  "properties": {
    "content": {
      "type": "string",
      "description": "草稿内容 JSON 字符串"
    },
    "output_folder": {
      "type": "string",
      "description": "输出文件夹路径（可选）"
    }
  },
  "required": ["content"]
}
```

**输出参数**：
```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "description": "执行状态"
    },
    "message": {
      "type": "string",
      "description": "结果消息"
    },
    "draft_ids": {
      "type": "array",
      "items": {"type": "string"},
      "description": "生成的草稿 ID 列表"
    }
  }
}
```

### 在 Bot 中使用端插件

1. 打开你的 Bot 编辑页面
2. 在"工具"选项卡中添加刚创建的端插件
3. 保存并发布 Bot
4. 运行本地示例脚本
5. 在 Coze 平台与 Bot 对话

**对话示例**：
```
你：帮我生成一个介绍中国美食的视频
Bot：好的，我来帮你生成...
     [Bot 调用端插件 generate_draft]
     [本地应用自动执行草稿生成]
Bot：草稿已生成！草稿ID是 xxx
```

### 在 Workflow 中使用端插件

1. 创建或编辑 Workflow
2. 添加"工具节点"
3. 选择端插件的 `generate_draft` 工具
4. 配置参数（可以从前置节点获取）
5. 运行本地示例脚本
6. 在 Coze 平台运行 Workflow

**Workflow 示例流程**：
```
节点1: 用户输入主题
  ↓
节点2: AI 生成脚本
  ↓
节点3: AI 生成图片
  ↓
节点4: 构建 JSON 数据
  ↓
节点5: 端插件 generate_draft
  参数: content={{node4.output}}
  ↓
节点6: 返回结果
```

## 🔧 自定义示例

你可以基于示例脚本进行修改：

### 添加自定义工具

```python
# 定义自定义工具处理函数
def my_custom_tool(args: dict) -> str:
    """自定义工具处理函数"""
    try:
        # 执行你的逻辑
        result = do_something(args)
        return json.dumps({
            "status": "success",
            "result": result
        })
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": str(e)
        })

# 注册工具
service.register_tool("my_custom_tool", my_custom_tool)
```

### 修改 Workflow 参数

编辑 `local_plugin_workflow_example.py` 中的 `WORKFLOW_PARAMETERS`：

```python
WORKFLOW_PARAMETERS = {
    "topic": "你的主题",
    "style": "你的风格",
    "duration": 60,  # 添加更多参数
    # ...
}
```

## ⚠️ 注意事项

1. **Token 安全**：不要将 Token 提交到版本控制系统
2. **服务状态**：脚本运行时需要保持运行状态
3. **网络连接**：确保能访问 Coze API
4. **错误处理**：查看日志输出了解执行情况

## 📚 相关文档

- [端插件使用指南](../docs/guides/LOCAL_PLUGIN_USAGE_GUIDE.md)
- [端插件详解](../docs/analysis/COZE_LOCAL_PLUGIN_DETAILED_EXPLANATION.md)
- [Bot vs Workflow 对比](../docs/analysis/COZE_BOT_VS_WORKFLOW_LOCAL_PLUGIN.md)

## 🐛 常见问题

### Q: 运行后没有反应
**A**: 检查 Token 和 ID 是否正确，查看日志输出

### Q: 工具没有被调用
**A**: 确认 Coze 平台上已正确配置端插件，且工具名称匹配

### Q: 如何调试？
**A**: 查看脚本输出的日志，包含详细的执行信息

## 💡 提示

- Bot 模式适合交互式使用，需要在 Coze 平台与 Bot 对话
- Workflow 模式适合自动化，运行脚本后 Workflow 自动执行
- 两种模式都不需要公网 IP，本地应用主动连接 Coze 云端

---

**开始使用**：
```bash
export COZE_API_TOKEN="your-token"
export COZE_BOT_ID="your-bot-id"
python examples/local_plugin_bot_example.py
```
