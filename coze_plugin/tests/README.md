# 测试文件夹 (Tests Directory)

本目录包含 Coze2JianYing 项目的所有测试文件，用于验证项目各个组件的功能。

## 测试文件说明

### 基础功能测试
- **`test_basic.py`** - 基础数据结构和文件操作测试
- **`test_tools.py`** - Coze 工具函数测试（create_draft, export_drafts）

### 功能修复验证测试
- **`test_create_draft_fix.py`** - create_draft 工具修复验证
- **`test_validation_fix.py`** - 参数验证修复测试
- **`test_draft_name_change.py`** - 草稿名称参数更新测试

### 架构变更测试
- **`test_folder_structure_changes.py`** - 文件夹结构优化测试
- **`test_simple_folder_structure.py`** - 简化文件夹结构测试

## 运行测试

### 运行所有测试
```bash
cd tests
python test_basic.py
python test_tools.py
# 依此类推...
```

### 单独运行特定测试
```bash
python tests/test_basic.py
```

## 测试覆盖的功能

1. **数据结构验证** - 草稿生成器接口数据模型
2. **工具函数功能** - Coze 插件工具的核心功能
3. **参数处理** - None 值处理和默认值逻辑
4. **文件系统操作** - 临时文件管理和清理
5. **UUID 管理系统** - 草稿的创建、发现和导出
6. **错误处理** - 各种异常情况的处理

## 测试原则

- 每个测试文件独立运行，不依赖其他测试
- 测试使用 `/tmp` 目录进行文件操作，运行后自动清理
- 模拟 Coze 平台的运行环境和约束条件
- 验证向后兼容性和新功能的正确性

## 开发指南

在添加新功能时，请：
1. 创建对应的测试文件
2. 遵循现有的测试命名规范
3. 包含正常场景和异常场景的测试
4. 确保测试的独立性和可重复性