# Copilot Instructions for Coze2JianYing

## 项目概述

这是一个完整的 Coze 到剪映工作流项目，核心是**草稿生成器应用** (`app/`)，提供 GUI 界面和 API 后端，将 JSON 转换为剪映草稿文件。

**子项目**：

- **Coze 插件** (`coze_plugin/`) - 为草稿生成器应用提供 Coze 插件配置和源码，处理参数和导出 JSON

**历史遗留**：

- `data_structures/` - 历史遗留的数据结构定义，待明确替代方案后将被移除

### Coze 关键概念

#### 插件 (Plugin)

**插件** 是 Coze 平台上的扩展工具，是Bot能力的核心扩展机制。插件为AI Agent提供了调用外部服务和执行特定任务的能力，使Bot能够突破纯语言交互的限制，完成实际的业务操作。

**插件的作用**：

- **扩展Bot能力边界**：通过插件，Bot可以查询数据库、调用第三方API、处理文件等
- **工具调用机制**：LLM通过Function Calling机制理解用户意图并选择合适的插件工具
- **参数自动提取**：AI从对话中提取工具所需的参数，实现自然语言到API调用的转换
- **结果处理反馈**：工具执行结果返回给LLM，AI整合信息生成最终回复

**插件类型**：

1. **云侧插件 - 在 Coze IDE 中创建**
   - **开发方式**：使用 Coze 提供的在线 IDE 直接编写代码
   - **支持语言**：Python 和 Node.js
   - **代码托管**：代码托管在 Coze 云端，由平台运行和维护
   - **适用场景**：快速原型开发、简单工具函数、无需复杂依赖的场景
   - **核心特点**：
     - 无需部署服务器，代码即服务
     - 内置运行时环境和常用依赖
     - 支持在线调试和测试
     - 资源和超时时间有限制（如 `/tmp` 目录仅 512MB）
   - **对应本项目**：`coze_plugin/` 目录中的工具函数源码，为"**手动草稿生成**"模式提供插件实现
     - 用户在Coze IDE中部署工具函数
     - 工具函数处理参数并生成JSON
     - 用户手动复制JSON到草稿生成器

2. **云侧插件 - 基于已有服务创建**
   - **开发方式**：基于已部署的HTTP/HTTPS服务创建插件
   - **服务位置**：可以是任何可访问的Web服务（云服务器、本地服务等）
   - **配置方式**：通过OpenAPI规范定义接口，配置认证和参数
   - **适用场景**：
     - 集成现有业务系统和API
     - 需要复杂依赖或大规模计算的场景
     - 需要访问内部网络资源
     - 对性能和资源有较高要求
   - **核心特点**：
     - 完全自主控制服务部署和资源
     - 可以使用任何编程语言和框架
     - 支持OAuth 2.0等复杂认证机制
     - 可以处理大规模数据和长时间运行任务
   - **对应本项目**：草稿生成器中的"**云端服务**"标签页，提供API服务模式
     - 草稿生成器启动FastAPI服务（需要公网访问，可通过ngrok等工具）
     - 在Coze中配置API端点和认证
     - Coze工作流自动调用API完成数据传输
     - 实现完全自动化的端到端流程

**插件的核心要素**：

1. **工具 (Tool)**
   - 插件的最小功能单元，每个工具执行一个明确的任务
   - 工具之间相互独立，可组合使用
   - 通过输入参数定义明确指导AI如何提取对话信息

2. **工具描述 (Tool Description)**
   - **名称**：简洁明确的工具名称
   - **功能描述**：详细说明工具的功能和使用场景，帮助LLM理解何时调用
   - **参数定义**：
     - 参数名称、类型、是否必需
     - 参数描述：清晰说明参数含义和格式要求
     - 参数示例：提供典型值帮助AI理解
   - **返回值说明**：描述工具执行结果的格式和含义

3. **Handler 函数** （Coze IDE 插件特有）
   - 每个工具必须导出名为 `handler` 的函数作为入口
   - 接收标准化的 `Args[Input]` 参数
   - 返回符合 `Output` 定义的结果
   - 通过 `args.logger` 记录执行日志

4. **API端点** （基于服务的插件特有）
   - 符合RESTful规范的HTTP接口
   - 使用OpenAPI/Swagger规范描述
   - 支持标准HTTP方法（GET, POST, PUT等）
   - 处理认证和错误响应

#### 工作流 (Workflow)

工作流是Coze平台上的自动化流程编排工具，是实现复杂AI应用的核心机制。

**工作流的作用**：

- **流程编排**：将多个AI能力（对话、插件、知识库等）按业务逻辑串联
- **条件控制**：根据执行结果动态选择分支，实现复杂业务逻辑
- **数据流转**：在不同节点间传递和转换数据
- **异常处理**：统一处理错误和异常情况

**工作流与插件的关系**：

- 工作流可以调用多个插件工具
- 插件工具可以在工作流的不同节点中使用
- 工作流负责协调插件调用顺序和数据传递
- 本项目中，Coze工作流调用插件工具生成草稿数据，最终输出JSON供草稿生成器使用

### 整体工作流程概述

