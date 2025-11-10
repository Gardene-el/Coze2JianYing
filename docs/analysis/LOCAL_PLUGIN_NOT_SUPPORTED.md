# 端侧插件（Local Plugin）在工作流中不可用的调查报告

本文档详细说明为什么 Coze 的端侧插件无法在工作流（Workflow）中达到预期效果。

## 📋 背景

在 Issue #125 和 #126 中，用户希望了解是否可以使用 cozepy SDK 实现端侧插件，以便：
- 无需公网 IP
- 在本地执行操作
- 在 Coze 工作流中被主动调用（类似云侧插件）

经过详细调查和验证，**结论是：端侧插件无法在工作流中使用**。

## 🔍 详细调查结果

### 1. Bot Chat 模式 - ✅ 支持端侧插件

在 Bot（智能体）对话模式中，cozepy SDK 提供完整的端侧插件支持：

#### API 结构
```python
# 发起对话
stream = coze.chat.stream(
    bot_id=bot_id,
    user_id=user_id,
    additional_messages=[Message.build_user_question_text(user_input)]
)

# 监听事件
for event in stream:
    # Bot 调用端侧插件的事件
    if event.event == ChatEventType.CONVERSATION_CHAT_REQUIRES_ACTION:
        # 获取工具调用信息
        tool_calls = event.chat.required_action.submit_tool_outputs.tool_calls
        
        # 执行本地工具
        for tool_call in tool_calls:
            result = execute_local_tool(tool_call.function.name, tool_call.function.arguments)
            tool_outputs.append(ToolOutput(tool_call_id=tool_call.id, output=result))
        
        # 提交工具执行结果
        coze.chat.submit_tool_outputs(
            conversation_id=event.chat.conversation_id,
            chat_id=event.chat.id,
            tool_outputs=tool_outputs,
            stream=True
        )
```

#### 关键特性
- ✅ **明确的事件类型**：`CONVERSATION_CHAT_REQUIRES_ACTION`
- ✅ **工具调用信息**：包含 `tool_calls` 字段，提供工具名称和参数
- ✅ **结果提交方法**：`submit_tool_outputs()` 方法
- ✅ **官方示例**：`examples/chat_local_plugin.py`

**示例代码来源**：
```python
# coze-py SDK examples/chat_local_plugin.py
if event.event == ChatEventType.CONVERSATION_CHAT_REQUIRES_ACTION:
    if not event.chat.required_action or not event.chat.required_action.submit_tool_outputs:
        continue
    tool_calls = event.chat.required_action.submit_tool_outputs.tool_calls
    tool_outputs: List[ToolOutput] = []
    for tool_call in tool_calls:
        print(f"function call: {tool_call.function.name} {tool_call.function.arguments}")
        local_function = LocalPluginMocker.get_function(tool_call.function.name)
        output = json.dumps({"output": local_function()})
        tool_outputs.append(ToolOutput(tool_call_id=tool_call.id, output=output))

    handle_stream(
        coze.chat.submit_tool_outputs(
            conversation_id=event.chat.conversation_id,
            chat_id=event.chat.id,
            tool_outputs=tool_outputs,
            stream=True,
        )
    )
```

### 2. Workflow 模式 - ❌ 不支持端侧插件

在 Workflow（工作流）模式中，**没有端侧插件支持**：

#### API 结构
```python
# 运行工作流
stream = coze.workflows.runs.stream(
    workflow_id=workflow_id,
    parameters=parameters
)

# 监听事件
for event in stream:
    # Workflow 事件类型
    if event.event == WorkflowEventType.MESSAGE:
        # 消息输出
        pass
    elif event.event == WorkflowEventType.ERROR:
        # 错误
        pass
    elif event.event == WorkflowEventType.INTERRUPT:
        # 中断 - 用于用户交互，不是工具调用！
        pass
    elif event.event == WorkflowEventType.DONE:
        # 完成
        pass
```

