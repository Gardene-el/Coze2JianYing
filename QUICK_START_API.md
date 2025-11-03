# FastAPI 快速启动脚本

## 快速开始

### 1. 启动 API 服务

```powershell
# 确保在项目根目录
cd c:\Users\aloud\Documents\Coze2JianYing

# 方法1: 使用 Python 模块方式启动
python -m app.api_main

# 方法2: 使用 uvicorn 直接启动（推荐，支持热重载）
uvicorn app.api_main:app --reload --host 127.0.0.1 --port 8000
```

### 2. 访问 API 文档

启动后，在浏览器中打开：

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **根路径**: http://127.0.0.1:8000/

### 3. 运行测试脚本

在新的终端窗口中运行：

```powershell
# 运行完整测试套件
python test_api_examples.py
```

### 4. 快速测试（命令行）

```powershell
# 健康检查
curl http://127.0.0.1:8000/api/example/health

# 创建一个项目
curl -X POST http://127.0.0.1:8000/api/example/items -H "Content-Type: application/json" -d '{\"name\":\"测试\",\"price\":100}'

# 查看所有项目
curl http://127.0.0.1:8000/api/example/items
```

## 接口概览

### 基础接口

- `GET /` - 根路径
- `GET /api/example/health` - 健康检查

### CRUD 操作

- `GET /api/example/items` - 获取列表
- `GET /api/example/items/{id}` - 获取单个
- `POST /api/example/items` - 创建
- `POST /api/example/items/batch` - 批量创建
- `PUT /api/example/items/{id}` - 完整更新
- `PATCH /api/example/items/{id}` - 部分更新
- `DELETE /api/example/items/{id}` - 删除

### 特殊功能

- `POST /api/example/upload` - 文件上传
- `POST /api/example/form` - 表单提交
- `GET /api/example/headers` - 请求头
- `GET /api/example/cookies` - Cookies
- `GET /api/example/download` - 文件下载
- `GET /api/example/stream` - 流式响应
- `POST /api/example/mixed/{id}` - 混合参数

### 错误测试

- `GET /api/example/error/400` - 400 错误
- `GET /api/example/error/404` - 404 错误
- `GET /api/example/error/500` - 500 错误

## 详细文档

完整的测试指南和说明请查看：`API_TEST_GUIDE.md`

## 故障排查

### 端口被占用

```powershell
# 使用其他端口
uvicorn app.api_main:app --reload --port 8001
```

### 依赖缺失

```powershell
# 安装依赖
pip install fastapi uvicorn[standard] pydantic requests
```

### 模块导入错误

确保在项目根目录运行命令。
