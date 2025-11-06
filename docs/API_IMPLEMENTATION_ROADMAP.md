# API 实现路线图（旧版）

> **⚠️ 注意：本文档已被弃用**
>
> 本文档描述的旧版 API 实现计划已被新的设计替代。
> 
> **请参考最新的 API 设计：[API_ENDPOINTS_REFERENCE.md](API_ENDPOINTS_REFERENCE.md)**
>
> 新实现包括：
> - Segment 创建和操作端点（`app/api/segment_routes.py`）
> - Draft 操作端点（`app/api/new_draft_routes.py`）
> - Segment 状态管理（`app/utils/segment_manager.py`）
> - 完整的 Segment 数据模型（`app/schemas/segment_schemas.py`）
>
> 本文档仅作为历史参考保留。

---

## 当前状态（历史）

### 已完成 ✅

#### 1. 核心架构设计（旧版）
- [x] 完整的 API 设计文档 (`docs/API_DESIGN.md`) - 已弃用
- [x] 数据模型定义 (`app/schemas/material_schemas.py.old`) - 已移除
- [x] 草稿状态管理器 (`app/utils/draft_state_manager.py`) - 仍在使用
- [x] API 路由实现 (`app/api/material_routes.py.old`) - 已移除

#### 2. API 端点实现（旧版 - 已移除）
- [x] ~~`POST /api/draft/create` - 创建草稿~~ - 已被新实现替代
- [x] ~~`POST /api/draft/{draft_id}/add-videos` - 添加视频~~ - 已移除
- [x] ~~`POST /api/draft/{draft_id}/add-audios` - 添加音频~~ - 已移除
- [x] ~~`POST /api/draft/{draft_id}/add-images` - 添加图片~~ - 已移除
- [x] ~~`POST /api/draft/{draft_id}/add-captions` - 添加字幕~~ - 已移除
- [x] ~~`GET /api/draft/{draft_id}/detail` - 查询草稿详情~~ - 已移除

### 新版实现 ✅

请查看 [API_ENDPOINTS_REFERENCE.md](API_ENDPOINTS_REFERENCE.md) 了解新版 API 的完整实现。

#### 已实现的新版端点

**Segment 创建**：
- `POST /api/segment/audio/create`
- `POST /api/segment/video/create`
- `POST /api/segment/text/create`
- `POST /api/segment/sticker/create`

**Segment 操作**：
- AudioSegment: `add_effect`, `add_fade`, `add_keyframe`
- VideoSegment: `add_animation`, `add_effect`, `add_fade`, `add_filter`, `add_mask`, `add_transition`, `add_background_filling`, `add_keyframe`
- TextSegment: `add_animation`, `add_bubble`, `add_effect`, `add_keyframe`
- StickerSegment: `add_keyframe`

**Draft 操作**：
- `POST /api/draft/create`
- `POST /api/draft/{draft_id}/add_track`
- `POST /api/draft/{draft_id}/add_segment`
- `POST /api/draft/{draft_id}/add_effect`
- `POST /api/draft/{draft_id}/add_filter`
- `POST /api/draft/{draft_id}/save`
- `GET /api/draft/{draft_id}/status`

**查询**：
- `GET /api/segment/{segment_type}/{segment_id}`

---

## 旧版待完成任务（已废弃）

#### 1. 素材下载管理
当前状态：基础框架已完成，待实现异步下载功能

**需要完成的任务**：
- [ ] 实现异步下载队列 (`MaterialDownloadQueue`)
- [ ] 扩展 `MaterialManager` 支持异步下载
- [ ] 实现下载状态追踪和更新
- [ ] 添加下载失败重试机制
- [ ] 实现下载进度回调

**实现计划**：

```python
# app/utils/material_download_queue.py
class MaterialDownloadQueue:
    """异步素材下载队列"""
    
    def __init__(self):
        self.queue = Queue()
        self.workers = []
        self.status_tracker = {}
    
    def add_task(self, draft_id, material_url, material_type):
        """添加下载任务"""
        pass
    
    def start_workers(self, num_workers=3):
        """启动下载工作线程"""
        pass
    
    def get_status(self, draft_id):
        """获取下载状态"""
        pass
```

