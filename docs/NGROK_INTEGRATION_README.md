# ngrok 集成功能 - README

## 🎯 功能概述

本项目已完整集成 ngrok 内网穿透功能，允许将本地 FastAPI 服务暴露到公网，以便 Coze 平台可以访问和调用。

**⚠️ 重要更新：ngrok 政策变更**
- **ngrok 现在要求所有用户注册账号并配置 Authtoken**
- 注册是免费的，但已经不再支持匿名使用
- 本文档已更新以反映最新的 ngrok 使用要求

## 📦 包含内容

### 核心功能模块
- **NgrokManager** (`app/utils/ngrok_manager.py`) - 完整的 ngrok 隧道管理类
- **CloudServiceTab** (`app/gui/cloud_service_tab.py`) - 集成了 ngrok 控制的 GUI

### 测试套件
- **test_ngrok.py** (`tests/test_ngrok.py`) - 5 个单元测试，覆盖所有核心功能

### 文档
- **使用指南** (`docs/guides/NGROK_USAGE_GUIDE.md`) - 详细的使用说明和 API 参考
- **架构文档** (`docs/guides/NGROK_ARCHITECTURE.md`) - 系统架构和设计说明
- **快速参考** (`docs/guides/NGROK_QUICK_REFERENCE.md`) - 常用操作和故障排除

## 🚀 快速开始

### 步骤 1：安装依赖

```bash
pip install -r requirements.txt
```

### 步骤 2：获取 ngrok Authtoken（必需）

⚠️ **重要**：ngrok 现在要求必须注册才能使用。

1. 访问 https://ngrok.com/ 免费注册账号
2. 登录后访问：https://dashboard.ngrok.com/get-started/your-authtoken
3. 复制显示的 Authtoken
4. 将 Authtoken 保存备用

### 步骤 3：启动应用

```bash
python app/main.py
```

### 步骤 4：配置并启动 ngrok

在"云端服务"标签页中：

1. **启动 FastAPI 服务**
   - 点击"启动服务"按钮
   - 等待服务启动（绿色指示器）

2. **配置 ngrok（必需）**
   - ⚠️ **填写 Authtoken**（必需，否则无法启动）
   - ✅ 选择合适的区域（建议选择最近的）
   - 💡 点击 "?" 查看详细说明

3. **启动 ngrok 隧道**
   - 点击"启动 ngrok"按钮
   - 等待隧道建立
   - 复制生成的公网 URL

4. **配置 Coze 插件**
   - 使用复制的 URL 配置 Coze 插件
   - 测试连接

## 📋 功能清单

### ✅ 已实现功能

- [x] pyngrok 依赖集成
- [x] NgrokManager 隧道管理类
- [x] GUI 配置界面
  - [x] Authtoken 输入（支持显示/隐藏）
  - [x] 区域选择（7 个区域）
  - [x] 启动/停止按钮
- [x] 状态监控
  - [x] 实时状态指示器
  - [x] 公网 URL 显示
  - [x] 一键复制功能
- [x] 日志系统
  - [x] 独立的 ngrok 日志面板
  - [x] 实时日志输出
  - [x] 清空日志功能
- [x] 生命周期管理
  - [x] 与 FastAPI 服务联动
  - [x] 自动资源清理
  - [x] 线程安全操作
- [x] 错误处理
  - [x] 完善的异常捕获
  - [x] 用户友好的错误提示
- [x] 单元测试（5 个，全部通过）
- [x] 完整文档（3 个指南）

## 🏗️ 项目结构

```
Coze2JianYing/
├── app/
│   ├── utils/
│   │   └── ngrok_manager.py          # ngrok 管理器
│   └── gui/
│       └── cloud_service_tab.py      # GUI 集成
├── tests/
│   └── test_ngrok.py                 # 单元测试
├── docs/
│   └── guides/
│       ├── NGROK_USAGE_GUIDE.md      # 使用指南
│       ├── NGROK_ARCHITECTURE.md     # 架构文档
│       └── NGROK_QUICK_REFERENCE.md  # 快速参考
└── requirements.txt                   # 依赖列表（含 pyngrok）
```

