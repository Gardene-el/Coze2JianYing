# Services 模块

## 概述

此目录用于存放 FastAPI 服务相关的代码。云端服务标签页中的 FastAPI 服务实现将放置在这里。

## 目录结构

```
services/
├── __init__.py          # 包初始化文件
├── README.md            # 本文档
├── api/                 # API 路由定义（待创建）
│   ├── __init__.py
│   └── routes.py
├── models/              # 数据模型（待创建）
│   ├── __init__.py
│   └── schemas.py
└── core/                # 核心服务逻辑（待创建）
    ├── __init__.py
    └── service.py
```

## 使用说明

### 创建 FastAPI 服务

FastAPI 服务用于云端服务标签页。服务实现应该：

1. 在 `services/core/service.py` 中定义主服务类
2. 在 `services/api/routes.py` 中定义 API 路由
3. 在 `services/models/schemas.py` 中定义数据模型
4. 在云端服务标签页中启动实际的 FastAPI 应用

### 示例代码结构

#### services/core/service.py
```python
from fastapi import FastAPI
import uvicorn

class DraftService:
    """草稿生成服务"""
    
    def __init__(self, port: int = 8000):
        self.app = FastAPI(title="剪映草稿生成服务")
        self.port = port
        self._setup_routes()
    
    def _setup_routes(self):
        # 注册路由
        pass
    
    def run(self):
        """运行服务"""
        uvicorn.run(self.app, host="localhost", port=self.port)
```

#### services/api/routes.py
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def root():
    return {"message": "剪映草稿生成服务"}

@router.get("/health")
async def health():
    return {"status": "healthy"}
```

#### services/models/schemas.py
```python
from pydantic import BaseModel

class DraftRequest(BaseModel):
    """草稿生成请求"""
    content: str
    output_folder: str

class DraftResponse(BaseModel):
    """草稿生成响应"""
    success: bool
    draft_path: str
    message: str
```

## 集成到云端服务标签页

在 `app/gui/cloud_service_tab.py` 中：

```python
def _run_service(self, port: int):
    """运行FastAPI服务"""
    try:
        from services.core.service import DraftService
        
        service = DraftService(port=port)
        service.run()
    except Exception as e:
        self.logger.error(f"FastAPI服务出错: {e}", exc_info=True)
        self.frame.after(0, self._on_service_error, e)
```

## 依赖项

FastAPI 服务需要以下依赖（已在 `requirements.txt` 中）：
- `fastapi>=0.104.0`
- `uvicorn[standard]>=0.24.0`
- `pydantic>=2.0.0`

## 开发指南

### 添加新的 API 端点

1. 在 `services/api/routes.py` 中定义路由
2. 在 `services/models/schemas.py` 中定义请求/响应模型
3. 在 `services/core/service.py` 中注册路由

### 测试

为服务代码创建测试文件：
- `tests/services/test_api.py` - API 路由测试
- `tests/services/test_service.py` - 服务逻辑测试

### 最佳实践

1. **路由组织**: 使用 APIRouter 组织相关的路由
2. **数据验证**: 使用 Pydantic 模型进行数据验证
3. **错误处理**: 实现统一的错误处理机制
4. **日志记录**: 使用 logging 模块记录服务日志
5. **异步操作**: 对 I/O 密集型操作使用 async/await

## 安全注意事项

1. **CORS 配置**: 根据需要配置 CORS 策略
2. **认证授权**: 如需要，实现认证机制
3. **输入验证**: 严格验证所有输入数据
4. **错误消息**: 避免在错误消息中泄露敏感信息

## 相关文档

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Uvicorn 文档](https://www.uvicorn.org/)
- [Pydantic 文档](https://docs.pydantic.dev/)

## 未来扩展

- [ ] 实现草稿生成 API
- [ ] 添加草稿列表查询接口
- [ ] 实现文件上传功能
- [ ] 添加 WebSocket 支持用于实时进度更新
- [ ] 实现 API 文档自动生成（Swagger UI）

## 注意事项

- FastAPI 服务需要公网访问才能被 Coze 调用，可以使用 ngrok 等工具
- 确保保持线程安全和 GUI 更新的正确性
- FastAPI 服务应在单独的线程或进程中运行，避免阻塞 GUI
