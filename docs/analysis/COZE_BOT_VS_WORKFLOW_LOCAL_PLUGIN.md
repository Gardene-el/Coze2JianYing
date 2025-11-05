# Coze 端插件：Bot vs Workflow 使用指南

本文档解释端插件在 Coze Bot 和 Coze Workflow 中的使用差异。

## 📋 核心问题

**问题**：端插件是否只能和 Coze Bot 进行事件驱动的流式对话？如果要给 Coze Workflow 使用端插件，会有什么区别？

**答案**：端插件**既可以用于 Bot，也可以用于 Workflow**，但使用方式和交互模式有显著区别。

## 🔍 技术架构对比

### 底层机制（相同）

无论是 Bot 还是 Workflow，端插件的底层技术是相同的：

```
┌─────────────────────────────────────────────────────────┐
│           端插件底层机制（Bot 和 Workflow 通用）         │
├─────────────────────────────────────────────────────────┤
│  1. SSE 流式通信                                         │
│  2. REQUIRES_ACTION 事件                                 │
│  3. submit_tool_outputs() 提交结果                       │
│  4. 本地应用主动连接云端                                 │
└─────────────────────────────────────────────────────────┘
```

**共同点**：
- ✅ 都使用 SSE（Server-Sent Events）进行通信
- ✅ 都通过 `CONVERSATION_CHAT_REQUIRES_ACTION` 事件触发
- ✅ 都使用 `coze.chat.submit_tool_outputs()` 提交结果
- ✅ 本地应用都不需要公网 IP

### 使用方式（不同）

虽然底层技术相同，但 Bot 和 Workflow 的使用方式差异很大：

## 🤖 Bot 中的端插件

### 特点

**对话驱动**：由用户消息触发，AI 决定是否调用工具

```
用户 → Bot: "帮我截个图"
Bot → 分析意图
Bot → 决定调用端插件 "screenshot"
本地应用 → 执行截图
本地应用 → 提交结果
Bot → 用户: "已截图，图片内容是..."
```

### 交互流程

```python
# Bot 端插件示例
def chat_with_bot():
    coze = Coze(auth=TokenAuth(token), base_url=COZE_CN_BASE_URL)
    
    # 用户发送消息
    user_input = input("你：")
    
    # 发起对话
    stream = coze.chat.stream(
        bot_id=bot_id,
        user_id=user_id,
        additional_messages=[Message.build_user_question_text(user_input)]
    )
    
    # 监听事件
    for event in stream:
        # Bot 的回复
        if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
            print(event.message.content, end="")
        
        # Bot 决定调用端插件
        elif event.event == ChatEventType.CONVERSATION_CHAT_REQUIRES_ACTION:
            # 执行本地工具
            handle_local_plugin(coze, event)
```

### 使用场景

1. **实时交互**
   ```
   用户："帮我看看桌面上有什么"
   → Bot 调用 screenshot
   → 用户立即看到分析结果
   ```

2. **多轮对话**
   ```
   用户："帮我读取 config.json"
   Bot："文件内容是..."
   用户："帮我修改 port 为 8080"
   Bot 调用 write_file
   → 保持会话上下文
   ```

3. **个性化服务**
   ```
   Bot 记住用户偏好
   根据历史调整工具调用
   ```

### 优点

- ✅ 灵活：AI 自主决定何时调用工具
- ✅ 交互式：用户可以随时介入
- ✅ 智能：Bot 理解上下文，选择合适的工具

### 缺点

- ⚠️ 不确定性：AI 可能不调用工具
- ⚠️ 需要用户参与：必须有人与 Bot 对话
- ⚠️ 难以批量处理：每次都要对话

## 🔄 Workflow 中的端插件

### 特点

**流程驱动**：按工作流节点固定顺序执行，确定性高

```
Workflow 开始
  ↓
节点1: 获取用户输入
  ↓
节点2: 调用端插件 "list_files"  ← 必然执行
  ↓
节点3: 分析文件列表
  ↓
节点4: 调用端插件 "read_file"   ← 必然执行
  ↓
节点5: 生成报告
  ↓
Workflow 结束
```

### 交互流程

```python
# Workflow 端插件示例
def run_workflow():
    coze = Coze(auth=TokenAuth(token), base_url=COZE_CN_BASE_URL)
    
    # 运行工作流（不是对话）
    stream = coze.workflows.run(
        workflow_id=workflow_id,
        parameters={"input_param": "value"}
    )
    
    # 监听工作流事件
    for event in stream:
        # 工作流节点输出
        if event.event == WorkflowEventType.NODE_FINISHED:
            print(f"节点 {event.node_id} 完成")
        
        # 工作流调用端插件
        elif event.event == WorkflowEventType.REQUIRES_ACTION:
            # 执行本地工具（与工作流节点对应）
            handle_workflow_plugin(coze, event)
```