**优先级**：高
**预计时间**：2-3 天

### 待完成 📋

#### 1. 草稿导出功能

**描述**：实现从 UUID 草稿配置生成剪映草稿文件的功能

**API 端点**：
```
POST /api/draft/{draft_id}/generate
```

**功能需求**：
1. 验证所有素材已下载
2. 调用 `DraftGenerator` 生成草稿
3. 返回生成的草稿路径
4. 支持导出到指定目录或默认剪映目录

**相关文件**：
- `app/api/draft_routes.py` - 添加新端点
- `app/utils/draft_generator.py` - 扩展支持从 UUID 配置生成

**优先级**：高
**预计时间**：2 天

#### 2. Coze IDE 插件更新

**描述**：更新现有 Coze 插件工具以支持新的 API 架构

**需要更新的工具**：
- `coze_plugin/tools/add_videos/` - 使用新的数据格式
- `coze_plugin/tools/add_audios/` - 使用新的数据格式
- `coze_plugin/tools/add_images/` - 使用新的数据格式
- `coze_plugin/tools/add_captions/` - 使用新的数据格式

**变更内容**：
1. 使用 `DraftStateManager` 管理状态
2. 统一数据格式与 API 一致
3. 改进错误处理
4. 更新文档和示例

**优先级**：中
**预计时间**：3 天

#### 3. 认证和安全

**描述**：为 API 添加认证机制，保护服务安全

**功能需求**：
1. API Key 认证
2. 请求限流
3. CORS 配置优化
4. 输入数据验证增强

**实现方案**：

```python
# app/api/auth.py
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key not in valid_api_keys:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

# 在路由中使用
@router.post("/draft/create", dependencies=[Security(verify_api_key)])
async def create_draft(...):
    pass
```

**优先级**：中
**预计时间**：1-2 天

#### 4. 批量操作支持

**描述**：支持批量创建和管理草稿

**API 端点**：
```
POST /api/draft/batch-create
POST /api/draft/batch-generate
DELETE /api/draft/batch-delete
```

**功能需求**：
1. 批量创建多个草稿
2. 批量生成草稿文件
3. 批量删除草稿
4. 批量查询状态

**优先级**：低
**预计时间**：2 天

#### 5. 数据持久化

**描述**：使用数据库替代文件系统存储草稿配置

**技术选型**：
- SQLite（本地部署）
- PostgreSQL（生产部署）

**数据模型**：
```python
# app/models/draft.py
class Draft(Base):
    __tablename__ = "drafts"
    
    id = Column(String, primary_key=True)  # UUID
    project_name = Column(String)
    width = Column(Integer)
    height = Column(Integer)
    fps = Column(Integer)
    status = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    # 关系
    tracks = relationship("Track", back_populates="draft")
    materials = relationship("Material", back_populates="draft")
```

**优先级**：低
**预计时间**：3-4 天

#### 6. WebSocket 实时状态推送

**描述**：使用 WebSocket 推送素材下载进度和草稿生成状态

**API 端点**：
```
WS /ws/draft/{draft_id}/status
```

**功能需求**：
1. 实时推送下载进度
2. 实时推送草稿生成进度
3. 推送错误和警告信息

**实现示例**：

```python
# app/api/websocket_routes.py
from fastapi import WebSocket

@app.websocket("/ws/draft/{draft_id}/status")
async def draft_status_websocket(websocket: WebSocket, draft_id: str):
    await websocket.accept()
    
    while True:
        status = draft_manager.get_download_status(draft_id)
        await websocket.send_json(status)
        await asyncio.sleep(1)
```

**优先级**：低
**预计时间**：2 天

#### 7. 测试覆盖

**描述**：为所有 API 端点编写完整的测试

**测试类型**：
1. 单元测试 - 测试各个函数和类
2. 集成测试 - 测试 API 端点
3. 端到端测试 - 测试完整工作流

