# Coze2JianYing API 接口设计文档

## 概述

本文档详细说明 Coze 与草稿生成器之间的**流式命令处理**接口设计，解决以下核心问题：

1. **素材下载管理**：Coze 传递的是网络链接，本地需要先下载素材再调用 pyJianYingDraft
2. **变量作用域问题**：通过 UUID 系统管理草稿状态，避免 Coze 工作流的变量索引干扰
3. **增量命令处理**：支持 Coze 流式发送指令，无需等待完整草稿数据

## 重要说明

本设计专注于**云端服务和本地服务的流式 API 模式**，允许 Coze 工作流以增量方式发送命令（创建草稿 → 添加素材 → 添加更多内容 → 生成）。

**注意**：本文档不涉及手动草稿生成模式（即 coze_plugin 工具导出完整 JSON 后手动粘贴到 GUI 的方式）。手动模式由现有的 coze_plugin/tools/ 中的工具函数支持，不在本次设计范围内。

## 架构设计

### 流式处理工作流程

```
┌──────────────────────────────────────────────────────────┐
│                    Coze 工作流                            │
│                                                           │
│  1. 生成素材 → 2. 调用 API → 3. 继续生成 → 4. 再调用 API │
│                                                           │
└──────────────────────┬───────────────────────────────────┘
                       │ HTTP API 调用（增量命令）
                       ▼
┌──────────────────────────────────────────────────────────┐
│              云端/本地 API 服务（FastAPI）                 │
│                                                           │
│  /api/draft/create          创建草稿 → 返回 UUID          │
│  /api/draft/{id}/add-videos  添加视频（流式）             │
│  /api/draft/{id}/add-audios  添加音频（流式）             │
│  /api/draft/{id}/add-images  添加图片（流式）             │
│  /api/draft/{id}/add-captions 添加字幕（流式）            │
│  /api/draft/{id}/detail      查询当前状态                 │
│  /api/draft/{id}/generate    最终生成草稿文件             │
│                                                           │
└──────────────────────┬───────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────┐
│           DraftStateManager（UUID 状态管理）               │
│                                                           │
│  - 基于 UUID 存储草稿配置                                  │
│  - 追踪每个素材的下载状态                                  │
│  - 支持增量添加轨道和片段                                  │
│                                                           │
└──────────────────────┬───────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────┐
│              MaterialManager（素材管理）                   │
│                                                           │
│  - 异步下载素材文件                                        │
│  - 更新下载状态                                            │
│                                                           │
└──────────────────────┬───────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────┐
│         DraftGenerator + pyJianYingDraft                  │
│                                                           │
│  - 从 UUID 配置生成剪映草稿                                │
│                                                           │
└──────────────────────┬───────────────────────────────────┘
                       ▼
              剪映草稿文件（JianYing Projects）
```

### 核心设计原则

1. **流式命令处理**：Coze 可以逐步发送命令，无需等待完整数据
2. **UUID 状态管理**：所有草稿操作使用 UUID 作为唯一标识符，解决变量作用域问题
3. **异步素材下载**：素材链接记录后异步下载，不阻塞命令处理
4. **无状态 API**：每次 API 调用都是独立的，状态通过 UUID 持久化存储

## API 接口设计

### 1. 草稿管理接口

#### 1.1 创建草稿

**接口名称**: `create_draft`

**功能**: 创建新的剪映草稿项目，返回 UUID 供后续操作使用

**输入参数**:
```json
{
  "draft_name": "项目名称",
  "width": 1920,
  "height": 1080,
  "fps": 30
}
```

**输出结果**:
```json
{
  "draft_id": "abc12345-def6-789a-bcde-f123456789ab",
  "success": true,
  "message": "草稿创建成功"
}
```

**API 端点** (RESTful):
- **Method**: `POST`
- **Path**: `/api/draft/create`
- **Body**: JSON 格式的输入参数

**Coze Handler** (云侧插件):
```python
def handler(args: Args[Input]) -> Dict[str, Any]:
    # 输入验证
    # 生成 UUID
    # 创建草稿配置文件
    # 返回结果
```

#### 1.2 导出草稿

**接口名称**: `export_drafts`

**功能**: 将草稿数据导出为 JSON 格式，供草稿生成器使用

**输入参数**:
```json
{
  "draft_ids": ["uuid1", "uuid2"],  // 或单个字符串 "uuid1"
  "remove_temp_files": false,
  "export_all": false
}
```

**输出结果**:
```json
{
  "draft_data": "{完整的JSON字符串}",
  "exported_count": 2,
  "success": true,
  "message": "成功导出 2 个草稿"
}
```

**API 端点**:
- **Method**: `POST`
- **Path**: `/api/draft/export`
- **Body**: JSON 格式的输入参数

### 2. 素材管理接口

#### 2.1 添加视频素材