完整的工作流涉及四个步骤的协作：

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────────┐    ┌─────────────┐
│    Coze     │───▶│  Coze 插件       │───▶│ 草稿生成器       │───▶│    剪映     │
│   工作流    │    │ (coze_plugin/)   │    │ (app/)          │    │             │
└─────────────┘    └──────────────────┘    └─────────────────┘    └─────────────┘
```

#### 详细流程说明

1. **Coze 工作流** → 生成素材和对应的参数
2. **Coze 插件** (`coze_plugin/`) → 在 Coze 中调用工具函数，将素材和参数处理后导出标准 JSON 数据
3. **草稿生成器** (`app/`) → 将 JSON 数据转换为剪映草稿文件，下载素材，生成完整项目
   - **方案一：手动粘贴** - 用户手动复制 Coze 插件输出的 JSON，粘贴到草稿生成器的"手动草稿生成"标签页
   - **方案二：云端服务传输** - Coze 通过 API 调用草稿生成器的"云端服务"（FastAPI 后端，需要公网访问），自动传输 JSON 数据
   - **方案三：脚本生成执行** _(实验性，开发中)_ - Coze 工作流生成 Python 脚本，在草稿生成器中执行脚本调用 API 序列。详见下文"🚧 正在开发的功能"部分
4. **剪映** → 用户在剪映中打开生成的草稿，进行最终编辑

#### 设计理念与技术约束

这种分离式架构设计是基于以下考虑：

- **Coze 文件空间限制**: Coze 平台的文件系统存储空间有限 (`/tmp` 目录仅 512MB)
- **工作流完整性需求**: 在 Coze 中单个工作流需要生成完整的剪映草稿内容参数
- **资源传输优化**: Coze 生成的素材都是网页链接形式，插件传输给草稿生成器不会直接传递资源文件，而是传递链接列表
- **独立部署需求**: 草稿生成器可以打包为独立 exe，供不熟悉编程的用户使用

### 项目组件的角色定位

#### 草稿生成器应用 (`app/`) - 核心项目

草稿生成器是本项目的核心，已发展为完整的应用，包含 GUI 界面和 API 后端：

1. **JSON 解析**: 解析 Coze 插件导出的 JSON 数据
2. **素材管理**: 从网络下载素材文件，统一存储管理
3. **草稿生成**: 调用 pyJianYingDraft 生成剪映草稿文件
4. **GUI 应用**: 提供友好的图形界面，支持日志查看和多标签页
   - **手动草稿生成标签页**: 用户手动粘贴 JSON 数据生成草稿
   - **云端服务标签页**: 管理 FastAPI 服务，支持 Coze 通过 API 自动传输数据（需要公网访问）
   - **脚本执行标签页**: 执行从 Coze 导出的 Python 脚本生成草稿
5. **API 后端**: FastAPI 服务，支持远程调用
6. **打包发布**: 可打包为 Windows exe 文件，独立分发

#### Coze 插件 (`coze_plugin/`) - 子项目

为草稿生成器应用提供 Coze 平台上的插件支持：

1. **参数处理与验证**: 接收 Coze 工作流传递的素材链接和处理参数
2. **pyJianYingDraft 功能映射**: 将 pyJianYingDraft 库中所有可设置的剪映参数选项包装为 Coze 工具函数
3. **JSON 数据生成**: 生成标准化的 JSON 格式数据，供草稿生成器使用
4. **链接资源管理**: 处理和验证 Coze 传递的网页链接资源
5. **两种插件形态支持**:
   - 云侧插件源码 (在 Coze IDE 中创建)：提供工具函数源码供用户部署
   - 服务端点配置 (基于已有服务创建)：配合草稿生成器的 API 后端使用

#### pyJianYingDraft 深度集成

本项目的核心组件都依赖 pyJianYingDraft 库：

- **参数完整性**: 理解和应用 pyJianYingDraft 中剪映内容的所有可配置参数
- **功能覆盖**: 确保剪映中所有可选择的参数设置都能在工具函数中体现
- **标准化输出**: 提供标准化的数据结构和参数格式

## 项目当前状态

### ✅ 已完成的核心功能

#### Coze 插件功能

1. **create_draft 工具** - UUID 草稿创建，支持完整的项目配置参数
2. **export_drafts 工具** - 单个和批量草稿导出，支持 `export_all` 功能
3. **get_media_duration 工具** - 网络媒体时长分析和时间轴计算
4. **add_videos/add_images/add_audios/add_captions 工具** - 添加各类媒体和字幕轨道
5. **make\_\*\_info 系列工具** - 动态生成各类段配置 JSON
6. **完整数据模型** - 草稿生成器接口和媒体处理模型
7. **测试体系** - coze_plugin/tests/ 中的完整测试套件

#### 草稿生成器应用功能

1. **GUI 应用** - 基于 Tkinter 的标签页架构图形界面
   - **草稿生成标签页** - 核心的草稿生成功能（手动粘贴 JSON）
   - **云端服务标签页** - FastAPI 服务管理，支持 Coze 通过 API 自动传输数据
   - **脚本执行标签页** - 执行从 Coze 导出的 Python 脚本
2. **API 后端** - FastAPI 服务，提供 RESTful 接口
   - 支持独立运行 (`python start_api.py`)
   - 支持云端服务标签页内启动（需要公网访问，可通过 ngrok）
   - 包含完整的 API 文档 (Swagger UI / ReDoc)
3. **多格式输入支持** - 智能识别多种 JSON 格式
4. **素材管理系统** - 统一下载和存储素材
5. **完整日志系统** - 文件和 GUI 双重日志，嵌入式日志面板
6. **打包脚本** - PyInstaller 构建 exe 文件
7. **GitHub Actions** - 自动化构建和发布

### 🔄 技术架构特点

- **UUID 管理系统**: 解决 Coze 平台状态管理难题
- **网络资源处理**: 支持 Coze 平台的链接资源模式
- **向后兼容性**: 所有系统更新保持 100% 向后兼容
- **错误处理完善**: 包含 NoneType 处理、参数验证等关键修复
- **模块化设计**: 三个子项目相对独立，易于维护
- **标签页架构**: GUI 采用标签页设计，功能模块化，变量隔离
- **API 与 GUI 集成**: 支持多种部署模式（独立 API、独立 GUI、云端服务集成）

### 📋 未来计划功能

- 视频轨道功能增强
- 关键帧动画支持
- 更多高级特效和滤镜
- Coze API 集成完善（当前已有基础配置界面）

### 🚧 正在开发的功能

#### 脚本生成方案 (Script Generation Approach) - **实验性开发中**

> **⚠️ 重要提示**: 此功能正在开发中，遇到重大技术挑战。仅在 issue 中**明确要求**时才进行相关开发工作。

**开发背景** ([Issue #168](https://github.com/Gardene-el/Coze2JianYing/issues/168), [Issue #169](https://github.com/Gardene-el/Coze2JianYing/issues/169)):

开发一种新的草稿生成方案，通过 Coze 插件的"云侧插件 - 在 Coze IDE 中创建"模式，生成并返回一段"按照插件中的工具函数调用顺序来执行对应 API 函数的 Python 脚本"，然后交给 app 来执行生成草稿。

这种方案允许用户在 Coze 工作流中构建草稿操作序列，最终导出为可在草稿生成器中直接执行的 Python 脚本。

**当前开发状态**:

- ✅ `scripts/handler_generator/` 中的生成器脚本已实现
- ✅ 使用生成的 handler 文件和 `export_script` 工具成功生成测试脚本
- ❌ 开发执行脚本的标签页时遇到阻碍
- ❌ handler_generator 脚本存在多个已知问题

**核心组件**:

1. **scripts/handler_generator/** - 开发端脚本生成系统
2. **coze_plugin/raw_tools/** - Coze 云端生成的 handler 文件
3. **coze_plugin/export_script/** - 导出脚本的 Coze 工具
4. **app/gui/** - 计划中的脚本执行标签页（未完成）

**三个执行环境说明**:

此方案涉及三个不同的执行环境，理解它们之间的关系对于开发至关重要：

| 执行环境      | 代码位置                                       | 执行者           | 作用                                        |
| ------------- | ---------------------------------------------- | ---------------- | ------------------------------------------- |
| **开发端**    | `scripts/handler_generator/`                   | 开发者在本地运行 | 从 API 定义自动生成 handler 文件            |
| **Coze 云端** | `coze_plugin/raw_tools/` 中生成的 handler 文件 | Coze 平台运行    | 在 Coze 工作流中记录 API 调用序列到脚本文件 |
| **应用端**    | `app/gui/` 中计划的脚本执行标签页              | 草稿生成器 GUI   | 执行从 Coze 导出的 Python 脚本生成草稿      |

**工作流程图**:

```
┌────────────────────────────────────────────────────────────────────────┐
│ 开发端 (Development Environment)                                       │
│ scripts/handler_generator/                                            │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  1. 扫描 API 定义 (A脚本)                                              │
│  2. 生成 handler 文件 (B-E脚本)                                        │
│     └─> 输出到 coze_plugin/raw_tools/                                 │
│                                                                        │
└────────────────┬───────────────────────────────────────────────────────┘
                 │
                 │ 生成的 handler 文件上传到 Coze
                 ↓
