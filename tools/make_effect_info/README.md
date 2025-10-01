# Make Effect Info Tool

## 功能描述

生成单个特效配置的 JSON 字符串表示。这是 `add_effects` 工具的辅助函数,用于创建可以被组合成数组的特效信息字符串。

### 使用场景

当你需要在 Coze 工作流中动态构建多个特效配置时,可以:
1. 多次调用 `make_effect_info` 生成每个特效的配置字符串
2. 将这些字符串收集到一个数组中
3. 将该数组作为 `effect_infos` 参数传递给 `add_effects` 工具

### 参数数量说明

本工具共有 **8 个参数**:
- **3 个必需参数**: `effect_type`, `start`, `end`
- **5 个可选参数**: `intensity`, `position_x`, `position_y`, `scale`, `properties`

这些参数基于 `EffectSegmentConfig` 数据结构设计,映射了剪映中特效的主要可配置属性。

## 输入参数

### Input 类型定义

```python
class Input(NamedTuple):
    # 必需字段
    effect_type: str                            # 特效类型名称(如"模糊"、"锐化"、"马赛克")
    start: int                                  # 开始时间(毫秒)
    end: int                                    # 结束时间(毫秒)
    
    # 可选:特效属性
    intensity: Optional[float] = 1.0            # 特效强度(0.0-1.0,默认1.0)
    
    # 可选:位置(用于局部特效)
    position_x: Optional[float] = None          # X位置(用于局部特效)
    position_y: Optional[float] = None          # Y位置(用于局部特效)
    scale: Optional[float] = 1.0                # 缩放(默认1.0)
    
    # 可选:自定义属性
    properties: Optional[str] = None            # 自定义特效属性的JSON字符串
```

### 参数说明

#### 必需参数
- `effect_type`: 特效类型名称,如"模糊"、"锐化"、"马赛克"、"色彩校正"等
- `start`: 特效在时间轴上的开始时间(毫秒)
- `end`: 特效在时间轴上的结束时间(毫秒)

#### 可选参数

**特效强度**:
- `intensity`: 特效的强度,范围 0.0-1.0,默认 1.0(最大强度)

**位置控制**(用于局部特效):
- `position_x`: X轴位置坐标
- `position_y`: Y轴位置坐标
- `scale`: 特效作用区域的缩放比例,默认 1.0

**自定义属性**:
- `properties`: 用于传递特定特效的额外参数,需要是JSON字符串格式
  - 例如: `'{"blur_radius": 10, "color": "#FF0000"}'`

所有可选参数只有在设置了非默认值时才会包含在输出字符串中。这样可以保持输出紧凑。

#### 特效类型说明

`effect_type` 的可用值取决于剪映支持的特效类型。常见的特效包括:

**基础特效**:
- `"模糊"` - 模糊效果
- `"锐化"` - 锐化效果
- `"马赛克"` - 马赛克/像素化效果
- `"黑白"` - 黑白效果
- `"怀旧"` - 怀旧/复古效果

**高级特效**:
- `"色彩校正"` - 色彩调整
- `"发光"` - 发光效果
- `"阴影"` - 阴影效果
- `"边框"` - 边框效果
- `"抖动"` - 抖动/晃动效果

**注意**: 
- 特效名称建议使用中文(这是剪映的标准)
- 具体支持的特效类型以剪映实际版本为准
- 某些特效可能需要通过 `properties` 参数传递额外配置

## 输出结果

### Output 类型定义

```python
class Output(NamedTuple):
    effect_info_string: str                     # 特效信息的 JSON 字符串
    success: bool                               # 操作是否成功
    message: str                                # 状态消息
```

### 输出格式

输出是一个紧凑的 JSON 字符串,例如:

```json
"{\"effect_type\":\"模糊\",\"start\":0,\"end\":3000}"
```

或带有可选参数:

```json
"{\"effect_type\":\"模糊\",\"start\":0,\"end\":3000,\"intensity\":0.8,\"position_x\":0.5,\"position_y\":0.5}"
```

## 使用示例

### 示例 1: 基本用法

```python
from tools.make_effect_info.handler import handler, Input
from runtime import Args

# 创建输入参数(仅必需字段)
input_data = Input(
    effect_type="模糊",
    start=0,
    end=3000
)

# 模拟Args对象
class MockArgs:
    def __init__(self, input_data):
        self.input = input_data

# 调用处理函数
result = handler(MockArgs(input_data))

print(f"成功: {result.success}")
print(f"生成的字符串: {result.effect_info_string}")
# 输出: {"effect_type":"模糊","start":0,"end":3000}
```

### 示例 2: 带完整参数

```python
# 创建输入参数(包含可选字段)
input_data = Input(
    effect_type="模糊",
    start=0,
    end=5000,
    intensity=0.7,
    position_x=0.5,
    position_y=0.5,
    scale=1.5
)

result = handler(MockArgs(input_data))
print(result.effect_info_string)
# 输出: {"effect_type":"模糊","start":0,"end":5000,"intensity":0.7,"position_x":0.5,"position_y":0.5,"scale":1.5}
```

