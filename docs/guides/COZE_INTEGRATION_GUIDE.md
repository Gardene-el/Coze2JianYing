# Coze 集成指南 - 使用 API Gateway 模式

本指南详细说明如何将 Coze2JianYing 的 FastAPI 服务与 Coze 平台集成，实现完全自动化的端到端工作流。

## 📋 目录

- [概述](#概述)
- [前置准备](#前置准备)
- [方式一：本地部署（推荐用于测试）](#方式一本地部署推荐用于测试)
- [方式二：云端部署（推荐用于生产）](#方式二云端部署推荐用于生产)
- [在 Coze 中配置插件](#在-coze-中配置插件)
- [工作流示例](#工作流示例)
- [常见问题](#常见问题)

## 概述

### 工作流架构

```
┌─────────────────┐
│  Coze 工作流     │  用户输入 → AI 生成素材和参数
│                 │
└────────┬────────┘
         │ 调用云侧插件（基于服务）
         │ HTTP POST
         ▼
┌─────────────────────────────┐
│  草稿生成器 FastAPI 服务     │  本地/云端部署
│  POST /api/draft/generate   │
│  • 接收 JSON 数据            │
│  • 下载素材                  │
│  • 生成草稿                  │
│  • 返回草稿信息              │
└─────────────────────────────┘
         │
         ▼
┌─────────────────┐
│    剪映草稿      │  用户在剪映中打开编辑
└─────────────────┘
```

### 核心优势

- ✅ **完全自动化** - 无需手动复制粘贴 JSON
- ✅ **实时反馈** - Coze Bot 返回草稿生成状态
- ✅ **灵活部署** - 支持本地或云端部署
- ✅ **安全可控** - 支持 Token 认证，保护 API 访问

## 前置准备

### 1. 确保已安装依赖

```bash
cd Coze2JianYing
pip install -r requirements.txt
```

### 2. 准备 Coze 账号

- 注册 [Coze 平台](https://www.coze.cn/) 账号
- 创建或准备使用的 Bot
- 获取 API Token（如需远程调用）

### 3. 确认剪映安装

- 确保已安装剪映专业版
- 确认草稿文件夹路径（通常在 `C:/Users/用户名/AppData/Local/JianyingPro/User Data/Projects/com.lveditor.draft`）

## 方式一：本地部署（推荐用于测试）

适合在本地电脑上测试和使用。

### 步骤 1：启动本地 API 服务

#### 方法 A：使用 GUI（最简单）

1. 运行草稿生成器 GUI：
   ```bash
   python app/main.py
   ```

2. 切换到"云端服务"标签页

3. 配置端口（默认 8000）

4. 点击"启动服务"按钮

5. 查看服务状态，确认显示"服务状态: 运行中"

#### 方法 B：使用命令行

```bash
python start_api.py
```

或使用 uvicorn 直接启动：

```bash
uvicorn app.api_main:app --host 127.0.0.1 --port 8000 --reload
```

### 步骤 2：验证服务运行

在浏览器中访问：

- API 文档（Swagger UI）: http://127.0.0.1:8000/docs
- 健康检查: http://127.0.0.1:8000/api/draft/health

### 步骤 3：配置内网穿透（如需 Coze 访问）

由于 Coze 需要访问公网 URL，云端服务需要通过内网穿透暴露。

#### 使用 ngrok（推荐）

1. 下载并安装 [ngrok](https://ngrok.com/)

2. 启动内网穿透：
   ```bash
   ngrok http 8000
   ```

3. 记录 ngrok 提供的公网 URL（例如：`https://abc123.ngrok.io`）

4. 这个 URL 将用于配置 Coze 插件

#### 其他内网穿透工具

- [localtunnel](https://localtunnel.github.io/www/)
- [Serveo](https://serveo.net/)
- [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)

### 步骤 4：获取 OpenAPI 规范

访问 http://127.0.0.1:8000/openapi.json 或通过 ngrok URL：

```bash
curl https://abc123.ngrok.io/openapi.json > openapi.json
```

保存此文件，后续在 Coze 中配置插件时需要。

## 方式二：云端部署（推荐用于生产）

适合长期使用和多人协作。

### 部署选项

#### 选项 A：部署到云服务器

1. **租用云服务器**（阿里云、腾讯云、AWS等）

2. **安装依赖**：
   ```bash
   # 更新系统
   sudo apt update && sudo apt upgrade -y
   
   # 安装 Python 3.12+
   sudo apt install python3.12 python3.12-venv -y
   
   # 克隆项目
   git clone https://github.com/Gardene-el/Coze2JianYing.git
   cd Coze2JianYing
   
   # 创建虚拟环境
   python3.12 -m venv venv
   source venv/bin/activate
   
   # 安装依赖
   pip install -r requirements.txt
   ```

3. **配置并启动服务**：
   ```bash
   # 使用 nohup 后台运行
   nohup uvicorn app.api_main:app --host 0.0.0.0 --port 8000 &
   
   # 或使用 systemd 服务（更专业）
   sudo nano /etc/systemd/system/coze2jianying.service
   ```

   systemd 服务配置示例：
   ```ini
   [Unit]
   Description=Coze2JianYing API Service
   After=network.target
   
   [Service]
   Type=simple
   User=your_username
   WorkingDirectory=/path/to/Coze2JianYing
   Environment="PATH=/path/to/Coze2JianYing/venv/bin"
   ExecStart=/path/to/Coze2JianYing/venv/bin/uvicorn app.api_main:app --host 0.0.0.0 --port 8000
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

   启动服务：
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start coze2jianying
   sudo systemctl enable coze2jianying  # 开机自启
   ```

4. **配置防火墙**：
   ```bash
   # 允许 8000 端口
   sudo ufw allow 8000/tcp
   ```

5. **配置域名和 SSL（可选但推荐）**：
   - 购买域名并解析到服务器 IP
   - 使用 Nginx 反向代理
   - 配置 Let's Encrypt SSL 证书

   Nginx 配置示例：
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

#### 选项 B：部署到 Serverless 平台

**Railway.app**（推荐，最简单）

1. 注册 [Railway.app](https://railway.app/)
2. 连接 GitHub 仓库
3. 选择 Coze2JianYing 项目
4. Railway 自动检测并部署
5. 获取公网 URL

**其他 Serverless 平台**：
- Render.com
- Fly.io
- Google Cloud Run
- AWS Lambda + API Gateway

### 获取云端 OpenAPI 规范

```bash
curl https://your-domain.com/openapi.json > openapi.json
```

## 在 Coze 中配置插件

### 步骤 1：创建云侧插件

1. 登录 [Coze 平台](https://www.coze.cn/)

2. 进入"扣子空间" → "资源库"

3. 点击右上角"+ 资源" → 选择"插件"

4. 插件创建方式选择：**"云侧插件 - 基于已有服务创建"**

5. 填写基本信息：
   - **插件名称**：Coze2JianYing 草稿生成器
   - **插件描述**：自动将 AI 生成的内容转换为剪映草稿
   - **图标**：上传项目 logo（可选）

### 步骤 2：配置 API

#### 方法 A：上传 OpenAPI 文件

1. 点击"导入 OpenAPI 规范"

2. 上传之前保存的 `openapi.json` 文件

3. 系统自动解析并生成工具列表

#### 方法 B：手动配置

1. 填写 **Base URL**：
   - 本地（通过 ngrok）：`https://abc123.ngrok.io`
   - 云端：`https://your-domain.com`

2. 添加工具 - **生成草稿**：
   - **工具名称**：`generate_draft`
   - **请求方法**：`POST`
   - **请求路径**：`/api/draft/generate`
   - **工具描述**：
     ```
     将 Coze 导出的 JSON 数据转换为剪映草稿文件。
     输入参数：
     - content: JSON 格式的草稿数据（字符串）
     - output_folder: 可选的输出路径
     返回草稿ID和文件夹路径信息。
     ```

3. 配置请求参数：
   - **content**
     - 类型：string
     - 必需：是
     - 描述：Coze 导出的 JSON 数据
   - **output_folder**
     - 类型：string
     - 必需：否
     - 描述：输出文件夹路径（可选）

4. 配置响应格式（可选）

### 步骤 3：配置认证（可选）

如需保护 API，添加认证：

1. 在插件配置中选择"认证方式"

2. 选择 **Bearer Token** 或 **API Key**

3. 配置 Token 值（需要在 API 服务端实现认证逻辑）

### 步骤 4：测试工具

1. 在插件配置页面，点击"测试工具"

2. 输入测试参数：
   ```json
   {
     "content": "{\"draft_id\": \"test-123\", \"project_name\": \"测试项目\"}",
     "output_folder": null
   }
   ```

3. 点击"执行"

4. 查看返回结果，确认工具正常工作

### 步骤 5：发布插件

1. 测试通过后，点击"发布"按钮

2. 选择发布范围：
   - **仅我可见**（私有）
   - **组织内可见**（团队）
   - **公开**（所有人）

3. 发布成功后，插件可在 Bot 中使用

## 工作流示例

### 基础工作流

```
1. 用户输入 → "帮我生成一个介绍中国美食的短视频"

2. Coze Bot 处理：
   - 使用 AI 生成脚本
   - 使用 DALL-E 或其他工具生成图片
   - 使用 TTS 生成配音
   - 组织时间轴和参数

3. 调用 Coze2JianYing 插件：
   - 准备 JSON 数据
   - 调用 generate_draft 工具
   - 传递 content 参数

4. 插件执行：
   - 接收 JSON
   - 下载素材
   - 生成草稿
   - 返回草稿信息

5. Bot 回复用户：
   - "草稿已生成！"
   - 显示草稿 ID
   - 显示文件夹路径
   - 提示在剪映中打开
```

### Coze 工作流节点配置示例

#### 节点 1：AI 内容生成

使用 Coze 内置的 AI 模型生成内容：

```
输入：用户需求
输出：视频脚本、素材需求
```

#### 节点 2：素材生成

调用图片生成、TTS等工具：

```
输入：脚本内容
输出：图片 URLs、音频 URLs
```

#### 节点 3：参数整理

使用 Coze 插件工具函数整理参数：

```
输入：素材 URLs、时间轴配置
输出：标准化 JSON
```

#### 节点 4：调用草稿生成

调用 Coze2JianYing 插件：

```
工具：generate_draft
参数：
  content: {{步骤3的JSON输出}}
  output_folder: null
```

#### 节点 5：结果反馈

格式化 Bot 回复：

```
输入：草稿生成结果
输出：友好的用户提示
```

## API 端点详细说明

### POST /api/draft/generate

生成剪映草稿的核心端点。

**请求示例**：

```bash
curl -X POST "http://your-domain.com/api/draft/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "{\"draft_id\": \"test-123\", \"project_name\": \"我的项目\", \"tracks\": [...]}",
    "output_folder": null
  }'
```

**响应示例**：

```json
{
  "status": "success",
  "message": "成功生成 1 个草稿",
  "draft_count": 1,
  "drafts": [
    {
      "draft_id": "12345678-1234-1234-1234-123456789abc",
      "project_name": "我的项目",
      "folder_path": "C:/Users/.../com.lveditor.draft/12345678-..."
    }
  ],
  "timestamp": "2025-11-04T08:00:00"
}
```

### GET /api/draft/status/{draft_id}

查询草稿生成状态。

**请求示例**：

```bash
curl "http://your-domain.com/api/draft/status/12345678-1234-1234-1234-123456789abc"
```

### GET /api/draft/list

列出所有已生成的草稿。

**请求示例**：

```bash
curl "http://your-domain.com/api/draft/list?skip=0&limit=10"
```

### GET /api/draft/health

健康检查端点，用于监控服务状态。

**响应示例**：

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-04T08:00:00",
  "services": {
    "draft_generator": true,
    "material_downloader": true,
    "jianying_folder_detected": true
  }
}
```

## 常见问题

### 1. Coze 无法访问云端服务

**原因**：Coze 只能访问公网 URL

**解决方案**：
- 使用内网穿透（ngrok等）
- 或部署到云服务器

### 2. API 调用超时

**原因**：草稿生成需要下载素材，可能耗时较长

**解决方案**：
- 优化素材大小
- 增加 Coze 工具调用超时时间
- 考虑使用异步处理（后台任务）

### 3. 找不到剪映文件夹

**原因**：API 服务无法检测到剪映安装路径

**解决方案**：
- 确认剪映专业版已安装
- 在请求中明确指定 `output_folder` 参数
- 检查文件夹权限

### 4. 素材下载失败

**原因**：网络问题或 URL 过期

**解决方案**：
- 检查网络连接
- 确认素材 URL 有效性
- 使用稳定的素材托管服务

### 5. JSON 格式错误

**原因**：Coze 传递的 JSON 格式不正确

**解决方案**：
- 使用 Coze 插件工具函数生成标准 JSON
- 参考 `data_structures/draft_generator_interface/` 中的数据模型
- 在 Coze 工作流中添加 JSON 验证步骤

### 6. 权限问题

**原因**：API 服务没有写入权限

**解决方案**：
- 检查输出文件夹权限
- 以正确的用户身份运行服务
- 使用默认检测的剪映文件夹

## 进阶配置

### 添加认证保护

修改 `app/api_main.py`，添加简单的 Token 认证：

```python
from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    # 验证 token（示例）
    if token != "your-secret-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return token

# 在路由中使用
@router.post("/generate", dependencies=[Security(verify_token)])
async def generate_draft(...):
    ...
```

### 配置 CORS

如需从不同域名访问 API，调整 CORS 配置：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.coze.cn", "https://api.coze.cn"],  # 只允许 Coze
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 添加日志记录

使用项目内置的日志系统记录 API 调用：

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)

@router.post("/generate")
async def generate_draft(request: DraftGenerateRequest):
    logger.info(f"收到草稿生成请求: {request.content[:100]}...")
    # ...
```

### 性能优化

1. **使用异步任务**：
   ```python
   from fastapi import BackgroundTasks
   
   @router.post("/generate")
   async def generate_draft(
       request: DraftGenerateRequest,
       background_tasks: BackgroundTasks
   ):
       # 立即返回，后台处理
       background_tasks.add_task(process_draft, request)
       return {"status": "processing", "message": "草稿正在生成中..."}
   ```

2. **添加缓存**：
   - 缓存已下载的素材
   - 缓存 OpenAPI 规范

3. **使用连接池**：
   - 优化 HTTP 请求性能

## 相关资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Coze 开发者文档](https://www.coze.cn/open/docs/developer_guides)
- [OpenAPI 规范](https://swagger.io/specification/)
- [ngrok 文档](https://ngrok.com/docs)

---

**需要帮助？**

- 提交 [GitHub Issue](https://github.com/Gardene-el/Coze2JianYing/issues)
- 查看 [完整项目文档](../README.md)
- 参考 [API 调查报告](./COZE_API_GATEWAY_INVESTIGATION.md)
