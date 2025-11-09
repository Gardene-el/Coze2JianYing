# Workflow 端插件调查报告

本文档回应 Issue #125/#126 中关于 Workflow 是否支持端插件的问题。

## 📋 问题

用户提出的核心问题：
1. 端插件是否只能被 Bot（智能体）调用？
2. 端插件是否只限于「创建会话」、「发起对话」、「提交工具执行结果」这三个 API？
3. 端插件能否像云侧插件一样，在 Coze 工作流中主动调用？

## 🔍 调查结果

### 1. cozepy SDK API 结构

经过对 cozepy SDK (v0.20.0) 的详细调查，发现：

#### Chat (对话) API

```python
# Bot 模式的 API
coze.chat.stream(
    bot_id=bot_id,
    user_id=user_id,
    additional_messages=[...]
)

# 事件类型
ChatEventType.CONVERSATION_CHAT_REQUIRES_ACTION  # 工具调用请求
```

#### Workflows API 

```python
# ✅ 正确的 API 路径
coze.workflows.runs.stream(
    workflow_id=workflow_id,
    parameters={...}
)

# ❌ 当前实现使用的（错误）
coze.workflows.run(...)  # 这个方法不存在！
```

**发现的问题**：
- 当前实现 (`app/services/local_plugin_service.py` 第 210 行) 使用了 `coze.workflows.run()`
- 实际 SDK 中应该使用 `coze.workflows.runs.stream()`
- 这是一个**实现错误**，需要修复

### 2. Workflow 事件类型

Workflow 的事件类型与 Chat 不同：

```python
# Workflow 事件类型
WorkflowEventType.MESSAGE    # 消息输出
WorkflowEventType.ERROR      # 错误
WorkflowEventType.DONE       # 完成
WorkflowEventType.INTERRUPT  # 中断（可能用于工具调用？）
WorkflowEventType.UNKNOWN    # 未知

# 没有 REQUIRES_ACTION 事件！
```

**WorkflowEvent 结构**：
```python
class WorkflowEvent:
    id: int
    event: WorkflowEventType
    message: Optional[WorkflowEventMessage]
    interrupt: Optional[WorkflowEventInterrupt]  # 中断信息
    error: Optional[WorkflowEventError]
    unknown: Optional[Dict]
```

**WorkflowEventInterrupt 结构**：
```python
class WorkflowEventInterrupt:
    interrupt_data: WorkflowEventInterruptData
    node_title: str

class WorkflowEventInterruptData:
    event_id: str
    type: int  # 类型代码
```

### 3. 关键发现：INTERRUPT 事件的用途

`INTERRUPT` 事件可能用于：
1. 工作流暂停/等待
2. 人工审核节点
3. **可能**用于端插件调用（需要进一步验证）

但与 Chat 的 `REQUIRES_ACTION` 不同，Workflow 的 `INTERRUPT` 事件：
- 没有 `tool_calls` 字段
- 没有 `submit_tool_outputs` 方法的明确对应
- 结构更加简化

### 4. Workflow 端插件支持的不确定性

**问题**：根据 cozepy SDK 的 API 结构，**无法确认 Workflow 是否真正支持端插件**。

**证据**：

**支持的证据**：
- ✅ Coze 官方文档提到端插件可用于 Bot 和 Workflow
- ✅ 项目中的文档 (`COZE_BOT_VS_WORKFLOW_LOCAL_PLUGIN.md`) 描述了 Workflow 使用端插件
- ✅ `INTERRUPT` 事件可能是端插件调用的机制

**不支持的证据**：
- ❌ cozepy SDK 中没有明确的 Workflow 工具调用 API
- ❌ 没有类似 `submit_tool_outputs` 的 Workflow 对应方法
- ❌ `WorkflowEventInterrupt` 结构不包含工具调用信息

### 5. 官方文档对比

#### Coze 官方文档

