# Database 模块

本目录包含数据库配置和连接管理。

## 结构说明

此目录用于存放数据库连接配置、会话管理和初始化代码。

### 规划的文件结构

```
database/
├── __init__.py
├── config.py           # 数据库配置
├── session.py          # 数据库会话管理
└── init_db.py          # 数据库初始化脚本
```

## 使用示例

```python
# config.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./coze2jianying.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# session.py
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 待开发功能

- [ ] SQLite/PostgreSQL 数据库配置
- [ ] 数据库会话管理
- [ ] 连接池配置
- [ ] 数据库迁移支持（Alembic）