### 关键区别

#### 1. 触发方式

**Bot**：
```python
# AI 决定是否调用
用户："帮我生成草稿"
→ AI 分析意图
→ AI 可能调用 generate_draft，也可能只是回复文本
```

**Workflow**：
```python
# 工作流节点固定调用
Workflow 节点配置：
  - 节点 ID: generate_draft_node
  - 工具: generate_draft (端插件)
  - 参数: {...}
→ 必然执行该工具，确定性 100%
```

#### 2. 参数传递

**Bot**：
```python
# AI 从对话中提取参数
用户："生成一个 1920x1080 的视频草稿"
→ AI 理解：width=1920, height=1080
→ 传递给端插件
```

**Workflow**：
```python
# 从工作流变量或前置节点获取参数
节点配置：
  input:
    width: {{workflow_input.width}}    # 工作流输入
    height: {{prev_node.output.height}}  # 上一节点输出
→ 参数明确，无需 AI 解析
```

#### 3. 执行顺序

**Bot**：
```
对话是动态的
→ 用户可能随时改变话题
→ 工具调用顺序不确定
→ 可能多次调用同一工具
```

**Workflow**：
```
流程是固定的
→ 节点按顺序执行
→ 工具调用顺序确定
→ 每个节点只执行一次（除非循环）
```

### 使用场景

1. **自动化任务**
   ```
   每天定时执行：
   1. 读取本地日志
   2. 分析数据
   3. 生成报告
   4. 保存到本地
   → 无需人工干预
   ```

2. **批量处理**
   ```
   Workflow 循环：
   For each file in files:
     1. 调用端插件读取文件
     2. 处理内容
     3. 调用端插件写入结果
   → 批量处理本地文件
   ```

3. **固定流程**
   ```
   视频制作流程：
   1. 生成脚本
   2. 调用端插件下载素材到本地
   3. 调用端插件生成剪映草稿
   4. 返回草稿路径
   → 流程固定，可重复执行
   ```

### 优点

- ✅ 确定性：工具必然被调用
- ✅ 自动化：无需用户交互
- ✅ 批量处理：可处理大量任务
- ✅ 可重复：相同输入产生相同结果

### 缺点

- ⚠️ 不够灵活：无法动态调整
- ⚠️ 需要预先设计：工作流需要提前规划
- ⚠️ 调试复杂：流程出错需要逐节点排查

## 📊 详细对比表

| 维度 | Bot 端插件 | Workflow 端插件 |
|------|-----------|----------------|
| **触发方式** | 对话消息，AI 决定 | 工作流节点，固定执行 |
| **交互性** | 需要用户输入 | 全自动，无需用户 |
| **确定性** | 低（AI 决策） | 高（预定义流程） |
| **参数来源** | AI 从对话提取 | 工作流变量/前置节点 |
| **执行顺序** | 动态，不确定 | 固定，可预测 |
| **状态管理** | 会话上下文 | 工作流变量 |
| **适用场景** | 实时交互、个性化服务 | 自动化任务、批量处理 |
| **灵活性** | 高 | 低 |
| **可重复性** | 低 | 高 |
| **调试难度** | 中 | 高 |

## 🔧 实际应用示例

### 示例 1：生成剪映草稿

#### Bot 方式

```python
# 用户对话触发
用户："帮我生成一个美食视频的草稿"

Bot 执行：
1. 理解用户意图
2. 可能先问："您想要什么风格？"
3. 用户回答后，决定调用 generate_draft
4. 调用端插件
5. 返回："草稿已生成在 C:/..."

特点：交互式，AI 自主决策
```

#### Workflow 方式

```python
# 工作流固定流程
输入：{"topic": "美食", "style": "快节奏"}

执行流程：
节点1: 生成脚本（AI 节点）
节点2: 生成图片（AI 绘图）
节点3: 生成配音（TTS）
节点4: 调用端插件 generate_draft
  参数：
    - content: {{node1.output}}
    - images: {{node2.output}}
    - audio: {{node3.output}}
节点5: 返回结果

特点：自动化，流程固定
```

### 示例 2：本地文件分析

#### Bot 方式