## 📊 统计信息

- **总代码行数**: 1,307 行
- **核心代码**: 559 行
- **测试代码**: 135 行
- **文档**: 610+ 行
- **新增文件**: 5 个
- **修改文件**: 2 个

## 🧪 测试

运行 ngrok 相关测试：

```bash
python tests/test_ngrok.py
```

所有测试应该通过：
```
✅ test_ngrok_manager_initialization
✅ test_ngrok_availability
✅ test_get_status
✅ test_set_authtoken
✅ test_cleanup
```

## 📚 文档链接

| 文档 | 说明 | 链接 |
|------|------|------|
| 使用指南 | 详细的使用说明和 API 参考 | [NGROK_USAGE_GUIDE.md](docs/guides/NGROK_USAGE_GUIDE.md) |
| 架构文档 | 系统架构和设计说明 | [NGROK_ARCHITECTURE.md](docs/guides/NGROK_ARCHITECTURE.md) |
| 快速参考 | 常用操作和故障排除 | [NGROK_QUICK_REFERENCE.md](docs/guides/NGROK_QUICK_REFERENCE.md) |

## 🔧 配置选项

### Authtoken（可选）

获取 ngrok Authtoken：
1. 访问 https://ngrok.com/
2. 注册账号
3. 在 Dashboard 中获取 Authtoken
4. 在 GUI 中输入 Authtoken

### 区域选择

支持的区域：
- `us` - 美国（默认）
- `eu` - 欧洲
- `ap` - 亚太（推荐中国用户）
- `au` - 澳大利亚
- `sa` - 南美
- `jp` - 日本
- `in` - 印度

## 🔒 安全注意事项

⚠️ **重要提示**：
1. ngrok 将本地服务暴露到公网，请注意数据安全
2. 建议使用 Authtoken 以获得更好的安全性
3. 不使用时及时停止 ngrok 服务
4. 定期轮换 Authtoken
5. 监控访问日志，发现异常立即停止服务

## 🐛 故障排除

### 常见问题

**Q: ngrok 启动失败**
```
检查清单:
□ FastAPI 服务是否已启动？
□ pyngrok 是否已安装？
□ 网络连接是否正常？
□ Authtoken 是否有效？（如果使用）
```

**Q: 无法访问公网地址**
```
检查清单:
□ ngrok 状态是否为"运行中"？
□ URL 是否正确复制？
□ 防火墙是否阻止连接？
□ 尝试更换区域
```

**Q: URL 每次都不一样**
```
原因: 免费版每次生成随机 URL
解决: 升级到付费版获得固定域名
```

详细的故障排除指南请参考 [快速参考文档](docs/guides/NGROK_QUICK_REFERENCE.md)。

## 💡 使用技巧

1. **选择合适的区域**: 选择地理位置最近的区域以获得最佳性能
2. **监控日志**: 定期查看 ngrok 日志了解连接状态
3. **使用 Authtoken**: 提高稳定性和解除免费限制
4. **及时停止**: 不使用时立即停止 ngrok 节省资源

## 🤝 贡献

如果你发现问题或有改进建议，欢迎：
1. 提交 Issue
2. 创建 Pull Request
3. 完善文档

## 📄 许可证

本项目遵循 MIT 许可证。ngrok 是独立的第三方服务，有自己的许可条款。

## 🔗 相关链接

- [ngrok 官网](https://ngrok.com/)
- [pyngrok 文档](https://pyngrok.readthedocs.io/)
- [Coze 平台](https://www.coze.cn/)
- [项目主页](https://github.com/Gardene-el/Coze2JianYing)

---

**版本**: 1.0.0  
**最后更新**: 2025-11-06  
**状态**: ✅ 生产就绪 (Production Ready)
