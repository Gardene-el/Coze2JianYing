# Coze API 设置功能实现文档

## 功能概述

在本地服务标签页中新增了 Coze API 配置区域，允许用户输入 API Token 和选择服务地址。

## 新增的 UI 组件

### Coze API 配置区域

位置：在"草稿文件夹设置"和"FastAPI 服务管理"之间

```
┌─────────────────────────────────────────────────────────────┐
│ Coze API 配置                                                │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ API Token: [**************************] [☐ 显示]        │ │
│ │ 服务地址:  [https://api.coze.cn ▼]                      │ │
│ │ 状态: 未配置                              [测试连接]     │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### UI 组件详细说明

1. **API Token 输入框**
   - 类型: Entry (密码模式，show="*")
   - 默认值: 空
   - 说明: 用户输入 Coze API Token
   - 特点: 不保存到本地文件或环境变量

2. **显示/隐藏复选框**
   - 类型: Checkbutton
   - 功能: 切换 Token 的可见性
   - 选中: 显示明文
   - 未选中: 显示为星号

3. **服务地址下拉框**
   - 类型: Combobox (只读)
   - 选项:
     - https://api.coze.cn (国内版，默认)
     - https://api.coze.com (国际版)
   - 默认值: https://api.coze.cn

4. **状态标签**
   - 显示当前配置状态:
     - "状态: 未配置" (灰色)
     - "状态: 已配置 ✓" (绿色)
     - "状态: 连接失败 ✗" (红色)
     - "状态: 测试连接中..." (黑色)

5. **测试连接按钮**
   - 功能: 验证 API Token 和服务地址
   - 点击后:
     - 检查 Token 是否为空
     - 尝试创建 Coze 客户端
     - 更新状态标签
     - 显示连接结果

## 实现的核心方法

### 1. `_toggle_token_visibility()`
切换 Token 输入框的显示/隐藏状态。

### 2. `_test_coze_connection()`
测试 Coze API 连接：
- 验证 Token 不为空
- 创建 Coze 客户端
- 保存配置到实例变量
- 更新 UI 状态
- 显示连接结果

### 3. `_get_coze_client()`
获取配置好的 Coze 客户端实例：
- 如果已存在，直接返回
- 否则，从输入框读取配置并创建
- 返回 Coze 客户端或 None

## 数据存储

### 实例变量
```python
self.coze_api_token = None      # API Token (字符串)
self.coze_base_url = COZE_CN_BASE_URL  # Base URL (字符串)
self.coze_client = None         # Coze 客户端实例
```

### 存储特点
- **仅内存存储**: 不保存到文件
- **不使用环境变量**: 不从 os.getenv() 读取
- **会话级别**: 应用关闭后清空
- **手动输入**: 每次启动应用需重新输入

## 使用流程

### 配置 Coze API
1. 在"Coze API 配置"区域输入 API Token
2. 选择服务地址 (国内版或国际版)
3. 点击"测试连接"按钮验证配置
4. 查看状态标签确认连接成功

### 获取 Coze 客户端
在其他代码中可以通过以下方式获取配置好的客户端：
```python
coze_client = self._get_coze_client()
if coze_client:
    # 使用 coze_client 进行 API 调用
    pass
else:
    # 处理未配置的情况
    pass
```

## 代码示例

### 初始化 Coze 客户端
```python
from cozepy import Coze, TokenAuth, COZE_CN_BASE_URL

# 从用户输入获取配置
coze_api_token = self.token_var.get().strip()
base_url = self.base_url_var.get()

# 初始化 Coze 客户端
coze = Coze(
    auth=TokenAuth(coze_api_token),
    base_url=base_url
)
```

## 测试验证

### 单元测试
- ✅ 导入测试: 验证 cozepy 库可用
- ✅ 结构测试: 验证所有必需的变量和方法
- ✅ UI 组件测试: 验证所有 UI 组件已创建

### 运行测试
```bash
python test_coze_api_settings.py
```

## 安全考虑

1. **密码模式**: Token 输入框默认为密码模式 (show="*")
2. **不持久化**: Token 不保存到磁盘
3. **内存存储**: 仅在运行时保存在内存中
4. **手动清理**: 应用关闭时自动清理

## 未来扩展

可能的扩展方向:
- 添加 Token 验证逻辑
- 支持更多的 Base URL 选项
- 添加 Token 过期检测
- 集成到 FastAPI 服务中使用

## 相关文件

- `app/gui/local_service_tab.py` - 主实现文件
- `test_coze_api_settings.py` - 单元测试
- `test_coze_gui.py` - GUI 测试 (需要图形环境)
