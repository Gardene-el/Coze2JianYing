# Coze API 参数详解与获取指南

本文档详细说明如何正确填写 `coze.chat.stream()` 的各项参数，以及如何从 Coze 平台获取这些值。

## 📋 参数总览

```python
stream = coze.chat.stream(
    bot_id="your-bot-id",              # 必需：Bot ID
    user_id="user-123",                # 必需：用户标识
    additional_messages=[...],         # 必需：消息内容
    conversation_id=None,              # 可选：会话ID
    stream=True,                       # 可选：是否流式返回
    custom_variables={},               # 可选：自定义变量
    auto_save_history=True,            # 可选：是否保存历史
)
```

## 1. bot_id（必需）

### 参数说明

- **类型**: `string`
- **用途**: Bot 的唯一标识符，用于指定要对话的 Bot
- **格式**: 通常是一串数字，例如 `"7365396538596818950"`

### 获取方法

#### 方法 1：从 Bot 详情页获取

1. 登录 [Coze 平台](https://www.coze.cn/)
2. 进入"扣子空间"
3. 点击你的 Bot 进入详情页
4. 在 URL 中可以看到 Bot ID

```
URL 示例：
https://www.coze.cn/space/73xxxxx19/bot/73xxxxx50

Bot ID 就是：73xxxxx50
```

#### 方法 2：从 API 接口获取

如果你发布了 Bot 为 API 服务：

1. 进入 Bot 详情页
2. 点击"发布"→"API"
3. 在"接入指南"中可以看到 Bot ID

#### 方法 3：通过代码获取（列出所有 Bot）

```python
from cozepy import Coze, TokenAuth, COZE_CN_BASE_URL

coze = Coze(auth=TokenAuth("your-token"), base_url=COZE_CN_BASE_URL)

# 列出工作空间中的所有 Bot
bots = coze.bots.list(space_id="your-space-id")
for bot in bots:
    print(f"Bot Name: {bot.name}, Bot ID: {bot.bot_id}")
```

### 填写示例

```python
# 正确示例
bot_id = "7365396538596818950"  # 从 Coze 平台复制的 Bot ID

# 错误示例
bot_id = "my-bot"               # ❌ 不能使用自定义名称
bot_id = "bot-123"              # ❌ 不能使用简写
```

## 2. user_id（必需）

### 参数说明

- **类型**: `string`
- **用途**: 标识当前对话的用户，用于会话管理、对话历史、用户画像等
- **格式**: 任意字符串，建议使用有意义的标识符

### 填写原则

#### 原则 1：保持一致性

同一用户的多次对话应使用相同的 `user_id`，这样：
- Bot 可以记住之前的对话内容
- 可以使用个性化功能
- 方便追踪用户行为

```python
# 推荐：使用用户的真实 ID
user_id = "user-12345"          # 来自你的用户系统
user_id = "alice@example.com"   # 使用邮箱
user_id = "github:alice"        # 使用第三方平台ID
```

#### 原则 2：唯一性

不同用户应使用不同的 `user_id`：

```python
# 为每个用户生成唯一 ID
import uuid

# 方法 1：使用 UUID
user_id = str(uuid.uuid4())  # "a1b2c3d4-..."

# 方法 2：使用用户登录名
user_id = f"user-{username}"  # "user-alice"

# 方法 3：使用会话ID（临时用户）
user_id = f"session-{session_id}"
```

#### 原则 3：安全性

不要在 `user_id` 中包含敏感信息：

```python
# 安全示例 ✅
user_id = "user-12345"

# 不安全示例 ❌
user_id = "alice-password123"  # 不要包含密码
user_id = "13800138000"        # 不要直接使用手机号
```

### 典型使用场景

#### 场景 1：已登录用户

```python
# 用户已登录你的系统
def chat_with_bot(logged_in_user, message):
    coze = Coze(auth=TokenAuth(token), base_url=COZE_CN_BASE_URL)
    
    # 使用登录用户的 ID
    stream = coze.chat.stream(
        bot_id=BOT_ID,
        user_id=f"user-{logged_in_user.id}",  # 使用用户ID
        additional_messages=[Message.build_user_question_text(message)]
    )
    # ...
```

#### 场景 2：匿名用户

```python
# 用户未登录，生成临时 ID
import secrets

def chat_with_bot_anonymous(message):
    # 生成一次性用户ID
    temp_user_id = f"guest-{secrets.token_urlsafe(8)}"
    
    stream = coze.chat.stream(
        bot_id=BOT_ID,
        user_id=temp_user_id,  # 临时ID
        additional_messages=[Message.build_user_question_text(message)]
    )
    # ...
```

#### 场景 3：测试环境

```python
# 开发测试时使用固定ID
stream = coze.chat.stream(
    bot_id=BOT_ID,
    user_id="test-user",  # 测试用ID
    additional_messages=[...]
)
```

## 3. additional_messages（必需）

### 参数说明

- **类型**: `List[Message]`
- **用途**: 本次对话要发送的消息内容
- **格式**: Message 对象列表

### 构建消息

#### 方法 1：纯文本消息（最常用）

```python
from cozepy import Message

# 构建用户问题
message = Message.build_user_question_text("你好，请帮我生成一个视频")

# 使用
stream = coze.chat.stream(
    bot_id=bot_id,
    user_id=user_id,
    additional_messages=[message]  # 放在列表中
)
```

#### 方法 2：多条消息

```python
messages = [
    Message.build_user_question_text("这是第一条消息"),
    Message.build_user_question_text("这是第二条消息"),
]

stream = coze.chat.stream(
    bot_id=bot_id,
    user_id=user_id,
    additional_messages=messages  # 多条消息
)
```

#### 方法 3：包含图片的消息

```python
# 构建包含图片的消息
message = Message.build_user_question_objects([
    {"type": "text", "text": "请分析这张图片"},
    {"type": "image", "file_url": "https://example.com/image.jpg"}
])

stream = coze.chat.stream(
    bot_id=bot_id,
    user_id=user_id,
    additional_messages=[message]
)
```

#### 方法 4：从用户输入构建

```python
def chat_with_user_input():
    # 获取用户输入
    user_input = input("请输入你的问题：")
    
    # 构建消息
    message = Message.build_user_question_text(user_input)
    
    # 发送
    stream = coze.chat.stream(
        bot_id=BOT_ID,
        user_id="user-123",
        additional_messages=[message]
    )
    
    # 处理响应
    for event in stream:
        if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
            print(event.message.content, end="", flush=True)
```

## 4. conversation_id（可选）

### 参数说明

- **类型**: `string` (可选)
- **用途**: 会话ID，用于继续之前的对话
- **默认**: `None`（创建新会话）

### 使用场景

#### 场景 1：继续之前的对话

```python
# 第一次对话
stream1 = coze.chat.stream(
    bot_id=bot_id,
    user_id=user_id,
    additional_messages=[Message.build_user_question_text("你好")]
)

# 从响应中获取 conversation_id
for event in stream1:
    conversation_id = event.chat.conversation_id
    break

# 继续对话（Bot 会记住之前的内容）
stream2 = coze.chat.stream(
    bot_id=bot_id,
    user_id=user_id,
    conversation_id=conversation_id,  # 使用之前的会话ID
    additional_messages=[Message.build_user_question_text("刚才我说了什么？")]
)
```

#### 场景 2：多轮对话管理

```python
class ConversationManager:
    def __init__(self, bot_id, user_id):
        self.bot_id = bot_id
        self.user_id = user_id
        self.conversation_id = None
        self.coze = Coze(auth=TokenAuth(token), base_url=COZE_CN_BASE_URL)
    
    def chat(self, message):
        """发送消息并保持会话"""
        stream = self.coze.chat.stream(
            bot_id=self.bot_id,
            user_id=self.user_id,
            conversation_id=self.conversation_id,  # 使用当前会话ID
            additional_messages=[Message.build_user_question_text(message)]
        )
        
        # 更新会话ID
        for event in stream:
            if not self.conversation_id:
                self.conversation_id = event.chat.conversation_id
            
            if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                print(event.message.content, end="", flush=True)
    
    def new_conversation(self):
        """开始新会话"""
        self.conversation_id = None

# 使用
manager = ConversationManager(BOT_ID, "user-123")
manager.chat("你好")               # 第一轮
manager.chat("我刚才说了什么？")    # 第二轮，Bot 记得第一轮
manager.new_conversation()         # 重置
manager.chat("你好")               # 新的对话
```

## 5. 其他可选参数

### stream（是否流式返回）

```python
# 流式返回（默认，推荐）
stream = coze.chat.stream(
    bot_id=bot_id,
    user_id=user_id,
    additional_messages=[...],
    stream=True  # 可省略，默认为 True
)

# 非流式返回（一次性获取完整结果）
response = coze.chat.create(  # 注意：使用 create 而非 stream
    bot_id=bot_id,
    user_id=user_id,
    additional_messages=[...]
)
```

### custom_variables（自定义变量）

```python
# 传递自定义变量给 Bot
stream = coze.chat.stream(
    bot_id=bot_id,
    user_id=user_id,
    additional_messages=[...],
    custom_variables={
        "user_name": "Alice",
        "user_level": "VIP",
        "language": "zh-CN"
    }
)
```

### auto_save_history（是否保存历史）

```python
# 不保存对话历史（隐私模式）
stream = coze.chat.stream(
    bot_id=bot_id,
    user_id=user_id,
    additional_messages=[...],
    auto_save_history=False  # 不保存到 Coze 平台
)
```

## 📚 官方文档链接

### 核心文档

1. **Coze 开放平台首页**
   - 网址：https://www.coze.cn/open
   - 内容：平台概览、快速开始

2. **API 文档 - Chat 接口**
   - 网址：https://www.coze.cn/open/docs/chat
   - 内容：详细的 API 参数说明、请求示例

3. **开发者文档 - 对话管理**
   - 网址：https://www.coze.cn/open/docs/developer_guides
   - 内容：会话管理、历史记录、多轮对话

### SDK 和示例

4. **Python SDK（cozepy）**
   - GitHub：https://github.com/coze-dev/coze-py
   - PyPI：https://pypi.org/project/cozepy/
   - 内容：SDK 源码、安装说明

5. **Coze Cookbook（示例代码）**
   - GitHub：https://github.com/coze-dev/coze-cookbook
   - 内容：完整的使用示例、最佳实践

6. **Chat Stream 示例**
   - 直接链接：https://github.com/coze-dev/coze-py/blob/main/examples/chat_stream.py
   - 内容：流式对话的完整示例代码

### 认证相关

7. **获取 Personal Access Token**
   - 网址：https://www.coze.cn/open/oauth/pats
   - 用途：创建和管理 API 令牌

8. **认证文档**
   - 网址：https://www.coze.cn/open/docs/authentication
   - 内容：各种认证方式说明

## 📖 完整示例代码

### 基础示例

```python
#!/usr/bin/env python3
"""
Coze Chat 基础示例
演示如何正确填写各项参数
"""

import os
from cozepy import (
    COZE_CN_BASE_URL,
    ChatEvent,
    ChatEventType,
    Coze,
    Message,
    TokenAuth,
)

# 1. 配置参数（从环境变量或配置文件读取）
COZE_API_TOKEN = os.getenv("COZE_API_TOKEN", "your-token-here")
COZE_BOT_ID = os.getenv("COZE_BOT_ID", "your-bot-id-here")

def main():
    # 2. 创建 Coze 客户端
    coze = Coze(
        auth=TokenAuth(COZE_API_TOKEN),
        base_url=COZE_CN_BASE_URL  # 国内版
    )
    
    # 3. 获取用户输入
    user_input = input("请输入你的问题：")
    
    # 4. 发起流式对话
    stream = coze.chat.stream(
        bot_id=COZE_BOT_ID,                    # Bot ID
        user_id="user-example",                # 用户ID（可自定义）
        additional_messages=[                  # 消息内容
            Message.build_user_question_text(user_input)
        ]
    )
    
    # 5. 处理响应
    print("\nBot 回复：")
    for event in stream:
        if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
            # 输出消息内容
            print(event.message.content, end="", flush=True)
    
    print("\n")

if __name__ == "__main__":
    main()
```

### 高级示例（多轮对话）

```python
#!/usr/bin/env python3
"""
Coze Chat 高级示例
支持多轮对话、会话管理
"""

import os
from cozepy import (
    COZE_CN_BASE_URL,
    ChatEvent,
    ChatEventType,
    Coze,
    Message,
    TokenAuth,
)

class ChatSession:
    """对话会话管理器"""
    
    def __init__(self, token: str, bot_id: str, user_id: str):
        self.coze = Coze(
            auth=TokenAuth(token),
            base_url=COZE_CN_BASE_URL
        )
        self.bot_id = bot_id
        self.user_id = user_id
        self.conversation_id = None
    
    def send_message(self, message: str) -> str:
        """发送消息并获取回复"""
        stream = self.coze.chat.stream(
            bot_id=self.bot_id,
            user_id=self.user_id,
            conversation_id=self.conversation_id,  # 保持会话
            additional_messages=[
                Message.build_user_question_text(message)
            ]
        )
        
        response = ""
        for event in stream:
            # 保存会话ID
            if not self.conversation_id:
                self.conversation_id = event.chat.conversation_id
            
            # 收集回复内容
            if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
                response += event.message.content
                print(event.message.content, end="", flush=True)
        
        print()  # 换行
        return response
    
    def reset(self):
        """重置会话"""
        self.conversation_id = None
        print("会话已重置")

def main():
    # 配置
    token = os.getenv("COZE_API_TOKEN", "your-token")
    bot_id = os.getenv("COZE_BOT_ID", "your-bot-id")
    user_id = "user-example"
    
    # 创建会话
    session = ChatSession(token, bot_id, user_id)
    
    print("Coze Chat 已启动（输入 'exit' 退出，'reset' 重置会话）")
    print("=" * 60)
    
    while True:
        # 获取用户输入
        user_input = input("\n你：")
        
        if user_input.lower() == "exit":
            break
        elif user_input.lower() == "reset":
            session.reset()
            continue
        
        # 发送消息
        print("Bot：", end="")
        session.send_message(user_input)

if __name__ == "__main__":
    main()
```

## ❓ 常见问题

### Q1: Bot ID 在哪里找？

**A**: 
1. 登录 Coze 平台
2. 进入你的 Bot 详情页
3. 查看 URL：`https://www.coze.cn/space/{space_id}/bot/{bot_id}`
4. 最后一段数字就是 Bot ID

### Q2: user_id 可以随便填吗？

**A**: 
- 可以是任意字符串
- 但建议保持一致性（同一用户用同一ID）
- 用于会话管理和用户画像

### Q3: 如何获取 API Token？

**A**: 
1. 访问 https://www.coze.cn/open/oauth/pats
2. 点击"创建令牌"
3. 设置名称和权限
4. 复制生成的 Token

### Q4: 支持哪些消息类型？

**A**: 
- 文本消息（最常用）
- 图片消息
- 文件消息
- 混合消息（文本+图片）

参考示例：https://github.com/coze-dev/coze-py/blob/main/examples/chat_multimode_stream.py

### Q5: 如何调试参数错误？

**A**: 
```python
try:
    stream = coze.chat.stream(...)
except Exception as e:
    print(f"错误：{e}")
    # 检查：
    # 1. Bot ID 是否正确
    # 2. Token 是否有效
    # 3. 参数格式是否正确
```

## 📝 参数检查清单

在调用 API 前，确认：

- [ ] `bot_id`：已从 Coze 平台获取
- [ ] `user_id`：已设置有意义的标识符
- [ ] `additional_messages`：消息格式正确
- [ ] `COZE_API_TOKEN`：Token 有效且有权限
- [ ] 网络连接：可以访问 api.coze.cn

## 🔗 快速链接汇总

| 资源 | 链接 |
|------|------|
| Coze 开放平台 | https://www.coze.cn/open |
| Chat API 文档 | https://www.coze.cn/open/docs/chat |
| Python SDK | https://github.com/coze-dev/coze-py |
| 示例代码库 | https://github.com/coze-dev/coze-cookbook |
| 获取 Token | https://www.coze.cn/open/oauth/pats |
| 开发者指南 | https://www.coze.cn/open/docs/developer_guides |

---

**文档版本**: v1.0  
**最后更新**: 2025-11-04  
**相关文档**: [Coze 端插件详解](./COZE_LOCAL_PLUGIN_DETAILED_EXPLANATION.md)
