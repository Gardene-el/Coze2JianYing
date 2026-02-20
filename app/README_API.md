# FastAPI 示例接口 README

本目录包含完整的 FastAPI 示例接口实现，用于学习和测试 FastAPI 的各种功能。

## 📁 文件说明

### 核心文件

- `api_main.py` - FastAPI 应用主入口
- `api/router.py` - 路由汇总
- `api/example_routes.py` - 示例接口实现
- `schemas/example_schemas.py` - 数据模型定义

### 测试文件

- `test_api_examples.py` - Python 自动化测试脚本

### 启动脚本

- `start_api.py` - Python 启动脚本
- `start_api.bat` - Windows 批处理启动脚本

### 文档

- `API_PROJECT_SUMMARY.md` - 项目总览
- `QUICK_START_API.md` - 快速入门
- `API_TEST_GUIDE.md` - 详细测试指南
- `API_DEMO.md` - 功能演示

## 🚀 快速开始

### 1. 启动服务

```bash
# 使用 Python 脚本
python start_api.py

# 或使用 uvicorn
uvicorn app.backend.api_main:app --reload
```

### 2. 访问文档

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### 3. 运行测试

```bash
python test_api_examples.py
```

## 📚 学习路径

1. 先看 `API_PROJECT_SUMMARY.md` 了解整体
2. 用 Swagger UI 交互式测试
3. 查看 `API_DEMO.md` 学习各接口用法
4. 运行 `test_api_examples.py` 自动化测试
5. 参考 `API_TEST_GUIDE.md` 深入学习

## ✨ 功能特性

- ✅ 所有 HTTP 方法 (GET, POST, PUT, PATCH, DELETE)
- ✅ 各种参数类型 (Query, Path, Body, Header, Cookie, Form, File)
- ✅ 数据验证 (Pydantic)
- ✅ 文件上传下载
- ✅ 流式响应
- ✅ 错误处理
- ✅ CORS 支持
- ✅ 自动文档生成

## 📖 更多信息

查看项目根目录下的 API 相关文档。
