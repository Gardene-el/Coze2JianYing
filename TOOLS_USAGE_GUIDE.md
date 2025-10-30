# Coze2JianYing 工具使用指南

本文档提供了项目中新增的四个工具（Sphinx、Click、Rich、FastAPI）的使用建议和集成方案。

## 📦 已添加的依赖项

### CLI 和终端工具
- **click** (>=8.1.0) - 命令行接口框架
- **rich** (>=13.0.0) - 终端美化输出

### 文档工具
- **sphinx** (>=7.0.0) - 文档生成器
- **sphinx-rtd-theme** (>=1.3.0) - Read the Docs 主题
- **sphinx-autodoc-typehints** (>=1.24.0) - 类型提示自动文档

### API 框架
- **fastapi** (>=0.104.0) - 现代 Web API 框架
- **uvicorn[standard]** (>=0.24.0) - ASGI 服务器
- **pydantic** (>=2.0.0) - 数据验证（FastAPI 依赖）

## 🎯 针对本项目的使用建议

### 1. Click - 命令行工具

#### 应用场景
为 Coze 插件和草稿生成器提供命令行接口，方便批量处理和自动化脚本。

#### 建议实现

**在 `coze_plugin/cli.py` 中创建 CLI 工具：**

```python
import click
from rich.console import Console
from .main import Coze2JianYing

console = Console()

@click.group()
@click.version_option(version='0.1.0')
def cli():
    """Coze2JianYing 命令行工具"""
    pass

@cli.command()
@click.option('--name', '-n', required=True, help='项目名称')
@click.option('--resolution', '-r', default='1920x1080', help='视频分辨率')
def create(name, resolution):
    """创建新的剪映草稿项目"""
    console.print(f"[green]正在创建项目: {name}[/green]")
    assistant = Coze2JianYing()
    draft = assistant.create_draft(name)
    console.print(f"[bold green]✓[/bold green] 项目创建成功！")

@cli.command()
@click.argument('video_path', type=click.Path(exists=True))
@click.option('--draft', '-d', help='草稿项目路径')
def add_video(video_path, draft):
    """添加视频到草稿"""
    console.print(f"[cyan]正在处理视频: {video_path}[/cyan]")
    # 实现视频添加逻辑
    console.print(f"[bold green]✓[/bold green] 视频添加成功！")

@cli.command()
@click.argument('draft_path', type=click.Path(exists=True))
@click.option('--output', '-o', help='输出路径')
def export(draft_path, output):
    """导出剪映草稿"""
    console.print(f"[cyan]正在导出草稿...[/cyan]")
    # 实现导出逻辑
    console.print(f"[bold green]✓[/bold green] 导出完成！")

if __name__ == '__main__':
    cli()
```

**在 `setup.py` 中注册 CLI 入口：**

```python
entry_points={
    "console_scripts": [
        "coze2jy=coze_plugin.cli:cli",
    ],
},
```

**使用示例：**

```bash
# 创建新项目
coze2jy create --name "我的vlog"

# 添加视频
coze2jy add-video video.mp4 --draft ./我的vlog

# 导出草稿
coze2jy export ./我的vlog --output ./output
```

---

### 2. Rich - 终端美化输出

#### 应用场景
优化日志输出、进度显示、错误信息，提升用户体验。

#### 建议实现

**替换现有的 print 语句：**