**接口名称**: `add_videos`

**功能**: 向指定草稿添加视频轨道和视频片段

**核心设计**：
- 接收**素材链接数组**而非本地文件路径
- 后端负责下载素材到 Assets 文件夹
- 支持视频片段的完整参数配置

**输入参数**:
```json
{
  "draft_id": "uuid",
  "videos": [
    {
      "material_url": "https://example.com/video1.mp4",
      "time_range": {"start": 0, "end": 5000},
      "position_x": 0.0,
      "position_y": 0.0,
      "scale_x": 1.0,
      "scale_y": 1.0,
      // ... 其他可选参数
    }
  ]
}
```

**处理流程**:
1. 验证 draft_id 和参数
2. 将素材链接加入下载队列
3. 下载完成后创建 VideoMaterial 对象
4. 创建 VideoSegment 并添加到轨道
5. 更新草稿配置

**输出结果**:
```json
{
  "success": true,
  "message": "成功添加 2 个视频片段",
  "download_status": {
    "completed": 2,
    "failed": 0
  }
}
```

**API 端点**:
- **Method**: `POST`
- **Path**: `/api/draft/{draft_id}/add-videos`
- **Body**: videos 数组

#### 2.2 添加音频素材

**接口名称**: `add_audios`

**功能**: 向指定草稿添加音频轨道和音频片段

**输入参数**:
```json
{
  "draft_id": "uuid",
  "audios": [
    {
      "material_url": "https://example.com/audio1.mp3",
      "time_range": {"start": 0, "end": 5000},
      "volume": 1.0,
      "fade_in": 0,
      "fade_out": 0,
      // ... 其他可选参数
    }
  ]
}
```

**API 端点**:
- **Method**: `POST`
- **Path**: `/api/draft/{draft_id}/add-audios`

#### 2.3 添加图片素材

**接口名称**: `add_images`

**功能**: 向指定草稿添加图片轨道和图片片段（作为静态视频）

**输入参数**:
```json
{
  "draft_id": "uuid",
  "images": [
    {
      "material_url": "https://example.com/image1.jpg",
      "time_range": {"start": 0, "end": 3000},
      "fit_mode": "fill",
      "background_color": "#000000",
      // ... 其他可选参数
    }
  ]
}
```

**API 端点**:
- **Method**: `POST`
- **Path**: `/api/draft/{draft_id}/add-images`

#### 2.4 添加字幕

**接口名称**: `add_captions`

**功能**: 向指定草稿添加字幕轨道和字幕片段

**输入参数**:
```json
{
  "draft_id": "uuid",
  "captions": [
    {
      "text": "字幕内容",
      "time_range": {"start": 0, "end": 2000},
      "font_family": "黑体",
      "font_size": 24,
      "color": "#FFFFFF",
      // ... 其他可选参数
    }
  ]
}
```

**API 端点**:
- **Method**: `POST`
- **Path**: `/api/draft/{draft_id}/add-captions`

### 3. 草稿查询接口

#### 3.1 查询草稿状态

**接口名称**: `get_draft_status`

**功能**: 查询草稿的当前状态和信息

**输入参数**:
```json
{
  "draft_id": "uuid"
}
```

**输出结果**:
```json
{
  "draft_id": "uuid",
  "status": "ready",  // ready, processing, error
  "project_name": "项目名称",
  "tracks_count": 3,
  "materials_count": 5,
  "download_status": {
    "total": 5,
    "completed": 5,
    "failed": 0,
    "pending": 0
  }
}
```

**API 端点**:
- **Method**: `GET`
- **Path**: `/api/draft/{draft_id}/status`

#### 3.2 列出所有草稿

**接口名称**: `list_drafts`

**功能**: 列出所有已创建的草稿

**API 端点**:
- **Method**: `GET`
- **Path**: `/api/draft/list`
- **Query Parameters**: `skip`, `limit`

## 素材下载管理

### 下载队列设计

```python
class MaterialDownloadQueue:
    """素材下载队列管理器"""
    
    def __init__(self):
        self.queue = []
        self.completed = {}
        self.failed = {}
    
    def add_download_task(self, url: str, draft_id: str):
        """添加下载任务"""
        pass
    
    def get_status(self, draft_id: str):
        """获取下载状态"""
        pass
    
    def download_worker(self):
        """后台下载工作线程"""
        pass
```

### 下载流程

1. **接收请求**：API 接收到添加素材的请求
2. **验证链接**：验证素材链接的有效性
3. **加入队列**：将下载任务加入队列
4. **后台下载**：独立线程异步下载素材
5. **更新状态**：下载完成后更新草稿配置
6. **错误处理**：下载失败时记录错误并重试

### MaterialManager 扩展

当前 MaterialManager 需要扩展以支持：

