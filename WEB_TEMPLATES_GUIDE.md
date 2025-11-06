# Web 模板使用指南

本文档说明如何使用 Coze2JianYing 项目的网页模板文件。

## 🎯 快速开始

### 方式一：启动 API 服务器（推荐）

这是访问完整网页界面的推荐方式，包含所有交互功能和 API 文档。

1. **启动服务器**：
   ```bash
   # 在项目根目录执行
   python start_api.py
   
   # 或者直接运行
   python -m app.api_main
   ```

2. **访问网页**：
   - 主页：http://localhost:8000
   - API 文档（Swagger UI）：http://localhost:8000/docs
   - API 文档（ReDoc）：http://localhost:8000/redoc
   - API 信息：http://localhost:8000/api
   - 健康检查：http://localhost:8000/api/health

3. **服务器配置**：
   
   默认配置：
   - 地址：`127.0.0.1`（本地访问）
   - 端口：`8000`
   - 自动重载：启用（开发模式）
   
   自定义配置（修改 `start_api.py`）：
   ```python
   from app.api_main import start_api_server
   
   # 自定义地址和端口
   start_api_server(host="0.0.0.0", port=8080)
   ```

### 方式二：直接打开 HTML 文件

如果只需要查看项目介绍，可以直接在浏览器中打开根目录的 `index.html` 文件。

1. **在文件管理器中**：
   - 找到项目根目录的 `index.html`
   - 双击打开（会使用默认浏览器）

2. **在浏览器中**：
   - 拖拽 `index.html` 文件到浏览器窗口
   - 或使用 `Ctrl+O`（Windows/Linux）/ `Cmd+O`（Mac）打开文件

3. **注意事项**：
   - 这种方式只能查看静态内容
   - API 文档和交互功能不可用
   - 建议使用方式一获得完整体验

## 📂 文件结构

```
Coze2JianYing/
├── index.html                    # 根目录简化版主页（可直接打开）
├── app/
│   ├── templates/               # HTML 模板目录
│   │   ├── index.html          # 完整主页模板（需要服务器）
│   │   └── README.md           # 模板文档
│   ├── static/                 # 静态资源目录
│   │   ├── css/
│   │   │   └── style.css      # 主样式表
│   │   └── js/
│   │       └── main.js        # 主 JavaScript 文件
│   └── api_main.py            # FastAPI 服务主入口
└── start_api.py               # 服务器启动脚本
```

## 🎨 页面功能

### 主页功能

访问 http://localhost:8000 后，你可以：

1. **浏览项目信息**
   - 项目简介和核心优势
   - 完整的工作流程图示
   - 功能特点展示

2. **快速导航**
   - 点击导航栏链接快速跳转到对应部分
   - 平滑滚动动画效果

3. **访问 API 文档**
   - 直接跳转到 Swagger UI 或 ReDoc
   - 查看完整的 API 接口文档

4. **查看项目状态**
   - 已完成功能列表
   - 待完善功能计划

5. **外部链接**
   - GitHub 仓库
   - Coze 插件商店
   - 下载 Release 版本

### 交互功能

1. **平滑滚动**：点击导航链接时平滑滚动到目标位置
2. **滚动动画**：页面元素在进入视口时显示淡入动画
3. **悬停效果**：鼠标悬停在卡片上时有提升效果
4. **代码复制**：代码示例右上角有复制按钮
5. **API 状态检测**：自动检测 API 服务器状态并显示
6. **彩蛋**：试试按下 ↑↑↓↓←→←→BA（Konami Code）

## 🔧 自定义配置

### 修改主题颜色

编辑 `app/static/css/style.css`，修改 CSS 变量：