┌────────────────────────────────────────────────────────────────────────┐
│ Coze 云端 (Coze Cloud Environment)                                    │
│ 在 Coze IDE 中部署的 handler 工具                                      │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  1. 用户在 Coze 工作流中调用各种工具                                    │
│  2. 每个工具调用被记录为 Python 代码                                    │
│  3. 代码追加到 /tmp/coze2jianying.py                                   │
│  4. 使用 export_script 工具导出完整脚本                                │
│     └─> 输出: Python 脚本字符串                                        │
│                                                                        │
└────────────────┬───────────────────────────────────────────────────────┘
                 │
                 │ 用户复制脚本到草稿生成器
                 ↓
┌────────────────────────────────────────────────────────────────────────┐
│ 应用端 (Application Environment)                                      │
│ app/gui/ 中计划的脚本执行标签页 (未完成)                               │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  1. 接收从 Coze 导出的 Python 脚本                                     │
│  2. 解析并验证脚本内容                                                  │
│  3. 执行脚本中的 API 调用序列                                          │
│  4. 生成剪映草稿文件                                                    │
│     └─> 输出: 剪映草稿项目                                             │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

#### Handler Generator 模块详解 (`scripts/handler_generator/`)

`scripts/handler_generator/` 包含 5 个核心步骤模块，用于从 FastAPI API 端点自动生成 Coze 兼容的 handler 文件。

##### 模块结构与职责

**数据模型**:

- `api_endpoint_info.py` - API 端点信息数据类，在各模块间传递数据

**步骤 1: API 扫描器** (`scan_api_endpoints.py`)

- **职责**: 扫描 `/src/api` 目录下所有 POST API 函数
- **主要类**: `APIScanner`
- **功能**:
  - 使用 AST 解析识别 `@router.post` 装饰的函数
  - 提取端点路径、请求/响应模型、路径参数等信息
  - 支持异步函数识别
- **输出**: `List[APIEndpointInfo]` 包含所有发现的 API 端点信息

**步骤 6: 文件夹创建器** (`create_tool_scaffold.py`)

- **职责**: 在 `coze_plugin/raw_tools` 下创建对应工具文件夹和文件
- **主要类**: `FolderCreator`
- **功能**:
  - 为每个 API 创建独立的工具目录
  - 生成 `handler.py` 文件
  - 生成 `README.md` 文档
- **输出**: 创建完整的工具目录结构

**步骤 3: Input/Output 生成器** (`generate_io_models.py`)

- **职责**: 定义 Coze handler 的 Input/Output NamedTuple 类型
- **主要类**: `InputOutputGenerator`
- **功能**:
  - 生成 Input 类（包含路径参数 + Request 模型字段）
  - 提取 Output 字段信息（返回 `Dict[str, Any]` 类型）
  - 处理复杂类型简化（如 Optional, List 等）
- **输出**: Input/Output 类型定义代码字符串

**步骤 5: Handler 函数生成器** (`generate_handler_function.py`)

- **职责**: 生成完整的 handler 函数实现
- **主要类**: `HandlerFunctionGenerator`
- **功能**:
  - 生成主 handler 函数框架
  - 实现 UUID 生成逻辑
  - 生成返回值结构
  - 添加错误处理和日志记录
- 调用步骤 4 生成的 API 调用代码
- **输出**: 完整的 handler 函数代码

**步骤 4: API 调用代码生成器** (`generate_api_call_code.py`)

- **职责**: 生成记录 API 调用的 Python 代码
- **主要类**: `APICallCodeGenerator`
- **功能**:
  - 生成 request 对象构造代码
  - 生成 API 调用代码字符串
  - 生成写入 `/tmp/coze2jianying.py` 的逻辑
  - 提取响应中的 ID（draft_id/segment_id）
