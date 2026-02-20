# 脚本执行器标签页

## 概述

脚本执行器标签页是实现"方案三：脚本生成执行"的核心组件。它允许用户执行从 Coze 导出的 Python 脚本，自动注入所需的 API 依赖项，并在 GUI 中提供完整的执行反馈。

## 功能特性

### 1. 脚本加载
- **文件加载**：支持从文件系统加载 Python 脚本
- **手动输入**：支持直接粘贴脚本内容
- **格式支持**：支持 `.py`、`.txt` 等多种文件格式

### 2. 脚本验证
- **语法检查**：执行前验证 Python 语法
- **依赖检测**：自动检测所需的 API 函数
- **错误提示**：提供详细的语法错误位置和描述

### 3. 自动依赖注入
脚本执行器会自动注入以下依赖：

#### API 函数
- **Draft 操作**：`create_draft`, `add_track`, `add_segment`, `save_draft` 等
- **Segment 创建**：`create_audio_segment`, `create_video_segment`, `create_text_segment` 等
- **Segment 操作**：`add_animation`, `add_effect`, `add_fade`, `add_keyframe` 等

#### Request 模型
- **Segment 创建**：`CreateAudioSegmentRequest`, `CreateVideoSegmentRequest` 等
- **Draft 操作**：`CreateDraftRequest`, `AddTrackRequest` 等
- **Segment 操作**：`AddEffectRequest`, `AddFadeRequest`, `AddAnimationRequest` 等
- **辅助模型**：`TimeRange`, `ClipSettings`, `TextStyle`, `Position`

#### 兼容性
- **CustomNamespace**：映射到 `SimpleNamespace`，兼容 Coze 导出的脚本格式

### 4. 异步执行
- **后台执行**：在独立线程中执行脚本，不阻塞 GUI
- **进度反馈**：实时显示执行状态
- **错误处理**：捕获并显示执行过程中的异常

## 使用方法

### 方式一：加载脚本文件

1. 点击"加载文件..."按钮
2. 选择从 Coze 导出的脚本文件（如 `测试用的脚本`）
3. 脚本内容会自动显示在文本框中
4. （可选）点击"验证脚本"检查语法
5. 点击"执行脚本"开始生成草稿

### 方式二：手动粘贴脚本

1. 直接在文本框中粘贴脚本内容
2. （可选）点击"验证脚本"检查语法
3. 点击"执行脚本"开始生成草稿

## 脚本格式

### Coze 导出的脚本格式示例

```python
# API 调用: create_draft
req_xxx = CreateDraftRequest(draft_name="demo", width=1920, height=1080, fps=30)
resp_xxx = await create_draft(req_xxx)
draft_id = resp_xxx.draft_id

# API 调用: add_track
req_yyy = AddTrackRequest(track_type="audio", track_name=None)
resp_yyy = await add_track(draft_id, req_yyy)

# API 调用: create_audio_segment
req_zzz = CreateAudioSegmentRequest(
    material_url="https://example.com/audio.mp3",
    target_timerange=CustomNamespace(start=0, duration=5000000),
    volume=1.0
)
resp_zzz = await create_audio_segment(req_zzz)

# API 调用: save_draft
resp_final = await save_draft(draft_id)
```

### 预处理后的脚本结构

脚本执行器会自动将上述脚本转换为：

```python
# === 自动注入的导入 ===
import sys
import asyncio
from pathlib import Path
from types import SimpleNamespace

# 导入所有API函数
from app.api.draft_routes import (...)
from app.api.segment_routes import (...)

# 导入所有Request模型
from app.schemas.general_schemas import (...)

# 兼容性映射
CustomNamespace = SimpleNamespace

# === 用户脚本开始 ===
async def main():
    """自动生成的main函数，包含用户脚本"""
    # 用户的脚本内容（自动缩进）
    req_xxx = CreateDraftRequest(draft_name="demo", width=1920, height=1080, fps=30)
    resp_xxx = await create_draft(req_xxx)
    # ...

# 运行主函数
if __name__ == "__main__":
    asyncio.run(main())
```

## 技术实现

### 脚本预处理 (`_preprocess_script`)

1. **移除引号**：处理脚本开头和结尾的引号（如果存在）
2. **注入导入**：添加所有必需的 import 语句
3. **包装异步函数**：将用户脚本包装在 `async def main()` 中
4. **代码缩进**：为用户脚本添加适当的缩进

### 脚本执行 (`_execute_script_worker`)

1. **预处理**：调用 `_preprocess_script` 处理脚本
2. **创建事件循环**：在新线程中创建 asyncio 事件循环
3. **执行脚本**：使用 `exec()` 执行预处理后的脚本
4. **GUI 更新**：使用 `frame.after()` 在主线程中更新 GUI

### 错误处理

- **语法错误**：在验证阶段捕获，显示错误位置
- **运行时错误**：在执行阶段捕获，显示错误堆栈
- **线程安全**：使用 `frame.after()` 确保 GUI 更新在主线程中进行

## 安全性考虑

### 当前实现
- 脚本在本地执行，不上传到任何远程服务器
- 使用 `exec()` 执行动态代码，仅限于本地环境

### 注意事项
- ⚠️ **仅执行信任的脚本**：不要执行来自不明来源的脚本
- ⚠️ **检查脚本内容**：执行前建议使用"验证脚本"功能检查语法
- ⚠️ **沙箱隔离**：当前实现未包含完整的沙箱隔离

## 常见问题

### Q: 脚本执行失败怎么办？
A: 
1. 点击"验证脚本"检查语法错误
2. 查看日志面板获取详细错误信息
3. 确保脚本格式符合 Coze 导出的标准格式

### Q: 支持哪些 API 函数？
A: 支持 `app/api/draft_routes.py` 和 `app/api/segment_routes.py` 中定义的所有 API 函数。

### Q: 可以执行自定义 Python 代码吗？
A: 可以，但建议仅执行 Coze 导出的标准脚本。自定义代码可能需要额外的依赖或导致意外行为。

### Q: 执行过程中可以取消吗？
A: 当前版本不支持中途取消。脚本会执行到完成或遇到错误。

## 测试

### 单元测试
```bash
python tests/test_script_executor.py
```

测试内容：
- 脚本预处理逻辑
- 引号处理
- 语法验证

### 集成测试
```bash
python tests/test_script_executor_integration.py
```

测试内容：
- 简单脚本执行
- 实际测试脚本验证

## 未来改进

- [ ] 添加脚本执行的中途取消功能
- [ ] 实现更完整的沙箱隔离
- [ ] 添加脚本执行的进度条
- [ ] 支持脚本的调试模式
- [ ] 添加脚本执行历史记录
- [ ] 支持脚本的批量执行

## 相关文件

- **主实现**：`app/gui/script_executor_tab.py`
- **窗口注册**：`app/gui/main_window.py`
- **单元测试**：`tests/test_script_executor.py`
- **集成测试**：`tests/test_script_executor_integration.py`
- **测试脚本**：`测试用的脚本`

## 参考资料

- [API 端点参考](../../docs/reference/API_ENDPOINTS_REFERENCE.md)
- [Draft Generator 接口](../../data_structures/draft_generator_interface/README.md)
- [开发路线图](../../docs/guides/DEVELOPMENT_ROADMAP.md)
