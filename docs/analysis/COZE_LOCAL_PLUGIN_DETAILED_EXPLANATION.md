# Coze 端插件机制详解 - 补充说明

本文档针对 [Issue #125 评论](https://github.com/Gardene-el/Coze2JianYing/pull/126#issuecomment-3484489878) 中提出的具体问题进行详细解答。

## 问题 1：Coze Bot 和 cozepy 应用的部署位置

### 1.1 部署位置确认

**答案：是的，你的理解完全正确！**

- ✅ **Coze Bot**：运行在**云端、公网**上（Coze 平台的服务器）
- ✅ **cozepy 应用**：运行在**本地、无需公网 IP** 的用户设备上

### 详细说明

#### Coze Bot（云端）

```
┌─────────────────────────────────────┐
│     Coze 云平台（api.coze.cn）       │
│                                     │
│  ┌─────────────────────────────┐   │
│  │      Coze Bot               │   │
│  │  - Bot ID: 你的机器人ID      │   │
│  │  - 运行在 Coze 服务器上      │   │
│  │  - 有公网地址               │   │
│  │  - 处理用户消息             │   │
│  │  - 调用云侧插件             │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

**特点**：
- 托管在 Coze 平台的云服务器上
- 有固定的公网访问地址（通过 Coze API）
- 24/7 运行，随时可访问
- 你通过 Bot ID 和 API Token 访问它

#### cozepy 应用（本地）

```
┌─────────────────────────────────────┐
│     你的本地电脑（无公网 IP）        │
│                                     │
│  ┌─────────────────────────────┐   │
│  │   cozepy 应用（Python 脚本） │   │
│  │  - 运行在本地                │   │
│  │  - 不需要公网 IP             │   │
│  │  - 主动连接到 Coze Bot       │   │
│  │  - 监听 Bot 的响应           │   │
│  └─────────────────────────────┘   │
│                                     │
└─────────────────────────────────────┘
```

**特点**：
- 运行在你自己的电脑或服务器上
- **不需要公网 IP**（重要！）
- **不需要开放任何端口**
- 你的应用主动向外连接到 Coze 云端
- 只在你运行脚本时才活跃

### 1.2 配置 cozepy 应用以接收 SSE 流式响应

#### 关键点：连接方向

**重要理解**：

```
错误理解 ❌: Coze Bot → cozepy 应用
             (Bot 主动连接到本地应用)

正确理解 ✅: cozepy 应用 → Coze Bot
             (本地应用主动连接到云端 Bot)
```

**为什么本地应用无需公网 IP？**

因为是**本地应用主动向外发起连接**：
1. 本地应用发起 HTTP 请求到 Coze 云端 API
2. Coze 返回 SSE（Server-Sent Events）流
3. 本地应用保持这个连接，持续接收事件
4. 这是**单向推送**：云端 → 本地（在已建立的连接上）

类似于：
- 你打开浏览器访问网站（主动连接）
- 网站推送实时通知给你（在已有连接上）
- 你不需要公网 IP 或开放端口

#### 具体配置步骤

**步骤 1：准备配置信息**

在 Coze 平台获取：
- **COZE_API_TOKEN**：你的个人访问令牌
  - 获取地址：https://www.coze.cn/open/oauth/pats
  - 创建一个新的 Personal Access Token
  
- **COZE_BOT_ID**：你的 Bot ID
  - 在 Bot 详情页面可以找到
  - 格式类似：`73xxxxxxxxxxxxxx19`

**步骤 2：编写 cozepy 应用代码**

```python
import os
from cozepy import (
    COZE_CN_BASE_URL,
    ChatEvent,
    ChatEventType,
    Coze,
    Message,
    Stream,
    TokenAuth,
    ToolOutput,
)

# 配置信息
COZE_API_TOKEN = os.getenv("COZE_API_TOKEN") or "your-token-here"
COZE_BOT_ID = os.getenv("COZE_BOT_ID") or "your-bot-id-here"

def main():
    # 1. 创建 Coze 客户端（主动连接到云端）
    coze = Coze(
        auth=TokenAuth(COZE_API_TOKEN),  # 你的认证令牌
        base_url=COZE_CN_BASE_URL        # 国内版: api.coze.cn
    )
    
    # 2. 发起流式对话（建立 SSE 连接）
    print("正在连接到 Coze Bot...")
    user_input = input("请输入你的问题：")
    
    stream = coze.chat.stream(
        bot_id=COZE_BOT_ID,
        user_id="user-123",  # 用户标识
        additional_messages=[
            Message.build_user_question_text(user_input)
        ]
    )
    
    # 3. 监听事件流
    print("已连接，等待 Bot 响应...\n")
    handle_stream(coze, stream)

def handle_stream(coze: Coze, stream: Stream[ChatEvent]):
    """处理 SSE 事件流"""
    for event in stream:
        # 普通消息输出
        if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
            print(event.message.content, end="", flush=True)
        
        # 端插件调用事件
        elif event.event == ChatEventType.CONVERSATION_CHAT_REQUIRES_ACTION:
            print("\n[检测到端插件调用请求]")
            handle_local_plugin(coze, event)

def handle_local_plugin(coze: Coze, event: ChatEvent):
    """处理端插件调用"""
    required_action = event.chat.required_action
    tool_call = required_action.submit_tool_outputs.tool_calls[0]
    
    print(f"工具名称: {tool_call.function.name}")
    print(f"工具参数: {tool_call.function.arguments}")
    
    # 执行本地功能（例如：生成草稿）
    result = execute_local_function(
        tool_call.function.name,
        tool_call.function.arguments
    )
    
    # 提交结果回云端 Bot
    output = ToolOutput(
        tool_call_id=tool_call.id,
        output=result
    )
    
    # 继续 SSE 流
    new_stream = coze.chat.submit_tool_outputs(
        conversation_id=event.chat.conversation_id,
        chat_id=event.chat.id,
        tool_outputs=[output],
        stream=True
    )
    
    # 继续监听
    handle_stream(coze, new_stream)

def execute_local_function(name: str, arguments: str):
    """执行本地功能"""
    import json
    
    if name == "generate_draft":
        # 调用本地草稿生成逻辑
        args = json.loads(arguments)
        # ... 你的草稿生成代码 ...
        return json.dumps({"status": "success", "draft_id": "..."})
    
    return json.dumps({"error": "Unknown function"})

if __name__ == "__main__":
    main()
```

**步骤 3：运行应用**

```bash
# 设置环境变量
export COZE_API_TOKEN="your-token"
export COZE_BOT_ID="your-bot-id"

# 运行应用
python your_cozepy_app.py
```

**运行效果**：

```
正在连接到 Coze Bot...
请输入你的问题：帮我生成一个视频
已连接，等待 Bot 响应...

[Bot 回复]: 好的，我来帮你生成视频...
[检测到端插件调用请求]
工具名称: generate_draft
工具参数: {"content": "...", "output_folder": null}
[本地执行草稿生成...]
[提交结果回 Bot...]
[Bot 继续回复]: 草稿已生成！草稿ID是...
```

#### 网络流程图

```
┌──────────────┐                    ┌──────────────┐
│ 本地 cozepy  │                    │  Coze Cloud  │
│   应用       │                    │    Bot       │
└──────┬───────┘                    └──────┬───────┘
       │                                   │
       │ 1. POST /v3/chat (stream=true)   │
       ├──────────────────────────────────>│
       │    Authorization: ******         │
       │                                   │
       │ 2. SSE Stream 建立                │
       │<──────────────────────────────────┤
       │    Content-Type: text/event-stream│
       │                                   │
       │ 3. 持续接收事件                   │
       │<──────────────────────────────────┤
       │    event: message.delta           │
       │    data: {"content": "你好..."}    │
       │                                   │
       │ 4. 接收端插件调用事件             │
       │<──────────────────────────────────┤
       │    event: requires_action         │
       │    data: {"tool_call": {...}}     │
       │                                   │
       │ 5. 本地执行功能                   │
       ├───┐                               │
       │   │ [截图/读文件/生成草稿等]      │
       │<──┘                               │
       │                                   │
       │ 6. 提交结果                       │
       ├──────────────────────────────────>│
       │    POST /v3/chat/submit_outputs   │
       │    tool_outputs: [...]            │
       │                                   │
       │ 7. 新的 SSE Stream                │
       │<──────────────────────────────────┤
       │    继续接收后续响应                │
       │                                   │
```

**关键点**：
- ✅ 所有连接都是本地应用主动发起的（向外连接）
- ✅ 不需要本地应用有公网 IP
- ✅ 不需要开放任何端口
- ✅ 使用标准的 HTTPS 协议，可以穿透防火墙和 NAT

## 问题 2："端插件"是什么？为什么需要它？

### 2.1 端插件的定义

**端插件**（Local Plugin / 本地插件）是 Coze 平台提供的一种特殊插件类型，允许 Bot 调用运行在**用户本地设备**上的功能。

### 2.2 与云侧插件的对比

| 特性 | 云侧插件 | 端插件 |
|------|---------|--------|
| **运行位置** | Coze 云端服务器 | 用户本地设备 |
| **访问范围** | 只能访问公网资源 | 可以访问本地资源 |
| **典型用途** | API 调用、数据库查询 | 截图、读取本地文件、生成本地文件 |
| **需要公网 IP** | 需要（服务端） | 不需要（客户端） |
| **配置方式** | 在 Coze IDE 中创建 | 配置为"端插件"类型 |

### 2.3 为什么需要端插件？

#### 使用场景 1：访问本地文件系统

**问题**：用户想让 Bot 分析本地代码项目

```
用户: "帮我分析一下 /home/user/project 目录下的 Python 代码"
```

**云侧插件**：
- ❌ 无法访问用户本地文件系统
- ❌ 无法读取 `/home/user/project` 目录

**端插件**：
- ✅ 本地应用可以读取本地文件
- ✅ 将文件内容提交给 Bot 分析

#### 使用场景 2：本地设备控制

**问题**：用户想让 Bot 截取当前屏幕

```
用户: "帮我看看我电脑屏幕上的错误信息"
```

**云侧插件**：
- ❌ 无法访问用户的屏幕
- ❌ 无法执行截图操作

**端插件**：
- ✅ 本地应用可以调用系统 API 截图
- ✅ 将截图上传给 Bot 分析

#### 使用场景 3：生成本地文件（与本项目相关）

**问题**：用户想让 Bot 生成剪映草稿到本地

```
用户: "帮我生成一个视频草稿"
```

**云侧插件方案**（当前实现）：
- ⚠️ Bot 生成 JSON → 需要用户手动下载 → 粘贴到草稿生成器
- ⚠️ 或者需要公网 IP（使用 ngrok 等）

**端插件方案**（可选实现）：
- ✅ Bot 调用本地端插件
- ✅ 本地应用直接生成草稿文件到剪映目录
- ✅ 无需公网 IP，无需手动操作

### 2.4 端插件的工作机制

#### 配置步骤

**1. 在 Coze 平台配置端插件**

创建插件时选择类型为"端插件"：

```json
{
  "api": {
    "type": "localplugin",
    "url": "http://localhost:3333/openapi.yaml"
  }
}
```

**注意**：这里的 URL 仅用于定义接口规范，不是实际调用地址！

**2. 定义工具函数**

在端插件配置中定义工具：

```yaml
# openapi.yaml
paths:
  /generate_draft:
    post:
      summary: "生成剪映草稿"
      parameters:
        - name: content
          in: body
          required: true
          schema:
            type: string
      responses:
        200:
          description: "草稿生成成功"
```

**3. 在本地应用中实现工具**

```python
class LocalPlugin:
    def generate_draft(self, tool_call_id: str, arguments: str) -> ToolOutput:
        """本地实现草稿生成"""
        import json
        from app.utils.draft_generator import DraftGenerator
        
        args = json.loads(arguments)
        generator = DraftGenerator()
        
        # 执行本地草稿生成
        draft_ids = generator.generate(
            content=args['content'],
            output_folder=None  # 使用默认路径
        )
        
        # 返回结果
        return ToolOutput(
            tool_call_id=tool_call_id,
            output=json.dumps({
                "status": "success",
                "draft_ids": draft_ids
            })
        )
```

#### 调用流程

```
1. 用户发送消息给 Bot
   用户 → Coze Bot: "生成视频草稿"

2. Bot 决定调用端插件
   Coze Bot → 生成 REQUIRES_ACTION 事件

3. 本地应用收到事件
   SSE Stream → 本地 cozepy 应用
   event.event == ChatEventType.CONVERSATION_CHAT_REQUIRES_ACTION

4. 本地应用执行功能
   本地应用 → 调用 LocalPlugin.generate_draft()
   本地应用 → 生成草稿文件到本地

5. 提交结果回 Bot
   本地应用 → Coze Bot: submit_tool_outputs()
   {"status": "success", "draft_ids": [...]}

6. Bot 继续对话
   Coze Bot → 用户: "草稿已生成！文件在..."
```

## 问题 3：监听、处理、生成、返回的实现细节

### 3.1 监听 Coze 事件流

#### 技术原理：SSE (Server-Sent Events)

SSE 是一种服务器向客户端推送实时数据的技术：

```python
# 发起 SSE 连接
stream = coze.chat.stream(
    bot_id=bot_id,
    user_id=user_id,
    additional_messages=[Message.build_user_question_text(user_input)]
)

# stream 是一个迭代器，持续产生事件
# 底层使用 HTTP/1.1 chunked transfer encoding
# Content-Type: text/event-stream
```

#### 事件类型

```python
for event in stream:
    # 事件类型枚举
    if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
        # Bot 正在输出消息（增量）
        print(event.message.content, end="")
    
    elif event.event == ChatEventType.CONVERSATION_CHAT_REQUIRES_ACTION:
        # Bot 需要调用端插件
        handle_local_plugin(coze, event)
    
    elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
        # 对话完成
        break
```

### 3.2 处理端插件调用

#### 解析调用请求

```python
def handle_local_plugin(coze: Coze, event: ChatEvent):
    # 1. 获取调用信息
    required_action = event.chat.required_action
    tool_calls = required_action.submit_tool_outputs.tool_calls
    
    # 2. 遍历所有工具调用（可能有多个）
    outputs = []
    for tool_call in tool_calls:
        # 工具名称
        function_name = tool_call.function.name
        # 工具参数（JSON 字符串）
        arguments = tool_call.function.arguments
        # 调用 ID（用于匹配响应）
        call_id = tool_call.id
        
        # 3. 执行对应的本地功能
        result = execute_function(function_name, arguments)
        
        # 4. 构建输出
        outputs.append(ToolOutput(
            tool_call_id=call_id,
            output=result
        ))
    
    # 5. 提交所有结果
    submit_results(coze, event, outputs)
```

#### 路由到具体函数

```python
def execute_function(name: str, arguments: str) -> str:
    """根据函数名称路由到具体实现"""
    import json
    
    args = json.loads(arguments)
    
    # 路由表
    if name == "generate_draft":
        return generate_draft_handler(args)
    elif name == "screenshot":
        return screenshot_handler(args)
    elif name == "list_files":
        return list_files_handler(args)
    else:
        return json.dumps({"error": f"Unknown function: {name}"})
```

### 3.3 生成草稿

#### 集成现有代码

```python
from app.utils.draft_generator import DraftGenerator

def generate_draft_handler(args: dict) -> str:
    """草稿生成处理器"""
    try:
        # 1. 创建草稿生成器
        generator = DraftGenerator()
        
        # 2. 执行生成
        draft_ids = generator.generate(
            content=args['content'],
            output_folder=args.get('output_folder')
        )
        
        # 3. 返回结果（JSON 字符串）
        return json.dumps({
            "status": "success",
            "message": f"成功生成 {len(draft_ids)} 个草稿",
            "draft_ids": draft_ids
        })
    
    except Exception as e:
        # 错误处理
        return json.dumps({
            "status": "error",
            "message": str(e)
        })
```

### 3.4 返回结果给 Bot

#### 提交结果

```python
def submit_results(coze: Coze, event: ChatEvent, outputs: List[ToolOutput]):
    """提交工具执行结果回 Bot"""
    
    # 1. 调用 submit_tool_outputs API
    new_stream = coze.chat.submit_tool_outputs(
        conversation_id=event.chat.conversation_id,
        chat_id=event.chat.id,
        tool_outputs=outputs,
        stream=True  # 继续使用流式响应
    )
    
    # 2. 继续监听新的事件流
    # Bot 会根据结果继续生成回复
    handle_stream(coze, new_stream)
```

#### 完整的递归处理

```python
def handle_stream(coze: Coze, stream: Stream[ChatEvent]):
    """递归处理事件流"""
    for event in stream:
        if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
            # 输出 Bot 回复
            print(event.message.content, end="", flush=True)
        
        elif event.event == ChatEventType.CONVERSATION_CHAT_REQUIRES_ACTION:
            # 处理端插件调用
            required_action = event.chat.required_action
            tool_calls = required_action.submit_tool_outputs.tool_calls
            
            outputs = []
            for tool_call in tool_calls:
                result = execute_function(
                    tool_call.function.name,
                    tool_call.function.arguments
                )
                outputs.append(ToolOutput(
                    tool_call_id=tool_call.id,
                    output=result
                ))
            
            # 提交并继续（递归）
            new_stream = coze.chat.submit_tool_outputs(
                conversation_id=event.chat.conversation_id,
                chat_id=event.chat.id,
                tool_outputs=outputs,
                stream=True
            )
            
            # 递归调用自己处理新流
            handle_stream(coze, new_stream)
            break  # 退出当前循环
```

## 完整示例：端插件版本的 Coze2JianYing

### 实现代码

```python
#!/usr/bin/env python3
"""
Coze2JianYing 端插件版本
演示如何使用 cozepy 端插件机制生成草稿
"""

import os
import json
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from cozepy import (
    COZE_CN_BASE_URL,
    ChatEvent,
    ChatEventType,
    Coze,
    Message,
    Stream,
    TokenAuth,
    ToolOutput,
)
from app.utils.draft_generator import DraftGenerator

# 配置
COZE_API_TOKEN = os.getenv("COZE_API_TOKEN")
COZE_BOT_ID = os.getenv("COZE_BOT_ID")

class Coze2JianYingLocalPlugin:
    """Coze2JianYing 本地插件实现"""
    
    def __init__(self, coze: Coze):
        self.coze = coze
        self.generator = DraftGenerator()
    
    def generate_draft(self, tool_call_id: str, arguments: str) -> ToolOutput:
        """生成草稿"""
        try:
            args = json.loads(arguments)
            
            # 执行草稿生成
            draft_ids = self.generator.generate(
                content=args['content'],
                output_folder=args.get('output_folder')
            )
            
            # 获取草稿路径
            default_folder = self.generator.detect_default_draft_folder()
            draft_info = []
            for draft_id in draft_ids:
                draft_info.append({
                    "draft_id": draft_id,
                    "folder_path": f"{default_folder}/{draft_id}"
                })
            
            return ToolOutput(
                tool_call_id=tool_call_id,
                output=json.dumps({
                    "status": "success",
                    "message": f"成功生成 {len(draft_ids)} 个草稿",
                    "drafts": draft_info
                })
            )
        
        except Exception as e:
            return ToolOutput(
                tool_call_id=tool_call_id,
                output=json.dumps({
                    "status": "error",
                    "message": str(e)
                })
            )

def handle_local_plugin(coze: Coze, event: ChatEvent, plugin: Coze2JianYingLocalPlugin):
    """处理端插件调用"""
    required_action = event.chat.required_action
    tool_calls = required_action.submit_tool_outputs.tool_calls
    
    outputs = []
    for tool_call in tool_calls:
        print(f"\n执行端插件: {tool_call.function.name}")
        
        if tool_call.function.name == "generate_draft":
            output = plugin.generate_draft(
                tool_call.id,
                tool_call.function.arguments
            )
            outputs.append(output)
    
    # 提交结果并继续
    new_stream = coze.chat.submit_tool_outputs(
        conversation_id=event.chat.conversation_id,
        chat_id=event.chat.id,
        tool_outputs=outputs,
        stream=True
    )
    
    handle_stream(coze, new_stream, plugin)

def handle_stream(coze: Coze, stream: Stream[ChatEvent], plugin: Coze2JianYingLocalPlugin):
    """处理事件流"""
    for event in stream:
        if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
            print(event.message.content, end="", flush=True)
        
        elif event.event == ChatEventType.CONVERSATION_CHAT_REQUIRES_ACTION:
            handle_local_plugin(coze, event, plugin)
            break

def main():
    """主函数"""
    if not COZE_API_TOKEN or not COZE_BOT_ID:
        print("请设置环境变量：")
        print("  export COZE_API_TOKEN='your-token'")
        print("  export COZE_BOT_ID='your-bot-id'")
        return
    
    # 创建 Coze 客户端
    coze = Coze(
        auth=TokenAuth(COZE_API_TOKEN),
        base_url=COZE_CN_BASE_URL
    )
    
    # 创建本地插件
    plugin = Coze2JianYingLocalPlugin(coze)
    
    print("Coze2JianYing 端插件已启动")
    print("=" * 60)
    
    while True:
        user_input = input("\n\n请输入你的需求（输入 'exit' 退出）：")
        if user_input.lower() == 'exit':
            break
        
        # 发起对话
        stream = coze.chat.stream(
            bot_id=COZE_BOT_ID,
            user_id="user-local",
            additional_messages=[Message.build_user_question_text(user_input)]
        )
        
        print("\nBot 回复：")
        handle_stream(coze, stream, plugin)

if __name__ == "__main__":
    main()
```

### 使用方法

```bash
# 1. 配置环境变量
export COZE_API_TOKEN="your-token"
export COZE_BOT_ID="your-bot-id"

# 2. 运行端插件应用
python coze2jianying_local_plugin.py

# 3. 交互
请输入你的需求：帮我生成一个介绍中国美食的视频

Bot 回复：
好的，我来帮你生成视频草稿...
执行端插件: generate_draft
[草稿生成中...]
草稿已生成！草稿ID是 xxx，文件夹路径是 yyy
```

## 总结

### 关键点回顾

1. **部署位置**：
   - ✅ Coze Bot 在云端（公网）
   - ✅ cozepy 应用在本地（无需公网 IP）

2. **连接方式**：
   - ✅ 本地应用**主动连接**到云端 Bot（向外连接）
   - ✅ 通过 SSE 接收事件推送
   - ✅ 不需要开放端口或公网 IP

3. **端插件作用**：
   - ✅ 让 Bot 能够调用本地设备上的功能
   - ✅ 访问本地文件系统
   - ✅ 执行本地操作（截图、文件生成等）

4. **实现机制**：
   - ✅ 监听：SSE 事件流
   - ✅ 处理：检测 REQUIRES_ACTION 事件
   - ✅ 生成：调用本地函数（如 DraftGenerator）
   - ✅ 返回：submit_tool_outputs() 提交结果

### 与当前项目方案的对比

| 特性 | 端插件方案 | 当前 API 方案 |
|------|-----------|--------------|
| **用户操作** | 完全自动 | 需要 ngrok（本地）或部署服务器（云端） |
| **公网要求** | 不需要 | 需要（API 需要公网访问） |
| **部署复杂度** | 简单（运行脚本） | 中等（配置内网穿透或云服务器） |
| **适用场景** | 个人使用 | 个人 + 团队 + 生产环境 |
| **扩展性** | 有限 | 强（RESTful API） |

### 建议

**当前项目架构保持不变（API 方案）**，原因：
- ✅ 支持更多部署模式
- ✅ 更容易扩展和维护
- ✅ 标准化的 RESTful API

**端插件作为可选增强**：
- 可以在未来作为"简易模式"提供
- 适合不想配置网络的个人用户
- 作为独立的启动脚本，不影响现有架构

---

**文档版本**: v1.0  
**创建时间**: 2025-11-04  
**相关 Issue**: [#125](https://github.com/Gardene-el/Coze2JianYing/issues/125)