- **输出**: 可追加到脚本文件的 Python 代码字符串

**辅助模块**: `schema_extractor.py`

- **职责**: 提取 Pydantic Schema 的字段信息
- **主要类**: `SchemaExtractor`
- **功能**:
  - 解析 Pydantic BaseModel 类定义
  - 提取字段名、类型、默认值、描述
  - 处理泛型类型（Optional, List 等）
- **用途**: 被步骤 3/4/5 调用以获取 schema 信息

##### 生成的 Handler 工作原理

生成的每个 handler 文件包含以下逻辑：

1. **接收参数**: 从 Coze 工作流接收 Input 参数
2. **生成 UUID**: 创建唯一标识符用于跟踪此次调用
3. **构造 API 调用代码**: 使用 E 脚本逻辑生成 Python 代码字符串
4. **追加到脚本文件**: 将代码追加到 `/tmp/coze2jianying.py`
5. **返回结果**: 返回包含生成的 UUID 的 Output

例如，调用 `create_draft` handler 时：

```python
# 在 Coze 中生成并追加到 /tmp/coze2jianying.py 的代码：
req_abc123 = CreateDraftRequest(name="我的草稿", canvas_ratio="16:9")
resp_abc123 = await create_draft(req_abc123)
draft_id_abc123 = resp_abc123.draft_id
```

##### 已知问题和挑战 (参考 [Issue #168](https://github.com/Gardene-el/Coze2JianYing/issues/168) 和 [Issue #169](https://github.com/Gardene-el/Coze2JianYing/issues/169))

虽然无法直接访问这些 issue 的详细内容，但根据开发历史和代码结构，已知的挑战包括：

**脚本生成器端 (handler_generator) 的问题**:

1. **类型推断不完善**: 复杂嵌套类型的处理可能不准确
2. **参数映射错误**: 某些 API 参数可能无法正确映射到 Input 类
3. **代码格式问题**: 生成的 Python 代码可能存在格式或语法问题
4. **依赖关系处理**: 多个 API 调用之间的依赖关系可能未正确表达
5. **错误处理不足**: 生成的代码缺少足够的异常处理逻辑

**脚本执行端 (应用标签页) 的问题**:

1. **执行环境差异**: Coze 云端生成的脚本与本地执行环境不匹配
2. **异步执行问题**: 生成的脚本包含 async/await 但执行环境可能不支持
3. **API 认证**: 脚本执行时如何处理 API 认证和授权
4. **错误恢复**: 执行失败时如何恢复和重试
5. **UI 集成**: 如何在 GUI 中展示执行进度和结果

**Coze 平台约束导致的问题**:

1. **文件大小限制**: `/tmp` 目录只有 512MB，生成的脚本可能过大
2. **执行超时**: Coze handler 函数有执行时间限制
3. **变量传递限制**: 大型脚本字符串可能超过 Coze 变量大小限制
4. **状态管理**: 无法在 Coze 中维护持久状态

##### Export Script 工具

`coze_plugin/export_script/` 包含专门用于导出生成的脚本的 Coze 工具：

**功能**:

- 读取 `/tmp/coze2jianying.py` 文件内容
- 将脚本内容作为字符串返回
- 支持可选的导出后清空文件功能

**使用场景**:
在 Coze 工作流的最后步骤调用，将累积的 API 调用序列导出为完整的 Python 脚本。

**参数**:

- `clear_content` (boolean): 是否在导出后清空文件内容

**返回**:

```json
{
  "script_content": "#!/usr/bin/env python3\n...",
  "file_size": 1234,
  "success": true,
  "message": "成功导出脚本文件，大小: 1234 字符"
}
```

##### 开发指南：何时和如何参与此功能开发

**⚠️ 重要约束**:

1. **仅在明确要求时工作**: 只有当 issue 中明确要求继续开发此功能时，才应该参与相关开发工作

2. **理解复杂性**: 这个方案涉及三个不同的执行环境，容易产生混淆：
   - 不要混淆开发端的生成器脚本和 Coze 云端的 handler
   - 不要混淆 Coze 生成的脚本和应用端执行的脚本
   - 明确当前工作在哪个环境

3. **问题排查顺序**:
   - 首先确认是哪个环境的问题
   - 其次确认是哪个模块（A-E）的问题
   - 最后再尝试修复

4. **测试策略**:
   - 开发端：使用 `scripts/test_generated_handlers.py` 验证生成的代码语法
   - Coze 云端：在 Coze IDE 中测试 handler 是否正确执行
   - 应用端：需要完整的端到端测试（当标签页完成后）

5. **修改原则**:
   - 修改 A-E 脚本时，确保向后兼容已生成的 handler
   - 修改 handler 模板时，重新生成所有工具进行测试
   - 不要破坏现有的手动粘贴和 API 调用两种草稿生成方案

**当前建议**:

由于此功能遇到重大技术挑战且应用端标签页未完成，建议：

- 暂停继续开发，除非 issue 中明确要求
- 优先考虑现有的两种草稿生成方案（手动粘贴和 API 调用）
- 如果必须继续，先解决应用端执行环境的基础问题
- 考虑是否有更简单的替代方案

## Coze 平台特性与约束

### 代码架构约束

- **无共同头文件概念**：每个工具函数脚本文件需要重复定义所需的自定义类和工具函数
- **文件系统限制**：默认可读写文件夹是 `/tmp`，大小限制 512MB，生命周期管理复杂
- **函数式风格**：避免在本地空间或脚本中存储状态变量，所有数据都应该通过参数传递

### 标准代码结构

每个 Coze 工具函数必须遵循以下模板：

```python
from runtime import Args
from typings.custom_handler_name.custom_handler_name import Input, Output

"""
Each file needs to export a function named `handler`. This function is the entrance to the Tool.

Parameters:
args: parameters of the entry function.
args.input - input parameters, you can get test input value by args.input.xxx.
args.logger - logger instance used to print logs, injected by runtime.

Remember to fill in input/output in Metadata, it helps LLM to recognize and use tool.

Return:
The return data of the function, which should match the declared output parameters.
"""
def handler(args: Args[Input])->Output:
    return {"message": "Hello, world!"}
```