```css
:root {
    --primary-color: #4a90e2;      /* 主色调 - 蓝色 */
    --secondary-color: #50c878;    /* 辅助色 - 绿色 */
    --accent-color: #ff6b6b;       /* 强调色 - 红色 */
    --dark-bg: #1a1a2e;            /* 深色背景 */
    --light-bg: #f8f9fa;           /* 浅色背景 */
    --text-dark: #2c3e50;          /* 深色文字 */
    --text-light: #ecf0f1;         /* 浅色文字 */
}
```

### 添加新页面

1. 在 `app/templates/` 创建新的 HTML 文件
2. 在 `app/api_main.py` 添加路由：

```python
@app.get("/your-page", response_class=HTMLResponse)
async def your_page():
    """你的新页面"""
    template_file = templates_path / "your-page.html"
    if template_file.exists():
        return HTMLResponse(content=template_file.read_text(encoding="utf-8"))
    return JSONResponse(content={"error": "Page not found"}, status_code=404)
```

### 修改服务器配置

编辑 `app/api_main.py` 中的 `start_api_server` 函数：

```python
def start_api_server(host: str = "127.0.0.1", port: int = 8000):
    """启动 FastAPI 服务器"""
    uvicorn.run(
        "app.api_main:app",
        host=host,            # 修改绑定地址
        port=port,            # 修改端口
        reload=True,          # 开发模式自动重载
        log_level="info"      # 日志级别
    )
```

## 🚀 生产环境部署

### 本地网络部署

如果需要在局域网内访问：

```bash
# 绑定到所有网络接口
python -c "from app.api_main import start_api_server; start_api_server(host='0.0.0.0', port=8000)"
```

然后在其他设备上访问：`http://你的IP地址:8000`

### 使用 Gunicorn（生产环境）

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动服务器（4个工作进程）
gunicorn app.api_main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 使用 Docker

创建 `Dockerfile`：

```dockerfile
FROM python:3.8-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "start_api.py"]
```

构建和运行：

```bash
docker build -t coze2jianying .
docker run -p 8000:8000 coze2jianying
```

## 🐛 故障排除

### 问题：无法访问网页

**解决方案**：
1. 确认服务器已启动：`python start_api.py`
2. 检查端口是否被占用：`netstat -an | grep 8000`
3. 尝试使用其他端口

### 问题：样式或 JavaScript 不加载

**解决方案**：
1. 确认 `app/static/` 目录存在且包含文件
2. 检查浏览器控制台的错误信息
3. 清除浏览器缓存后重试

### 问题：API 文档不显示

**解决方案**：
1. 访问 http://localhost:8000/docs 确认路径正确
2. 确认 FastAPI 版本 >= 0.68.0
3. 检查是否有 JavaScript 错误

### 问题：彩蛋不工作

**解决方案**：
1. 确认在正确的页面（主页）
2. 按键顺序：↑↑↓↓←→←→BA（使用方向键和字母键）
3. 确保 JavaScript 已加载

## 📚 相关文档

- [项目 README](../README.md) - 项目总体介绍
- [API 快速开始](../API_QUICKSTART.md) - API 接口使用指南
- [模板文档](app/templates/README.md) - 模板系统详细说明
- [GitHub 仓库](https://github.com/Gardene-el/Coze2JianYing)

## 📝 更新日志

### 2024-11-06
- ✨ 创建完整的网页模板系统
- ✨ 实现响应式设计和动画效果
- ✨ 集成 FastAPI 静态文件服务
- ✨ 添加交互功能和彩蛋
- 📝 创建使用指南文档

## 💡 提示

- 开发时使用 `reload=True` 模式，代码修改后自动重载
- 生产环境建议关闭 `reload` 并使用 Gunicorn
- 使用浏览器开发工具（F12）调试 CSS 和 JavaScript
- 定期查看 [GitHub Releases](https://github.com/Gardene-el/Coze2JianYing/releases) 获取更新

## 📄 许可证

本项目采用 GPL-3.0 许可证。详见 [LICENSE](../LICENSE) 文件。

---

Made with ❤️ by [Gardene-el](https://github.com/Gardene-el)
