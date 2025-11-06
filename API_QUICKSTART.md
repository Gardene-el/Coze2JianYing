# API 接口实现 - 快速开始指南

本文档提供快速开始指南，帮助你快速了解和使用新的 API 接口系统。

## 概览

本次实现完成了 Issue #4 "接口设计和实现"，提供了完整的 API 架构来解决 Coze 与本地草稿生成器的通信问题。

### 核心特性

✅ **UUID 管理系统** - 解决变量作用域问题  
✅ **素材状态追踪** - 管理素材下载状态  
✅ **统一接口设计** - API 和 Coze 插件保持一致  
✅ **完整数据验证** - Pydantic 模型验证  
✅ **详细文档** - 设计、使用、实施全覆盖

## 快速开始

### 1. 启动 API 服务

```bash
# 确保在项目根目录
cd Coze2JianYing

# 启动 API 服务
python start_api.py
```

服务将运行在 `http://localhost:8000`

### 2. 访问 API 文档

打开浏览器访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. 测试 API

使用 Python 测试：

```python
import requests

# 创建草稿
response = requests.post("http://localhost:8000/api/draft/create", json={
    "draft_name": "测试项目",
    "width": 1920,
    "height": 1080,
    "fps": 30
})

draft_id = response.json()["draft_id"]
print(f"草稿 ID: {draft_id}")

# 添加图片
response = requests.post(
    f"http://localhost:8000/api/draft/{draft_id}/add-images",
    json={
        "draft_id": draft_id,
        "images": [{
            "material_url": "https://example.com/image.jpg",
            "time_range": {"start": 0, "end": 3000}
        }]
    }
)

print(response.json())
```

## 主要 API 端点

### 草稿管理

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/draft/create` | POST | 创建新草稿 |
| `/api/draft/{id}/detail` | GET | 查询草稿详情 |

### 素材管理

| 端点 | 方法 | 功能 |
|------|------|------|
| `/api/draft/{id}/add-videos` | POST | 添加视频片段 |
| `/api/draft/{id}/add-audios` | POST | 添加音频片段 |
| `/api/draft/{id}/add-images` | POST | 添加图片片段 |
| `/api/draft/{id}/add-captions` | POST | 添加字幕片段 |

## 文档索引

### 核心文档

1. **[API 设计文档](./docs/API_DESIGN.md)** 📐
   - 完整的架构设计
   - 接口规范定义
   - 两种通信方式详解
   - 素材下载管理方案

2. **[API 使用示例](./docs/API_USAGE_EXAMPLES.md)** 💡
   - Python 代码示例
   - curl 命令示例
   - Coze 工作流示例
   - 错误处理示例

3. **[实施路线图](./docs/API_IMPLEMENTATION_ROADMAP.md)** 🗺️
   - 已完成功能清单
   - 待实现功能计划
   - 技术债务说明
   - 性能优化计划

4. **[问题解决方案](./ISSUE_4_SOLUTION.md)** ✅
   - Issue #4 完整回答
   - 三个问题的解决方案
   - 实现成果总结
   - 技术架构图

### 代码文档

- `app/schemas/material_schemas.py` - 数据模型定义
- `app/utils/draft_state_manager.py` - 状态管理器
- `app/api/material_routes.py` - API 路由实现

## 工作流程

### 完整工作流

```
1. 创建草稿
   POST /api/draft/create
   → 返回 draft_id (UUID)

2. 添加素材
   POST /api/draft/{draft_id}/add-videos
   POST /api/draft/{draft_id}/add-audios
   POST /api/draft/{draft_id}/add-images
   POST /api/draft/{draft_id}/add-captions

3. 查询状态
   GET /api/draft/{draft_id}/detail
   → 检查下载状态

4. 生成草稿（待实现）
   POST /api/draft/{draft_id}/generate
   → 生成剪映草稿文件