## 项目结构规划

### 核心组件

#### 1. Coze Plugin 子项目

位置：`coze_plugin/` 目录

包含专门为 Coze 平台设计的插件工具和核心助手功能：

- `main.py` - 核心助手类和主程序入口
- `tools/` - Coze 工具函数脚本
  - `create_draft/` - 创建草稿工具
  - `export_drafts/` - 导出草稿工具
  - `get_media_duration/` - 媒体时长分析工具
  - `add_videos/`, `add_images/`, `add_audios/`, `add_captions/` - 添加各类轨道
  - `make_*_info/` - 动态生成配置工具
- `base_tools/` - 基础工具函数
- `tests/` - 完整的测试套件
- `examples/` - 使用示例

#### 2. 草稿生成器应用

位置：`app/` 目录

包含完整的应用程序，含 GUI 和 API：

- `main.py` - GUI 应用入口
- `api_main.py` - API 服务入口
- `gui/` - 图形界面模块
  - `main_window.py` - 主窗口（标签页容器）
  - `base_tab.py` - 标签页基类
  - `draft_generator_tab.py` - 草稿生成标签页
  - `cloud_service_tab.py` - 云端服务管理标签页
  - `script_executor_tab.py` - 脚本执行标签页
  - `log_window.py` - 日志窗口
- `api/` - API 路由模块
  - `router.py` - API 路由定义
  - `example_routes.py` - 示例路由
- `utils/` - 核心工具模块
  - `draft_generator.py` - 草稿生成主逻辑
  - `coze_parser.py` - Coze 输出解析
  - `converter.py` - 数据转换
  - `material_manager.py` - 素材管理
  - `logger.py` - 日志系统
- `core/` - 核心业务逻辑
- `models/` - 数据模型
- `schemas/` - API 数据模式
- `services/` - 业务服务层
- `database/` - 数据库相关（预留）

#### 3. 数据结构脚本 (Data Structure Scripts)

位置：`data_structures/` 目录

包含可复用的数据结构定义：

- `draft_generator_interface/` - 草稿生成器接口模型
  - `models.py` - 完整的接口数据模型
  - `README.md` - 详细的接口文档
- `media_models/` - 媒体文件模型
  - `models.py` - 媒体处理数据模型
  - `README.md` - 媒体模型文档

#### 4. 项目文档

位置：`docs/` 目录

完整的项目文档系统：

- `guides/` - 开发与使用指南
  - `DEVELOPMENT_ROADMAP.md` - 功能开发历程
  - `DRAFT_MANAGEMENT_GUIDE.md` - 草稿管理指南
- `draft_generator/` - 草稿生成器专门文档
  - 架构、工作流程、组件指南等
- `reference/` - API 参考文档
  - 接口文档、参数列表等
- `updates/` - 功能更新记录
- `analysis/` - 技术分析报告

#### 5. 构建和部署

- `build.py` - PyInstaller 打包脚本
- `start_api.py` - API 服务快速启动脚本
- `start_api.bat` - Windows 批处理启动脚本
- `.github/workflows/` - CI/CD 配置
- `requirements.txt` - 项目依赖
- `setup.py` - 项目安装配置

### 实际项目结构 (当前状态)

```
Coze2JianYing/
├── coze_plugin/                # 🔌 Coze 插件子项目
│   ├── __init__.py            # 子项目初始化
│   ├── README.md              # 子项目说明文档
│   ├── main.py                # 核心助手类和主程序入口
│   ├── tools/                 # Coze 工具函数脚本 (已实现)
│   │   ├── create_draft/      # ✅ 创建草稿工具
│   │   ├── export_drafts/     # ✅ 导出草稿工具
│   │   ├── get_media_duration/# ✅ 媒体时长分析工具
│   │   ├── add_videos/        # ✅ 添加视频工具
│   │   ├── add_audios/        # ✅ 添加音频工具
│   │   ├── add_images/        # ✅ 添加图片工具
│   │   ├── add_captions/      # ✅ 添加字幕工具
│   │   ├── add_effects/       # ⚠️ 特效工具（已弃用，待重新实现）
│   │   └── make_*_info/       # ✅ 各类配置生成工具
│   ├── raw_tools/             # 🏗️ 自动生成的handler工具（实验性）
│   │   └── (各API对应的工具)  # 由handler_generator生成
│   ├── export_script/         # 📤 导出脚本工具（实验性）
│   │   ├── handler.py         # 导出/tmp/coze2jianying.py的工具
│   │   └── README.md          # 工具文档
│   ├── base_tools/            # 基础工具函数
│   ├── tests/                 # ✅ 完整测试套件
│   └── examples/              # 使用示例
├── app/                       # 📦 草稿生成器应用
│   ├── main.py               # GUI 应用入口
│   ├── api_main.py           # API 服务入口
│   ├── gui/                  # 图形界面模块
│   │   ├── main_window.py   # 主窗口
│   │   ├── base_tab.py      # 标签页基类
│   │   ├── draft_generator_tab.py  # 草稿生成标签页
│   │   ├── cloud_service_tab.py    # 云端服务标签页
│   │   ├── script_executor_tab.py  # 脚本执行标签页
│   │   └── log_window.py    # 日志窗口
│   ├── api/                  # API 路由
│   │   ├── router.py        # 主路由
│   │   └── example_routes.py # 示例路由
│   ├── utils/                # 核心工具模块
│   │   ├── draft_generator.py    # 草稿生成主逻辑
│   │   ├── coze_parser.py        # Coze 输出解析
│   │   ├── converter.py          # 数据转换
│   │   ├── material_manager.py   # 素材管理
│   │   └── logger.py             # 日志系统
│   ├── core/                 # 核心业务逻辑
│   ├── models/               # 数据模型
│   ├── schemas/              # API 数据模式
│   ├── services/             # 业务服务层
│   └── database/             # 数据库相关（预留）
├── data_structures/          # 📊 数据结构定义 (已实现)
│   ├── draft_generator_interface/  # ✅ 草稿生成器接口
│   │   ├── models.py
│   │   └── README.md
│   └── media_models/         # ✅ 媒体文件模型
│       ├── models.py
│       └── README.md
├── docs/                     # ✅ 项目文档目录
│   ├── guides/               # 开发与使用指南
│   │   └── DEVELOPMENT_ROADMAP.md  # 功能开发历程
│   ├── draft_generator/      # 草稿生成器文档
│   ├── reference/            # API 参考文档
│   ├── updates/              # 功能更新记录
│   └── analysis/             # 技术分析报告
├── scripts/                  # 🛠️ 实用工具脚本
│   ├── handler_generator/    # 🏗️ Handler 生成器模块（实验性）
│   │   ├── scan_api_endpoints.py         # 步骤1：扫描API端点
│   │   ├── generate_io_models.py         # 步骤3：生成Input/Output类型
│   │   ├── generate_api_call_code.py     # 步骤4：生成API调用代码
│   │   ├── generate_handler_function.py  # 步骤5：生成handler函数
│   │   ├── create_tool_scaffold.py       # 步骤6：创建工具文件夹
│   │   ├── generate_custom_class_handlers.py # 附加流程：自定义类 handler 生成
│   │   ├── schema_extractor.py           # 辅助：Schema提取器
│   │   ├── api_endpoint_info.py          # 数据模型
│   │   └── README.md                     # 模块文档
│   ├── generate_handler_from_api.py      # Handler生成器主程序
│   └── coze_json_formatter.py # JSON 格式化工具
├── build.py                 # 🔨 PyInstaller 打包脚本
├── start_api.py             # 🚀 API 快速启动脚本
├── start_api.bat            # 🪟 Windows 批处理启动
├── .github/workflows/       # ⚙️ CI/CD 配置
│   └── build.yml           # 构建和发布工作流
├── requirements.txt         # ✅ 项目依赖
├── setup.py                 # ✅ 安装配置
└── README.md                # ✅ 项目说明
```