```python
用户："帮我分析一下项目代码"
Bot："好的，请问是哪个目录？"
用户："/home/user/project"
Bot → 调用端插件 list_files
Bot："发现 50 个文件，我来分析..."
用户："只看 Python 文件"
Bot → 再次调用，过滤结果

# 代码
for event in stream:
    if event.event == ChatEventType.CONVERSATION_CHAT_REQUIRES_ACTION:
        # AI 决定调用哪个工具
        tool_name = event.required_action.tool_calls[0].function.name
        if tool_name == "list_files":
            result = list_local_files(args)
        elif tool_name == "read_file":
            result = read_local_file(args)
```

#### Workflow 方式

```python
输入：{"directory": "/home/user/project"}

节点1: 调用端插件 list_files
  参数: {{workflow_input.directory}}
节点2: 过滤 Python 文件（代码节点）
节点3: 循环读取文件
  For each file:
    调用端插件 read_file
节点4: 汇总分析（AI 节点）
节点5: 生成报告

# 代码
for event in stream:
    if event.event == WorkflowEventType.REQUIRES_ACTION:
        # 根据节点 ID 确定调用哪个工具
        node_id = event.node_id
        if node_id == "list_files_node":
            result = list_local_files(args)
        elif node_id == "read_file_node":
            result = read_local_file(args)
```

## 💡 如何选择？

### 选择 Bot 端插件 的情况

✅ **需要实时交互**
- 用户需要参与决策
- 根据用户反馈调整

✅ **灵活性要求高**
- 不同用户有不同需求
- AI 需要理解上下文

✅ **个性化服务**
- 根据用户历史调整
- 智能推荐工具

**示例场景**：
- 智能助手
- 客服机器人
- 个人助理

### 选择 Workflow 端插件 的情况

✅ **自动化任务**
- 无需人工干预
- 定时执行

✅ **批量处理**
- 处理大量文件
- 重复性任务

✅ **固定流程**
- 流程明确
- 需要可重复

**示例场景**：
- 自动化视频制作（如本项目）
- 批量文件处理
- 数据采集和分析

### 结合使用

**最佳实践**：Bot 作为入口，触发 Workflow

```
用户 → Bot: "帮我批量生成 10 个视频"
Bot → 理解需求
Bot → 触发 Workflow
Workflow → 自动执行
  - 节点1-10: 分别生成视频
  - 每个节点调用端插件 generate_draft
Workflow → 完成
Bot → 用户: "已完成，生成了 10 个视频"
```

## 📝 对本项目的影响

### 当前项目需求

**Coze2JianYing 的使用场景**：

```
用户需求：
"帮我生成一个介绍中国美食的视频"

期望流程：
1. 生成脚本
2. 生成图片
3. 生成配音
4. 生成剪映草稿
```

### 推荐方案

**方案 1：纯 Workflow（推荐）**

```
Coze Workflow:
  节点1: AI 生成脚本
  节点2: AI 生成图片
  节点3: TTS 生成配音
  节点4: 云侧插件生成 JSON
  节点5: 端插件/API 生成草稿

优点：
✅ 流程固定，可重复
✅ 批量处理能力
✅ 适合自动化
```

**方案 2：Bot + Workflow 混合**

```
Bot 对话：
  用户描述需求
  ↓
  Bot 理解并确认
  ↓
  触发 Workflow
  ↓
  Workflow 执行（端插件）
  ↓
  Bot 反馈结果

优点：
✅ 用户体验好
✅ 灵活性高
✅ 结合两者优势
```

**方案 3：纯 API（当前实现）**

```
不使用端插件，使用云侧插件 + API

Workflow → 云侧插件 → FastAPI → 草稿生成器

优点：
✅ 无需本地应用常驻
✅ 支持远程部署
✅ 团队协作友好
```

### 结论

**对于 Coze2JianYing 项目**：

1. **端插件可以用于 Workflow**，技术上完全可行
2. **但不推荐**：
   - 需要本地应用常驻运行
   - 不利于团队协作
   - 部署复杂

3. **推荐继续使用当前方案**（云侧插件 + API）：
   - ✅ 更灵活的部署方式
   - ✅ 支持云端部署
   - ✅ 团队协作友好

4. **可选增强**：提供端插件版本作为"简易模式"
   - 适合个人用户
   - 不想配置网络
   - 一键运行

## 🔗 相关文档

- [端插件详解](./COZE_LOCAL_PLUGIN_DETAILED_EXPLANATION.md)
- [API 参数指南](../reference/COZE_API_PARAMETERS_GUIDE.md)
- [Coze 集成指南](../guides/COZE_INTEGRATION_GUIDE.md)
- [Workflow 官方文档](https://www.coze.cn/open/docs/workflow)

---

**文档版本**: v1.0  
**创建时间**: 2025-11-04  
**相关 Issue**: [#125](https://github.com/Gardene-el/Coze2JianYing/issues/125)
