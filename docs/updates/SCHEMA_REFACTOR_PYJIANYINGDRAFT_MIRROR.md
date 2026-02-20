# Schema 重构：镜像 pyJianYingDraft 类定义

## 修改日期
2024-01-XX

## 修改摘要

本次重构将 `app/schemas/general_schemas.py` 中的数据模型改为完全镜像 pyJianYingDraft 库的真实类定义，移除了 AI 错误生成的自定义类。

### 主要修改

1. ✅ **重新定义 ClipSettings** - 从错误的"图像调节参数"改为正确的"变换参数"
2. ✅ **移除 Position 类** - pyJianYingDraft 中不存在此类，位置通过 ClipSettings 表示
3. ✅ **完善 TextStyle** - 添加缺失的 font_size 和 color 字段
4. ✅ **新增 CropSettings** - 添加之前缺失的裁剪设置类
5. ✅ **更新请求模型** - CreateTextSegmentRequest、CreateStickerSegmentRequest 等
6. ✅ **修复代码问题** - 移除未使用的导入和重复的字段定义

## 问题描述

`app/schemas/general_schemas.py` 中的 `ClipSettings`、`Position` 和 `TextStyle` 类是 AI 错误生成的，不符合 pyJianYingDraft 库的实际定义。这导致了以下问题：

1. **ClipSettings** 被错误定义为图像调节参数（亮度、对比度等），而实际应该是变换参数（位置、缩放、旋转、透明度）
2. **Position** 类在 pyJianYingDraft 中根本不存在，位置信息通过 ClipSettings 的 `transform_x` 和 `transform_y` 表示
3. **TextStyle** 缺少关键字段（字体大小、颜色），只有格式标记（加粗、斜体、下划线）

## 解决方案

### 1. 重新定义 ClipSettings（镜像 pyJianYingDraft）

**修改前（错误）：**
```python
class ClipSettings(BaseModel):
    """图像调节设置"""
    brightness: float = Field(0.0, description="亮度 -1.0 到 1.0")
    contrast: float = Field(0.0, description="对比度 -1.0 到 1.0")
    saturation: float = Field(0.0, description="饱和度 -1.0 到 1.0")
    temperature: float = Field(0.0, description="色温 -1.0 到 1.0")
    hue: float = Field(0.0, description="色相 -1.0 到 1.0")
```

**修改后（正确）：**
```python
class ClipSettings(BaseModel):
    """
    图像调节设置（镜像 pyJianYingDraft.ClipSettings）
    对应 pyJianYingDraft 的 ClipSettings 类，用于控制片段的变换属性
    """
    alpha: float = Field(1.0, description="透明度 (0.0-1.0)", ge=0.0, le=1.0)
    rotation: float = Field(0.0, description="旋转角度（度）")
    scale_x: float = Field(1.0, description="X 轴缩放比例", gt=0)
    scale_y: float = Field(1.0, description="Y 轴缩放比例", gt=0)
    transform_x: float = Field(0.0, description="X 轴位置偏移")
    transform_y: float = Field(0.0, description="Y 轴位置偏移")
```

### 2. 移除 Position 类，使用 ClipSettings 代替

**修改前：**
```python
class Position(BaseModel):
    """位置信息"""
    x: float = Field(0.0, description="X 坐标")
    y: float = Field(0.0, description="Y 坐标")

class CreateTextSegmentRequest(BaseModel):
    # ...
    position: Optional[Position] = Field(None, description="位置")
```

**修改后：**
```python
# Position 类已删除

class CreateTextSegmentRequest(BaseModel):
    # ...
    clip_settings: Optional[ClipSettings] = Field(
        None, description="图像调节设置（位置、缩放、旋转、透明度）"
    )
```

### 3. 完善 TextStyle（镜像 pyJianYingDraft）

**修改前：**
```python
class TextStyle(BaseModel):
    """文本样式"""
    bold: bool = Field(False, description="是否加粗")
    italic: bool = Field(False, description="是否斜体")
    underline: bool = Field(False, description="是否下划线")
```

**修改后：**
```python
class TextStyle(BaseModel):
    """
    文本样式（镜像 pyJianYingDraft.TextStyle）
    对应 pyJianYingDraft 的 TextStyle 类，用于控制文本的样式属性
    """
    font_size: float = Field(24.0, description="字体大小", gt=0)
    color: List[float] = Field([1.0, 1.0, 1.0], description="文字颜色 RGB (0.0-1.0)")
    bold: bool = Field(False, description="是否加粗")
    italic: bool = Field(False, description="是否斜体")
    underline: bool = Field(False, description="是否下划线")
```

