# Schema 重构说明 - 镜像 pyJianYingDraft 类定义

## 📋 修改概述

本次重构将 `app/schemas/segment_schemas.py` 中的数据模型改为**完全镜像 pyJianYingDraft 库的真实类定义**，移除了 AI 错误生成的自定义类。

## ❌ 发现的问题

原始的 schema 定义存在以下严重问题：

1. **ClipSettings 定义错误**
   - 错误地定义为"图像调节参数"（亮度、对比度、饱和度等）
   - 实际应该是"变换参数"（位置、缩放、旋转、透明度）

2. **Position 类不存在**
   - 在 pyJianYingDraft 中根本没有 Position 类
   - 位置信息通过 `ClipSettings.transform_x` 和 `transform_y` 表示

3. **TextStyle 不完整**
   - 缺少关键字段：`font_size` 和 `color`
   - 只有格式标记（加粗、斜体、下划线）

4. **CropSettings 缺失**
   - 裁剪功能需要的 `CropSettings` 类完全缺失

## ✅ 修改内容

### 1. ClipSettings - 完全重写

**之前（错误）：**
```python
class ClipSettings(BaseModel):
    brightness: float = Field(0.0, description="亮度 -1.0 到 1.0")
    contrast: float = Field(0.0, description="对比度 -1.0 到 1.0")
    saturation: float = Field(0.0, description="饱和度 -1.0 到 1.0")
    temperature: float = Field(0.0, description="色温 -1.0 到 1.0")
    hue: float = Field(0.0, description="色相 -1.0 到 1.0")
```

**现在（正确）：**
```python
class ClipSettings(BaseModel):
    """镜像 pyJianYingDraft.ClipSettings"""
    alpha: float = Field(1.0, description="透明度 (0.0-1.0)")
    rotation: float = Field(0.0, description="旋转角度（度）")
    scale_x: float = Field(1.0, description="X 轴缩放比例")
    scale_y: float = Field(1.0, description="Y 轴缩放比例")
    transform_x: float = Field(0.0, description="X 轴位置偏移")
    transform_y: float = Field(0.0, description="Y 轴位置偏移")
```

### 2. Position - 完全移除

```python
# ❌ 已删除 - pyJianYingDraft 中不存在此类
# class Position(BaseModel):
#     x: float
#     y: float
```

使用 `ClipSettings` 的 `transform_x` 和 `transform_y` 代替。

### 3. TextStyle - 添加缺失字段

**之前：**
```python
class TextStyle(BaseModel):
    bold: bool = Field(False)
    italic: bool = Field(False)
    underline: bool = Field(False)
```

**现在：**
```python
class TextStyle(BaseModel):
    """镜像 pyJianYingDraft.TextStyle"""
    font_size: float = Field(24.0, description="字体大小")
    color: List[float] = Field([1.0, 1.0, 1.0], description="文字颜色 RGB (0.0-1.0)")
    bold: bool = Field(False)
    italic: bool = Field(False)
    underline: bool = Field(False)
```

### 4. CropSettings - 新增

```python
class CropSettings(BaseModel):
    """镜像 pyJianYingDraft.CropSettings"""
    upper_left_x: float = Field(0.0, description="左上角 X 坐标 (0.0-1.0)")
    upper_left_y: float = Field(0.0, description="左上角 Y 坐标 (0.0-1.0)")
    upper_right_x: float = Field(1.0, description="右上角 X 坐标 (0.0-1.0)")
    upper_right_y: float = Field(0.0, description="右上角 Y 坐标 (0.0-1.0)")
    lower_left_x: float = Field(0.0, description="左下角 X 坐标 (0.0-1.0)")
    lower_left_y: float = Field(1.0, description="左下角 Y 坐标 (0.0-1.0)")
    lower_right_x: float = Field(1.0, description="右下角 X 坐标 (0.0-1.0)")
    lower_right_y: float = Field(1.0, description="右下角 Y 坐标 (0.0-1.0)")
```

## 🔄 受影响的 API 请求模型

### CreateTextSegmentRequest

**字段变更：**
```diff
- font_size: Optional[float]          # 移到 text_style 中
- color: Optional[str]                # 移到 text_style 中（改为 RGB 列表）
- position: Optional[Position]        # 删除
+ text_style: Optional[TextStyle]     # 现在包含 font_size 和 color
+ clip_settings: Optional[ClipSettings]  # 替代 position，支持更多变换
```

**使用示例：**
```python
# 之前
request = CreateTextSegmentRequest(
    text_content="Hello",
    font_size=24.0,
    color="#FFFFFF",
    position={"x": 0.5, "y": 0.0}
)

# 现在
request = CreateTextSegmentRequest(
    text_content="Hello",
    text_style={"font_size": 24.0, "color": [1.0, 1.0, 1.0]},
    clip_settings={"transform_x": 0.5, "transform_y": 0.0}
)
```

