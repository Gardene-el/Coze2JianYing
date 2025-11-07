# ngrok 快速参考卡

## 快速开始 (3 步)

```
1. 启动 FastAPI 服务
   • 在"云端服务"标签页
   • 点击"启动服务"
   • 确认服务运行中 (🟢)

2. 启动 ngrok 隧道
   • 点击"启动 ngrok"
   • 等待连接建立
   • 查看生成的公网 URL

3. 配置 Coze 插件
   • 复制公网 URL
   • 在 Coze 中配置插件
   • 测试连接
```

## 常用操作

| 操作 | 步骤 |
|------|------|
| **获取公网 URL** | 启动 ngrok → 查看"公网地址"栏 → 点击"复制"按钮 |
| **查看 API 文档** | 公网地址 + `/docs`，如: `https://abc123.ngrok.io/docs` |
| **停止隧道** | 点击"停止 ngrok"按钮 |
| **查看日志** | 查看"ngrok 日志"面板 |
| **清空日志** | 点击日志面板的"清空日志"按钮 |
| **更换区域** | 停止 ngrok → 选择新区域 → 重新启动 |

## 配置选项

### Authtoken (可选)
```
作用: 提升稳定性和性能，解除免费限制
获取: https://ngrok.com/ → 注册 → Dashboard → Authtoken
配置: 粘贴到"Authtoken"输入框
```

### 区域选择
```
us - 美国 (默认)      ← 亚洲用户可选 ap
eu - 欧洲
ap - 亚太            ← 推荐中国用户
au - 澳大利亚
sa - 南美
jp - 日本            ← 推荐日本用户
in - 印度
```

**选择建议**: 选择地理位置最近的区域以获得最佳性能

## 状态指示器

| 指示器 | 含义 |
|--------|------|
| 🔴 红色 | ngrok 未运行 |
| 🟢 绿色 | ngrok 运行中 |
| "未启动" | ngrok 尚未启动 |
| "运行中" | 隧道已建立，可以使用 |

## 常见问题快速解决

### 问题: 首次启动出现下载错误
```
错误信息:
  AttributeError: 'NoneType' object has no attribute 'write'
  PyngrokNgrokInstallError: An error occurred while downloading ngrok

原因: GUI 应用中 pyngrok 下载二进制文件时的输出问题

解决:
  • 本项目已自动处理 (v1.1.0+)
  • 重启应用，问题已修复
  • 手动预安装: python -c "from pyngrok import ngrok; ngrok.install_ngrok()"
```

### 问题: 监控或停止时出现超时错误
```
错误信息:
  TimeoutError: timed out
  PyngrokNgrokURLError: ngrok client exception, URLError: timed out

原因: ngrok API 响应缓慢或网络不稳定

解决:
  • 本项目已改进超时处理 (v1.3.0+)
  • 监控线程永不停止，会持续重试
  • 网络恢复后自动继续监控
  • 停止失败时会自动清理本地状态
  • 如需强制清理：重启应用或结束 ngrok.exe 进程
  • 改善网络连接或更换 ngrok 区域
```

### 问题: ngrok 启动失败
```
✓ 检查清单:
  □ FastAPI 服务是否已启动？
  □ pyngrok 是否已安装？(pip install pyngrok)
  □ 网络连接是否正常？
  □ Authtoken 是否有效？(如果使用)
```

### 问题: 无法访问公网地址
```
✓ 检查清单:
  □ ngrok 状态是否为"运行中"？
  □ 公网 URL 是否正确复制？
  □ 防火墙是否阻止连接？
  □ 尝试更换区域
```

### 问题: URL 每次都不一样
```
原因: 免费版每次生成随机 URL
解决: 
  • 接受这个限制 (免费使用)
  • 或升级到付费版获得固定域名
```

### 问题: 连接速度慢
```
优化方法:
  1. 选择更近的区域
  2. 检查本地网络
  3. 考虑升级带宽
  4. 使用付费版
```

## 使用技巧

### 💡 技巧 1: 快速复制 URL
```
启动 ngrok 后 → 点击"复制"按钮 → 直接粘贴到 Coze
```

### 💡 技巧 2: 保持连接稳定
```
• 配置 Authtoken (提升稳定性)
• 选择合适区域 (降低延迟)
• 监控日志 (及时发现问题)
```

### 💡 技巧 3: 安全使用
```
• 使用完毕立即停止 ngrok
• 定期轮换 Authtoken
• 监控访问日志
• 避免暴露敏感数据
```

### 💡 技巧 4: 调试问题
```
查看日志顺序:
1. ngrok 日志面板 (查看隧道状态)
2. 服务实时日志 (查看 API 请求)
3. 系统日志 (查看详细错误)
```

## 限制说明

### 免费版限制
- ❌ URL 每次启动都会变化
- ❌ 连接数有限
- ❌ 带宽有限
- ❌ 不支持自定义域名

### 付费版优势
- ✅ 固定域名
- ✅ 更高连接数
- ✅ 更大带宽
- ✅ 更多功能

## 键盘快捷键 (GUI)

```
当前暂无快捷键，使用鼠标点击操作
```

## 命令行等效操作

如果你熟悉命令行，以下是等效操作：

```bash
# 安装 ngrok
pip install pyngrok

# 设置 authtoken
ngrok authtoken YOUR_TOKEN

# 启动隧道
ngrok http 8000 --region us

# 查看隧道
curl http://127.0.0.1:4040/api/tunnels
```

## API 端点参考

使用 ngrok URL 访问以下端点：

```
健康检查:  GET  {ngrok_url}/api/draft/health
API 文档:  GET  {ngrok_url}/docs
OpenAPI:   GET  {ngrok_url}/openapi.json

示例:
  https://abc123.ngrok.io/api/draft/health
  https://abc123.ngrok.io/docs
```

## 紧急情况处理

### 🚨 如果 ngrok 无法停止
```
1. 尝试点击"停止 ngrok"按钮
2. 如果失败，停止 FastAPI 服务
3. 如果仍然失败，重启应用程序
4. 最后手段: 结束进程 (任务管理器)
```

### 🚨 如果发现可疑访问
```
1. 立即停止 ngrok
2. 检查 ngrok 日志
3. 检查服务日志
4. 考虑轮换 Authtoken
5. 如有必要，联系 ngrok 支持
```

## 获取帮助

- 📖 详细文档: [NGROK_USAGE_GUIDE.md](./NGROK_USAGE_GUIDE.md)
- 🏗️ 架构说明: [NGROK_ARCHITECTURE.md](./NGROK_ARCHITECTURE.md)
- 🌐 ngrok 官方文档: https://ngrok.com/docs
- 💬 提交问题: [GitHub Issues](https://github.com/Gardene-el/Coze2JianYing/issues)

---

**最后更新**: 2025-11-06
**版本**: 1.0.0
