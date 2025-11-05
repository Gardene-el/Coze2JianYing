# API 使用示例

本文档提供 Coze2JianYing API 的完整使用示例，展示如何通过两种方式（Coze IDE 插件和 API 服务）与草稿生成器通信。

## 前置准备

### 方式一：Coze IDE 插件（手动模式）

1. 在 Coze 平台创建云侧插件
2. 复制 `coze_plugin/tools/` 中的工具函数代码
3. 在 Coze 工作流中调用工具函数
4. 手动复制输出的 JSON 到草稿生成器

### 方式二：API 服务（自动模式）

1. 启动草稿生成器的 API 服务：
```bash
python start_api.py
```

2. API 服务会运行在 `http://localhost:8000`

3. 访问 API 文档：
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## 完整工作流示例

### 示例 1：创建简单的图片+音频视频

这个示例展示如何创建一个包含背景音乐和图片的简单视频。

#### 使用 Python 请求 API

```python
import requests
import json

# API 基础地址
API_BASE = "http://localhost:8000"

# 步骤 1: 创建草稿
print("步骤 1: 创建草稿")
create_response = requests.post(
    f"{API_BASE}/api/draft/create",
    json={
        "draft_name": "我的图片视频",
        "width": 1920,
        "height": 1080,
        "fps": 30
    }
)
create_data = create_response.json()
draft_id = create_data["draft_id"]
print(f"草稿 ID: {draft_id}")

# 步骤 2: 添加背景音乐
print("\n步骤 2: 添加背景音乐")
audio_response = requests.post(
    f"{API_BASE}/api/draft/{draft_id}/add-audios",
    json={
        "draft_id": draft_id,
        "audios": [
            {
                "material_url": "https://example.com/background-music.mp3",
                "time_range": {"start": 0, "end": 15000},  # 15秒
                "volume": 0.8,
                "fade_in": 1000,
                "fade_out": 1000
            }
        ]
    }
)
print(f"音频添加结果: {audio_response.json()['message']}")

# 步骤 3: 添加图片序列
print("\n步骤 3: 添加图片序列")
images = [
    {
        "material_url": "https://example.com/image1.jpg",
        "time_range": {"start": 0, "end": 3000},
        "fit_mode": "fill",
        "background_color": "#000000"
    },
    {
        "material_url": "https://example.com/image2.jpg",
        "time_range": {"start": 3000, "end": 6000},
        "fit_mode": "fill",
        "background_color": "#000000"
    },
    {
        "material_url": "https://example.com/image3.jpg",
        "time_range": {"start": 6000, "end": 9000},
        "fit_mode": "fill",
        "background_color": "#000000"
    },
]

image_response = requests.post(
    f"{API_BASE}/api/draft/{draft_id}/add-images",
    json={
        "draft_id": draft_id,
        "images": images
    }
)
print(f"图片添加结果: {image_response.json()['message']}")

# 步骤 4: 添加字幕
print("\n步骤 4: 添加字幕")
captions = [
    {
        "text": "欢迎观看",
        "time_range": {"start": 0, "end": 3000},
        "font_family": "黑体",
        "font_size": 48.0,
        "color": "#FFFFFF",
        "position_y": -200.0,  # 屏幕下方
        "bold": True
    },
    {
        "text": "我的相册",
        "time_range": {"start": 3000, "end": 6000},
        "font_family": "黑体",
        "font_size": 48.0,
        "color": "#FFFFFF",
        "position_y": -200.0,
        "bold": True
    }
]

caption_response = requests.post(
    f"{API_BASE}/api/draft/{draft_id}/add-captions",
    json={
        "draft_id": draft_id,
        "captions": captions
    }
)
print(f"字幕添加结果: {caption_response.json()['message']}")

# 步骤 5: 查询草稿详情
print("\n步骤 5: 查询草稿详情")
detail_response = requests.get(f"{API_BASE}/api/draft/{draft_id}/detail")
detail = detail_response.json()
print(f"项目名称: {detail['project_name']}")
print(f"轨道数量: {detail['tracks_count']}")
print(f"素材数量: {detail['materials_count']}")
print(f"下载状态: {detail['download_status']}")

print("\n✅ 草稿创建完成！")
print(f"草稿 ID: {draft_id}")
```

#### 使用 curl 命令