```python
class MaterialManager:
    def download_from_url_async(self, url: str) -> str:
        """异步下载素材"""
        # 1. 生成唯一文件名
        # 2. 下载到 Assets 文件夹
        # 3. 返回本地路径
        pass
    
    def get_download_status(self, url: str):
        """查询下载状态"""
        pass
    
    def batch_download(self, urls: List[str]):
        """批量下载素材"""
        pass
```

## 变量作用域解决方案

### UUID 管理系统

**问题**：Coze 工作流中，每次函数调用都会产生新的变量索引，无法在不同调用间共享草稿对象

**解决方案**：使用 UUID 作为草稿的唯一标识符，实现跨调用的状态持久化

```
用户输入参数 → create_draft → UUID
                                  ↓
                            add_videos(UUID, videos)   ← 流式添加
                            add_audios(UUID, audios)   ← 流式添加
                            add_captions(UUID, captions) ← 流式添加
                                  ↓
                            generate(UUID)  ← 最终生成草稿文件
```

### 状态存储

**文件系统存储** (当前实现):
- 位置：`/tmp/jianying_assistant/drafts/{uuid}/`
- 结构：每个草稿一个文件夹，包含 `draft_config.json`
- 生命周期：持久化存储，支持跨会话访问
- 优点：简单、无需数据库依赖

**持久化存储** (未来扩展):
- 位置：数据库（SQLite/PostgreSQL）
- 支持草稿历史记录和版本管理
- 支持更复杂的查询和统计

## 流式 API 服务实现

### API 服务模式（重点）

**特点**：
- Coze 工作流通过 HTTP API 直接调用本地/云端服务
- 支持增量、流式发送命令
- 无需等待完整数据，边生成边处理
- 完全自动化，无需人工干预

**实现位置**：`app/api/material_routes.py`

**工作流**：
```
Coze 工作流 → HTTP API 调用（增量）→ FastAPI 服务 → DraftStateManager
                                                          ↓
                                                    素材异步下载
                                                          ↓
                                                    pyJianYingDraft
                                                          ↓
                                                    剪映草稿文件
```

**示例**：
```python
# coze_plugin/tools/add_videos/handler.py
def handler(args: Args[Input]) -> Dict[str, Any]:
    draft_id = args.input.draft_id
    videos = args.input.videos
    
```python
# app/api/material_routes.py
@router.post("/draft/{draft_id}/add-videos")
async def add_videos(
    draft_id: str,
    request: AddVideosRequest
):
    # 1. 验证 draft_id 是否存在
    config = draft_manager.get_draft_config(draft_id)
    if not config:
        raise HTTPException(status_code=404, detail="草稿不存在")
    
    # 2. 转换并添加视频片段（记录素材 URL）
    segments = [video.dict() for video in request.videos]
    draft_manager.add_track(draft_id, "video", segments)
    
    # 3. 素材将在后台异步下载（或在 generate 时下载）
    
    # 4. 返回结果
    return {
        "success": True,
        "message": f"成功添加 {len(segments)} 个视频片段",
        "segments_added": len(segments)
    }
```

**在 Coze 中配置 API 插件**：

1. 创建"云侧插件 - 基于已有服务创建"
2. 配置服务地址：`http://localhost:8000` 或远程地址
3. 导入 OpenAPI 规范（从 `/openapi.json` 获取）
4. 在工作流中直接调用 API 端点

## 远程部署支持

### 本地服务模式

**场景**：草稿生成器在本地运行，Coze 通过内网穿透访问

**步骤**：
1. 启动本地 API 服务：`python start_api.py`
2. 使用内网穿透工具（ngrok、frp）暴露端口
3. 在 Coze 中配置穿透后的公网 URL

**示例（ngrok）**：
```bash
# 启动 API 服务
python start_api.py  # 运行在 localhost:8000

# 在另一个终端启动 ngrok
ngrok http 8000

# 获得公网 URL: https://xxxx.ngrok.io
# 在 Coze 中配置此 URL
```

### 云端服务模式

**场景**：草稿生成器部署在云服务器，Coze 直接访问

**配置**：
1. 在服务器上启动 FastAPI 服务
2. 配置域名或公网 IP
3. 在 Coze 插件配置中填入 API 地址
4. 配置认证（API Key 或 OAuth）

**认证机制**：
```python
# app/api/auth.py
def verify_api_key(api_key: str):
    """验证 API Key"""
    # 检查 API Key 是否有效
    pass

# 在路由中使用
@router.post("/draft/create")
async def create_draft(
    request: CreateDraftRequest,
    api_key: str = Header(...)
):
    verify_api_key(api_key)
    # 处理请求
```

### 本地服务（内网穿透）

**场景**：草稿生成器运行在本地，通过内网穿透暴露给 Coze

**工具选择**：
- ngrok
- frp
- localtunnel

