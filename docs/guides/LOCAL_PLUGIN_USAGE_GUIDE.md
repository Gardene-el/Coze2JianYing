# Coze 端插件（Local Plugin）使用指南

本指南介绍如何使用 Coze2JianYing 的端插件功能，实现无需公网 IP 的本地草稿生成。

## 📖 什么是端插件？

**端插件**（Local Plugin）是 Coze 平台提供的一种特殊插件类型，允许 Bot/Workflow 调用运行在**用户本地设备**上的功能。

### 与云端服务的区别

| 特性 | 云端服务（当前实现） | 端插件（新增功能） |
|------|---------------------|-------------------|
| **需要公网 IP** | 是（需要 ngrok 或云服务器） | 否（本地应用主动连接） |
| **部署复杂度** | 中等（需配置内网穿透） | 简单（运行脚本即可） |
| **适用场景** | 团队协作、生产环境 | 个人使用、快速原型 |
| **资源访问** | 仅限服务器本地 | 用户设备本地资源 |

### 工作原理

```
┌─────────────────────────────────────────────────────────┐
│                    端插件工作流程                         │
├─────────────────────────────────────────────────────────┤
│  1. 本地应用主动连接到 Coze 云端（无需公网 IP）           │
│  2. 通过 SSE 接收 Coze Bot/Workflow 的事件流              │
│  3. 监听 REQUIRES_ACTION 事件（端插件调用请求）           │
│  4. 在本地执行功能（如生成剪映草稿）                      │
│  5. 将结果提交回 Coze Bot/Workflow                        │
└─────────────────────────────────────────────────────────┘
```

**关键优势**：
- ✅ 本地应用**主动向外连接**，无需被动接受外部请求
- ✅ 不需要公网 IP 地址
- ✅ 不需要开放任何端口
- ✅ 可以穿透大多数防火墙和 NAT

## 🚀 快速开始

### 前置要求

1. **Python 环境**：Python 3.8+
2. **安装依赖**：
   ```bash
   pip install cozepy>=0.20.0
   ```
