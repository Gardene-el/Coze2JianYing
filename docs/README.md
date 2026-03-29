# 项目文档目录

本目录包含 Coze2JianYing 项目的所有详细文档，按类别组织。

## 📂 文档结构

### 📘 [guides/](./guides/) - 开发与使用指南

开发者和用户指南，帮助理解项目架构和使用方法。

* **[DEVELOPMENT\_ROADMAP.md](./guides/DEVELOPMENT_ROADMAP.md)** - 项目功能开发历程，记录各功能的实现背景和方法
* **[COZE\_INTEGRATION\_GUIDE.md](./guides/COZE_INTEGRATION_GUIDE.md)** - Coze 平台集成指南（API Gateway 模式）
* **[generate\_coze\_openapi\_guide.md](./guides/generate_coze_openapi_guide.md)** - Coze OpenAPI 生成指南

### 🔄 [updates/](./updates/) - 功能更新记录

记录各个功能模块的实现过程和技术细节。

* **[ADD\_VIDEOS\_UPDATE.md](./updates/ADD_VIDEOS_UPDATE.md)** - `add_videos` 和 `make_video_info` 实现总结
* **[ADD\_CAPTIONS\_UPDATE.md](./updates/ADD_CAPTIONS_UPDATE.md)** - `add_captions` 和 `make_caption_info` 实现总结
* **[ADD\_EFFECTS\_UPDATE.md](./updates/ADD_EFFECTS_UPDATE.md)** - `add_effects` 和 `make_effect_info` 实现总结
* **[MAKE\_IMAGE\_INFO\_UPDATE.md](./updates/MAKE_IMAGE_INFO_UPDATE.md)** - `make_image_info` 实现总结
* **[ISSUE\_162\_SUMMARY.md](./updates/ISSUE_162_SUMMARY.md)** - Issue #162 Handler Generator 完成总结
* **[IMPLEMENTATION\_COMPLETE.md](./updates/IMPLEMENTATION_COMPLETE.md)** - GitHub Issue 模板实现完成总结
* **[ISSUE\_TEMPLATE\_IMPLEMENTATION\_SUMMARY.md](./updates/ISSUE_TEMPLATE_IMPLEMENTATION_SUMMARY.md)** - GitHub Issue 模板实现详细总结

### 🔧 [fixes/](./fixes/) - 问题修复记录

记录重要的 Bug 修复和问题解决方案。

* **[USAGE\_GUIDE.md](./fixes/USAGE_GUIDE.md)** - Handler Generator 修复后使用指南

### 🔍 [analysis/](./analysis/) - 技术分析与审计报告

深入的技术分析、设计评审和审计报告。

* **[AUDIT\_REPORT.md](./analysis/AUDIT_REPORT.md)** - `add_*` 和 `make_*_info` 函数系统审计报告（821行）
* **[AUDIT\_SUMMARY.md](./analysis/AUDIT_SUMMARY.md)** - 审计总结
* **[DRAFT\_INTERFACE\_ANALYSIS.md](./analysis/DRAFT_INTERFACE_ANALYSIS.md)** - Draft Generator Interface 完整性分析
* **[ADD\_FUNCTIONS\_MECHANISM\_INVESTIGATION.md](./analysis/ADD_FUNCTIONS_MECHANISM_INVESTIGATION.md)** - `add_*` 函数机制调查报告
* **[AddEffectRequest\_DESIGN\_ANALYSIS.md](./analysis/AddEffectRequest_DESIGN_ANALYSIS.md)** - AddEffectRequest 设计分析
* **[generate\_coze\_openapi\_design.md](./analysis/generate_coze_openapi_design.md)** - Coze OpenAPI 生成器技术设计
* **[HANDLER\_GENERATOR\_SCHEMA\_ADAPTATION.md](./analysis/HANDLER_GENERATOR_SCHEMA_ADAPTATION.md)** - Handler Generator Schema 适配说明
* **[DETAILED\_SCHEMA\_ADAPTATION\_EXPLANATION.md](./analysis/DETAILED_SCHEMA_ADAPTATION_EXPLANATION.md)** - Schema 适配详细说明
* **[CUSTOM\_CLASS\_HANDLER\_GENERATION.md](./analysis/CUSTOM_CLASS_HANDLER_GENERATION.md)** - 自定义类 Handler 生成系统
* **[handler\_structure\_analysis.md](./analysis/handler_structure_analysis.md)** - Handler 代码结构分析
* **[handler\_structure\_summary\_cn.md](./analysis/handler_structure_summary_cn.md)** - Handler 结构分析总结（中文）
* **[readme\_structure\_analysis.md](./analysis/readme_structure_analysis.md)** - README 文档结构分析
* **[readme\_structure\_summary\_cn.md](./analysis/readme_structure_summary_cn.md)** - README 文档结构总结（中文）
* **[COZE\_LOCAL\_PLUGIN\_DETAILED\_EXPLANATION.md](./analysis/COZE_LOCAL_PLUGIN_DETAILED_EXPLANATION.md)** - Coze 端侧插件详细说明
* **[THREAD\_VS\_PROCESS\_EXPLANATION.md](./analysis/THREAD_VS_PROCESS_EXPLANATION.md)** - 线程与进程选择说明