```python
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()

# 1. 美化日志输出（替换 src/utils/logger.py）
console.print("[bold green]✓[/bold green] 草稿创建成功！")
console.print("[bold red]✗[/bold red] 文件下载失败", style="red")
console.print("[yellow]⚠[/yellow] 警告: 素材格式不标准", style="yellow")

# 2. 进度条显示（用于素材下载）
with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    console=console
) as progress:
    task = progress.add_task("[cyan]下载素材...", total=100)
    for i in range(100):
        progress.update(task, advance=1)
        # 下载逻辑

# 3. 表格展示（用于显示草稿信息）
table = Table(title="草稿素材列表")
table.add_column("类型", style="cyan")
table.add_column("文件名", style="magenta")
table.add_column("状态", style="green")
table.add_row("视频", "intro.mp4", "✓ 已下载")
table.add_row("音频", "bgm.mp3", "✓ 已下载")
console.print(table)

# 4. 面板显示（用于显示配置信息）
panel = Panel(
    "[bold cyan]项目配置[/bold cyan]\n"
    "名称: 我的vlog\n"
    "分辨率: 1920x1080\n"
    "帧率: 30fps",
    expand=False
)
console.print(panel)

# 5. 语法高亮（显示 JSON 配置）
json_content = '{"name": "项目", "fps": 30}'
syntax = Syntax(json_content, "json", theme="monokai", line_numbers=True)
console.print(syntax)
```

**集成到现有 GUI 日志系统：**

在 `src/utils/logger.py` 中：

```python
from rich.console import Console
from rich.logging import RichHandler
import logging

# 使用 Rich 的日志处理器
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=Console(), rich_tracebacks=True)]
)

logger = logging.getLogger(__name__)
```

---

### 3. Sphinx - 文档生成

#### 应用场景
自动生成 API 文档，维护项目使用说明和开发文档。

#### 建议实现步骤

**1. 初始化 Sphinx 配置：**

```bash
cd docs
sphinx-quickstart
```

配置选项：
- 项目名称: Coze2JianYing
- 作者: Gardene-el
- 语言: zh_CN
- 启用 autodoc: 是

**2. 配置 `docs/source/conf.py`：**

```python
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
]

html_theme = 'sphinx_rtd_theme'
language = 'zh_CN'
```

**3. 编写文档结构：**

```
docs/
├── source/
│   ├── conf.py
│   ├── index.rst
│   ├── api/
│   │   ├── coze_plugin.rst
│   │   └── draft_generator.rst
│   ├── guides/
│   │   ├── installation.rst
│   │   └── quickstart.rst
│   └── examples/
│       └── basic_usage.rst
```

**4. 生成文档：**

```bash
cd docs
make html
# 文档生成在 docs/build/html/index.html
```

**5. 添加到项目 README：**

在主 README.md 中添加文档链接：

```markdown
## 📖 文档

完整文档请访问：[Coze2JianYing 文档](https://your-docs-url)

或在本地构建：
```bash
cd docs
make html
```
```

---

### 4. FastAPI - API 服务

#### 应用场景
提供 REST API 接口，让其他应用可以通过 HTTP 调用草稿生成功能。

#### 建议实现

**创建 `api/main.py`：**

```python
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="Coze2JianYing API",
    description="Coze 到剪映草稿生成 API",
    version="0.1.0"
)

# 数据模型
class DraftCreate(BaseModel):
    name: str
    resolution: str = "1920x1080"
    fps: int = 30

class DraftResponse(BaseModel):
    draft_id: str
    name: str
    status: str

class MediaAdd(BaseModel):
    draft_id: str
    media_url: str
    media_type: str  # "video", "audio", "image"

# API 端点
@app.get("/")
def root():
    """API 根路径"""
    return {"message": "Coze2JianYing API", "version": "0.1.0"}

@app.post("/api/draft/create", response_model=DraftResponse)
def create_draft(draft: DraftCreate):
    """创建新的剪映草稿"""
    try:
        # 调用 Coze2JianYing 创建草稿
        from coze_plugin.main import Coze2JianYing
        assistant = Coze2JianYing()
        draft_obj = assistant.create_draft(draft.name)
        
        return DraftResponse(
            draft_id="draft_123456",
            name=draft.name,
            status="created"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/media/add")
def add_media(media: MediaAdd):
    """添加媒体到草稿"""
    try:
        # 实现媒体添加逻辑
        return {"status": "success", "message": "媒体添加成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/draft/{draft_id}")
def get_draft(draft_id: str):
    """获取草稿信息"""
    # 实现草稿信息查询
    return {
        "draft_id": draft_id,
        "name": "项目名称",
        "status": "in_progress"
    }

@app.post("/api/draft/{draft_id}/export")
def export_draft(draft_id: str):
    """导出草稿"""
    try:
        # 实现草稿导出逻辑
        return {
            "status": "success",
            "export_path": f"/output/{draft_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 启动服务器
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

**启动 API 服务：**

```bash
# 开发模式（自动重载）
uvicorn api.main:app --reload

