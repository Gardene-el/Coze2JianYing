# ngrok 政策变更说明 (2025)

## 更新日期
2025-11-09

## 变更概述

ngrok 已更新其服务政策，**现在要求所有用户注册账号并配置 Authtoken 才能使用**。这是 ngrok 官方的政策变更，影响所有使用 ngrok 的项目和用户。

## 错误信息

如果尝试在没有配置 Authtoken 的情况下启动 ngrok，会收到以下错误：

```
ERR_NGROK_4018
authentication failed: Usage of ngrok requires a verified account and authtoken.

Sign up for an account: https://dashboard.ngrok.com/signup
Install your authtoken: https://dashboard.ngrok.com/get-started/your-authtoken
```

## 影响范围

### 对用户的影响

**之前（2024 及更早）**：
- ✅ 无需注册即可使用 ngrok
- ✅ 匿名使用，自动生成随机 URL
- ✅ 零配置快速开始

**现在（2025 起）**：
- ⚠️ 必须注册 ngrok 账号
- ⚠️ 必须配置 Authtoken
- ⚠️ 需要邮箱验证账号

### 对本项目的影响

1. **GUI 更新**：
   - 将 "Authtoken (可选)" 改为 "Authtoken (必需)"
   - 提示信息从蓝色改为红色警告
   - 添加 Authtoken 验证，未填写时拒绝启动

2. **文档更新**：
   - 更新所有文档以反映新政策
   - 强调注册是必需的
   - 提供详细的注册和获取 Authtoken 指南

3. **用户体验**：
   - 用户必须先注册才能使用 ngrok 功能
   - 首次使用需要额外的设置步骤

## 解决方案

### 用户操作步骤

1. **注册 ngrok 账号**：
   - 访问：https://ngrok.com/
   - 点击 "Sign up" 免费注册
   - 使用邮箱进行验证

2. **获取 Authtoken**：
   - 登录 ngrok
   - 访问：https://dashboard.ngrok.com/get-started/your-authtoken
   - 复制显示的 Authtoken

3. **配置 Authtoken**：
   - 在本应用的"云端服务"标签页
   - 将 Authtoken 粘贴到输入框
   - 点击"启动 ngrok"

### 免费账号功能

注册是免费的，免费账号提供：
- ✅ 随机生成的公网 URL（每次不同）
- ✅ 基本的带宽和连接数配额
- ✅ 适合开发和测试使用
- ⚠️ URL 每次都不同（无法固定）
- ⚠️ 有带宽和连接数限制

### 付费账号功能

如需更多功能可升级到付费账号：
- 🎯 固定的自定义域名
- 🎯 更高的带宽和连接数
- 🎯 更稳定的连接
- 🎯 多个并发隧道

## 技术实现

### 代码变更

1. **GUI 验证** (`app/gui/cloud_service_tab.py`):
```python
# 验证 authtoken 是否已填写
if not authtoken:
    messagebox.showerror(
        "需要 Authtoken",
        "ngrok 现在要求必须配置 Authtoken 才能使用。\n\n"
        "请执行以下步骤：\n"
        "1. 访问 https://ngrok.com/ 免费注册账号\n"
        "2. 在 Dashboard 获取 Authtoken\n"
        "3. 将 Authtoken 填入上方输入框\n"
        # ...
    )
    return
```

2. **标签更新**:
```python
# 旧：text="Authtoken (可选):"
# 新：text="Authtoken (必需):"
self.ngrok_token_label = ttk.Label(self.ngrok_config_frame, text="Authtoken (必需):")
```

3. **提示信息**:
```python
# 旧：蓝色提示 "无需注册即可使用"
# 新：红色警告 "需要免费注册账号"
self.ngrok_info_label = ttk.Label(
    text="⚠️ 注意：ngrok 现在需要免费注册账号并配置 Authtoken 才能使用。",
    foreground="red"
)
```

### 向后兼容性

- ✅ 已有 Authtoken 的用户不受影响
- ✅ 代码 API 接口保持不变
- ✅ 仅增加了必要的验证逻辑

## 常见问题

### Q: 为什么 ngrok 改变了政策？
A: 这是 ngrok 官方的商业决策，可能是为了：
- 更好地管理用户和资源
- 防止滥用
- 提供更稳定的服务

### Q: 注册需要付费吗？
A: 不需要。注册是完全免费的，免费账号已经可以满足基本的开发和测试需求。

### Q: 我的 Authtoken 安全吗？
A: Authtoken 是敏感信息，应妥善保管：
- 不要在公开场合分享
- 不要提交到代码仓库
- 如果泄露，立即在 ngrok 网站重置

### Q: 有替代方案吗？
A: 如果不想注册 ngrok，可以考虑：
- 使用其他内网穿透服务（如 localtunnel, serveo 等）
- 自建隧道服务
- 使用云服务器部署

## 参考链接

- ngrok 官网：https://ngrok.com/
- ngrok Dashboard：https://dashboard.ngrok.com/
- 获取 Authtoken：https://dashboard.ngrok.com/get-started/your-authtoken
- ngrok 文档：https://ngrok.com/docs

## 更新记录

- **2025-11-09**: 更新本项目以适配 ngrok 新政策
  - GUI 界面更新
  - 文档更新
  - 添加 Authtoken 验证

---

**状态**: ✅ 已完成适配
**影响**: 用户需要注册 ngrok 账号才能使用
**操作**: 必需 - 所有用户都需要获取 Authtoken
