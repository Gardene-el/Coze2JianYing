# 项目功能开发历程

本文档记录项目各个功能和规范的开发顺序，解释每个功能出现的应用背景、原因和具体实现方法，帮助开发者理解项目架构。

## 开发顺序

### 1. 项目基础结构 - [Issue #2](https://github.com/Gardene-el/CozeJianYingAssistent/issues/2), [PR #3](https://github.com/Gardene-el/CozeJianYingAssistent/pull/3)

**应用背景**: 项目从空白仓库开始，需要建立标准的 Python 项目结构以支持后续 Coze 插件开发

**实现要求**: 
- 需要引用 pyJianYingDraft 项目作为核心依赖
- 建立标准的 Python 包管理结构

**具体做法**:
- 采用标准 Python 包结构 (`coze_jianying_assistant/` 主包目录)
- 选择 `pyJianYingDraft>=0.2.5` 作为核心依赖，通过 GitHub Advisory Database 验证安全性
- 建立 `requirements.txt`、`setup.py` 等标准配置文件
- 设置 GPL-3.0 开源协议

### 2. Coze 平台开发规范 - [Issue #6](https://github.com/Gardene-el/CozeJianYingAssistent/issues/6), [PR #7](https://github.com/Gardene-el/CozeJianYingAssistent/pull/7)

**应用背景**: Coze 平台有独特的运行环境限制，需要建立专门的开发规范来适配这些约束

**核心约束问题**:
- `/tmp` 目录只有 512MB 空间限制
- 无共同头文件概念，每个工具函数需重复定义依赖
- 强制函数式编程风格，不能存储状态变量
- 必须导出 `handler` 函数作为工具入口

**具体做法**:
- 确立四阶段工作流架构: `Coze 工作流 → Coze插件(本项目) → 草稿生成器 → 剪映`
- 建立分离式架构设计，解决文件空间限制和中间数据索引干扰
- 制定标准的 Coze 工具函数模板，包含 `Args[Input] -> Output` 结构
- 建立完整的开发规范文档 (`.github/copilot-instructions.md`)

### 3. 媒体时长分析工具 - [Issue #8](https://github.com/Gardene-el/CozeJianYingAssistent/issues/8), [PR #9](https://github.com/Gardene-el/CozeJianYingAssistent/pull/9)

**应用背景**: Coze 工作流需要准确的媒体时长信息来进行时间轴计算，但传入的都是网络链接而非本地文件

**实现需求**:
- 接收网络链接数组，获取每个媒体文件的时长
- 计算累积时间轴，为后续视频编辑提供时间控制信息
- 需要处理各种网络媒体格式和特殊服务(如 Volcano Engine TTS)

**具体做法**:
- 实现 `get_media_duration` 工具函数
- 支持输入格式: `{"links": ["https://.../1.mp4", "https://.../2.mp4"]}`
- 输出累积时间轴: `{"all_timelines": [{"start": 0, "end": total}], "timelines": [individual_ranges]}`
- 针对 Volcano Engine TTS 添加专门的 URL 过期检查和错误处理
- 建立网络资源处理的标准模式

### 4. UUID 草稿管理系统 - [Issue #10](https://github.com/Gardene-el/CozeJianYingAssistent/issues/10), [PR #11](https://github.com/Gardene-el/CozeJianYingAssistent/pull/11)

**应用背景**: Coze 平台的变量索引模式会在工作流中产生大量中间数据索引，对用户造成干扰

**核心问题**:
- 如果仅靠 input/output 传递数据，会导致 Coze 变量系统保留大量中间数据
- 需要一个独立的草稿管理方案来避免变量索引复杂性
- 需要支持草稿的创建、修改、导出全生命周期管理

**具体做法**:
- 设计 UUID 管理系统: `用户输入 → create_draft → UUID → 添加内容工具 → export_drafts`
- 实现 `create_draft` 工具: 输入项目基本设置(分辨率、帧率等)，输出 UUID
- 实现 `export_drafts` 工具: 输入 UUID 或 UUID 数组，输出标准化 JSON 数据
- 草稿存储在 `/tmp/jianying_assistant/drafts/{uuid}` 结构化目录中
- 添加 `export_all` 功能支持批量导出所有草稿
- 建立完整的参数映射，覆盖 pyJianYingDraft 的所有配置选项
- 处理 NoneType 参数错误，添加默认值处理逻辑

### 5. 项目架构整理 - [Issue #12](https://github.com/Gardene-el/CozeJianYingAssistent/issues/12), [PR #13](https://github.com/Gardene-el/CozeJianYingAssistent/pull/13)

**应用背景**: 项目已具备完整功能，但缺乏系统性的架构组织和文档体系

**整理需求**:
- 测试文件散布在根目录，需要统一管理
- README.md 需要反映实际项目状态
- 缺乏功能开发历程的记录和说明
- 开发规范需要基于实际架构进行优化

**具体做法**:
- 创建 `tests/` 目录，移动所有测试文件并添加测试文档
- 更新 README.md，准确描述四阶段工作流架构和已实现功能
- 创建本文档，记录功能开发的背景和实现方法
- 更新 `.github/copilot-instructions.md`，基于实际项目结构优化开发规范