# 生产模式
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

**API 使用示例：**

```python
import requests

# 创建草稿
response = requests.post(
    "http://localhost:8000/api/draft/create",
    json={"name": "我的项目", "resolution": "1920x1080"}
)
draft_id = response.json()["draft_id"]

# 添加视频
requests.post(
    "http://localhost:8000/api/media/add",
    json={
        "draft_id": draft_id,
        "media_url": "https://example.com/video.mp4",
        "media_type": "video"
    }
)

# 导出草稿
requests.post(f"http://localhost:8000/api/draft/{draft_id}/export")
```

**访问 API 文档：**

FastAPI 自动生成交互式 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🔧 集成优先级建议

根据本项目的特点，建议按以下顺序集成：

### 1. 优先级：高 ⭐⭐⭐
**Rich - 终端美化输出**
- **原因**: 项目已有 GUI 和日志系统，Rich 可以立即改善用户体验
- **工作量**: 小，主要是替换现有的 print 和日志输出
- **影响**: 直接提升终端输出的可读性和专业度

### 2. 优先级：高 ⭐⭐⭐
**Click - 命令行工具**
- **原因**: 补充 GUI，提供自动化和批量处理能力
- **工作量**: 中，需要设计 CLI 命令结构
- **影响**: 扩展项目使用场景，支持脚本化操作

### 3. 优先级：中 ⭐⭐
**FastAPI - API 服务**
- **原因**: 使项目可以作为服务被其他应用调用
- **工作量**: 中到大，需要设计 API 接口和处理异步逻辑
- **影响**: 扩展项目的集成能力，支持远程调用

### 4. 优先级：低 ⭐
**Sphinx - 文档生成**
- **原因**: 项目文档已有基础（docs/ 目录），Sphinx 用于自动化和规范化
- **工作量**: 中，需要组织现有文档并配置自动生成
- **影响**: 提升文档质量和可维护性

---

## 📝 实施建议

### 阶段 1：快速集成（1-2天）
1. 用 Rich 改进现有的日志输出和进度显示
2. 创建基础的 Click CLI 命令（create, export）

### 阶段 2：功能扩展（3-5天）
3. 完善 CLI 工具，添加更多命令和选项
4. 开发基础的 FastAPI 服务

### 阶段 3：文档完善（2-3天）
5. 配置 Sphinx，生成 API 文档
6. 整合现有文档到 Sphinx 体系

---

## 🧪 测试建议

为每个工具编写简单的测试：

```python
# tests/test_cli.py
from click.testing import CliRunner
from coze_plugin.cli import cli

def test_create_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['create', '--name', 'test'])
    assert result.exit_code == 0

# tests/test_api.py
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_create_draft():
    response = client.post("/api/draft/create", json={
        "name": "test",
        "resolution": "1920x1080"
    })
    assert response.status_code == 200
```

---

## 📚 参考资源

- **Click**: https://click.palletsprojects.com/
- **Rich**: https://rich.readthedocs.io/
- **Sphinx**: https://www.sphinx-doc.org/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Uvicorn**: https://www.uvicorn.org/

---

## 💡 注意事项

1. **版本兼容性**: 所有依赖已设置最低版本要求，保证功能可用
2. **可选安装**: 这些工具可以按需安装，不影响核心功能
3. **渐进式集成**: 建议逐个工具集成，每个工具测试通过后再进行下一个
4. **保持简洁**: 集成工具时保持代码简洁，避免过度设计

---

**最后更新**: 2024-10-30