## 编码指南

### Coze 工具函数开发规范

1. **函数入口**：
   - 必须导出名为 `handler` 的函数
   - 使用 `Args[Input]` 类型注解
   - 返回符合 `Output` 定义的数据

2. **依赖管理**：
   - 在每个脚本内部重新定义所需的类和函数
   - 可以 import 公共库如 `pyjianyingdraft`
   - 避免跨文件的自定义依赖

3. **文件操作**：
   - 尽量避免使用 `/tmp` 目录
   - 如必须使用，确保及时清理
   - 优先使用内存处理或参数传递

4. **状态管理**：
   - 避免全局变量和类属性存储状态
   - 所有状态通过函数参数传递
   - 采用函数式编程风格

5. **资源链接处理**：
   - Coze 传递的素材均为网页链接格式
   - 工具函数应验证链接有效性
   - 传递链接列表而非直接下载资源文件
   - 为草稿生成器保留链接信息以便后续处理

### pyJianYingDraft 集成与参数覆盖

#### 核心集成目标

本项目使用 pyJianYingDraft 不仅仅是为了生成草稿文件，更重要的是：

1. **完整参数映射**: 将 pyJianYingDraft 中所有可配置的剪映参数选项包装为 Coze 工具函数
2. **功能全覆盖**: 确保剪映中所有可设置的参数都能通过本项目的工具函数进行配置
3. **参数验证**: 理解并验证各种参数组合的有效性和兼容性

#### 1. 正确的导入方式：

```python
from pyJianYingDraft import DraftFolder, VideoMaterial, AudioMaterial
from pyJianYingDraft import VideoSegment, AudioSegment, TextSegment
from pyJianYingDraft import FilterType, TransitionType, EffectSegment
# 导入所有相关的参数类型和枚举
```

#### 2. 链接资源处理模式：

```python
# 处理 Coze 传递的网页链接
def process_media_links(args: Args[Input]) -> Output:
    video_links = args.input.video_urls  # 网页链接列表
    audio_links = args.input.audio_urls  # 音频链接列表

    # 验证链接有效性但不下载
    validated_links = validate_media_links(video_links + audio_links)

    # 生成 JSON 数据供草稿生成器使用
    draft_json = {
        "video_resources": video_links,
        "audio_resources": audio_links,
        "processing_parameters": extract_jianyingdraft_params(args.input)
    }

    return {"draft_json": draft_json}
```

#### 3. 参数映射示例：

```python
# 将 pyJianYingDraft 的所有参数选项映射到工具函数
def map_video_parameters(input_params):
    """映射视频相关的所有可配置参数"""
    return {
        "filter_type": FilterType.from_string(input_params.filter),
        "transition_type": TransitionType.from_string(input_params.transition),
        "crop_settings": CropSettings(**input_params.crop_config),
        "effect_settings": process_effect_parameters(input_params.effects),
        # ... 包含所有 pyJianYingDraft 支持的参数
    }
```

### 文档规范

每个工具函数和数据结构都必须有对应的 README.md，包含：

1. **功能描述**：简要说明工具的用途
2. **输入参数**：详细列出所有输入参数及其类型
3. **输出结果**：说明返回值的结构和含义
4. **使用示例**：提供完整的使用代码示例
5. **注意事项**：特殊限制或注意点

#### README 模板

````markdown
# [工具名称]

## 功能描述

[简要描述工具的功能和用途]

## 输入参数

### Input 类型定义

```python
class Input:
    param1: str  # 参数1说明
    param2: int  # 参数2说明
    # ...
```
````

## 输出结果

### Output 类型定义

```python
class Output:
    result1: str    # 结果1说明
    result2: bool   # 结果2说明
    # ...
```

## 使用示例

```python
# 示例代码
```

## 注意事项

- [列出重要的注意事项]
- [性能考虑]
- [错误处理说明]

````

## 开发最佳实践