### 4. 新增 CropSettings（镜像 pyJianYingDraft）

添加了之前缺失的 `CropSettings` 类，用于裁剪功能：

```python
class CropSettings(BaseModel):
    """
    裁剪设置（镜像 pyJianYingDraft.CropSettings）
    对应 pyJianYingDraft 的 CropSettings 类，用于定义裁剪区域的四个角点坐标
    """
    upper_left_x: float = Field(0.0, description="左上角 X 坐标 (0.0-1.0)", ge=0.0, le=1.0)
    upper_left_y: float = Field(0.0, description="左上角 Y 坐标 (0.0-1.0)", ge=0.0, le=1.0)
    upper_right_x: float = Field(1.0, description="右上角 X 坐标 (0.0-1.0)", ge=0.0, le=1.0)
    upper_right_y: float = Field(0.0, description="右上角 Y 坐标 (0.0-1.0)", ge=0.0, le=1.0)
    lower_left_x: float = Field(0.0, description="左下角 X 坐标 (0.0-1.0)", ge=0.0, le=1.0)
    lower_left_y: float = Field(1.0, description="左下角 Y 坐标 (0.0-1.0)", ge=0.0, le=1.0)
    lower_right_x: float = Field(1.0, description="右下角 X 坐标 (0.0-1.0)", ge=0.0, le=1.0)
    lower_right_y: float = Field(1.0, description="右下角 Y 坐标 (0.0-1.0)", ge=0.0, le=1.0)
```

## 受影响的 API 请求模型

### CreateTextSegmentRequest

**字段变更：**
- ❌ 移除：`font_size: Optional[float]`
- ❌ 移除：`color: Optional[str]`（十六进制格式）
- ❌ 移除：`position: Optional[Position]`
- ✅ 修改：`text_style: Optional[TextStyle]`（现在包含 font_size 和 color）
- ✅ 新增：`clip_settings: Optional[ClipSettings]`（替代 position，并支持更多变换）

### CreateStickerSegmentRequest

**字段变更：**
- ❌ 移除：`position: Optional[Position]`
- ❌ 移除：`scale: Optional[float]`
- ✅ 新增：`clip_settings: Optional[ClipSettings]`（包含 scale_x、scale_y 和位置）

### CreateVideoSegmentRequest

**字段变更：**
- ✅ 新增：`crop_settings: Optional[CropSettings]`（之前示例中有但字段定义缺失）

**示例修复：**
- ✅ 添加：`speed: 1.0`（之前字段定义有但示例中遗漏）
- ✅ 添加：`change_pitch: False`（之前字段定义有但示例中遗漏）

## 与 pyJianYingDraft 的对应关系

| general_schemas.py | pyJianYingDraft | 说明 |
|-------------------|-----------------|------|
| `ClipSettings` | `ClipSettings` | ✅ 完全镜像 |
| `TextStyle` | `TextStyle` | ✅ 完全镜像 |
| `CropSettings` | `CropSettings` | ✅ 完全镜像 |
| `TimeRange` | `Timerange` | ⚠️ 名称不同，但概念对应 |
| ~~`Position`~~ | ❌ 不存在 | 已删除，使用 ClipSettings 代替 |

## 转换逻辑参考

在 `app/utils/converter.py` 中已有正确的转换逻辑：

```python
def convert_clip_settings(self, transform_dict: Dict[str, Any]) -> ClipSettings:
    """
    转换变换设置
    Draft Generator Interface: {position_x, position_y, scale_x, scale_y, rotation, opacity}
    pyJianYingDraft: ClipSettings(alpha, rotation, scale_x, scale_y, transform_x, transform_y)
    """
    settings = ClipSettings(
        alpha=get_value_or_default("opacity", 1.0),
        rotation=get_value_or_default("rotation", 0.0),
        scale_x=get_value_or_default("scale_x", 1.0),
        scale_y=get_value_or_default("scale_y", 1.0),
        transform_x=get_value_or_default("position_x", 0.0),
        transform_y=get_value_or_default("position_y", 0.0)
    )
    return settings
```

## 兼容性影响

### ⚠️ 破坏性变更

此修改是**破坏性变更**，会影响：