**配置步骤**：
1. 启动本地 API 服务（默认 `localhost:8000`）
2. 使用内网穿透工具创建公网 URL
3. 在 Coze 中配置穿透后的 URL

## 完整使用示例

### 流式 API 调用示例（推荐）

这是本项目的核心使用方式，支持 Coze 工作流增量发送命令。

```python
# 在 Coze 工作流中配置 HTTP 请求

# 步骤1：创建草稿
POST https://your-server.com/api/draft/create
Body: {
    "draft_name": "我的视频项目",
    "width": 1920,
    "height": 1080,
    "fps": 30
}
Response: {"draft_id": "uuid", "success": true}

# 步骤2：添加第一批视频（流式）
POST https://your-server.com/api/draft/{draft_id}/add-videos
Body: {
    "draft_id": "{draft_id}",
    "videos": [{
        "material_url": "https://example.com/video1.mp4",
        "time_range": {"start": 0, "end": 5000}
    }]
}
Response: {"success": true, "segments_added": 1}

# 步骤3：继续添加音频（流式，无需等待视频下载完成）
POST https://your-server.com/api/draft/{draft_id}/add-audios
Body: {
    "draft_id": "{draft_id}",
    "audios": [{
        "material_url": "https://example.com/audio1.mp3",
        "time_range": {"start": 0, "end": 5000},
        "volume": 0.8
    }]
}
Response: {"success": true, "segments_added": 1}

# 步骤4：添加更多视频（流式，Coze 可以继续生成内容）
POST https://your-server.com/api/draft/{draft_id}/add-videos
Body: {
    "draft_id": "{draft_id}",
    "videos": [{
        "material_url": "https://example.com/video2.mp4",
        "time_range": {"start": 5000, "end": 10000}
    }]
}

# 步骤5：添加字幕
POST https://your-server.com/api/draft/{draft_id}/add-captions
Body: {
    "draft_id": "{draft_id}",
    "captions": [{
        "text": "欢迎观看",
        "time_range": {"start": 0, "end": 2000}
    }]
}

# 步骤6：查询当前状态
GET https://your-server.com/api/draft/{draft_id}/detail
Response: {
    "draft_id": "uuid",
    "tracks_count": 3,
    "materials_count": 3,
    "download_status": {
        "total": 3,
        "completed": 2,
        "pending": 1,
        "failed": 0
    }
}

# 步骤7：生成草稿文件（待实现）
POST https://your-server.com/api/draft/{draft_id}/generate
Response: {"folder_path": "本地路径", "success": true}
```

**关键特性**：
- ✅ **流式处理**：无需等待完整数据，Coze 可以边生成边发送
- ✅ **增量添加**：可以多次调用 add-* 端点添加内容
- ✅ **异步下载**：素材在后台下载，不阻塞命令处理
- ✅ **状态查询**：随时查询草稿状态和下载进度

## 开发路线图

### 阶段一：核心流式 API（已完成 ✅）
- [x] 实现 `create_draft` API 端点
- [x] 实现 `add_videos` API 端点
- [x] 实现 `add_audios` API 端点
- [x] 实现 `add_images` API 端点
- [x] 实现 `add_captions` API 端点
- [x] 实现草稿状态查询接口 (`detail`)
- [x] UUID 状态管理系统

### 阶段二：素材下载管理（待实现）
- [ ] 实现异步下载队列
- [ ] 扩展 MaterialManager 支持异步下载
- [ ] 实现下载状态实时更新
- [ ] 添加下载失败重试机制

### 阶段三：草稿生成（待实现）
- [ ] 实现 `generate` API 端点
- [ ] 集成 DraftGenerator 和 pyJianYingDraft
- [ ] 支持从 UUID 配置生成草稿文件
- [ ] 等待所有素材下载完成后生成

### 阶段四：OpenAPI 和文档
- [x] FastAPI 自动生成 OpenAPI 规范
- [x] Swagger UI 界面 (`/docs`)
- [ ] 为 Coze 插件配置提供 OpenAPI 导出
- [ ] 完善 API 文档和示例

### 阶段五：认证和安全
- [ ] 实现 API Key 认证
- [ ] 添加请求限流
- [ ] 实现 HTTPS 支持
- [ ] 添加日志审计

### 阶段五：持久化存储
- [ ] 设计数据库模型
- [ ] 实现草稿持久化
- [ ] 支持草稿历史记录
- [ ] 实现草稿搜索和管理

## 总结

本设计文档提供了完整的 API 接口规范，解决了 Coze 与草稿生成器通信的三个核心问题：

1. **素材下载管理**：通过异步下载队列和 MaterialManager 扩展
2. **变量作用域**：通过 UUID 管理系统避免 Coze 变量索引干扰
3. **接口规范**：为两种通信方式（Coze IDE 插件和 API 服务）提供统一设计

下一步工作重点是实现完整的 API 端点，并扩展素材下载管理功能。
