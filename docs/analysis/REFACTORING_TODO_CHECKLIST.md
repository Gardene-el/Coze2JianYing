# Schema 重构后续工作 Checklist

## 🔥 紧急修复（立即执行）

### 修复 segment_routes.py 中的严重错误

- [ ] **修复 add_video_keyframe 函数**
  - [ ] 找到第一个 `add_text_keyframe` 函数定义（约 1138 行）
  - [ ] 将函数名改为 `add_video_keyframe`
  - [ ] 将装饰器路径改为 `/video/{segment_id}/add_keyframe`
  - [ ] 将 Response Model 改为 `AddVideoKeyframeResponse`
  - [ ] 将 Request 改为 `AddVideoKeyframeRequest`
  - [ ] 确认函数体内检查 `segment_type == "video"`
  - [ ] 将函数移动到 VideoSegment 操作端点区域

- [ ] **修复 add_sticker_keyframe 函数**
  - [ ] 找到 `add_sticker_keyframe` 函数（约 1207 行）
  - [ ] 将 `AddKeyframeRequest` 改为 `AddStickerKeyframeRequest`
  - [ ] 将 `AddKeyframeResponse` 改为 `AddStickerKeyframeResponse`
  - [ ] 更新日志消息为"贴纸关键帧"

- [ ] **修复 add_text_keyframe 函数**
  - [ ] 找到第二个 `add_text_keyframe` 函数（约 1487 行）
  - [ ] 将 `AddKeyframeRequest` 改为 `AddTextKeyframeRequest`
  - [ ] 确认装饰器路径是 `/text/{segment_id}/add_keyframe`
  - [ ] 确认函数体内检查 `segment_type == "text"`

- [ ] **验证文件结构**
  - [ ] 确认没有重复的函数定义
  - [ ] 确认端点按 Segment 类型正确分组
  - [ ] 确认所有导入的 Schema 都存在

## ⚠️ 重要更新（高优先级）

### 更新 GUI 和脚本执行器

- [ ] **app/gui/script_executor_tab.py**
  - [ ] 更新所有 Schema imports：
    - [ ] `AddEffectRequest` → `AddAudioEffectRequest`, `AddVideoEffectRequest`
    - [ ] `AddFadeRequest` → `AddAudioFadeRequest`, `AddVideoFadeRequest`
    - [ ] `AddKeyframeRequest` → `Add*KeyframeRequest` (4个)
    - [ ] `AddAnimationRequest` → `AddVideoAnimationRequest`, `AddTextAnimationRequest`
    - [ ] `AddFilterRequest` → `AddVideoFilterRequest`
    - [ ] `AddMaskRequest` → `AddVideoMaskRequest`
    - [ ] `AddTransitionRequest` → `AddVideoTransitionRequest`
    - [ ] `AddBackgroundFillingRequest` → `AddVideoBackgroundFillingRequest`
    - [ ] `AddBubbleRequest` → `AddTextBubbleRequest`
  - [ ] 更新脚本预处理逻辑中的 Schema 引用
  - [ ] 测试脚本执行功能

### 更新测试文件

- [ ] **tests/test_script_executor.py**
  - [ ] 更新所有 Schema imports
  - [ ] 更新测试用例中的 Schema 使用
  - [ ] 运行测试确保通过

- [ ] **tests/test_script_executor_integration.py**
  - [ ] 更新所有 Schema imports
  - [ ] 更新集成测试中的 Schema 使用
  - [ ] 运行集成测试确保通过

### 验证 API 功能

- [ ] **手动测试 API 端点**
  - [ ] 测试 Audio 相关端点（effect, fade, keyframe）
  - [ ] 测试 Video 相关端点（所有操作）
  - [ ] 测试 Text 相关端点（animation, bubble, effect, keyframe）
  - [ ] 测试 Sticker 相关端点（keyframe）
  - [ ] 确认错误处理正常工作

- [ ] **检查 API 文档**
  - [ ] 访问 `/docs` (Swagger UI)
  - [ ] 确认所有端点显示正确的 Schema
  - [ ] 确认示例数据正确

## 📦 Coze 插件更新（中优先级）

### 更新现有 Handler 文件

- [ ] **add_audio_effect**
  - [ ] `coze_plugin/raw_tools/add_audio_effect/handler.py`
  - [ ] 更新导入：`AddEffectRequest` → `AddAudioEffectRequest`
  - [ ] 更新 README.md

- [ ] **add_video_effect**
  - [ ] `coze_plugin/raw_tools/add_video_effect/handler.py`
  - [ ] 更新导入：`AddEffectRequest` → `AddVideoEffectRequest`
  - [ ] 更新 README.md

- [ ] **add_audio_fade**
  - [ ] 更新导入：`AddFadeRequest` → `AddAudioFadeRequest`
  - [ ] 更新 README.md

- [ ] **add_video_fade**
  - [ ] 更新导入：`AddFadeRequest` → `AddVideoFadeRequest`
  - [ ] 更新 README.md

- [ ] **add_audio_keyframe**
  - [ ] 更新导入：`AddKeyframeRequest` → `AddAudioKeyframeRequest`
  - [ ] 更新 README.md

- [ ] **add_video_keyframe**
  - [ ] 更新导入：`AddKeyframeRequest` → `AddVideoKeyframeRequest`
  - [ ] 更新 README.md

- [ ] **add_text_keyframe**
  - [ ] 更新导入：`AddKeyframeRequest` → `AddTextKeyframeRequest`
  - [ ] 更新 README.md

