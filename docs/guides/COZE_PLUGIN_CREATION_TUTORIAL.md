# 使用 OpenAPI 规范在 Coze 创建插件 - 图文教程

本教程演示如何使用生成的 `openapi.json` 文件在 Coze 平台创建"基于已有服务"的云侧插件。

## 📋 前置准备

1. ✅ 已生成 API 规范文件：`python scripts/export_api_specs.py`
2. ✅ API 服务已部署（本地或云端）
3. ✅ 如本地部署，已配置内网穿透（如 ngrok）
4. ✅ 拥有 Coze 平台账号

## 🚀 创建插件步骤

### 步骤 1: 访问 Coze 平台

1. 打开浏览器，访问 [https://www.coze.cn/](https://www.coze.cn/)
2. 登录你的账号
3. 进入"扣子空间"

### 步骤 2: 创建新插件

1. 点击左侧导航栏的"资源库"
2. 点击右上角的"+ 资源"按钮
3. 在弹出菜单中选择"插件"

### 步骤 3: 选择创建方式

在"创建插件"对话框中：

1. 选择创建方式：**"云侧插件 - 基于已有服务创建"**
2. 点击"下一步"或"确定"

### 步骤 4: 填写基本信息

填写插件的基本信息：

- **插件名称**: `Coze2JianYing API`（或自定义名称）
- **插件描述**: 
  ```
  Coze剪映草稿生成器 API，提供完整的剪映草稿创建和管理功能。
  支持创建草稿、添加轨道、添加各类素材片段（视频、音频、图片、文本等），
  以及全自动生成剪映草稿文件。
  ```
- **图标**: 可选，上传项目 logo 或使用默认图标

### 步骤 5: 导入 OpenAPI 规范

这是最关键的一步：

1. 在插件配置页面，找到"导入 API 规范"或"导入 OpenAPI"选项
2. 点击"上传文件"或"选择文件"
3. 选择 `api_specs/openapi.json` 文件
4. 点击"上传"或"导入"

**预期结果**：
- Coze 会自动解析文件
- 显示检测到的 API 端点数量（应该是 31 个）
- 列出所有工具函数

### 步骤 6: 配置服务地址

上传 OpenAPI 文件后，需要配置实际的服务地址：

#### 本地部署（使用 ngrok）

```
Base URL: https://abc123.ngrok.io
```

**获取 ngrok URL**：
```bash
# 终端 1: 启动 API 服务
python start_api.py

# 终端 2: 启动 ngrok
ngrok http 8000

# 复制 ngrok 显示的 Forwarding URL
# 例如: https://abc123.ngrok-free.app
```

#### 云端部署

```
Base URL: https://your-domain.com
```

**示例**：
- 阿里云: `https://api.example.com`
- Railway: `https://coze2jianying-production.up.railway.app`
- Vercel: `https://coze2jianying.vercel.app`

### 步骤 7: 查看导入的工具

导入成功后，你应该能看到以下工具分组：

#### 草稿操作工具组（~10 个工具）
- `create_draft` - 创建草稿
- `add_track_to_draft` - 添加轨道
- `add_segment_to_draft` - 添加片段
- `add_global_effect` - 添加全局特效
- `add_global_filter` - 添加全局滤镜
- `save_draft` - 保存草稿
- `get_draft_status` - 查询草稿状态
- 等...

#### 片段管理工具组（~20 个工具）
- `create_audio_segment` - 创建音频片段
- `create_video_segment` - 创建视频片段
- `create_text_segment` - 创建文本片段
- `create_sticker_segment` - 创建贴纸片段
- `create_effect_segment` - 创建特效片段
- `create_filter_segment` - 创建滤镜片段
- `add_audio_effect` - 添加音频特效
- `set_audio_volume` - 设置音频音量
- 等...

### 步骤 8: 测试工具函数

在发布插件前，必须测试关键工具：

#### 测试 create_draft

1. 选择 `create_draft` 工具
2. 点击"测试"按钮
3. 填写测试参数：
   ```json
   {
     "draft_name": "测试项目",
     "width": 1920,
     "height": 1080,
     "fps": 30
   }
   ```
4. 点击"执行"
5. 查看返回结果：
   ```json
   {
     "draft_id": "12345678-1234-1234-1234-123456789abc",
     "success": true,
     "message": "草稿创建成功"
   }
   ```
6. **保存返回的 `draft_id`**，用于后续测试

#### 测试 create_audio_segment

1. 选择 `create_audio_segment` 工具
2. 填写测试参数：
   ```json
   {
     "material_url": "https://example.com/audio.mp3",
     "time_range": {
       "start": 0,
       "end": 5000
     },
     "volume": 1.0,
     "speed": 1.0
   }
   ```
3. 点击"执行"
4. 保存返回的 `segment_id`

#### 测试 add_track_to_draft

1. 选择 `add_track_to_draft` 工具
2. 填写测试参数（使用之前保存的 draft_id 和 segment_id）：
   ```json
   {
     "draft_id": "12345678-1234-1234-1234-123456789abc",
     "track_type": "audio",
     "segment_ids": ["segment_id_from_previous_step"]
   }
   ```
3. 点击"执行"

### 步骤 9: 配置认证（可选）

如果你的 API 需要认证：

1. 在插件配置页面找到"认证"或"Security"选项
2. 选择认证类型：
   - **Bearer Token**: 适合 JWT 认证
   - **API Key**: 适合简单的 API Key 认证
   - **OAuth 2.0**: 适合复杂的第三方认证
3. 配置认证参数
4. 重新测试工具确认认证生效

**注意**：当前 Coze2JianYing API 默认不需要认证，此步骤可跳过。

### 步骤 10: 发布插件

所有测试通过后：

1. 点击"发布"按钮
2. 选择发布范围：
   - **仅我可见**：私有使用
   - **组织内可见**：团队共享
   - **公开**：所有人可用
3. 确认发布

🎉 **恭喜！插件创建成功！**

## 🔧 在 Bot 中使用插件

### 创建测试 Bot

1. 返回 Coze 主页
2. 点击"创建 Bot"
3. 填写 Bot 基本信息

### 添加插件

1. 在 Bot 编辑页面，点击"添加工具"
2. 选择"插件"
3. 找到并添加你刚创建的插件
4. 选择要使用的工具函数

### 测试工作流

创建一个简单的工作流测试插件：

```
1. 用户输入: "创建一个 1920x1080 的视频草稿"

2. AI 解析: 提取参数
   - draft_name: "用户视频"
   - width: 1920
   - height: 1080
   - fps: 30

3. 调用插件: create_draft
   - 传入参数
   - 获取 draft_id

4. 返回结果: "草稿已创建！ID: {draft_id}"
```

## 📝 常见问题

### Q1: 上传 OpenAPI 文件后显示"解析失败"？

**可能原因**：
- 文件格式错误
- OpenAPI 版本不支持
- JSON 语法错误

**解决方案**：
1. 重新生成文件：`python scripts/export_api_specs.py`
2. 验证 JSON 格式：使用 [JSONLint](https://jsonlint.com/) 验证
3. 尝试使用 `swagger.json`（Swagger 2.0）替代

### Q2: 工具测试时返回 "Network Error" 或 "Connection Refused"？

**可能原因**：
- API 服务未启动
- Base URL 配置错误
- 防火墙阻止
- ngrok 隧道已过期（免费版 8 小时）

**解决方案**：
1. 确认 API 服务运行：`curl http://localhost:8000/`
2. 重启 ngrok 获取新 URL
3. 更新插件配置中的 Base URL
4. 检查防火墙设置

### Q3: 部分工具显示但无法使用？

**可能原因**：
- 工具参数配置错误
- 请求格式不匹配
- API 端点不存在

**解决方案**：
1. 访问 API 文档：`http://localhost:8000/docs`
2. 手动测试该端点
3. 检查 OpenAPI 文件中的定义
4. 查看 API 服务日志

### Q4: 如何更新插件配置？

当 API 有更新时：

1. 重新生成 OpenAPI 文件
2. 进入插件编辑页面
3. 重新上传新的 `openapi.json`
4. 或手动修改工具配置
5. 重新测试
6. 发布更新

## 🎯 最佳实践

### 1. 使用环境变量

在测试和生产环境使用不同的 Base URL：

```
测试: https://test-abc123.ngrok.io
生产: https://api.your-domain.com
```

### 2. 版本管理

在插件描述中注明版本：

```
Coze2JianYing API v1.0.0
最后更新: 2024-11-08
```

### 3. 错误处理

在 Bot 工作流中添加错误处理：

```
如果工具调用失败:
  - 记录错误
  - 返回友好提示
  - 提供重试选项
```

### 4. 日志监控

查看 API 服务日志，监控调用情况：

```bash
# 查看实时日志
tail -f logs/api.log

# 或在代码中添加日志
logger.info(f"Coze 调用: {endpoint} - 参数: {params}")
```

## 📚 相关资源

- [API 集合协议文件详解](API_COLLECTION_PROTOCOLS_GUIDE.md)
- [Coze 集成指南](COZE_INTEGRATION_GUIDE.md)
- [API 快速开始](../../API_QUICKSTART.md)
- [OpenAPI 规范](https://spec.openapis.org/oas/latest.html)
- [Coze 开发者文档](https://www.coze.cn/open/docs/)

## 🆘 需要帮助？

如遇到问题，请：

1. 查看本教程的常见问题部分
2. 查阅 [API 集合协议文件详解](API_COLLECTION_PROTOCOLS_GUIDE.md)
3. 提交 [GitHub Issue](https://github.com/Gardene-el/Coze2JianYing/issues)
4. 附上完整的错误信息和日志

---

**完成本教程后，你应该能够**：
- ✅ 成功在 Coze 创建基于 API 的插件
- ✅ 配置和测试所有工具函数
- ✅ 在 Bot 中集成和使用插件
- ✅ 处理常见的集成问题

**下一步**：创建完整的 AI 工作流，实现从用户输入到生成剪映草稿的全自动流程！