### 错误处理
- 使用 `args.logger` 记录日志
- 提供详细的错误信息
- 优雅处理异常情况

### 性能优化
- 避免大文件在 `/tmp` 中的长期存储
- 使用流式处理处理大型媒体文件
- 合理使用内存缓存

### 测试指南

项目包含完整的测试体系，主要集中在 `coze_plugin/tests/` 目录中。

#### 测试组织
- **`coze_plugin/tests/`** 目录包含所有 Coze 插件工具的测试
- 每个测试文件独立运行，无相互依赖
- 测试文件命名：`test_[功能名称].py`
- 包含 README.md 说明测试目的和运行方法

#### 测试类型
- **基础功能测试** (`test_basic.py`): 数据结构和核心功能
- **工具函数测试** (`test_tools.py`, `test_add_*.py`): Coze 工具的端到端测试
- **修复验证测试**: 验证特定 bug 修复的有效性
- **架构变更测试**: 验证系统升级的向后兼容性

#### 测试编写规范
```python
#!/usr/bin/env python3
"""
Test description and purpose
"""

def test_specific_function():
    """Test the specific function with description"""
    print("=== Testing specific function ===")

    # Setup
    # Test execution
    # Assertions
    # Cleanup

    print("✅ Test passed!")
    return True

if __name__ == "__main__":
    # Run all tests
    results = []
    results.append(test_specific_function())

    print(f"\\n=== Test Summary ===")
    print(f"Tests passed: {sum(results)}/{len(results)}")
````

#### 测试运行

```bash
# 运行单个测试
python coze_plugin/tests/test_basic.py

# 运行所有测试
cd coze_plugin/tests && python test_*.py
```

### 性能优化

- 避免大文件在 `/tmp` 中的长期存储
- 使用流式处理处理大型媒体文件
- 合理使用内存缓存

### 原有测试考虑

- 每个工具函数都应该可以独立测试
- 提供不同场景的测试用例
- 考虑边界条件和异常情况

## 集成 Coze 平台

### Metadata 配置

确保在 Coze 平台上正确配置工具的 Metadata：

- 输入输出参数定义要与代码一致
- 提供清晰的工具描述
- 设置合适的超时时间

### 调试建议

- 使用 `args.logger` 输出调试信息
- 在开发阶段返回详细的中间结果
- 考虑添加调试模式开关

## 草稿生成器接口规范

### 数据交换格式

本项目生成的 JSON 数据需要符合草稿生成器的输入规范：

```python
# 标准输出格式 (占位符定义)
{
    "project_info": {
        "name": "项目名称",
        "resolution": "1920x1080",
        "frame_rate": 30
    },
    "media_resources": {
        "video_urls": ["https://example.com/video1.mp4", ...],
        "audio_urls": ["https://example.com/audio1.mp3", ...],
        "image_urls": ["https://example.com/image1.jpg", ...]
    },
    "timeline_config": {
        "video_tracks": [...],  # 视频轨道配置
        "audio_tracks": [...],  # 音频轨道配置
        "text_tracks": [...]    # 文字轨道配置
    },
    "processing_parameters": {
        # 所有 pyJianYingDraft 参数的完整映射
        # *占位符：待草稿生成器项目建立后详细定义*
    }
}
```

### 接口设计原则

- **链接传递**: 所有媒体资源均以 URL 形式传递
- **参数完整**: 包含 pyJianYingDraft 支持的所有配置选项
- **向前兼容**: 设计时考虑未来草稿生成器的扩展需求
- **验证机制**: 提供数据格式验证和错误处理

_注：具体接口规范将在草稿生成器项目建立后进行详细补充和完善_

## 重要架构说明：pyJianYingDraft 段类型映射

### 媒体资源引用方式

本项目通过各段配置类的 `material_url` 字段直接引用网络资源URL，无需单独的 MediaResource 类：

- 在 Coze 工作流中，各 segment 直接使用 URL 引用媒体资源
- 资源类型从 segment 类型自动推断（VideoSegment → 视频，AudioSegment → 音频，等）
- 在草稿生成器中，URL 被下载为本地文件，然后传递给 pyJianYingDraft 的 Material 类（`VideoMaterial(path)` 或 `AudioMaterial(path)`）

### pyJianYingDraft 段类型层次结构

理解 pyJianYingDraft 的段类型层次结构对于正确使用 Draft Generator Interface 至关重要：

```
BaseSegment (基类)
├── MediaSegment (媒体片段基类 - 不是直接使用的段类型)
│   ├── AudioSegment (音频片段) ✅
│   └── VisualSegment (视觉片段基类 - 不是直接使用的段类型)
│       ├── VideoSegment (视频片段 - 也用于图片!) ✅
│       ├── TextSegment (文本/字幕片段) ✅
│       └── StickerSegment (贴纸片段) ✅
├── EffectSegment (特效片段 - 独立轨道) ✅
└── FilterSegment (滤镜片段 - 独立轨道) ✅
```

**关键点**:

1. `MediaSegment` 和 `VisualSegment` 是基类，不直接实例化
2. **图片在 pyJianYingDraft 中作为 `VideoSegment` 处理**（静态视频）
3. `EffectSegment` 和 `FilterSegment` 放置在独立轨道上

### Draft Generator Interface 段配置类映射

| 配置类                 | pyJianYingDraft 类 | 说明                    |
| ---------------------- | ------------------ | ----------------------- |
| `VideoSegmentConfig`   | `VideoSegment`     | 视频片段                |
| `AudioSegmentConfig`   | `AudioSegment`     | 音频片段                |
| `ImageSegmentConfig`   | `VideoSegment`     | ⚠️ 图片作为静态视频处理 |
| `TextSegmentConfig`    | `TextSegment`      | 文本/字幕片段           |
| `StickerSegmentConfig` | `StickerSegment`   | 贴纸片段                |
| `EffectSegmentConfig`  | `EffectSegment`    | 特效片段（独立轨道）    |
| `FilterSegmentConfig`  | `FilterSegment`    | 滤镜片段（独立轨道）    |

### 轨道和段类型的严格对应关系

**关键原则**: pyJianYingDraft 的 Track 是泛型类 `Track[Seg_type]`，每种轨道类型只接受一种特定的段类型。

#### 轨道-段类型映射表

| 轨道类型  | pyJianYingDraft Track   | 接受的段类型   | 本项目配置类                           |
| --------- | ----------------------- | -------------- | -------------------------------------- |
| `video`   | `Track[VideoSegment]`   | VideoSegment   | VideoSegmentConfig, ImageSegmentConfig |
| `audio`   | `Track[AudioSegment]`   | AudioSegment   | AudioSegmentConfig                     |
| `text`    | `Track[TextSegment]`    | TextSegment    | TextSegmentConfig                      |
| `sticker` | `Track[StickerSegment]` | StickerSegment | StickerSegmentConfig                   |
| `effect`  | `Track[EffectSegment]`  | EffectSegment  | EffectSegmentConfig                    |
| `filter`  | `Track[FilterSegment]`  | FilterSegment  | FilterSegmentConfig                    |

**重要规则**:

1. ❌ **没有 "image" 轨道类型** - 图片放在 video 轨道上
2. ✅ video 轨道可以同时包含 VideoSegmentConfig 和 ImageSegmentConfig
3. ✅ 其他轨道只能包含对应的单一段类型
4. ✅ TrackConfig 包含运行时验证，确保段类型与轨道类型匹配
5. ✅ effect 和 filter 轨道是独立轨道

#### 使用示例

```python
# ✅ 正确: video 轨道包含视频段
video_track = TrackConfig(
    track_type="video",
    segments=[VideoSegmentConfig(...)]
)

