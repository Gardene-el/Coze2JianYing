# Windows 编码问题修复说明

## 问题描述

在 GitHub Actions 的 Windows runner 上运行 `semantic-release` 时遇到编码错误：

```
Error: 'charmap' codec can't decode byte 0x90 in position 177: character maps to <undefined>
```

### 问题原因

1. **Windows 默认编码**：Windows 系统默认使用 `cp1252` (charmap) 编码，而不是 UTF-8
2. **Git commit 包含中文**：项目的 commit 消息中包含中文字符
3. **环境变量未持久化**：PowerShell 的 `[System.Environment]::SetEnvironmentVariable(..., 'Process')` 只影响当前步骤，不会传递到后续步骤
4. **semantic-release 读取历史**：`semantic-release` 需要读取完整的 Git commit 历史来分析版本号，遇到非 ASCII 字符时解码失败

## 解决方案

### 1. Job 级别设置环境变量

在 `.github/workflows/release.yml` 的 job 级别添加 UTF-8 环境变量：

```yaml
jobs:
  release:
    runs-on: windows-latest
    
    env:
      PYTHONIOENCODING: utf-8
      PYTHONUTF8: 1
      LANG: en_US.UTF-8
      LC_ALL: en_US.UTF-8
```

### 2. 每个步骤设置控制台代码页

在每个 PowerShell 步骤的开始添加：

```powershell
chcp 65001  # Windows UTF-8 代码页
```

### 3. 使用 GITHUB_ENV 持久化环境变量

```powershell
echo "PYTHONIOENCODING=utf-8" >> $env:GITHUB_ENV
echo "PYTHONUTF8=1" >> $env:GITHUB_ENV
```

这确保环境变量在所有后续步骤中都可用。

### 4. 配置 Git 使用 UTF-8

```powershell
git config --global core.quotepath false
git config --global i18n.commitencoding utf-8
git config --global i18n.logoutputencoding utf-8
git config --global core.pager "cat"
```

### 5. 添加调试步骤

新增调试步骤帮助诊断编码问题：

```yaml
- name: Debug Git Log Encoding
  run: |
    chcp 65001
    Write-Host "=== 测试 Git Log 编码 ==="
    git log --oneline -5
    Write-Host "=== Python 编码测试 ==="
    python -c "import sys; print(f'stdout encoding: {sys.stdout.encoding}'); print(f'default encoding: {sys.getdefaultencoding()}')"
```

### 6. 使用详细模式 (-vv)

在 `semantic-release` 命令中添加 `-vv` 参数，便于查看详细错误信息：

```powershell
semantic-release version -vv
semantic-release publish -vv
```

### 7. 优化版本号获取

将 "Get new version" 步骤改为从 Git tags 获取，避免重复调用可能失败的 `semantic-release version --print`：

```powershell
$latestTag = git describe --tags --abbrev=0
echo "version=$latestTag" >> $env:GITHUB_OUTPUT
```

## 修复效果

修复后，工作流应该能够：

1. ✅ 正确读取包含中文的 Git commit 历史
2. ✅ 成功运行 `semantic-release version` 和 `semantic-release publish`
3. ✅ 自动创建 Release 和上传 exe 文件
4. ✅ 在调试步骤中显示正确的编码配置

## 验证步骤

1. 提交包含中文的 commit 到 `develop` 分支
2. 合并到 `main` 分支触发 release 工作流
3. 查看 Actions 日志中的 "Debug Git Log Encoding" 步骤
4. 确认 `stdout encoding` 显示为 `utf-8`
5. 确认 `semantic-release` 成功运行无编码错误

## 相关 Commit

- Commit: [fix: 修复 Windows 编码问题导致 semantic-release 失败](https://github.com/Gardene-el/Coze2JianYing/commit/bc4c583)

## 参考资料

- [Python UTF-8 Mode](https://docs.python.org/3/library/os.html#utf8-mode)
- [GitHub Actions Environment Variables](https://docs.github.com/en/actions/learn-github-actions/variables)
- [Windows Code Pages](https://learn.microsoft.com/en-us/windows/win32/intl/code-page-identifiers)
- [Git i18n Configuration](https://git-scm.com/docs/git-config#Documentation/git-config.txt-i18ncommitEncoding)

## 备选方案

如果上述修复仍然不能完全解决问题，可以考虑：

### 方案 A：使用 Linux Runner

```yaml
jobs:
  release:
    runs-on: ubuntu-latest  # 改用 Linux
```

Linux 默认使用 UTF-8，不会有编码问题。但需要调整构建脚本以支持跨平台。

### 方案 B：避免在 Commit 中使用非 ASCII 字符

在项目贡献指南中要求：
- Commit 消息使用英文
- 中文说明放在 PR 描述或文档中

### 方案 C：使用 Docker Container

```yaml
jobs:
  release:
    runs-on: windows-latest
    container:
      image: python:3.11
```

在容器中运行可以获得更一致的 UTF-8 环境。

## 结论

通过在多个层面设置 UTF-8 编码（job 环境、PowerShell 代码页、Git 配置、Python 环境），应该能够完全解决 Windows runner 上的编码问题，使自动化发布流程正常工作。