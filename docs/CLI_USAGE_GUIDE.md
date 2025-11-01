# CLI 使用指南

本文档介绍如何使用 Coze剪映草稿生成器 的命令行界面（CLI）版本。

## 概述

CLI 版本提供了命令行界面，适合以下场景：
- 脚本自动化处理
- 批量生成草稿
- 服务器端部署
- CI/CD 集成

## 安装与运行

### 使用预编译版本

下载 `CozeJianYingDraftGenerator-CLI.exe` 后，可以直接在命令行中运行：

```bash
# 查看帮助信息
CozeJianYingDraftGenerator-CLI.exe --help

# 查看版本信息
CozeJianYingDraftGenerator-CLI.exe --version
```

### 从源码运行

```bash
# 进入项目目录
cd Coze2JianYing

# 激活虚拟环境（如果使用）
venv\Scripts\activate

# 运行 CLI
python src/CLI/main.py --help
```

## 可用命令

### 1. generate - 生成草稿

从 JSON 文件生成剪映草稿。

**基本用法：**

```bash
CozeJianYingDraftGenerator-CLI.exe generate <JSON文件路径>
```

**参数说明：**

- `JSON_FILE`: Coze 导出的 JSON 文件路径（必需）
- `-o, --output PATH`: 指定输出目录路径（可选，默认为 `./output`）
- `-v, --verbose`: 显示详细日志信息（可选）

**示例：**

```bash
# 基本用法
CozeJianYingDraftGenerator-CLI.exe generate draft.json

# 指定输出目录
CozeJianYingDraftGenerator-CLI.exe generate draft.json -o C:\MyDrafts

# 显示详细日志
CozeJianYingDraftGenerator-CLI.exe generate draft.json -v

# 组合使用
CozeJianYingDraftGenerator-CLI.exe generate draft.json -o C:\MyDrafts -v
```

### 2. info - 显示程序信息

显示程序的基本信息。

**用法：**

```bash
CozeJianYingDraftGenerator-CLI.exe info
```

## 输出说明

### 成功输出

当草稿成功生成时，CLI 会显示：

```
╭──────────────────────────────────────╮
│ Coze剪映草稿生成器 CLI                │
│ 正在处理您的请求...                   │
╰──────────────────────────────────────╯

✓ 草稿生成成功！
输出目录: C:\MyDrafts
```

### 错误输出

当发生错误时，CLI 会显示错误信息并返回非零退出码：

```
✗ 错误: 无法读取 JSON 文件
```

## 批处理示例

### Windows 批处理脚本

创建 `batch_generate.bat` 文件：

```batch
@echo off
setlocal enabledelayedexpansion

set CLI_PATH=CozeJianYingDraftGenerator-CLI.exe
set INPUT_DIR=.\input
set OUTPUT_DIR=.\output

for %%f in (%INPUT_DIR%\*.json) do (
    echo Processing %%f...
    %CLI_PATH% generate "%%f" -o "%OUTPUT_DIR%\%%~nf"
    if !errorlevel! neq 0 (
        echo Failed to process %%f
    ) else (
        echo Successfully processed %%f
    )
)

echo All files processed.
pause
```

### PowerShell 脚本

创建 `batch_generate.ps1` 文件：

```powershell
$cliPath = ".\CozeJianYingDraftGenerator-CLI.exe"
$inputDir = ".\input"
$outputDir = ".\output"

Get-ChildItem -Path $inputDir -Filter *.json | ForEach-Object {
    Write-Host "Processing $($_.Name)..."
    
    $outputPath = Join-Path $outputDir $_.BaseName
    & $cliPath generate $_.FullName -o $outputPath
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Successfully processed $($_.Name)" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to process $($_.Name)" -ForegroundColor Red
    }
}

Write-Host "`nAll files processed."
```

## 退出码

CLI 使用以下退出码：

- `0`: 成功执行
- `1`: 发生错误

可以在脚本中检查退出码来判断执行结果：

```batch
CozeJianYingDraftGenerator-CLI.exe generate draft.json
if %errorlevel% equ 0 (
    echo Success!
) else (
    echo Failed!
)
```

## 日志文件

CLI 会在项目目录的 `logs/app_cli.log` 中记录详细日志，包括：

- 操作时间戳
- 处理步骤
- 错误详情
- 调试信息

查看日志文件可以帮助诊断问题。

## 常见问题

### Q: 如何在不同目录下运行 CLI？

A: 可以将 CLI 可执行文件的路径添加到系统 PATH 环境变量中，或者使用完整路径：

```bash
C:\Tools\CozeJianYingDraftGenerator-CLI.exe generate C:\Drafts\draft.json
```

### Q: 如何自动化处理多个文件？

A: 参考上面的批处理示例，或者使用其他脚本语言（Python、Node.js 等）调用 CLI。

### Q: CLI 和 GUI 版本有什么区别？

A: 功能上完全相同，只是交互方式不同：
- CLI 适合自动化和批处理
- GUI 提供可视化界面，更直观易用

### Q: 如何在服务器上使用 CLI？

A: CLI 版本不需要图形界面，可以直接在 Windows Server 上运行。确保安装了必要的依赖（如果从源码运行）。

## 技术支持

如有问题或建议，请访问：
- GitHub Issues: https://github.com/Gardene-el/Coze2JianYing/issues
- 项目文档: https://github.com/Gardene-el/Coze2JianYing/tree/main/docs
