# Schemas 模块

本目录包含所有 Pydantic 数据模型定义（API 请求/响应模型）。

## 结构说明

此目录用于存放 API 的输入输出数据结构定义，使用 Pydantic 进行数据验证。

### 规划的文件结构

```
schemas/
├── __init__.py
├── draft.py            # 草稿相关的请求/响应模型
├── material.py         # 素材相关的请求/响应模型
├── common.py           # 通用响应模型
└── coze.py             # Coze 输出格式模型
```

## 使用示例

```python
from pydantic import BaseModel, Field
from typing import List, Optional

class DraftRequest(BaseModel):
    json_data: str = Field(..., description="Coze 输出的 JSON 数据")
    output_dir: Optional[str] = Field(None, description="输出目录")
    draft_uuid: Optional[str] = Field(None, description="草稿 UUID")

class DraftResponse(BaseModel):
    status: str
    draft_paths: List[str]
    message: Optional[str] = None

class MaterialInfo(BaseModel):
    url: str
    type: str  # video, audio, image
    duration: Optional[float] = None
```

## 待开发功能

- [ ] DraftRequest 和 DraftResponse schemas
- [ ] MaterialRequest 和 MaterialResponse schemas
- [ ] Coze 输出格式验证 schema
- [ ] 错误响应 schema
