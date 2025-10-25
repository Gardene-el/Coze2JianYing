# 项目文档目录

本目录包含 Coze2JianYing 项目的所有详细文档，按类别组织。

## 📂 文档结构

### 📘 [guides/](./guides/) - 开发与使用指南
开发者和用户指南，帮助理解项目架构和使用方法。

- **[DEVELOPMENT_ROADMAP.md](./guides/DEVELOPMENT_ROADMAP.md)** - 项目功能开发历程，记录各功能的实现背景和方法
- **[DRAFT_MANAGEMENT_GUIDE.md](./guides/DRAFT_MANAGEMENT_GUIDE.md)** - 草稿管理系统使用指南
- **[PROJECT_REFACTORING_REPORT.md](./guides/PROJECT_REFACTORING_REPORT.md)** - 🆕 项目重构报告：coze_plugin 子项目创建

### 🔄 [updates/](./updates/) - 功能更新记录
记录各个功能模块的实现过程和技术细节。

- **[ADD_VIDEOS_UPDATE.md](./updates/ADD_VIDEOS_UPDATE.md)** - add_videos 和 make_video_info 实现总结
- **[ADD_CAPTIONS_UPDATE.md](./updates/ADD_CAPTIONS_UPDATE.md)** - add_captions 和 make_caption_info 实现总结
- **[ADD_EFFECTS_UPDATE.md](./updates/ADD_EFFECTS_UPDATE.md)** - add_effects 和 make_effect_info 实现总结
- **[MAKE_IMAGE_INFO_UPDATE.md](./updates/MAKE_IMAGE_INFO_UPDATE.md)** - make_image_info 实现总结

### 🔍 [analysis/](./analysis/) - 技术分析与审计报告
深入的技术分析、设计评审和审计报告。

- **[AUDIT_REPORT.md](./analysis/AUDIT_REPORT.md)** - add_* 和 make_*_info 函数系统审计报告
- **[AUDIT_SUMMARY.md](./analysis/AUDIT_SUMMARY.md)** - 审计总结
- **[DRAFT_INTERFACE_ANALYSIS.md](./analysis/DRAFT_INTERFACE_ANALYSIS.md)** - Draft Generator Interface 完整性分析
- **[ADD_FUNCTIONS_MECHANISM_INVESTIGATION.md](./analysis/ADD_FUNCTIONS_MECHANISM_INVESTIGATION.md)** - add_* 函数机制调查报告

### 📖 [reference/](./reference/) - API 参考与快速查询
API 参考文档、参数列表和快速查询指南。

- **[DRAFT_INTERFACE_DOCUMENTATION_INDEX.md](./reference/DRAFT_INTERFACE_DOCUMENTATION_INDEX.md)** - Draft Interface 文档索引
- **[DRAFT_INTERFACE_QUICK_REFERENCE.md](./reference/DRAFT_INTERFACE_QUICK_REFERENCE.md)** - Draft Interface 快速参考
- **[EXPORTED_PARAMETERS_LIST.md](./reference/EXPORTED_PARAMETERS_LIST.md)** - 导出参数列表
- **[PARAMETER_COMPLETION_SUMMARY.md](./reference/PARAMETER_COMPLETION_SUMMARY.md)** - 参数完成度总结
- **[SEGMENT_MAPPING_CORRECTIONS.md](./reference/SEGMENT_MAPPING_CORRECTIONS.md)** - 段类型映射修正说明

## 🔗 其他文档

- **[主 README](../README.md)** - 项目主页和快速入门
- **[Copilot 开发指南](../.github/copilot-instructions.md)** - GitHub Copilot 开发规范
- **[Coze 插件文档](../coze_plugin/README.md)** - Coze 插件子项目说明
- **[工具函数文档](../coze_plugin/tools/)** - 各个 Coze 工具函数的详细说明
- **[数据结构文档](../data_structures/)** - 数据模型和接口定义
- **[测试文档](../coze_plugin/tests/README.md)** - 测试指南和规范

## 📝 文档维护规范

### 文档添加指南

当添加新文档时，请遵循以下规则：

1. **指南类文档** → `docs/guides/`
   - 面向用户或开发者的使用指南
   - 项目架构和设计理念说明
   - 工作流程和最佳实践

2. **功能更新记录** → `docs/updates/`
   - 新功能实现总结
   - 功能模块开发过程记录
   - 命名格式：`<FEATURE_NAME>_UPDATE.md`

3. **技术分析报告** → `docs/analysis/`
   - 代码审计报告
   - 架构分析文档
   - 设计决策评审

4. **参考文档** → `docs/reference/`
   - API 参考文档
   - 参数列表和配置说明
   - 快速查询指南

### 文档编写原则

- **清晰的目的**：每个文档应有明确的目标读者和用途
- **结构化内容**：使用标题、列表和表格组织信息
- **实例说明**：提供代码示例和使用场景
- **保持更新**：随代码变更及时更新相关文档
- **中文优先**：项目文档以中文为主，确保国内开发者易于理解

## 🔍 快速查找

**我想了解...**

- 项目是如何发展的？ → [DEVELOPMENT_ROADMAP.md](./guides/DEVELOPMENT_ROADMAP.md)
- 如何使用草稿管理系统？ → [DRAFT_MANAGEMENT_GUIDE.md](./guides/DRAFT_MANAGEMENT_GUIDE.md)
- 某个功能是怎么实现的？ → [updates/](./updates/) 目录
- 系统设计是否合理？ → [analysis/](./analysis/) 目录
- API 参数有哪些？ → [reference/](./reference/) 目录
