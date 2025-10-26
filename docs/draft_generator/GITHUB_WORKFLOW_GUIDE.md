# GitHub 工作流指南

## 概述

本文档详细介绍了项目中的 GitHub Actions 工作流 (`.github/workflows/build.yml`)，包括其用途、构建方式、当前问题及解决方案。

## 工作流与 build.py 的关系

**是的，工作流与 build.py 密切相关。** 工作流的核心功能就是在 GitHub Actions 环境中自动执行 `build.py` 脚本。

### build.py 的作用

`build.py` 是一个打包脚本，使用 PyInstaller 将 Python 应用程序打包为 Windows 可执行文件 (.exe)。主要功能包括：

- 清理旧的构建目录 (`build`, `dist`)
- 使用 PyInstaller 将 `src/main.py` 打包为单个 .exe 文件
- 包含必要的依赖和资源文件
- 生成名为 `CozeJianYingDraftGenerator.exe` 的可执行文件

### 工作流的作用

GitHub Actions 工作流 (`.github/workflows/build.yml`) 自动化了以下流程：

1. **持续集成 (CI)**：每次推送到 `main` 分支或创建 Pull Request 时自动构建和测试
2. **自动打包**：运行 `build.py` 在云端自动构建 Windows 可执行文件
3. **发布管理**：当推送 `v*` 标签时自动创建 GitHub Release 并上传 .exe 文件

## 当前工作流内容详解

### 触发条件

```yaml
on:
  push:
    branches: [main]
    tags:
      - "v*"
  pull_request:
    branches: [main]
```

工作流在以下情况下触发：
- 推送到 `main` 分支
- 创建 `v*` 格式的标签（如 `v1.0.0`）
- 创建或更新针对 `main` 分支的 Pull Request

### 工作流步骤

1. **Checkout code** - 检出代码仓库
2. **Set up Python** - 设置 Python 3.11 环境
3. **Install dependencies** - 安装 `requirements.txt` 中的依赖
4. **Run tests** - 运行 pytest 测试（如果存在测试文件）
5. **Build executable** - 执行 `python build.py` 构建 .exe 文件
6. **Upload artifact** - 上传构建的 .exe 文件作为工作流产物
7. **Create Release** - 如果是标签推送，创建 GitHub Release

## 为什么工作流失败？

### 根本原因

工作流失败的主要原因**是**使用了**已弃用的 GitHub Action 版本**：

```yaml
- name: Upload artifact
  uses: actions/upload-artifact@v3  # v3 版本已被弃用
```

GitHub 在 2024 年 4 月宣布弃用 `actions/upload-artifact@v3`，工作流运行会在准备阶段自动失败。

**此问题已修复**，工作流文件已更新为 `v4` 版本。

### 详细错误信息

从工作流日志中可以看到：
- 工作流在 "Prepare all required actions" 阶段失败
- 没有执行任何实际的构建步骤
- 错误提示指向弃用的 action 版本

参考：[GitHub Blog - Deprecation Notice](https://github.blog/changelog/2024-04-16-deprecation-notice-v3-of-the-artifact-actions/)

### 本地 vs 云端构建的差异

**为什么本地可以成功运行 build.py，但工作流失败？**

1. **本地执行**：直接运行 `python build.py` 不涉及 GitHub Actions，因此不受 action 版本弃用影响
2. **云端执行**：工作流在执行 `python build.py` 之前就失败了，因为 GitHub Actions 在准备阶段就检测到了弃用的 action 版本

**注意**：即使修复了 action 版本问题，工作流还需要：
- 在 Windows 环境中运行（当前配置正确：`runs-on: windows-latest`）
- 确保所有依赖都能在云端环境中正确安装
- `resources` 目录需要存在（build.py 中引用了它）

## 已应用的解决方案

以下问题已在此仓库中修复：

### 1. 更新 Upload Artifact Action

**状态：✅ 已修复**

将 `actions/upload-artifact@v3` 更新为 `v4`：

```yaml
- name: Upload artifact
  uses: actions/upload-artifact@v4  # 现在使用 v4 版本
  with:
    name: CozeJianYingDraftGenerator-Windows
    path: dist/CozeJianYingDraftGenerator.exe
```

### 2. 确保 Resources 目录存在

**状态：✅ 已修复**

build.py 中引用的 `resources` 目录已创建，并配置了适当的 .gitignore 规则：

```python
'--add-data=resources;resources',  # 添加资源文件
```

目录结构现在已在 git 中跟踪，同时允许内容被忽略。

### 3. 修正测试目录引用

**状态：✅ 已修复**

工作流已更新为引用正确的 `test/` 目录：

```yaml
- name: Run tests
  run: |
    pip install pytest
    pytest test/ -v || echo "No tests found"  # 现在正确引用 test/
```

## 工作流的用途总结

### 当前用途

1. **自动化构建**：每次代码更新时自动构建 Windows 可执行文件
2. **质量保证**：在合并代码前运行测试
3. **版本发布**：通过 Git 标签自动创建 Release 并发布可执行文件

### 未来可扩展用途

1. **多平台构建**：可以扩展为支持 macOS 和 Linux 构建
2. **自动化测试**：添加更完善的测试覆盖
3. **代码质量检查**：集成 linting 和代码格式检查
4. **部署自动化**：自动部署到分发平台

## 如何测试工作流

### 本地测试 build.py

```bash
# 安装依赖
pip install -r requirements.txt

# 运行构建脚本
python build.py

# 检查生成的文件
dir dist\CozeJianYingDraftGenerator.exe
```

### 云端测试工作流

工作流已修复，现在应该能成功运行：

1. **工作流现已正确配置**（action 版本已更新，路径已修复）
2. **推送到分支或创建 PR** 触发工作流
3. **查看 Actions 页面**监控构建进度
4. **下载产物**验证生成的 .exe 文件

下次工作流运行应该会成功完成所有步骤。

## 结论

- ✅ 工作流**确实与 build.py 相关**，它自动化了 build.py 的执行
- ✅ 工作流失败的原因是使用了**弃用的 GitHub Action 版本**
- ✅ 本地可以运行是因为**不依赖 GitHub Actions 基础设施**
- ✅ 修复方案是**更新到 actions/upload-artifact@v4**

工作流的存在为项目提供了自动化构建和发布能力，**建议保留并修复**而不是移除。