3. **Coze 账号**：注册 [Coze 平台](https://www.coze.cn/)
4. **获取凭证**：
   - **API Token**：在 [个人访问令牌页面](https://www.coze.cn/open/oauth/pats) 创建
   - **Bot ID** 或 **Workflow ID**：在对应资源的详情页获取

### 基本使用示例

#### 示例 1：Bot 对话模式

```python
#!/usr/bin/env python3
"""
端插件 Bot 模式示例
"""
import os
from app.services.local_plugin_service import LocalPluginService, create_draft_tool_handler
from app.utils.draft_generator import DraftGenerator
from app.utils.logger import get_logger

# 配置
COZE_API_TOKEN = os.getenv("COZE_API_TOKEN")  # 从环境变量获取
COZE_BOT_ID = os.getenv("COZE_BOT_ID")

def main():
    # 创建日志记录器
    logger = get_logger(__name__)
    
    # 创建端插件服务
    service = LocalPluginService(
        coze_token=COZE_API_TOKEN,
        logger=logger
    )
    
    # 注册草稿生成工具
    draft_generator = DraftGenerator()
    draft_handler = create_draft_tool_handler(draft_generator)
    service.register_tool("generate_draft", draft_handler)
    
    # 启动 Bot 模式
    logger.info("启动端插件服务（Bot 模式）...")
    success = service.start_bot_mode(
        bot_id=COZE_BOT_ID,
        user_id="local-user",
        initial_message="帮我生成一个视频草稿"  # 可选的初始消息
    )
    
    if success:
        logger.info("服务已启动，等待 Bot 调用...")
        # 保持运行
        try:
            while service.is_running:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("收到中断信号，停止服务...")
            service.stop()
    else:
        logger.error("服务启动失败")

if __name__ == "__main__":
    main()
```

**运行方式**：
```bash
export COZE_API_TOKEN="your-token-here"
export COZE_BOT_ID="your-bot-id-here"
python examples/local_plugin_bot_example.py
```

#### 示例 2：Workflow 模式

```python
#!/usr/bin/env python3
"""
端插件 Workflow 模式示例
"""
import os
from app.services.local_plugin_service import LocalPluginService, create_draft_tool_handler
from app.utils.draft_generator import DraftGenerator
from app.utils.logger import get_logger

# 配置
COZE_API_TOKEN = os.getenv("COZE_API_TOKEN")
COZE_WORKFLOW_ID = os.getenv("COZE_WORKFLOW_ID")

def main():
    logger = get_logger(__name__)
    
    # 创建服务并注册工具
    service = LocalPluginService(coze_token=COZE_API_TOKEN, logger=logger)
    draft_generator = DraftGenerator()
    service.register_tool("generate_draft", create_draft_tool_handler(draft_generator))
    
    # 启动 Workflow 模式
    logger.info("启动端插件服务（Workflow 模式）...")
    success = service.start_workflow_mode(
        workflow_id=COZE_WORKFLOW_ID,
        parameters={
            "topic": "中国美食",
            "style": "快节奏"
        }
    )
    
    if success:
        logger.info("Workflow 已启动...")
        # Workflow 模式通常会自动完成，无需保持运行
        try:
            while service.is_running:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            service.stop()

if __name__ == "__main__":
    main()
```

## 🔧 在 Coze 平台配置端插件

### 步骤 1：创建端插件

1. 登录 [Coze 平台](https://www.coze.cn/)
2. 进入**资源库** → 点击 **"+ 资源"**
3. 选择 **"插件工具"** → **"端插件"**
4. 填写基本信息：
   - **插件名称**：Coze2JianYing Local Plugin
   - **插件描述**：在本地生成剪映草稿

### 步骤 2：定义工具函数

在端插件配置中添加工具：

#### 工具：generate_draft

**基本信息**：
- **工具名称**：`generate_draft`
- **工具描述**：根据内容生成剪映草稿到本地

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
      "description": "输出文件夹路径（可选，默认为剪映草稿目录）"
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
      "description": "执行状态：success 或 error"
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

### 步骤 3：在 Bot/Workflow 中使用

#### 在 Bot 中使用

1. 创建或编辑 Bot
2. 在 **"工具"** 选项卡中添加端插件
3. Bot 会在需要时自动调用端插件

**对话示例**：
```
用户：帮我生成一个介绍中国美食的视频
Bot：好的，我来帮你生成...
      [Bot 调用端插件 generate_draft]
      [本地应用执行草稿生成]
Bot：草稿已生成！草稿ID是 xxx，保存在 C:/Users/.../JianyingPro/...
```

#### 在 Workflow 中使用

1. 创建或编辑 Workflow
2. 添加 **"工具节点"**
3. 选择端插件中的 `generate_draft` 工具
4. 配置参数：
   ```
   content: {{previous_node.output}}
   output_folder: null
   ```

**Workflow 示例**：
```
节点1: AI 生成脚本
  ↓
节点2: AI 生成图片
  ↓
节点3: 构建 JSON 数据
  ↓
节点4: 端插件 generate_draft
  参数: content={{node3.output}}
  ↓
节点5: 返回结果
```

## 📋 API 参考

### LocalPluginService

端插件服务主类。

#### 构造函数

```python
service = LocalPluginService(
    coze_token: str,           # Coze API Token (必需)
    base_url: str = COZE_CN_BASE_URL,  # API 基础 URL
    logger: Optional[Logger] = None    # 日志记录器
)
```

#### 方法

##### register_tool()

注册工具处理函数。

```python
def register_tool(
    tool_name: str,           # 工具名称（如 "generate_draft"）
    handler: Callable[[Dict], str]  # 处理函数
) -> None
```

**处理函数签名**：
```python
def handler(args: dict) -> str:
    """
    Args:
        args: 工具参数字典
    
    Returns:
        执行结果 JSON 字符串
    """
    # 执行逻辑
    return json.dumps({"status": "success", ...})
```

##### start_bot_mode()

启动 Bot 对话模式。

```python
def start_bot_mode(
    bot_id: str,                      # Coze Bot ID
    user_id: str = "local-user",      # 用户 ID
    initial_message: Optional[str] = None  # 初始消息
) -> bool
```

**返回**：是否启动成功

##### start_workflow_mode()

启动 Workflow 工作流模式。

```python
def start_workflow_mode(
    workflow_id: str,                    # Coze Workflow ID
    parameters: Optional[Dict[str, Any]] = None  # 工作流参数
) -> bool
```

**返回**：是否启动成功

##### stop()

停止服务。

```python
def stop() -> None
```

### create_draft_tool_handler()

创建草稿生成工具处理函数的工厂函数。

```python
handler = create_draft_tool_handler(
    draft_generator: DraftGenerator  # DraftGenerator 实例
) -> Callable[[Dict], str]
```

**返回**：可用于 `register_tool()` 的处理函数

## 🎯 实际应用场景

### 场景 1：个人视频制作助手

**需求**：个人用户希望通过对话快速生成视频草稿，无需配置复杂的网络。

**方案**：使用端插件 Bot 模式

```python
# local_plugin_assistant.py
service = LocalPluginService(coze_token=TOKEN)
service.register_tool("generate_draft", draft_handler)
service.start_bot_mode(bot_id=BOT_ID, user_id="user-123")

# 运行后，在 Coze 平台与 Bot 对话：
# 用户："帮我做一个介绍故宫的视频"
# Bot 会自动调用本地的 generate_draft 工具
# 草稿直接生成到用户的剪映目录
```

### 场景 2：批量内容生产

**需求**：使用 Workflow 批量生成多个视频草稿。

**方案**：使用端插件 Workflow 模式

```python
# Workflow 配置
节点1: 循环节点（遍历主题列表）
  For each topic in ["美食", "旅游", "科技", ...]
    节点2: AI 生成脚本
    节点3: 端插件 generate_draft
    
# 本地应用
service = LocalPluginService(coze_token=TOKEN)
service.register_tool("generate_draft", draft_handler)
service.start_workflow_mode(
    workflow_id=WORKFLOW_ID,
    parameters={"topics": ["美食", "旅游", "科技"]}
)
```

### 场景 3：定时任务

**需求**：每天自动生成当日新闻视频草稿。

**方案**：定时触发 Workflow + 端插件

```python
# cron job 或 系统计划任务
# 每天 8:00 运行

import schedule
import time

def daily_generation():
    service = LocalPluginService(coze_token=TOKEN)
    service.register_tool("generate_draft", draft_handler)
    service.start_workflow_mode(
        workflow_id=WORKFLOW_ID,
        parameters={"date": datetime.now().isoformat()}
    )

schedule.every().day.at("08:00").do(daily_generation)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## ⚠️ 注意事项

### 1. Token 安全

- ❌ 不要将 Token 硬编码在源代码中
- ✅ 使用环境变量或配置文件
- ✅ 添加 `.env` 到 `.gitignore`

```python
# 推荐做法
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("COZE_API_TOKEN")
```

### 2. 服务运行

- 端插件服务需要**持续运行**以接收事件
- Bot 模式：需要保持运行，直到用户结束对话
- Workflow 模式：通常在 Workflow 执行完成后自动结束

### 3. 错误处理

- 工具处理函数应该捕获所有异常并返回错误信息
- 不要让异常导致服务崩溃

```python
def safe_handler(args: dict) -> str:
    try:
        # 执行逻辑
        result = do_something(args)
        return json.dumps({"status": "success", "result": result})
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return json.dumps({"status": "error", "message": str(e)})
```

### 4. 网络要求

- 需要能够访问 Coze API（`api.coze.cn` 或 `api.coze.com`）
- 如果在企业网络中，确保防火墙允许 HTTPS 出站连接

## 🔄 与云端服务的对比

| 维度 | 云端服务（FastAPI） | 端插件（cozepy） |
|------|-------------------|-----------------|
| **公网 IP** | 需要 | 不需要 |
| **部署方式** | 服务器 / ngrok | 运行脚本 |
| **适用场景** | 团队、生产 | 个人、测试 |
| **扩展性** | 高 | 中 |
| **维护成本** | 中等 | 低 |
| **团队协作** | 支持 | 不支持 |

### 推荐使用原则

- **个人使用 + 快速原型**：优先选择端插件
- **团队协作 + 生产环境**：使用云端服务（FastAPI）
- **两者结合**：开发阶段用端插件，生产环境切换到云端服务

## 🐛 常见问题

### Q1: 启动后没有响应

**可能原因**：
- Token 或 Bot/Workflow ID 错误
- 网络无法访问 Coze API

**解决方法**：
1. 检查 Token 和 ID 是否正确
2. 测试网络连接：`curl https://api.coze.cn`
3. 查看日志输出

### Q2: 工具没有被调用

**Bot 模式可能原因**：
- Bot 没有配置端插件
- Bot 的 AI 决定不调用工具

**Workflow 模式可能原因**：
- Workflow 节点配置错误
- 工具名称不匹配

### Q3: cozepy 版本兼容性

**建议版本**：`cozepy>=0.20.0`

如遇到兼容性问题：
```bash
pip install --upgrade cozepy
```

## 📚 相关文档

- [端插件详解](../analysis/COZE_LOCAL_PLUGIN_DETAILED_EXPLANATION.md)
- [Bot vs Workflow 对比](../analysis/COZE_BOT_VS_WORKFLOW_LOCAL_PLUGIN.md)
- [Coze API 参数指南](../reference/COZE_API_PARAMETERS_GUIDE.md)
- [Coze 官方文档 - 端插件](https://www.coze.cn/open/docs/guides/use_local_plugin)

## 🎉 总结

端插件功能为 Coze2JianYing 提供了一种**更简单、无需公网 IP** 的使用方式，特别适合个人用户和快速原型开发。

**核心优势**：
- ✅ 无需配置 ngrok 或云服务器
- ✅ 一行命令启动，开箱即用
- ✅ 直接访问本地资源
- ✅ 适合个人使用和快速迭代

**开始使用**：
```bash
# 1. 设置环境变量
export COZE_API_TOKEN="your-token"
export COZE_BOT_ID="your-bot-id"

# 2. 运行端插件服务
python examples/local_plugin_bot_example.py

# 3. 在 Coze 平台与 Bot 对话，自动生成草稿！
```

---

**文档版本**: v1.0  
**创建时间**: 2024-11-09  
**相关 Issue**: [#125](https://github.com/Gardene-el/Coze2JianYing/issues/125), [#126](https://github.com/Gardene-el/Coze2JianYing/issues/126)
