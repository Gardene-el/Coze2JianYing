# Models 模块

本目录包含所有数据库模型定义（SQLAlchemy/ORM 模型）。

## 结构说明

此目录用于存放数据库表的 ORM 模型定义，使用 SQLAlchemy。

### 规划的文件结构

```
models/
├── __init__.py
├── base.py             # 基础模型类
├── draft.py            # 草稿模型
├── material.py         # 素材模型
└── user.py             # 用户模型（如需要）
```

## 使用示例

```python
from sqlalchemy import Column, Integer, String, DateTime
from backend.models.base import Base

class Draft(Base):
    __tablename__ = "drafts"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, unique=True, index=True)
    name = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

## 待开发功能

- [ ] Draft 草稿模型
- [ ] Material 素材模型
- [ ] Project 项目模型
- [ ] 关系定义和外键约束