**测试文件**：
```
tests/
├── unit/
│   ├── test_draft_state_manager.py
│   ├── test_material_schemas.py
│   └── test_material_download_queue.py
├── integration/
│   ├── test_draft_api.py
│   ├── test_material_api.py
│   └── test_generate_api.py
└── e2e/
    └── test_full_workflow.py
```

**优先级**：中
**预计时间**：4-5 天

#### 8. OpenAPI 文档增强

**描述**：完善 OpenAPI 规范，添加更多示例和说明

**需要完成的任务**：
1. 为所有端点添加详细描述
2. 提供完整的请求/响应示例
3. 添加错误响应示例
4. 生成客户端 SDK（Python、JavaScript）

**优先级**：低
**预计时间**：1 天

## 实施计划

### 第一阶段（高优先级）

**时间**：1-2 周

**目标**：完成核心功能，实现基本可用的 API 系统

**任务清单**：
1. ✅ 实现基础 API 端点（已完成）
2. 🚧 实现异步素材下载队列
3. 🚧 实现草稿导出功能
4. ⏳ 编写基础测试

**验收标准**：
- 可以通过 API 创建草稿
- 可以添加各类素材
- 素材自动异步下载
- 可以生成剪映草稿文件

### 第二阶段（中优先级）

**时间**：2-3 周

**目标**：完善功能，提升稳定性和安全性

**任务清单**：
1. ⏳ 更新 Coze IDE 插件
2. ⏳ 实现认证和安全机制
3. ⏳ 完善测试覆盖
4. ⏳ 优化错误处理

**验收标准**：
- Coze 插件与 API 数据格式统一
- API 有基本的安全保护
- 测试覆盖率达到 80%
- 错误信息清晰明确

### 第三阶段（低优先级）

**时间**：3-4 周

**目标**：增强功能，支持生产环境部署

**任务清单**：
1. ⏳ 实现批量操作
2. ⏳ 数据持久化
3. ⏳ WebSocket 实时推送
4. ⏳ 完善文档和示例

**验收标准**：
- 支持大规模批量操作
- 数据可靠存储和恢复
- 实时状态更新
- 文档完整且易懂

## 技术债务

### 当前已知问题

1. **素材下载是同步的**
   - 问题：添加素材时会阻塞 API 响应
   - 解决方案：实现异步下载队列
   - 优先级：高

2. **草稿配置存储在文件系统**
   - 问题：不支持并发访问，难以扩展
   - 解决方案：使用数据库存储
   - 优先级：中

3. **没有认证机制**
   - 问题：任何人都可以访问 API
   - 解决方案：实现 API Key 认证
   - 优先级：中

4. **错误处理不够完善**
   - 问题：某些错误信息不够明确
   - 解决方案：统一错误处理和日志记录
   - 优先级：低

5. **缺少测试**
   - 问题：修改代码时容易引入 bug
   - 解决方案：编写完整的测试套件
   - 优先级：中

## 性能优化计划

### 当前性能指标

- API 响应时间：< 100ms（不含下载）
- 并发处理能力：未测试
- 素材下载速度：取决于网络
- 草稿生成时间：< 5s

### 优化目标

1. **API 响应优化**
   - 目标：< 50ms
   - 方案：使用缓存、优化数据库查询

2. **并发处理优化**
   - 目标：支持 100+ 并发请求
   - 方案：使用异步 IO、增加工作线程

3. **下载速度优化**
   - 目标：最大化利用带宽
   - 方案：并行下载、使用 CDN

4. **草稿生成优化**
   - 目标：< 3s
   - 方案：优化文件 IO、并行处理

## 维护计划

### 日常维护任务

- 监控 API 错误率
- 检查素材下载失败率
- 清理过期的临时文件
- 更新依赖包版本

### 定期维护任务

- 每周：检查日志文件，处理错误
- 每月：性能测试，优化瓶颈
- 每季度：安全审计，更新安全措施

## 参考资料

- [API 设计文档](./API_DESIGN.md)
- [API 使用示例](./API_USAGE_EXAMPLES.md)
- [开发路线图](./guides/DEVELOPMENT_ROADMAP.md)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Pydantic 文档](https://docs.pydantic.dev/)
