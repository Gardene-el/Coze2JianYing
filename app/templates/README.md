# Web 模板文件说明

本目录包含 Coze2JianYing 项目的网页模板文件。

## 文件结构

```
app/
├── templates/          # HTML 模板文件
│   └── index.html     # 主页模板（由 FastAPI 服务）
├── static/            # 静态资源文件
│   ├── css/
│   │   └── style.css  # 主样式表
│   └── js/
│       └── main.js    # 主 JavaScript 文件
```

## 使用方法

### 方式一：通过 FastAPI 服务访问（推荐）

1. 启动 API 服务器：
   ```bash
   python start_api.py
   ```

2. 在浏览器中访问：
   - 主页：http://localhost:8000
   - API 文档（Swagger UI）：http://localhost:8000/docs
   - API 文档（ReDoc）：http://localhost:8000/redoc

### 方式二：直接在浏览器中打开

项目根目录下的 `index.html` 文件可以直接在浏览器中打开，它提供了一个简化版的项目介绍页面。

## 功能特点

### 主页 (index.html)

- **完整的项目介绍**：展示 Coze2JianYing 的核心优势和功能特点
- **工作流程图示**：可视化展示从 Coze 到剪映的完整工作流程
- **快速开始指南**：帮助用户快速上手使用项目
- **API 文档链接**：便捷访问 Swagger UI 和 ReDoc 文档
- **项目状态展示**：显示已完成和待完善的功能
- **响应式设计**：适配桌面和移动设备

### 样式表 (style.css)

- **现代化设计**：采用渐变色和卡片式布局
- **动画效果**：平滑的滚动和悬停动画
- **响应式布局**：自适应不同屏幕尺寸
- **自定义 CSS 变量**：便于主题定制

### JavaScript (main.js)

- **平滑滚动**：点击导航链接平滑滚动到对应区域
- **滚动动画**：元素进入视口时的淡入效果
- **代码复制功能**：一键复制代码示例
- **API 状态检查**：自动检测 API 服务器状态
- **彩蛋功能**：隐藏的 Konami Code 彩蛋

## 自定义与扩展

### 修改主题颜色

在 `style.css` 中修改 CSS 变量：

```css
:root {
    --primary-color: #4a90e2;    /* 主色调 */
    --secondary-color: #50c878;  /* 辅助色 */
    --accent-color: #ff6b6b;     /* 强调色 */
    /* ... 其他颜色变量 */
}
```

### 添加新页面

1. 在 `app/templates/` 目录下创建新的 HTML 文件
2. 在 `app/api_main.py` 中添加新的路由：

```python
@app.get("/your-page", response_class=HTMLResponse)
async def your_page():
    template_file = templates_path / "your-page.html"
    return HTMLResponse(content=template_file.read_text(encoding="utf-8"))
```

### 添加静态资源

- CSS 文件：放在 `app/static/css/` 目录
- JavaScript 文件：放在 `app/static/js/` 目录
- 图片文件：放在 `app/static/images/` 目录（需要创建）

在 HTML 中引用：
```html
<link rel="stylesheet" href="/static/css/your-style.css">
<script src="/static/js/your-script.js"></script>
<img src="/static/images/your-image.png" alt="描述">
```

## 技术栈

- **HTML5**：语义化标记
- **CSS3**：现代样式特性（Grid、Flexbox、动画等）
- **JavaScript (ES6+)**：现代 JavaScript 特性
- **FastAPI**：静态文件服务和模板渲染

## 浏览器兼容性

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- 其他现代浏览器

## 开发建议

1. **开发时使用 FastAPI 服务器**：启用热重载功能，修改后自动刷新
2. **使用浏览器开发工具**：调试 CSS 和 JavaScript
3. **保持响应式设计**：测试不同屏幕尺寸
4. **优化性能**：压缩 CSS/JS，优化图片大小

## 已知问题

目前没有已知的严重问题。如果发现问题，请在 [GitHub Issues](https://github.com/Gardene-el/Coze2JianYing/issues) 中报告。

## 更新日志

### 2024-11-06
- ✨ 创建完整的网页模板系统
- ✨ 实现响应式设计
- ✨ 添加动画和交互效果
- ✨ 集成 FastAPI 静态文件服务
- ✨ 添加 API 状态检查功能
- ✨ 创建根目录简化版 index.html

## 许可证

本项目采用 GPL-3.0 许可证。详见项目根目录的 LICENSE 文件。
