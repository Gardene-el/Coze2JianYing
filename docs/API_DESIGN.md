# Coze2JianYing API 接口设计文档

## 概述

本文档详细说明 Coze 与草稿生成器之间的通信接口设计，解决以下核心问题：

1. **素材下载管理**：Coze 传递的是网络链接，本地需要先下载素材再调用 pyJianYingDraft
2. **变量作用域问题**：通过 UUID 系统管理草稿状态，避免 Coze 工作流的变量索引干扰
3. **接口规范统一**：为两种通信方式（Coze IDE 插件和 API 服务）提供统一的设计规范

## 架构设计

### 工作流程

```
┌──────────┐    ┌──────────────┐    ┌─────────────────┐    ┌─────────────┐
│  Coze    │───▶│  插件/API    │───▶│  草稿生成器     │───▶│   剪映      │
│  工作流  │    │  接口层      │    │  (后端处理)     │    │             │
└──────────┘    └──────────────┘    └─────────────────┘    └─────────────┘
     │                 │                      │
     │                 │                      │
  传递指令          UUID + 参数           素材下载 +
  + 参数            + 素材链接            pyJianYingDraft
```

### 核心设计原则

1. **UUID 索引**：所有草稿操作使用 UUID 作为唯一标识符
2. **异步下载**：素材链接传递给后端，由后端负责下载和管理
3. **无状态接口**：每次 API 调用都是独立的，状态通过 UUID 查询
4. **统一格式**：Coze IDE 插件和 API 服务使用相同的数据格式

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

**问题**：Coze 工作流中，每次函数调用都会产生新的变量索引

**解决方案**：使用 UUID 作为草稿的唯一标识符

```
用户输入参数 → create_draft → UUID
                                  ↓
                            add_videos(UUID, videos)
                            add_audios(UUID, audios)
                            add_captions(UUID, captions)
                                  ↓
                            export_drafts([UUID])
                                  ↓
                            完整JSON数据
```

### 状态存储

**临时存储** (当前实现):
- 位置：`/tmp/jianying_assistant/drafts/{uuid}/`
- 结构：每个草稿一个文件夹，包含 `draft_config.json`
- 生命周期：工作流执行期间

**持久化存储** (建议):
- 位置：数据库或文件系统
- 支持草稿历史记录
- 支持跨会话访问

## 两种通信方式的实现

### 方式一：Coze IDE 插件（云侧插件 - 手动模式）

**特点**：
- 用户在 Coze IDE 中部署工具函数
- 工具函数处理参数并生成 JSON
- 用户手动复制 JSON 到草稿生成器

**实现位置**：`coze_plugin/tools/`

**工作流**：
```
Coze 工作流 → 调用插件工具 → 生成JSON → 用户复制 → 草稿生成器GUI
```

**示例**：
```python
# coze_plugin/tools/add_videos/handler.py
def handler(args: Args[Input]) -> Dict[str, Any]:
    draft_id = args.input.draft_id
    videos = args.input.videos
    
    # 加载草稿配置
    config = load_draft_config(draft_id)
    
    # 添加视频信息（仅记录链接，不下载）
    config['tracks'].append({
        'type': 'video',
        'segments': videos
    })
    
    # 保存配置
    save_draft_config(draft_id, config)
    
    return {
        'success': True,
        'message': f'成功添加 {len(videos)} 个视频'
    }
```

### 方式二：API 服务（基于服务的插件 - 自动模式）

**特点**：
- 草稿生成器启动 FastAPI 服务
- Coze 工作流自动调用 API
- 完全自动化的端到端流程

**实现位置**：`app/api/`

**工作流**：
```
Coze 工作流 → HTTP请求 → FastAPI服务 → 草稿生成器后端 → 自动完成
```

**API 实现示例**：
```python
# app/api/draft_routes.py
@router.post("/draft/{draft_id}/add-videos")
async def add_videos(
    draft_id: str,
    videos: List[VideoSegmentConfig]
):
    # 1. 验证 draft_id
    # 2. 添加下载任务
    # 3. 创建视频轨道
    # 4. 返回结果
    pass
```

**OpenAPI 配置**（用于 Coze 插件配置）：
```yaml
openapi: 3.0.0
info:
  title: Coze剪映草稿生成器 API
  version: 1.0.0
paths:
  /api/draft/create:
    post:
      summary: 创建草稿
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateDraftRequest'
```

## SSH/远程调用支持

### 远程 API 部署

**场景**：草稿生成器部署在远程服务器，Coze 通过网络调用

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

### 示例1：通过 Coze IDE 插件手动模式

```python
# 在 Coze 工作流中的步骤

# 步骤1：创建草稿
create_result = call_tool('create_draft', {
    'draft_name': '我的视频项目',
    'width': 1920,
    'height': 1080,
    'fps': 30
})
draft_id = create_result['draft_id']

# 步骤2：添加视频
add_videos_result = call_tool('add_videos', {
    'draft_id': draft_id,
    'videos': [
        {
            'material_url': 'https://example.com/video1.mp4',
            'time_range': {'start': 0, 'end': 5000}
        }
    ]
})

# 步骤3：添加音频
add_audios_result = call_tool('add_audios', {
    'draft_id': draft_id,
    'audios': [
        {
            'material_url': 'https://example.com/audio1.mp3',
            'time_range': {'start': 0, 'end': 5000}
        }
    ]
})

# 步骤4：导出草稿
export_result = call_tool('export_drafts', {
    'draft_ids': draft_id
})

# 步骤5：用户复制 export_result['draft_data'] 到草稿生成器
```

### 示例2：通过 API 服务自动模式

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
Response: {"draft_id": "uuid"}

# 步骤2：添加视频
POST https://your-server.com/api/draft/{draft_id}/add-videos
Body: {
    "videos": [...]
}

# 步骤3：添加音频
POST https://your-server.com/api/draft/{draft_id}/add-audios
Body: {
    "audios": [...]
}

# 步骤4：生成草稿（自动下载素材并生成）
POST https://your-server.com/api/draft/{draft_id}/generate
Response: {"folder_path": "本地路径", "success": true}
```

## 开发路线图

### 阶段一：完善 API 端点（当前任务）
- [ ] 实现 `add_videos` API 端点
- [ ] 实现 `add_audios` API 端点
- [ ] 实现 `add_images` API 端点
- [ ] 实现 `add_captions` API 端点
- [ ] 实现草稿状态查询接口

### 阶段二：素材下载管理
- [ ] 实现异步下载队列
- [ ] 扩展 MaterialManager 支持异步下载
- [ ] 实现下载状态查询
- [ ] 添加下载失败重试机制

### 阶段三：OpenAPI 文档生成
- [ ] 生成完整的 OpenAPI 规范文件
- [ ] 提供 Swagger UI 界面
- [ ] 为 Coze 插件配置提供导出功能

### 阶段四：认证和安全
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