### 📖 [reference/](./reference/) - API 参考与快速查询

API 参考文档、参数列表和快速查询指南。

* **[API\_RESPONSE\_STANDARD.md](./reference/API_RESPONSE_STANDARD.md)** - API 响应标准（capcut 风格 `code/message/data`）
* **[COZE\_API\_PARAMETERS\_GUIDE.md](./reference/COZE_API_PARAMETERS_GUIDE.md)** - Coze API 参数详解与获取指南
* **[DRAFT\_INTERFACE\_DOCUMENTATION\_INDEX.md](./reference/DRAFT_INTERFACE_DOCUMENTATION_INDEX.md)** - Draft Interface 文档索引
* **[DRAFT\_INTERFACE\_QUICK\_REFERENCE.md](./reference/DRAFT_INTERFACE_QUICK_REFERENCE.md)** - Draft Interface 快速参考
* **[EXPORTED\_PARAMETERS\_LIST.md](./reference/EXPORTED_PARAMETERS_LIST.md)** - `export_drafts` 导出参数完整列表
* **[PARAMETER\_COMPLETION\_SUMMARY.md](./reference/PARAMETER_COMPLETION_SUMMARY.md)** - `add_*`/`make_*_info` 参数完整性校正总结
* **[SEGMENT\_MAPPING\_CORRECTIONS.md](./reference/SEGMENT_MAPPING_CORRECTIONS.md)** - pyJianYingDraft 段类型映射修正说明
* **[VISUAL\_DEMO\_ISSUE\_TEMPLATES.md](./reference/VISUAL_DEMO_ISSUE_TEMPLATES.md)** - GitHub Issue 模板可视化演示

### 📦 [draft\_generator/](./draft_generator/) - 草稿生成器文档

`src/backend/DraftGenerator` 模块的使用与设计文档。

* **[COZE\_CONVERSION\_GUIDE.md](./draft_generator/COZE_CONVERSION_GUIDE.md)** - Coze 输出到草稿的转换指南
* **[COZE\_OUTPUT\_CONVERTER\_GUIDE.md](./draft_generator/COZE_OUTPUT_CONVERTER_GUIDE.md)** - Coze 输出转换工具指南
* **[CONVERTER\_TOOL\_SUMMARY.md](./draft_generator/CONVERTER_TOOL_SUMMARY.md)** - 转换工具总结
* **[MATERIAL\_MANAGER\_GUIDE.md](./draft_generator/MATERIAL_MANAGER_GUIDE.md)** - 素材管理器使用指南
* **[MATERIAL\_MANAGER\_FEASIBILITY.md](./draft_generator/MATERIAL_MANAGER_FEASIBILITY.md)** - 素材管理器可行性分析
* **[MULTI\_FORMAT\_INPUT\_GUIDE.md](./draft_generator/MULTI_FORMAT_INPUT_GUIDE.md)** - 多格式输入支持指南
* **[GITHUB\_WORKFLOW\_GUIDE.md](./draft_generator/GITHUB_WORKFLOW_GUIDE.md)** - GitHub Actions 工作流指南（中文）
* **[GITHUB\_WORKFLOW\_GUIDE\_EN.md](./draft_generator/GITHUB_WORKFLOW_GUIDE_EN.md)** - GitHub Actions 工作流指南（English）
* **[SCRIPT\_EXECUTOR\_TAB.md](./draft_generator/SCRIPT_EXECUTOR_TAB.md)** - 脚本执行标签页说明
* **[SCRIPT\_EXECUTOR\_UI.md](./draft_generator/SCRIPT_EXECUTOR_UI.md)** - 脚本执行器 UI 设计
* **[UPDATE\_ASSETS\_PATH.md](./draft_generator/UPDATE_ASSETS_PATH.md)** - 素材路径更新说明

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
2. **功能更新记录** → `docs/updates/`：新功能实现总结，命名格式 `<FEATURE>_UPDATE.md`
3. **技术分析报告** → `docs/analysis/`：代码审计、架构分析、设计决策评审
4. **参考文档** → `docs/reference/`：API 参考、参数列表、快速查询指南
5. **草稿生成器** → `docs/draft_generator/`：`DraftGenerator` 模块相关文档

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
* 某个 coze\_plugin 工具如何实现？ → [updates/](./updates/) 目录
* 系统设计是否合理？ → [analysis/](./analysis/) 目录
* API 参数有哪些？ → [reference/](./reference/) 目录
* 草稿生成器如何工作？ → [draft\_generator/](./draft_generator/) 目录
