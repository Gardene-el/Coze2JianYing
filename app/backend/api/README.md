# API 模块

本目录包含所有 FastAPI 路由和端点定义。

## 结构说明

此目录用于存放后端应用的 API 路由处理程序，使用 FastAPI 框架。

### 规划的文件结构

```
api/
├── __init__.py
├── routes/              # API 路由模块
│   ├── __init__.py
│   ├── draft.py        # 草稿相关的 API 端点
│   ├── material.py     # 素材管理 API 端点
│   └── health.py       # 健康检查端点
└── dependencies.py      # API 依赖项
```

## 使用示例

```python
from fastapi import APIRouter
from app.backend.schemas.draft import DraftRequest, DraftResponse
from app.backend.DraftGenerator.draft_generator import DraftGenerator

router = APIRouter()

@router.post("/draft/generate", response_model=DraftResponse)
async def generate_draft(request: DraftRequest):
    generator = DraftGenerator()
    result = generator.generate_from_json(request.json_data)
    return {"status": "success", "draft_paths": result}
```

## 待开发功能

- [ ] 草稿生成 API 端点
- [ ] 素材上传和管理端点
- [ ] 草稿列表和查询端点
- [ ] WebSocket 实时进度通知