#### 关键缺失
- ❌ **没有工具调用事件**：不存在 `REQUIRES_ACTION` 或类似事件
- ❌ **没有工具调用信息**：事件中没有 `tool_calls` 字段
- ❌ **没有结果提交方法**：没有 `submit_tool_outputs()` 的对应方法
- ❌ **没有官方示例**：SDK 中没有 Workflow 端侧插件的示例

#### INTERRUPT 事件的真实用途

Workflow 中的 `INTERRUPT` 事件用于**用户交互节点**（如问答节点），不是用于工具调用：

```python
# INTERRUPT 事件数据结构（来自测试数据）
{
    "interrupt_data": {
        "data": "",
        "event_id": "7404830425073352713/2769808280134765896",
        "type": 2
    },
    "node_title": "问答"
}
```

特点：
- 用于暂停工作流，等待用户输入
- 使用 `resume()` 方法继续执行，传递用户输入数据
- **不包含工具调用信息**
- **不是为端侧插件设计的**

### 3. 技术对比

| 特性 | Bot Chat | Workflow |
|------|----------|----------|
| **本地插件事件** | `CONVERSATION_CHAT_REQUIRES_ACTION` ✅ | **不存在** ❌ |
| **工具调用字段** | `tool_calls` + `submit_tool_outputs` ✅ | **不存在** ❌ |
| **提交结果方法** | `submit_tool_outputs()` ✅ | 只有 `resume()` ⚠️ |
| **官方示例** | `chat_local_plugin.py` ✅ | **没有** ❌ |
| **文档说明** | 明确支持 ✅ | 未提及 ❌ |

### 4. 官方文档验证