```

## 数据格式示例

### 创建草稿

**请求**：
```json
{
  "draft_name": "我的视频",
  "width": 1920,
  "height": 1080,
  "fps": 30
}
```

**响应**：
```json
{
  "draft_id": "12345678-1234-1234-1234-123456789abc",
  "success": true,
  "message": "草稿创建成功"
}
```

### 添加视频

**请求**：
```json
{
  "draft_id": "uuid",
  "videos": [
    {
      "material_url": "https://example.com/video.mp4",
      "time_range": {"start": 0, "end": 5000},
      "position_x": 0.0,
      "position_y": 0.0,
      "scale_x": 1.0,
      "scale_y": 1.0,
      "volume": 1.0,
      "speed": 1.0
    }
  ]
}
```

**响应**：
```json
{
  "success": true,
  "message": "成功添加 1 个视频片段",
  "segments_added": 1,
  "download_status": {
    "total": 1,
    "completed": 0,
    "failed": 0,
    "pending": 1
  }
}
```

## 技术栈

- **FastAPI** - Web 框架
- **Pydantic** - 数据验证
- **Uvicorn** - ASGI 服务器
- **Python 3.8+** - 运行环境

## 项目结构

```
Coze2JianYing/
├── app/
│   ├── api/
│   │   ├── material_routes.py  # 素材管理 API ✨ 新增
│   │   ├── draft_routes.py     # 草稿生成 API
│   │   └── router.py           # 路由汇总 ✨ 更新
│   ├── schemas/
│   │   ├── material_schemas.py # 数据模型 ✨ 新增
│   │   └── draft_schemas.py    # 草稿模型
│   └── utils/
│       ├── draft_state_manager.py  # 状态管理器 ✨ 新增
│       ├── material_manager.py     # 素材管理器
│       └── draft_generator.py      # 草稿生成器
├── docs/
│   ├── API_DESIGN.md              # API 设计 ✨ 新增
│   ├── API_USAGE_EXAMPLES.md      # 使用示例 ✨ 新增
│   └── API_IMPLEMENTATION_ROADMAP.md  # 路线图 ✨ 新增
└── ISSUE_4_SOLUTION.md            # 解决方案 ✨ 新增
```

## 常见问题

### Q: 如何查看素材下载状态？

A: 调用 `GET /api/draft/{draft_id}/detail` 端点，查看 `download_status` 字段。

### Q: 支持哪些素材格式？

A: 支持所有 pyJianYingDraft 支持的格式，包括常见的视频（mp4、mov）、音频（mp3、wav）、图片（jpg、png）格式。

### Q: API 可以远程访问吗？

A: 可以。启动时绑定到 `0.0.0.0:8000`，配置防火墙规则即可。建议添加认证机制。

### Q: 如何在 Coze 中使用？

A: 两种方式：
1. **手动模式** - 使用 Coze IDE 插件，复制 JSON 到草稿生成器
2. **自动模式** - 在 Coze 中配置 API 服务地址，自动调用 API

### Q: 如何处理素材下载失败？

A: 当前版本会记录失败状态，待异步下载队列实现后将支持自动重试。

## 下一步计划

### 高优先级
- [ ] 实现异步素材下载队列
- [ ] 实现草稿生成 API 端点
- [ ] 编写集成测试

### 中优先级
- [ ] 更新 Coze IDE 插件
- [ ] 添加 API 认证
- [ ] 完善错误处理

### 低优先级
- [ ] 批量操作支持
- [ ] 数据库持久化
- [ ] WebSocket 实时推送

## 贡献

欢迎贡献！如果你有任何建议或发现问题，请：

1. 查看 [API 设计文档](./docs/API_DESIGN.md)
2. 阅读 [实施路线图](./docs/API_IMPLEMENTATION_ROADMAP.md)
3. 提交 Issue 或 Pull Request

## 许可证

本项目采用 GPL-3.0 许可证。详见 [LICENSE](./LICENSE) 文件。

## 相关链接

- [项目主页](https://github.com/Gardene-el/Coze2JianYing)
- [Issue #4](https://github.com/Gardene-el/Coze2JianYing/issues/4)
- [pyJianYingDraft](https://github.com/GuanYixuan/pyJianYingDraft)
- [Coze 平台](https://www.coze.cn/)

---

**快速访问**：
- 📖 [完整 API 文档](http://localhost:8000/docs)
- 🎯 [API 设计文档](./docs/API_DESIGN.md)
- 💡 [使用示例](./docs/API_USAGE_EXAMPLES.md)
- ✅ [解决方案总结](./ISSUE_4_SOLUTION.md)