### CreateStickerSegmentRequest

**字段变更：**
```diff
- position: Optional[Position]        # 删除
- scale: Optional[float]              # 删除
+ clip_settings: Optional[ClipSettings]  # 包含 scale_x、scale_y 和位置
```

**使用示
例：**
```python
# 之前
request = CreateStickerSegmentRequest(
    material_url="...",
    position={"x": 0.5, "y": 0.5},
    scale=1.5
)

# 现在
request = CreateStickerSegmentRequest(
    material_url="...",
    clip_settings={
        "transform_x": 0.5,
        "transform_y": 0.5,
        "scale_x": 1.5,
        "scale_y": 1.5
    }
)
```

### CreateVideoSegmentRequest

**字段变更：**
```diff
+ crop_settings: Optional[CropSettings]  # 新增（之前示例中有但字段定义缺失）
```

**示例修复：**
- ✅ 添加：`speed: 1.0`（之前字段定义有但示例中遗漏）
- ✅ 添加：`change_pitch: False`（之前字段定义有但示例中遗漏）

## 📊 与 pyJianYingDraft 的对应关系

| segment_schemas.py | pyJianYingDraft | 状态 |
|-------------------|-----------------|------|
| `TimeRange` | `Timerange` | ⚠️ 名称不同，但结构对应 |
| `ClipSettings` | `ClipSettings` | ✅ 完全镜像 |
| `TextStyle` | `TextStyle` | ✅ 完全镜像 |
| `CropSettings` | `CropSettings` | ✅ 完全镜像 |
| ~~`Position`~~ | ❌ 不存在 | ❌ 已删除 |

## 🔧 转换逻辑参考

`app/utils/converter.py` 中已有正确的转换实现：

```python
def convert_clip_settings(self, transform_dict: Dict[str, Any]) -> ClipSettings:
    """转换变换设置"""
    return ClipSettings(
        alpha=transform_dict.get("opacity", 1.0),
        rotation=transform_dict.get("rotation", 0.0),
        scale_x=transform_dict.get("scale_x", 1.0),
        scale_y=transform_dict.get("scale_y", 1.0),
        transform_x=transform_dict.get("position_x", 0.0),
        transform_y=transform_dict.get("position_y", 0.0)
    )
```

## ⚠️ 破坏性变更警告

这是一个**破坏性变更**，会影响：

### 1. API 使用者
需要更新请求格式以匹配新的 schema 定义。

### 2. Coze 插件工具
需要同步更新：
- `coze_plugin/tools/` 中的工具函数
- `coze_plugin/raw_tools/` 中自动生成的 handler（需要重新生成）

### 3. 文档
需要更新 API 参考文档。

## ✅ 验证测试

运行以下命令验证修改：

```bash
python -c "from app.schemas.segment_schemas import ClipSettings, TextStyle, CropSettings, TimeRange; print('✅ 所有类成功导入')"
```

## 📚 设计原则

**核心原则：尽可能镜像 pyJianYingDraft 的类定义，而不是 AI 幻想制造的自定义类。**

### 为什么这样设计？

1. ✅ **减少混淆**：开发者可以直接参考 pyJianYingDraft 文档
2. ✅ **简化转换**：减少转换层的复杂度和出错可能
3. ✅ **保持一致**：API schema 反映底层库的真实结构
4. ✅ **易于维护**：当 pyJianYingDraft 更新时，更容易同步

### 避免的错误模式

- ❌ 不要创建"更友好"的抽象层（如 Position）
- ❌ 不要假设字段含义（如 ClipSettings = 图像调节）
- ❌ 不要省略重要字段（如 TextStyle 的 font_size）
- ❌ 不要在没有验证的情况下添加字段

## 📖 相关文档

- 详细修改记录：`docs/updates/SCHEMA_REFACTOR_PYJIANYINGDRAFT_MIRROR.md`
- 数据转换器：`app/utils/converter.py`
- 项目架构指南：`.github/copilot-instructions.md`
- pyJianYingDraft 库：https://github.com/GuanYixuan/pyJianYingDraft

## 🚀 下一步行动

### 必须完成

- [x] 更新 `app/schemas/segment_schemas.py`
- [ ] 更新 API 文档（`docs/reference/API_ENDPOINTS_REFERENCE.md`）
- [ ] 测试所有受影响的 API 端点
- [ ] 更新 Coze 插件工具以匹配新 schema
- [ ] 运行完整的测试套件

### 可选优化

- [ ] 为旧 API 提供兼容层（deprecated 字段）
- [ ] 重新生成 `coze_plugin/raw_tools/` 中的 handler
- [ ] 更新所有示例和教程

---

**修改日期**：2024-01-XX  
**修改人员**：基于用户反馈和 pyJianYingDraft 真实定义进行修正
