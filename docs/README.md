# 项目文档目录

本目录包含 Coze2JianYing 项目的所有详细文档，按类别组织。

## 📂 文档结构

### 📘 [guides/](./guides/) - 开发与使用指南

开发者和用户指南，帮助理解项目架构和使用方法。

* **[DEVELOPMENT\_ROADMAP.md](./guides/DEVELOPMENT_ROADMAP.md)** - 项目功能开发历程，记录各功能的实现背景和方法
* **[COZE\_INTEGRATION\_GUIDE.md](./guides/COZE_INTEGRATION_GUIDE.md)** - Coze 平台集成指南（API Gateway 模式）
* **[generate\_coze\_openapi\_guide.md](./guides/generate_coze_openapi_guide.md)** - Coze OpenAPI 生成指南

### [analysis/](./analysis/) - 技术分析与审计报告

深入的技术分析、设计评审和审计报告。

* **[DRAFT\_INTERFACE\_ANALYSIS.md](./analysis/DRAFT_INTERFACE_ANALYSIS.md)** - Draft Generator Interface 完整性分析

### 📖 [reference/](./reference/) - API 参考与快速查询

API 参考文档、参数列表和快速查询指南。

* **[API\_RESPONSE\_STANDARD.md](./reference/API_RESPONSE_STANDARD.md)** - API 响应标准（capcut 风格 `code/message/data`）

### ⚙️ [handler\_generator/](./handler_generator/) - Handler 生成器文档

`scripts/handler_generator/` 脚本的设计与使用。

* **[CUSTOMNAMESPACE\_HANDLING.md](./handler_generator/CUSTOMNAMESPACE_HANDLING.md)** - CustomNamespace 处理方案说明

## 🔗 其他文档

* **[主 README](../README.md)** - 项目主页和快速入门
* **[Copilot 开发指南](../.github/copilot-instructions.md)** - GitHub Copilot 开发规范
* **[Coze 插件文档](../coze_plugin/README.md)** - Coze 插件子项目说明
* **[工具函数文档](../coze_plugin/tools/)** - 各个 Coze 工具函数的详细说明

## 📝 文档维护规范

### 文档添加指南

当添加新文档时，请遵循以下规则：

1. **指南类文档** → `docs/guides/`：面向用户或开发者的使用指南、项目架构说明
2. **技术分析报告** → `docs/analysis/`：代码审计、架构分析、设计决策评审
3. **参考文档** → `docs/reference/`：API 参考、参数列表、快速查询指南
4. **Handler 生成器** → `docs/handler_generator/`：`scripts/handler_generator/` 脚本相关文档

### 文档编写原则

* **清晰的目的**：每个文档应有明确的目标读者和用途
* **结构化内容**：使用标题、列表和表格组织信息
* **实例说明**：提供代码示例和使用场景
* **保持更新**：随代码变更及时更新相关文档
* **中文优先**：项目文档以中文为主

## 🔍 快速查找

**我想了解...**

* 项目是如何发展的？ → [DEVELOPMENT\_ROADMAP.md](./guides/DEVELOPMENT_ROADMAP.md)
* API 响应格式是什么？ → [API\_RESPONSE\_STANDARD.md](./reference/API_RESPONSE_STANDARD.md)
* 系统设计是否合理？ → [analysis/](./analysis/) 目录
* CustomNamespace 如何处理？ → [handler\_generator/](./handler_generator/) 目录