根据用户提供的链接：
- [通过 API 使用端插件](https://www.coze.cn/open/docs/guides/use_local_plugin)
- [coze-example](https://github.com/coze-dev/coze-cookbook/tree/main/examples/local_plugin)

**需要验证**：官方文档中是否明确说明 Workflow 支持端插件？

#### 当前实现的假设

当前代码假设：
1. Workflow 可以触发端插件调用
2. 使用 `WorkflowEventType.REQUIRES_ACTION` 事件（但这个事件不存在！）
3. 可以使用类似 Chat 的 `submit_tool_outputs` 方法

**这些假设可能是错误的！**

## 🎯 结论

### 确定的事实

1. ✅ **Bot 模式完全支持端插件**
   - API 完整：`chat.stream()` + `REQUIRES_ACTION` 事件
   - 可以提交结果：`chat.submit_tool_outputs()`
   - 已验证可行

2. ❌ **当前 Workflow 实现有错误**
   - 使用了不存在的 `coze.workflows.run()` API
   - 应该使用 `coze.workflows.runs.stream()`

3. ❓ **Workflow 端插件支持不明确**
   - SDK API 结构不清晰
   - 缺少明确的工具调用机制
   - 需要进一步验证

### 回答用户问题

**Q1: 端插件是否只能被 Bot 调用？**

**A1**: 根据 cozepy SDK (v0.20.0) 的 API 结构分析：
- **Bot 模式**：✅ 完全支持，API 完整，已验证
- **Workflow 模式**：❓ 不确定，需要进一步调查

当前实现假设 Workflow 支持端插件，但：
1. 使用了错误的 API (`workflows.run()` 不存在)
2. 假设了不存在的事件类型 (`WorkflowEventType.REQUIRES_ACTION`)
3. 缺少 Workflow 提交工具结果的明确方法

**Q2: 端插件是否只限于创建会话、发起对话、提交工具执行结果？**

**A2**: 对于 **Bot 模式**，是的：
- `coze.chat.stream()` - 发起对话
- `ChatEventType.CONVERSATION_CHAT_REQUIRES_ACTION` - 接收工具调用请求
- `coze.chat.submit_tool_outputs()` - 提交工具执行结果

对于 **Workflow 模式**：
- SDK 中有 `coze.workflows.runs.stream()` API
- 但**没有明确的工具调用和结果提交机制**
- `INTERRUPT` 事件的具体用途不明

**Q3: 端插件能否在 Coze 工作流中主动调用？**

**A3**: **需要进一步验证**。

可能的情况：

**情况 A：Workflow 支持端插件（需要修复实现）**
```python
# 正确的 API
stream = coze.workflows.runs.stream(
    workflow_id=workflow_id,
    parameters=parameters
)

for event in stream:
    if event.event == WorkflowEventType.INTERRUPT:
        # 可能是工具调用？
        # 但如何提交结果？
        # 是否有对应的 resume 方法？
        pass
```

**情况 B：Workflow 不支持端插件**
- 端插件仅限于 Bot 对话场景
- Workflow 只能使用云侧插件（通过 HTTP API）
- 这与用户的预期不符

## 🚨 问题和建议

### 当前实现的问题

1. **API 错误** (严重)
   - `coze.workflows.run()` 不存在
   - 需要改为 `coze.workflows.runs.stream()`

2. **事件类型错误** (严重)
   - 代码假设 `WorkflowEventType.REQUIRES_ACTION` 存在
   - 实际只有 `MESSAGE`, `ERROR`, `DONE`, `INTERRUPT`, `UNKNOWN`

3. **结果提交机制不明** (阻塞)
   - Chat 有 `submit_tool_outputs()`
   - Workflow 有 `runs.resume()` 但不确定是否用于工具调用

### 建议的调查步骤

1. **查阅 Coze 官方文档**
   - 确认 Workflow 是否真正支持端插件
   - 了解 `INTERRUPT` 事件的具体用途
   - 查找 Workflow 工具调用的示例

2. **检查 coze-cookbook 示例**
   - 查看是否有 Workflow 端插件的实际示例
   - 验证 API 使用方式

3. **联系 Coze 技术支持**
   - 询问 Workflow 端插件的官方支持状态
   - 获取正确的 API 使用文档

4. **实际测试**
   - 尝试使用正确的 API 运行 Workflow
   - 观察实际的事件流
   - 验证是否真的可以调用本地工具

## 📚 相关资源

### SDK 文档
- cozepy SDK: https://github.com/coze-dev/coze-py
- 版本: 0.20.0
- 维护者: chyroc@bytedance.com

### 官方文档
- [通过 API 使用端插件](https://www.coze.cn/open/docs/guides/use_local_plugin)
- [Coze API 文档](https://www.coze.cn/open/docs/)

### 相关代码文件
- `app/services/local_plugin_service.py` - 第 210 行 (错误的 API)
- `docs/analysis/COZE_BOT_VS_WORKFLOW_LOCAL_PLUGIN.md` - 第 142-162 行 (假设的 Workflow 用法)

## 🎬 下一步行动

1. **立即修复 API 错误**
   - 将 `coze.workflows.run()` 改为 `coze.workflows.runs.stream()`

2. **验证 Workflow 支持**
   - 查阅官方文档和示例
   - 实际测试 Workflow API

3. **更新文档**
   - 如果 Workflow 不支持端插件，更新相关文档
   - 明确说明端插件的适用范围

4. **回复用户**
   - 说明调查结果
   - 提供明确的答案和建议

---

**调查日期**: 2024-11-09  
**调查者**: GitHub Copilot Agent  
**相关 Issue**: [#125](https://github.com/Gardene-el/Coze2JianYing/issues/125), [#126](https://github.com/Gardene-el/Coze2JianYing/issues/126)  
**状态**: 🔴 需要进一步验证