# ✅ 正确: video 轨道包含图片段
video_track = TrackConfig(
    track_type="video",  # 注意：不是 "image"
    segments=[ImageSegmentConfig(...)]
)

# ✅ 正确: video 轨道混合视频和图片
video_track = TrackConfig(
    track_type="video",
    segments=[VideoSegmentConfig(...), ImageSegmentConfig(...)]
)

# ❌ 错误: "image" 轨道类型不存在
image_track = TrackConfig(
    track_type="image",  # 错误！
    segments=[ImageSegmentConfig(...)]
)

# ❌ 错误: audio 轨道不能包含 video 段
audio_track = TrackConfig(
    track_type="audio",
    segments=[VideoSegmentConfig(...)]  # 错误！
)
```

### 常见误解和注意事项

1. **误解**: ImageSegment 是独立的段类型，有独立的轨道
   - **实际**: pyJianYingDraft 没有 ImageSegment 和 image 轨道，图片使用 VideoSegment 放在 video 轨道上
   - **本项目**: `ImageSegmentConfig` 提供简化接口，但必须放在 `track_type="video"` 的轨道上

2. **误解**: 所有段类型都可以添加到同一个轨道
   - **实际**: 每种轨道只接受特定的段类型，pyJianYingDraft 在运行时强制验证
   - **本项目**: TrackConfig 包含 `__post_init__` 验证，会在创建时检查段类型匹配

3. **误解**: tracks 列表必须包含特定数量或类型的轨道
   - **实际**: tracks 是灵活的列表，可以包含任意数量和类型的轨道
   - **本项目**: 示例展示多种轨道只是为了演示，实际使用时根据需要添加

## 开发历程文档规范

### DEVELOPMENT_ROADMAP.md 编写规范

当添加新功能或进行重要更新时，必须在 `docs/guides/DEVELOPMENT_ROADMAP.md` 中记录开发过程。遵循以下规范：

#### 文档目标

- 帮助开发者和学习者快速理解项目架构
- 解释每个功能出现的应用背景和原因
- 记录具体的实现方法和技术决策
- 保持简洁务实，避免营销性语言

#### 内容结构

每个新功能的记录应包含以下部分：

```markdown
### N. 功能名称 - [Issue #X](链接), [PR #Y](链接)

**应用背景**: 说明为什么需要这个功能，解决什么实际问题

**实现需求**: (如果复杂功能需要)

- 列出主要的技术需求
- 说明约束条件和挑战

**具体做法**:

- 详细说明实现方案
- 列出关键的技术细节
- 包含重要的代码结构或API设计
- 说明如何解决主要挑战
```

#### 编写原则

1. **重点在于技术实现**: 重点解释应用背景、原因和具体做法
2. **链接到实际Issues/PRs**: 必须包含GitHub issue和PR的完整链接
3. **避免时间线营销**: 不强调"第几阶段"、"里程碑"等营销性描述
4. **保持实用性**: 专注于帮助理解架构和功能，不包含项目展望或成长数据
5. **按开发顺序**: 按照功能开发的实际顺序记录，体现依赖关系

#### 禁止内容

- 避免"第一阶段"、"成熟化"等阶段性描述
- 不包含"核心技术概念演进"、"设计决策记录"等理论性章节
- 不添加"项目成长数据"、"未来展望"等市场化内容
- 减少时间戳和日期，除非对理解技术演进必要

#### 更新要求

- 每次添加新功能时必须更新此文档
- 保持文档与实际代码同步
- 定期检查链接有效性
- 确保新内容符合既定格式

## 相关资源

### Coze 平台资源

- [Coze 开发者文档](https://www.coze.cn/open/docs/developer_guides)
- [Coze 插件开发指南](https://www.coze.cn/open/docs/developer_guides)
- [GitHub Copilot 最佳实践](https://gh.io/copilot-coding-agent-tips)

### pyJianYingDraft 资源

- [pyJianYingDraft 文档](https://github.com/GuanYixuan/pyJianYingDraft)
- [剪映草稿格式说明](https://github.com/GuanYixuan/pyJianYingDraft/blob/main/README.md)

### 项目生态系统

- **Coze 工作流**: AI 驱动的内容生成和参数配置
- **本项目 (Coze 插件)**: 参数处理和 JSON 数据生成
- **草稿生成器** _(占位符)_: JSON 数据转换为剪映草稿文件
- **剪映**: 最终的视频编辑和输出