#### Bot Chat 端侧插件文档
- ✅ Coze 官方文档：[通过 API 使用端插件](https://www.coze.cn/open/docs/guides/use_local_plugin)
- ✅ SDK 示例：`coze-py/examples/chat_local_plugin.py`
- ✅ 明确说明支持 Bot Chat

#### Workflow 端侧插件文档
- ❌ 官方文档未提及 Workflow 支持端侧插件
- ❌ SDK 中没有 Workflow 端侧插件示例
- ❌ coze-cookbook 中没有相关示例

### 5. cozepy SDK 源码证据

根据对 cozepy SDK (v0.20.0) 的调查：

#### Chat API 结构
```python
class ChatEvent:
    event: ChatEventType
    chat: Chat  # 包含 required_action 字段
    message: Optional[Message]
    # ...

class RequiredAction:
    submit_tool_outputs: SubmitToolOutputs  # 工具调用信息

class SubmitToolOutputs:
    tool_calls: List[ToolCall]  # 工具调用列表
```

#### Workflow API 结构
```python
class WorkflowEvent:
    id: int
    event: WorkflowEventType
    message: Optional[WorkflowEventMessage]
    interrupt: Optional[WorkflowEventInterrupt]  # 中断信息，不是工具调用
    error: Optional[WorkflowEventError]
    unknown: Optional[Dict]

class WorkflowEventInterrupt:
    interrupt_data: WorkflowEventInterruptData
    node_title: str  # 节点标题

class WorkflowEventInterruptData:
    event_id: str
    type: int  # 类型代码，不是工具调用
```

**关键差异**：
- Chat 有专门的 `RequiredAction` 和 `ToolCall` 结构
- Workflow 只有通用的 `Interrupt` 结构，用途完全不同

## 🎯 结论

### 端侧插件的适用范围

**✅ 支持的场景**：
- Bot Chat（智能体对话）模式
- 需要用户交互的场景
- AI 决定何时调用工具

**❌ 不支持的场景**：
- Workflow（工作流）模式
- 自动化批量处理
- 固定流程中的工具调用

### 为什么端侧插件无法在工作流中使用？

1. **架构设计差异**
   - Bot Chat 设计为交互式对话，支持动态工具调用
   - Workflow 设计为固定流程执行，不支持动态本地工具

2. **事件机制不同**
   - Bot Chat 有专门的 `REQUIRES_ACTION` 事件处理工具调用
   - Workflow 只有 `INTERRUPT` 事件处理用户交互

3. **API 接口缺失**
   - Bot Chat 有 `submit_tool_outputs()` 提交工具结果
   - Workflow 没有对应的工具结果提交接口

4. **官方未提供支持**
   - 官方文档只提到 Bot Chat 支持端侧插件
   - SDK 中没有 Workflow 端侧插件的示例代码

## 💡 替代方案

既然端侧插件无法在工作流中使用，以下是可行的替代方案：

### 方案 1：使用 Bot Chat 代替 Workflow

**适用场景**：需要端侧插件功能

```python
# Bot 可以配置内部工作流，同时支持端侧插件
stream = coze.chat.stream(
    bot_id=bot_id,  # Bot 内部配置了工作流逻辑
    user_id=user_id,
    additional_messages=[Message.build_user_question_text(user_input)]
)
```

**优点**：
- ✅ 完整支持端侧插件
- ✅ 可以在 Bot 内部配置工作流逻辑
- ✅ 无需公网 IP

**缺点**：
- ⚠️ 需要用户发起对话
- ⚠️ 不适合完全自动化的场景

### 方案 2：使用云端服务模式（当前项目已实现）

**适用场景**：工作流自动化调用

```python
# 本地启动 FastAPI 服务
# Workflow 通过 API 节点调用（需要公网访问）
```

**优点**：
- ✅ 工作流可以直接调用
- ✅ 适合自动化场景
- ✅ 标准的 RESTful API

**缺点**：
- ⚠️ 需要公网 IP（ngrok 或云服务器）
- ⚠️ 需要维护 HTTP 服务

**说明**：本项目的"云端服务"标签页已经实现了这个方案。

### 方案 3：封装为 HTTP 服务

**适用场景**：需要本地功能，但可以接受 HTTP 方式

```python
# 1. 将本地功能封装为 HTTP API
from fastapi import FastAPI
app = FastAPI()

@app.post("/generate_draft")
def generate_draft(data: dict):
    # 执行本地草稿生成
    return {"draft_id": "..."}

# 2. 使用 ngrok 暴露到公网
# ngrok http 8000

# 3. 在 Workflow 中添加 API 节点
# 调用 https://xxx.ngrok.io/generate_draft
```

**优点**：
- ✅ 工作流可以调用
- ✅ 实现相对简单

**缺点**：
- ⚠️ 需要公网访问（ngrok）
- ⚠️ 本质上是云端服务

## 📚 参考资料

### 官方文档
- [通过 API 使用端插件](https://www.coze.cn/open/docs/guides/use_local_plugin)
- [发起对话](https://www.coze.cn/open/docs/developer_guides/chat_v3)
- [提交工具执行结果](https://www.coze.cn/open/docs/developer_guides/chat_submit_tool_outputs)

### SDK 示例
- Bot Chat 端侧插件：`coze-py/examples/chat_local_plugin.py`
- Workflow 流式执行：`coze-py/examples/workflow_stream.py`
- coze-cookbook：https://github.com/coze-dev/coze-cookbook

### 本项目相关
- 云端服务实现：`app/gui/cloud_service_tab.py`（支持工作流调用，需要公网 IP）
- 本地服务标签页：`app/gui/local_service_tab.py`（已说明不可用）

## 🎬 总结

**核心结论**：

1. ✅ **Bot Chat 完全支持端侧插件**
   - API 完整
   - 文档齐全
   - 有官方示例

2. ❌ **Workflow 不支持端侧插件**
   - 没有工具调用机制
   - 没有 API 支持
   - 官方未提供

3. 💡 **工作流场景的解决方案**
   - 使用 Bot Chat（内部配置工作流逻辑）
   - 使用云端服务模式（需要公网 IP）
   - 将本地功能封装为 HTTP 服务

**建议**：
- 如果必须在工作流中实现，使用本项目的"云端服务"功能
- 如果可以接受对话模式，可以向 Coze 团队反馈，请求 Workflow 支持端侧插件

---

**调查完成日期**：2024-11-10  
**相关 Issue**：[#125](https://github.com/Gardene-el/Coze2JianYing/issues/125), [#126](https://github.com/Gardene-el/Coze2JianYing/issues/126)  
**调查结论**：端侧插件仅支持 Bot Chat，不支持 Workflow