```bash
# 步骤 1: 创建草稿
curl -X POST http://localhost:8000/api/draft/create \
  -H "Content-Type: application/json" \
  -d '{
    "draft_name": "我的图片视频",
    "width": 1920,
    "height": 1080,
    "fps": 30
  }'

# 保存返回的 draft_id
DRAFT_ID="<返回的UUID>"

# 步骤 2: 添加背景音乐
curl -X POST "http://localhost:8000/api/draft/${DRAFT_ID}/add-audios" \
  -H "Content-Type: application/json" \
  -d '{
    "draft_id": "'$DRAFT_ID'",
    "audios": [{
      "material_url": "https://example.com/background-music.mp3",
      "time_range": {"start": 0, "end": 15000},
      "volume": 0.8,
      "fade_in": 1000,
      "fade_out": 1000
    }]
  }'

# 步骤 3: 添加图片
curl -X POST "http://localhost:8000/api/draft/${DRAFT_ID}/add-images" \
  -H "Content-Type: application/json" \
  -d '{
    "draft_id": "'$DRAFT_ID'",
    "images": [{
      "material_url": "https://example.com/image1.jpg",
      "time_range": {"start": 0, "end": 3000},
      "fit_mode": "fill"
    }]
  }'

# 步骤 4: 查询详情
curl http://localhost:8000/api/draft/${DRAFT_ID}/detail
```

### 示例 2：创建视频剪辑

这个示例展示如何创建一个包含多个视频片段的视频。

```python
import requests

API_BASE = "http://localhost:8000"

# 创建草稿
response = requests.post(f"{API_BASE}/api/draft/create", json={
    "draft_name": "视频剪辑",
    "width": 1920,
    "height": 1080,
    "fps": 30
})
draft_id = response.json()["draft_id"]

# 添加视频片段
videos = [
    {
        "material_url": "https://example.com/video1.mp4",
        "time_range": {"start": 0, "end": 10000},
        "material_range": {"start": 5000, "end": 15000},  # 从视频的5秒开始，取10秒
        "volume": 1.0,
        "speed": 1.0
    },
    {
        "material_url": "https://example.com/video2.mp4",
        "time_range": {"start": 10000, "end": 20000},
        "volume": 0.8,  # 第二段音量降低
        "speed": 1.2    # 加速播放
    }
]

response = requests.post(
    f"{API_BASE}/api/draft/{draft_id}/add-videos",
    json={"draft_id": draft_id, "videos": videos}
)
print(response.json())
```

### 示例 3：在 Coze 工作流中使用

#### 配置 Coze 插件（基于服务）

1. 在 Coze 平台创建"云侧插件 - 基于已有服务创建"
2. 配置 OpenAPI 规范（可从 `http://localhost:8000/openapi.json` 获取）
3. 设置服务地址：`http://your-server:8000`

#### 工作流示例

```
【开始】
    ↓
【AI 生成内容】
  - 生成图片列表
  - 生成字幕文本
    ↓
【调用创建草稿 API】
  POST /api/draft/create
    ↓
【获取 draft_id】
  保存到变量 {{draft_id}}
    ↓
【调用添加图片 API】
  POST /api/draft/{{draft_id}}/add-images
    ↓
【调用添加字幕 API】
  POST /api/draft/{{draft_id}}/add-captions
    ↓
【调用添加音频 API】
  POST /api/draft/{{draft_id}}/add-audios
    ↓
【查询下载状态】
  GET /api/draft/{{draft_id}}/detail
    ↓
【生成草稿】
  调用草稿生成器的 generate 接口
    ↓
【结束】
  返回草稿路径
```

## Coze IDE 插件使用示例

### 创建草稿

```python
# 在 Coze 工作流中
create_result = call_tool('create_draft', {
    'draft_name': '我的视频项目',
    'width': 1920,
    'height': 1080,
    'fps': 30
})

# 获取 UUID
draft_id = create_result['draft_id']
# 输出: "abc12345-def6-789a-bcde-f123456789ab"
```

### 添加图片

```python
# 生成图片配置
image_config = call_tool('make_image_info', {
    'image_url': 'https://example.com/image.jpg',
    'start': 0,
    'end': 3000,
    'fit_mode': 'fill'
})

# 添加到草稿
add_result = call_tool('add_images', {
    'draft_id': draft_id,
    'images': image_config
})
```

### 导出草稿

```python
# 导出单个草稿
export_result = call_tool('export_drafts', {
    'draft_ids': draft_id,
    'remove_temp_files': True
})

# 获取 JSON 数据
draft_json = export_result['draft_data']

# 用户复制 draft_json 到草稿生成器
```

## 错误处理

### API 错误响应

所有 API 端点在出错时返回标准错误格式：

```json
{
  "detail": "错误消息",
  "status_code": 400
}
```

### 常见错误码

- `404 Not Found`: 草稿不存在
- `400 Bad Request`: 请求参数无效
- `500 Internal Server Error`: 服务器内部错误

### Python 错误处理示例

