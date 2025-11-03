# FastAPI 示例接口测试指南

本文档提供了完整的 API 测试指南，包括启动服务、使用各种工具测试接口的方法。

## 📋 目录

1. [启动 API 服务](#启动-api-服务)
2. [使用 Swagger UI 测试](#使用-swagger-ui-测试)
3. [使用 curl 测试](#使用-curl-测试)
4. [使用 Python requests 测试](#使用-python-requests-测试)
5. [使用 Postman 测试](#使用-postman-测试)
6. [接口列表](#接口列表)

---

## 🚀 启动 API 服务

### 方法 1: 直接运行

```powershell
# 确保在项目根目录
cd c:\Users\aloud\Documents\Coze2JianYing

# 激活虚拟环境（如果有）
# .\.venv\Scripts\Activate.ps1

# 运行 API 服务
python -m app.api_main
```

### 方法 2: 使用 uvicorn 直接启动

```powershell
uvicorn app.api_main:app --reload --host 127.0.0.1 --port 8000
```

### 启动成功标志

看到以下信息表示服务启动成功：

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## 📚 使用 Swagger UI 测试

这是最简单直观的测试方法！

### 访问 Swagger UI

1. 启动服务后，在浏览器中打开：**http://127.0.0.1:8000/docs**
2. 你会看到所有可用的 API 接口
3. 点击任意接口 → 点击 "Try it out" → 填写参数 → 点击 "Execute"
4. 查看响应结果

### 访问 ReDoc

- 另一个文档界面：**http://127.0.0.1:8000/redoc**

---

## 💻 使用 curl 测试

### 1. GET 请求 - 健康检查

```powershell
curl http://127.0.0.1:8000/api/example/health
```

### 2. GET 请求 - 带查询参数

```powershell
# 获取 Items 列表（带分页）
curl "http://127.0.0.1:8000/api/example/items?skip=0&limit=10"

# 获取 Items 列表（带搜索）
curl "http://127.0.0.1:8000/api/example/items?search=test&is_active=true"
```

### 3. POST 请求 - 创建 Item

```powershell
curl -X POST http://127.0.0.1:8000/api/example/items `
  -H "Content-Type: application/json" `
  -d '{\"name\":\"测试项目\",\"description\":\"这是一个测试\",\"price\":99.99,\"is_active\":true}'
```

### 4. GET 请求 - 获取单个 Item

```powershell
curl http://127.0.0.1:8000/api/example/items/1
```

### 5. PATCH 请求 - 部分更新

```powershell
curl -X PATCH http://127.0.0.1:8000/api/example/items/1 `
  -H "Content-Type: application/json" `
  -d '{\"price\":199.99}'
```

### 6. PUT 请求 - 完整更新

```powershell
curl -X PUT http://127.0.0.1:8000/api/example/items/1 `
  -H "Content-Type: application/json" `
  -d '{\"name\":\"更新后的项目\",\"description\":\"完整更新\",\"price\":299.99,\"is_active\":false}'
```

### 7. DELETE 请求

```powershell
curl -X DELETE http://127.0.0.1:8000/api/example/items/1
```

### 8. POST 请求 - 批量创建

```powershell
curl -X POST http://127.0.0.1:8000/api/example/items/batch `
  -H "Content-Type: application/json" `
  -d '{\"items\":[{\"name\":\"项目1\",\"price\":10},{\"name\":\"项目2\",\"price\":20}]}'
```

### 9. POST 请求 - 文件上传

```powershell
# 创建测试文件
"测试内容" | Out-File -FilePath test.txt -Encoding utf8

# 上传文件
curl -X POST http://127.0.0.1:8000/api/example/upload `
  -F "file=@test.txt"
```

### 10. POST 请求 - 表单数据

```powershell
curl -X POST http://127.0.0.1:8000/api/example/form `
  -F "name=张三" `
  -F "email=zhangsan@example.com" `
  -F "age=25" `
  -F "message=你好"
```

### 11. GET 请求 - 带自定义 Header

```powershell
curl http://127.0.0.1:8000/api/example/headers `
  -H "X-Custom-Header: my-custom-value" `
  -H "User-Agent: MyCustomAgent/1.0"
```

### 12. GET 请求 - 文件下载

```powershell
curl http://127.0.0.1:8000/api/example/download -o downloaded.txt
```

---

## 🐍 使用 Python requests 测试

创建一个测试脚本 `test_api.py`：

```python
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# 1. 健康检查
def test_health():
    response = requests.get(f"{BASE_URL}/api/example/health")
    print("健康检查:", response.json())

# 2. 创建 Item
def test_create_item():
    data = {
        "name": "Python测试项目",
        "description": "使用requests库创建",
        "price": 123.45,
        "is_active": True
    }
    response = requests.post(f"{BASE_URL}/api/example/items", json=data)
    print("创建Item:", response.json())
    return response.json()["id"]

# 3. 获取 Item 列表
def test_get_items():
    params = {"skip": 0, "limit": 10, "search": "测试"}
    response = requests.get(f"{BASE_URL}/api/example/items", params=params)
    print("获取列表:", response.json())

# 4. 获取单个 Item
def test_get_item(item_id):
    response = requests.get(f"{BASE_URL}/api/example/items/{item_id}")
    print(f"获取Item {item_id}:", response.json())

# 5. 更新 Item
def test_update_item(item_id):
    data = {"price": 999.99}
    response = requests.patch(f"{BASE_URL}/api/example/items/{item_id}", json=data)
    print("更新Item:", response.json())

# 6. 批量创建
def test_batch_create():
    data = {
        "items": [
            {"name": "批量项目1", "price": 10},
            {"name": "批量项目2", "price": 20},
            {"name": "批量项目3", "price": 30}
        ]
    }
    response = requests.post(f"{BASE_URL}/api/example/items/batch", json=data)
    print("批量创建:", response.json())

# 7. 文件上传
def test_upload_file():
    files = {"file": ("test.txt", "测试文件内容", "text/plain")}
    response = requests.post(f"{BASE_URL}/api/example/upload", files=files)
    print("文件上传:", response.json())

# 8. 表单提交
def test_form_submit():
    data = {
        "name": "李四",
        "email": "lisi@example.com",
        "age": 30,
        "message": "表单测试"
    }
    response = requests.post(f"{BASE_URL}/api/example/form", data=data)
    print("表单提交:", response.json())

# 9. 自定义 Header
def test_custom_headers():
    headers = {
        "X-Custom-Header": "my-value",
        "User-Agent": "PythonTestClient/1.0"
    }
    response = requests.get(f"{BASE_URL}/api/example/headers", headers=headers)
    print("自定义Header:", response.json())

# 10. Cookies
def test_cookies():
    cookies = {"session_id": "abc123", "user_id": "user456"}
    response = requests.get(f"{BASE_URL}/api/example/cookies", cookies=cookies)
    print("Cookies:", response.json())

# 11. 文件下载
def test_download():
    response = requests.get(f"{BASE_URL}/api/example/download")
    with open("downloaded_by_python.txt", "wb") as f:
        f.write(response.content)
    print("文件已下载")

# 12. 删除 Item
def test_delete_item(item_id):
    response = requests.delete(f"{BASE_URL}/api/example/items/{item_id}")
    print("删除Item:", response.json())

# 13. 错误处理测试
def test_errors():
    response = requests.get(f"{BASE_URL}/api/example/error/404")
    print(f"404错误: {response.status_code} - {response.json()}")

# 运行所有测试
if __name__ == "__main__":
    print("=" * 50)
    print("开始测试 FastAPI 接口")
    print("=" * 50)

    test_health()
    item_id = test_create_item()
    test_get_items()
    test_get_item(item_id)
    test_update_item(item_id)
    test_batch_create()
    test_upload_file()
    test_form_submit()
    test_custom_headers()
    test_cookies()
    test_download()
    test_errors()
    test_delete_item(item_id)

    print("=" * 50)
    print("测试完成！")
    print("=" * 50)
```

运行测试：

```powershell
python test_api.py
```

---

## 📮 使用 Postman 测试

### 导入 Collection

创建文件 `postman_collection.json`：

```json
{
  "info": {
    "name": "Coze剪映草稿生成器 API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "健康检查",
      "request": {
        "method": "GET",
        "url": "http://127.0.0.1:8000/api/example/health"
      }
    },
    {
      "name": "获取Items列表",
      "request": {
        "method": "GET",
        "url": {
          "raw": "http://127.0.0.1:8000/api/example/items?skip=0&limit=10",
          "query": [
            { "key": "skip", "value": "0" },
            { "key": "limit", "value": "10" }
          ]
        }
      }
    },
    {
      "name": "创建Item",
      "request": {
        "method": "POST",
        "header": [{ "key": "Content-Type", "value": "application/json" }],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"name\": \"测试项目\",\n  \"description\": \"这是测试\",\n  \"price\": 99.99,\n  \"is_active\": true\n}"
        },
        "url": "http://127.0.0.1:8000/api/example/items"
      }
    }
  ]
}
```

在 Postman 中：File → Import → 选择这个 JSON 文件

---

## 📋 接口列表

### 基础接口

| 方法 | 路径                  | 描述     |
| ---- | --------------------- | -------- |
| GET  | `/`                   | 根路径   |
| GET  | `/api/example/health` | 健康检查 |

### CRUD 操作

| 方法   | 路径                           | 描述            |
| ------ | ------------------------------ | --------------- |
| GET    | `/api/example/items`           | 获取 Items 列表 |
| GET    | `/api/example/items/{item_id}` | 获取单个 Item   |
| POST   | `/api/example/items`           | 创建 Item       |
| POST   | `/api/example/items/batch`     | 批量创建 Items  |
| PUT    | `/api/example/items/{item_id}` | 完整更新 Item   |
| PATCH  | `/api/example/items/{item_id}` | 部分更新 Item   |
| DELETE | `/api/example/items/{item_id}` | 删除 Item       |

### 特殊功能

| 方法 | 路径                    | 描述         |
| ---- | ----------------------- | ------------ |
| POST | `/api/example/upload`   | 文件上传     |
| POST | `/api/example/form`     | 表单提交     |
| GET  | `/api/example/headers`  | 读取请求头   |
| GET  | `/api/example/cookies`  | 读取 Cookies |
| GET  | `/api/example/download` | 文件下载     |
| GET  | `/api/example/stream`   | 流式响应     |
| POST | `/api/example/mixed`    | 混合参数     |

### 错误测试

| 方法 | 路径                     | 描述          |
| ---- | ------------------------ | ------------- |
| GET  | `/api/example/error/400` | 模拟 400 错误 |
| GET  | `/api/example/error/404` | 模拟 404 错误 |
| GET  | `/api/example/error/500` | 模拟 500 错误 |

---

## 🔥 快速测试流程

按以下顺序测试可以快速验证所有功能：

```powershell
# 1. 启动服务
python -m app.api_main

# 2. 在浏览器中打开 Swagger UI
start http://127.0.0.1:8000/docs

# 3. 在新的 PowerShell 窗口中测试
# 健康检查
curl http://127.0.0.1:8000/api/example/health

# 创建一个项目
curl -X POST http://127.0.0.1:8000/api/example/items -H "Content-Type: application/json" -d '{\"name\":\"测试\",\"price\":100}'

# 查看所有项目
curl http://127.0.0.1:8000/api/example/items

# 4. 运行 Python 测试脚本
python test_api.py
```

---

## 📝 注意事项

1. **端口占用**: 如果 8000 端口被占用，修改 `api_main.py` 中的端口号
2. **CORS**: 生产环境中要设置具体的 `allow_origins`
3. **错误处理**: 示例中使用了全局异常处理
4. **数据持久化**: 当前使用内存存储（fake_db），重启服务后数据会丢失
5. **文件上传**: 大文件上传需要配置 `max_upload_size`

---

## 🎯 学习要点

通过这些示例，你可以学习到：

- ✅ GET/POST/PUT/PATCH/DELETE 方法
- ✅ Query 参数、Path 参数、Body 参数
- ✅ 请求头（Headers）和 Cookies
- ✅ 文件上传和下载
- ✅ 表单数据处理
- ✅ 流式响应
- ✅ 错误处理
- ✅ 数据验证（Pydantic）
- ✅ API 文档自动生成（Swagger UI）
- ✅ 混合参数使用

---

## 🆘 故障排查

### 问题 1: 服务无法启动

```powershell
# 检查是否安装了 FastAPI 和 uvicorn
pip install fastapi uvicorn[standard]
```

### 问题 2: 端口已被占用

```powershell
# 查看端口占用
netstat -ano | findstr :8000

# 更换端口
uvicorn app.api_main:app --port 8001
```

### 问题 3: 导入错误

确保在项目根目录运行，并且使用 `-m` 模式：

```powershell
python -m app.api_main
```

---

## 📚 延伸阅读

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [Uvicorn 文档](https://www.uvicorn.org/)

---

**祝测试愉快！** 🎉