### 示例 3: 带自定义属性

```python
import json

# 创建自定义属性
custom_props = {
    "blur_radius": 15,
    "edge_detection": True
}

input_data = Input(
    effect_type="高级模糊",
    start=1000,
    end=4000,
    intensity=0.9,
    properties=json.dumps(custom_props)
)

result = handler(MockArgs(input_data))
print(result.effect_info_string)
# 输出: {"effect_type":"高级模糊","start":1000,"end":4000,"intensity":0.9,"properties":{"blur_radius":15,"edge_detection":true}}
```

### 示例 4: 与 add_effects 配合使用(完整工作流)

这是本工具的主要使用场景:

```python
# 步骤 1: 使用 make_effect_info 生成多个特效信息字符串
effect1_info = make_effect_info(
    effect_type="模糊",
    start=0,
    end=3000,
    intensity=0.5
)
# 返回: {"effect_type":"模糊","start":0,"end":3000,"intensity":0.5}

effect2_info = make_effect_info(
    effect_type="锐化",
    start=3000,
    end=6000,
    intensity=0.8
)
# 返回: {"effect_type":"锐化","start":3000,"end":6000,"intensity":0.8}

# 步骤 2: 将字符串收集到数组中
effect_infos_array = [
    effect1_info.effect_info_string,
    effect2_info.effect_info_string
]

# 步骤 3: 将数组字符串传递给 add_effects
add_effects(
    draft_id="your-draft-uuid",
    effect_infos=effect_infos_array  # 数组字符串格式!
)
```

### 示例 5: 在 Coze 工作流中使用

在 Coze 工作流中,你可以这样组合使用:

```
1. [make_effect_info 节点1] → 生成第一个特效配置字符串
   输入: effect_type="模糊", start=0, end=3000, intensity=0.5
   输出: effect_info_string

2. [make_effect_info 节点2] → 生成第二个特效配置字符串
   输入: effect_type="锐化", start=3000, end=6000
   输出: effect_info_string

3. [数组节点] → 将多个字符串组合成数组
   输入: [节点1.effect_info_string, 节点2.effect_info_string]
   输出: effect_infos_array

4. [add_effects 节点] → 添加特效到草稿
   输入: draft_id="...", effect_infos=effect_infos_array
   输出: segment_ids, segment_infos
```

## 注意事项

### 输出优化
- 工具只会在输出中包含非默认值的参数
- 这使得输出字符串保持紧凑,减少数据传输
- 例如: 如果 `intensity=1.0`(默认值),则不会包含在输出中

### 时间参数验证
- `start` 必须 >= 0
- `end` 必须 > `start`
- 时间单位为毫秒

### 与 add_effects 的兼容性
- 输出的字符串格式完全兼容 `add_effects` 的 `effect_infos` 参数
- 可以使用数组字符串格式(新增)、数组对象格式或 JSON 字符串格式

### 自定义属性格式
- `properties` 参数必须是有效的 JSON 字符串
- 如果提供了无效的 JSON,工具会返回错误消息
- 空的 properties 对象不会包含在输出中

## 错误处理

工具会验证以下情况:

1. **缺少必需参数**: 如果缺少 `effect_type`、`start` 或 `end`,返回错误
2. **无效时间范围**: 如果 `start < 0` 或 `end <= start`,返回错误
3. **无效的 properties JSON**: 如果 properties 不是有效的 JSON 字符串,返回错误
4. **其他异常**: 任何意外错误都会被捕获并返回错误消息

## 与其他工具的关系

### make_effect_info → add_effects
这是主要的使用流程:
1. `make_effect_info` 生成单个特效的配置字符串
2. 多个字符串组合成数组
3. `add_effects` 接收数组并添加特效到草稿

### 替代方案
如果你的特效配置是静态的,也可以:
- 直接使用数组对象格式传递给 `add_effects`
- 使用 JSON 字符串格式传递给 `add_effects`

`make_effect_info` 主要用于需要动态构建配置的场景。

## 设计参考

本工具的设计严格遵循以下参考资料:
1. **源码参考**: `tools/make_image_info/handler.py`, `tools/make_audio_info/handler.py`
2. **PR参考**: [PR #17](https://github.com/Gardene-el/CozeJianYingAssistent/pull/17), [PR #25](https://github.com/Gardene-el/CozeJianYingAssistent/pull/25)
3. **Issue参考**: [Issue #16](https://github.com/Gardene-el/CozeJianYingAssistent/issues/16), [Issue #24](https://github.com/Gardene-el/CozeJianYingAssistent/issues/24)
4. **数据结构**: `EffectSegmentConfig` in `data_structures/draft_generator_interface/models.py`