1. **API 使用者**：需要更新请求格式
   - 文本段：从 `font_size` + `color` + `position` 改为 `text_style` + `clip_settings`
   - 贴纸段：从 `position` + `scale` 改为 `clip_settings`

2. **Coze 插件工具**：需要同步更新
   - `coze_plugin/tools/add_captions/` 等工具需要适配新的参数结构
   - `coze_plugin/raw_tools/` 中自动生成的工具需要重新生成

### ✅ 向前兼容

转换器（`app/utils/converter.py`）已经正确实现了转换逻辑，无需修改。

## 后续工作

### 必须完成

1. ✅ 更新 `app/schemas/general_schemas.py` 
2. ⏳ 更新相关 API 文档（`docs/reference/API_ENDPOINTS_REFERENCE.md`）
3. ⏳ 测试所有受影响的 API 端点
4. ⏳ 更新 Coze 插件工具以匹配新的 schema

### 可选优化

1. 考虑是否需要为旧 API 提供兼容层（deprecated 字段）
2. 为 `coze_plugin/raw_tools/` 重新运行 handler_generator
3. 更新所有示例和测试用例

## 参考文档

- `app/utils/converter.py` - 数据结构转换器（已有正确实现）
- `.github/copilot-instructions.md` - 项目架构指南
- `docs/reference/DRAFT_INTERFACE_QUICK_REFERENCE.md` - 接口快速参考
- pyJianYingDraft 库文档

## 设计原则总结

**核心原则**：尽可能镜像 pyJianYingDraft 的类定义，而不是 AI 幻想制造的自定义类。

- ✅ **镜像真实库**：直接使用 pyJianYingDraft 的类结构和字段名
- ✅ **避免抽象**：不要创建"更友好"的抽象层（如 Position），除非有充分理由
- ✅ **保持一致**：API schema 应该反映底层库的真实结构
- ✅ **文档清晰**：在类定义中明确标注"镜像 pyJianYingDraft.XXX"

这种设计使得：
1. 开发者更容易理解 API 和底层库的对应关系
2. 减少转换层的复杂度和出错可能
3. 便于参考 pyJianYingDraft 文档进行开发

## 实际修改清单

### general_schemas.py 文件修改

#### 1. 导入部分 (L11-14)
- ❌ 移除：`from enum import Enum`（未使用）
- ❌ 移除：`from pydantic import validator`（未使用）

#### 2. ClipSettings 类 (L25-36)
- 完全重写，从 5 个错误字段改为 6 个正确字段
- 新字段：alpha, rotation, scale_x, scale_y, transform_x, transform_y

#### 3. TextStyle 类 (L39-48)
- ✅ 新增：`font_size: float` 字段
- ✅ 新增：`color: List[float]` 字段（RGB 0.0-1.0）
- ✅ 保留：bold, italic, underline 字段

#### 4. Position 类 (L43-47)
- ❌ 完全移除（原有 x, y 两个字段）

#### 5. CropSettings 类 (L51-80)
- ✅ 新增整个类（8 个角点坐标字段）

#### 6. CreateVideoSegmentRequest (L117-118)
- ✅ 新增：`crop_settings: Optional[CropSettings]` 字段
- ✅ 更新示例中的 clip_settings 内容
- ✅ 修复示例：添加缺失的 `speed` 和 `change_pitch` 字段

#### 7. CreateTextSegmentRequest (L153-161)
- ❌ 移除：`font_size: Optional[float]` 字段
- ❌ 移除：`color: Optional[str]` 字段
- ❌ 移除：`position: Optional[Position]` 字段
- ✅ 修改：`text_style` 字段描述
- ✅ 新增：`clip_settings: Optional[ClipSettings]` 字段

#### 8. CreateStickerSegmentRequest (L190-195)
- ❌ 移除：`position: Optional[Position]` 字段
- ❌ 移除：`scale: Optional[float]` 字段
- ✅ 新增：`clip_settings: Optional[ClipSettings]` 字段

#### 9. AddSegmentToDraftResponse (L304)
- ✅ 移除重复的 `timestamp` 字段定义

### 文件统计

- **总行数变化**：约 +40 行（主要是 CropSettings 和更详细的注释）
- **类数量**：4 个（原 4 个，但 Position 被移除，CropSettings 被新增）
- **受影响的请求模型**：3 个（CreateVideoSegmentRequest, CreateTextSegmentRequest, CreateStickerSegmentRequest）