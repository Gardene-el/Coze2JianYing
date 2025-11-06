# ngrok 集成使用指南

## 概述

本项目集成了 ngrok 内网穿透功能，允许将本地运行的 FastAPI 服务暴露到公网，以便 Coze 平台可以访问和调用。

## 功能特性

### 1. NgrokManager 工具类

位于 `app/utils/ngrok_manager.py`，提供完整的 ngrok 隧道管理功能：

- **隧道管理**: 启动、停止、监控 ngrok 隧道
- **配置选项**: 支持 authtoken 设置和区域选择
- **状态监控**: 实时监控隧道状态和连接
- **自动清理**: 应用退出时自动清理资源

### 2. 云端服务标签页集成

在 GUI 的"云端服务"标签页中提供完整的 ngrok 控制界面：

#### ngrok 配置区域
- **Authtoken 输入**: 支持显示/隐藏敏感信息
- **区域选择**: 支持多个 ngrok 服务器区域
  - `us` - 美国 (默认)
  - `eu` - 欧洲
  - `ap` - 亚太
  - `au` - 澳大利亚
  - `sa` - 南美
  - `jp` - 日本
  - `in` - 印度

#### ngrok 状态显示
- **状态指示器**: 红/绿灯显示运行状态
- **状态文本**: 实时显示当前状态
- **公网地址**: 显示 ngrok 生成的公网 URL
- **一键复制**: 快速复制 URL 到剪贴板

#### ngrok 控制
- **启动按钮**: 启动 ngrok 隧道（需先启动 FastAPI 服务）
- **停止按钮**: 停止 ngrok 隧道
- **日志显示**: 实时显示 ngrok 操作日志

## 使用步骤

### 1. 安装依赖

确保已安装 pyngrok：

```bash
pip install pyngrok
```

或使用项目的 requirements.txt：

```bash
pip install -r requirements.txt
```

### 2. 获取 ngrok Authtoken（可选）

免费使用 ngrok 不需要 authtoken，但有一些限制。要获取完整功能：

1. 访问 [ngrok 官网](https://ngrok.com/)
2. 注册并登录账号
3. 在 Dashboard 中获取 Authtoken
4. 将 Authtoken 填入 GUI 配置区域

### 3. 启动服务

1. **启动 FastAPI 服务**:
   - 在"云端服务"标签页中
   - 配置端口（默认 8000）
   - 点击"启动服务"按钮

2. **配置 ngrok**:
   - （可选）输入 Authtoken
   - 选择合适的区域（建议选择距离最近的区域）

3. **启动 ngrok**:
   - 点击"启动 ngrok"按钮
   - 等待连接建立
   - 复制生成的公网 URL

### 4. 配置 Coze 插件

使用 ngrok 生成的公网 URL 配置 Coze 插件：

1. 公网地址示例: `https://abc123.ngrok.io`
2. API 文档地址: `https://abc123.ngrok.io/docs`
3. 在 Coze 平台的插件配置中使用此 URL

## 注意事项

### 安全性
- ⚠️ ngrok 将本地服务暴露到公网，请注意数据安全
- 建议使用 Authtoken 以获得更好的安全性和稳定性
- 定期轮换 Authtoken
- 不使用时及时停止 ngrok 服务

### 性能
- 免费版 ngrok 有带宽和连接数限制
- 升级到付费版可获得更好的性能和稳定性
- 选择地理位置接近的区域可以降低延迟

### 限制
- 免费版每次启动会生成不同的 URL
- URL 格式为随机字符串 (如 `abc123.ngrok.io`)
- 付费版可以使用固定域名

### 故障排除

#### ngrok 启动失败
1. 检查 pyngrok 是否正确安装
2. 确认 FastAPI 服务已启动
3. 检查网络连接
4. 验证 Authtoken 是否有效（如果使用）

#### 无法访问公网地址
1. 确认 ngrok 隧道状态为"运行中"
2. 检查防火墙设置
3. 尝试更换区域
4. 查看 ngrok 日志了解详细错误

#### URL 经常变化
- 这是免费版的正常行为
- 考虑升级到付费版获得固定域名

## API 参考

### NgrokManager 类

```python
from app.utils.ngrok_manager import NgrokManager

# 创建管理器实例
manager = NgrokManager(logger=your_logger)

# 检查可用性
if manager.is_ngrok_available():
    # 设置 authtoken
    manager.set_authtoken("your_authtoken")
    
    # 启动隧道
    public_url = manager.start_tunnel(
        port=8000,
        region="us"
    )
    
    # 获取状态
    status = manager.get_status()
    
    # 停止隧道
    manager.stop_tunnel()
```

### 主要方法

- `is_ngrok_available()`: 检查 pyngrok 是否可用
- `set_authtoken(authtoken)`: 设置 ngrok authtoken
- `start_tunnel(port, authtoken, region, protocol)`: 启动隧道
- `stop_tunnel()`: 停止隧道
- `get_status()`: 获取当前状态
- `get_tunnels()`: 获取所有活动隧道
- `kill_all()`: 终止所有 ngrok 进程

## 开发说明

### 文件结构

```
app/
├── utils/
│   └── ngrok_manager.py      # ngrok 管理器核心实现
└── gui/
    └── cloud_service_tab.py  # GUI 集成
tests/
└── test_ngrok.py             # 单元测试
```

### 集成要点

1. **生命周期管理**: ngrok 的启停与 FastAPI 服务联动
2. **状态同步**: UI 状态与实际运行状态保持一致
3. **错误处理**: 完善的异常处理和用户提示
4. **资源清理**: 确保应用退出时正确清理资源

## 相关链接

- [ngrok 官网](https://ngrok.com/)
- [pyngrok 文档](https://pyngrok.readthedocs.io/)
- [ngrok 文档](https://ngrok.com/docs)
- [Coze 集成指南](../docs/guides/COZE_INTEGRATION_GUIDE.md)

## 许可证

本项目遵循 MIT 许可证。ngrok 是独立的第三方服务，有自己的许可条款。