```python
import requests

try:
    response = requests.post(
        f"{API_BASE}/api/draft/create",
        json={"draft_name": "测试"},
        timeout=10
    )
    response.raise_for_status()
    data = response.json()
    print(f"成功: {data}")
    
except requests.exceptions.HTTPError as e:
    print(f"HTTP 错误: {e}")
    print(f"响应内容: {e.response.text}")
    
except requests.exceptions.ConnectionError:
    print("连接错误: 无法连接到 API 服务")
    
except requests.exceptions.Timeout:
    print("超时错误: 请求超时")
    
except Exception as e:
    print(f"未知错误: {e}")
```

## 高级用法

### 批量处理

```python
import requests
from concurrent.futures import ThreadPoolExecutor

API_BASE = "http://localhost:8000"

def create_draft_for_image_set(image_urls):
    """为一组图片创建草稿"""
    # 创建草稿
    response = requests.post(f"{API_BASE}/api/draft/create", json={
        "draft_name": f"图片集_{len(image_urls)}张"
    })
    draft_id = response.json()["draft_id"]
    
    # 添加图片
    images = [
        {
            "material_url": url,
            "time_range": {"start": i * 3000, "end": (i + 1) * 3000}
        }
        for i, url in enumerate(image_urls)
    ]
    
    requests.post(
        f"{API_BASE}/api/draft/{draft_id}/add-images",
        json={"draft_id": draft_id, "images": images}
    )
    
    return draft_id

# 批量处理多组图片
image_sets = [
    ["img1.jpg", "img2.jpg", "img3.jpg"],
    ["img4.jpg", "img5.jpg", "img6.jpg"],
    ["img7.jpg", "img8.jpg", "img9.jpg"]
]

with ThreadPoolExecutor(max_workers=3) as executor:
    draft_ids = list(executor.map(create_draft_for_image_set, image_sets))

print(f"创建了 {len(draft_ids)} 个草稿")
```

### 自定义下载回调

```python
import requests
import time

def wait_for_download_complete(draft_id, timeout=60):
    """等待素材下载完成"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = requests.get(f"{API_BASE}/api/draft/{draft_id}/detail")
        detail = response.json()
        download_status = detail["download_status"]
        
        if download_status["pending"] == 0:
            if download_status["failed"] > 0:
                print(f"警告: {download_status['failed']} 个素材下载失败")
            print("所有素材下载完成")
            return True
        
        print(f"下载进度: {download_status['completed']}/{download_status['total']}")
        time.sleep(2)
    
    print("下载超时")
    return False

# 使用示例
draft_id = create_and_add_materials()
if wait_for_download_complete(draft_id):
    print("可以开始生成草稿了")
```

## 测试和调试

### 使用 Swagger UI 测试

1. 访问 `http://localhost:8000/docs`
2. 点击任意端点
3. 点击 "Try it out"
4. 填写参数
5. 点击 "Execute"
6. 查看响应结果

### 使用 Postman 测试

1. 导入 OpenAPI 规范：`http://localhost:8000/openapi.json`
2. 自动生成所有 API 端点
3. 设置环境变量：`API_BASE = http://localhost:8000`
4. 创建测试集合

### 日志查看

API 服务的日志会输出到控制台和日志文件：

```bash
# 查看实时日志
tail -f logs/api_server.log

# 查看错误日志
grep ERROR logs/api_server.log
```

## 部署建议

### 本地开发

```bash
python start_api.py
```

### 生产部署

```bash
# 使用 gunicorn
gunicorn app.api_main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# 使用 Docker
docker build -t coze2jianying-api .
docker run -p 8000:8000 coze2jianying-api
```

### 内网穿透（用于 Coze 调用本地服务）

```bash
# 使用 ngrok
ngrok http 8000

# 使用 frp
./frpc -c frpc.ini
```

## 常见问题

### Q: 如何知道素材下载是否完成？

A: 调用 `/api/draft/{draft_id}/detail` 端点查看 `download_status`。

### Q: 可以同时添加多个轨道吗？

A: 可以。每次调用 `add-*` 端点都会创建一个新轨道。

### Q: 如何删除已创建的草稿？

A: 当前版本需要手动删除 `/tmp/jianying_assistant/drafts/{uuid}` 目录，未来会添加删除 API。

### Q: API 支持远程调用吗？

A: 支持。启动时绑定到 `0.0.0.0`，配置防火墙规则即可远程访问。建议添加认证机制。

## 更多资源

- [完整 API 设计文档](./API_DESIGN.md)
- [API 参考文档](http://localhost:8000/docs)
- [项目 README](../README.md)
- [开发路线图](./guides/DEVELOPMENT_ROADMAP.md)