- [ ] **add_sticker_keyframe**
  - [ ] 更新导入：`AddKeyframeRequest` → `AddStickerKeyframeRequest`
  - [ ] 更新 README.md

- [ ] **add_video_animation**
  - [ ] 更新导入：`AddAnimationRequest` → `AddVideoAnimationRequest`
  - [ ] 更新 README.md

- [ ] **add_text_animation**
  - [ ] 更新导入：`AddAnimationRequest` → `AddTextAnimationRequest`
  - [ ] 更新 README.md

- [ ] **其他受影响的工具**
  - [ ] add_video_filter（如果存在）
  - [ ] add_video_mask（如果存在）
  - [ ] add_video_transition（如果存在）
  - [ ] add_video_background_filling（如果存在）
  - [ ] add_text_bubble（如果存在）

### 重新生成 Handler（如果使用 Handler Generator）

- [ ] **检查是否需要重新生成**
  - [ ] 查看 `scripts/handler_generator/` 是否存在
  - [ ] 检查是否有生成脚本在使用

- [ ] **如果需要重新生成**
  - [ ] 运行 handler generator 脚本
  - [ ] 验证生成的代码正确
  - [ ] 提交生成的新文件

## 📚 文档更新（低优先级）

### API 参考文档

- [ ] **docs/API_ENDPOINTS_REFERENCE.md**
  - [ ] 更新所有 Request Schema 名称
  - [ ] 更新所有 Response Schema 名称
  - [ ] 更新代码示例
  - [ ] 确保示例代码可运行

### 项目文档

- [ ] **docs/draft_generator/SCRIPT_EXECUTOR_TAB.md**
  - [ ] 更新 Schema 导入示例
  - [ ] 更新使用说明

- [ ] **README.md**（如果有相关内容）
  - [ ] 更新快速开始中的代码示例
  - [ ] 更新 Schema 引用

- [ ] **其他相关文档**
  - [ ] 搜索所有包含旧 Schema 名称的文档
  - [ ] 逐一更新

### 生成迁移指南

- [ ] **创建 MIGRATION_GUIDE.md**
  - [ ] 列出所有 Schema 名称变更
  - [ ] 提供迁移示例代码
  - [ ] 说明 Breaking Changes
  - [ ] 提供向后兼容方案（如果需要）

## ✅ 验证和测试

### 单元测试

- [ ] **编写新的测试**
  - [ ] 测试所有新 Schema 的验证逻辑
  - [ ] 测试参数边界条件
  - [ ] 测试错误情况

- [ ] **运行现有测试**
  - [ ] `pytest tests/` 全部通过
  - [ ] 修复失败的测试

### 集成测试

- [ ] **端到端测试**
  - [ ] 创建完整的草稿生成流程测试
  - [ ] 测试所有 Segment 类型的操作
  - [ ] 验证生成的草稿文件正确

### 回归测试

- [ ] **确保无意外 Breaking Changes**
  - [ ] API 端点路径未改变
  - [ ] HTTP 响应格式未改变
  - [ ] 功能行为未改变

## 🚀 发布准备

### 版本管理

- [ ] **更新版本号**
  - [ ] 确定版本号（建议使用语义化版本）
  - [ ] 更新 `setup.py` 或 `pyproject.toml`

- [ ] **更新 CHANGELOG**
  - [ ] 记录所有 Breaking Changes
  - [ ] 列出新增的 Schema
  - [ ] 说明迁移路径

### 代码审查

- [ ] **自我审查**
  - [ ] 检查所有修改的文件
  - [ ] 确认命名一致性
  - [ ] 确认没有遗漏的文件

- [ ] **提交代码**
  - [ ] 创建有意义的 commit 信息
  - [ ] 推送到远程仓库
  - [ ] 创建 Pull Request（如果适用）

### 发布

- [ ] **创建 Release**
  - [ ] 标记版本 tag
  - [ ] 编写 Release Notes
  - [ ] 发布到 GitHub Releases

- [ ] **更新部署**
  - [ ] 如果有线上环境，更新部署
  - [ ] 通知相关用户

## 📋 完成检查

- [ ] 所有紧急修复已完成
- [ ] 所有重要更新已完成
- [ ] 所有测试通过
- [ ] 文档已更新
- [ ] 代码已提交
- [ ] 版本已发布

---

## 备注

### 预估工作量

- 🔥 紧急修复：**1-2 小时**
- ⚠️ 重要更新：**3-4 小时**
- 📦 Coze 插件更新：**2-3 小时**
- 📚 文档更新：**2-3 小时**
- ✅ 测试和验证：**2-3 小时**

**总计：约 10-15 小时**

### 参考文档

- [Schema 重构完成报告](./SCHEMA_REFACTORING_COMPLETED.md)
- [Segment Routes 紧急修复指南](./SEGMENT_ROUTES_URGENT_FIXES.md)
- [Schema 重构计划](./SCHEMA_REFACTORING_PLAN.md)
- [AddEffectRequest 设计分析](./AddEffectRequest_DESIGN_ANALYSIS.md)

### 遇到问题时

1. 参考 `SEGMENT_ROUTES_URGENT_FIXES.md` 了解具体修复方法
2. 查看 `SCHEMA_REFACTORING_COMPLETED.md` 了解完整变更
3. 运行测试验证修改正确性
4. 如有疑问，保留详细日志以便排查

---

**创建日期**：2024年
**最后更新**：执行重构时
**状态**：待执行