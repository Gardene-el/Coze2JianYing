# Add Effects Tool

## 功能描述

向现有草稿添加特效轨道和特效片段。每次调用会创建一个新的特效轨道,包含指定的所有特效。支持特效的强度、位置、缩放等完整参数设置。

## 输入参数

### Input 类型定义

```python
class Input(NamedTuple):
    draft_id: str                              # 现有草稿的UUID
    effect_infos: Any                          # 特效信息：支持多种格式输入
```

### effect_infos 输入格式

支持多种输入格式,自动识别和处理:

#### 格式1: 数组对象(推荐用于静态配置)
```json
[
  {
    "effect_type": "模糊",
    "start": 0,
    "end": 3000,
    "intensity": 0.8,
    "position_x": 0.5,
    "position_y": 0.5,
    "scale": 1.5
  }
]
```

#### 格式2: 数组字符串(推荐用于动态配置)
数组中每个元素是 JSON 字符串。通常与 `make_effect_info` 工具配合使用:
```json
[
  "{\"effect_type\":\"模糊\",\"start\":0,\"end\":3000,\"intensity\":0.8}",
  "{\"effect_type\":\"锐化\",\"start\":3000,\"end\":6000}"
]
```

#### 格式3: JSON字符串
整个数组作为一个 JSON 字符串:
```json
"[{\"effect_type\":\"模糊\",\"start\":0,\"end\":3000,\"intensity\":0.8}]"
```

#### 格式4: 其他可迭代类型
工具还支持元组(tuple)等其他可迭代类型,会自动转换为列表处理。

#### 必需字段
- `effect_type`: 特效类型名称
- `start`: 开始时间(毫秒)
- `end`: 结束时间(毫秒)

#### 可选字段
- `intensity`: 特效强度(0.0-1.0,默认1.0)
- `position_x`: X轴位置(用于局部特效)
- `position_y`: Y轴位置(用于局部特效)
- `scale`: 特效作用区域缩放(默认1.0)
- `properties`: 自定义特效属性字典

## 输出结果

### Output 类型定义

```python
class Output(NamedTuple):
    segment_ids: List[str]                 # 生成的片段UUID列表
    segment_infos: List[Dict[str, Any]]    # 片段信息列表
    success: bool                          # 操作是否成功
    message: str                           # 状态消息
```

### segment_infos 格式

```json
[
  {
    "id": "efde9038-64b8-40d2-bdab-fca68e6bf943",
    "start": 0,
    "end": 3000
  }
]
```

## 使用示例

### 基本用法

#### 方法1: 使用数组格式(推荐用于静态配置)

```python
from tools.add_effects.handler import handler, Input
from runtime import Args

# 创建输入参数(数组格式)
input_data = Input(
    draft_id="d5eaa880-ae11-441c-ae7e-1872d95d108f",
    effect_infos=[{
        "effect_type": "模糊",
        "start": 0,
        "end": 3000,
        "intensity": 0.8
    }]
)

# 模拟Args对象
class MockArgs:
    def __init__(self, input_data):
        self.input = input_data

# 调用处理函数
result = handler(MockArgs(input_data))

print(f"成功: {result.success}")
print(f"片段数量: {len(result.segment_ids)}")
print(f"片段ID: {result.segment_ids}")
```

#### 方法2: 使用数组字符串格式(推荐用于动态配置)

配合 `make_effect_info` 工具使用:

```python
from tools.make_effect_info.handler import handler as make_effect_info_handler
from tools.add_effects.handler import handler as add_effects_handler

# 步骤1: 使用 make_effect_info 生成特效信息字符串
effect1_result = make_effect_info_handler(MockArgs(Input(
    effect_type="模糊",
    start=0,
    end=3000,
    intensity=0.8
)))

effect2_result = make_effect_info_handler(MockArgs(Input(
    effect_type="锐化",
    start=3000,
    end=6000
)))

# 步骤2: 将字符串收集到数组中
effect_infos_array = [
    effect1_result.effect_info_string,
    effect2_result.effect_info_string
]

# 步骤3: 传递数组字符串给 add_effects
result = add_effects_handler(MockArgs(Input(
    draft_id="d5eaa880-ae11-441c-ae7e-1872d95d108f",
    effect_infos=effect_infos_array  # 数组字符串格式
)))

print(f"成功添加 {len(result.segment_ids)} 个特效")
```

#### 方法3: 使用JSON字符串格式

```python
# 创建输入参数(JSON字符串格式)
input_data = Input(
    draft_id="d5eaa880-ae11-441c-ae7e-1872d95d108f",
    effect_infos='[{"effect_type":"模糊","start":0,"end":3000,"intensity":0.8}]'
)
```

### 复杂参数示例

#### 数组格式:
```json
{
    "draft_id": "d5eaa880-ae11-441c-ae7e-1872d95d108f",
    "effect_infos": [
        {
            "effect_type": "模糊",
            "start": 0,
            "end": 3000,
            "intensity": 0.7,
            "position_x": 0.5,
            "position_y": 0.5,
            "scale": 1.5
        },
        {
            "effect_type": "锐化",
            "start": 3000,
            "end": 6000,
            "intensity": 0.9
        }
    ]
}
```

#### 带自定义属性的特效:
```json
{
    "draft_id": "d5eaa880-ae11-441c-ae7e-1872d95d108f",
    "effect_infos": [
        {
            "effect_type": "高级模糊",
            "start": 0,
            "end": 5000,
            "intensity": 0.8,
            "properties": {
                "blur_radius": 15,
                "edge_detection": true,
                "blur_type": "gaussian"
            }
        }
    ]
}
```

## 注意事项

### 时间单位
- 所有时间参数使用毫秒(ms)为单位
- `start` 和 `end` 定义特效在时间轴上的作用区间
- 特效会应用于该时间段内的视频内容

### 特效类型
- `effect_type` 的值应该是剪映支持的特效名称
- 常用特效: "模糊"、"锐化"、"马赛克"、"黑白"、"怀旧"等
- 具体支持的特效以剪映版本为准

### 位置和缩放
- `position_x` 和 `position_y` 用于局部特效的定位
- `scale` 用于控制特效作用区域的大小
- 这些参数对全局特效可能无效

### 轨道管理
- 每次调用都会创建一个新的特效轨道
- 同一轨道内的特效按时间顺序应用
- 不同轨道的特效可以叠加

### 错误处理
- 如果draft_id不存在,返回失败状态
- 如果effect_infos格式无效,返回详细错误信息
- 如果特效类型不支持,仍会创建片段(由剪映处理)

### 性能考虑
- 大量特效可能影响视频渲染性能
- 建议合理控制特效数量和强度
- 复杂的自定义属性可能增加处理时间

## 与其他工具的集成

### 与 create_draft 配合使用
1. 使用 `create_draft` 创建基础草稿
2. 使用 `add_effects` 添加特效轨道
3. 使用 `export_drafts` 导出完整配置

### 与 make_effect_info 配合使用
1. 使用 `make_effect_info` 生成特效配置字符串
2. 将多个字符串收集到数组
3. 使用 `add_effects` 添加到草稿

### 在 Coze 工作流中的应用

#### 动态配置场景(推荐使用 make_effect_info + add_effects):
```
1. [make_effect_info 节点1] → 生成特效1配置
2. [make_effect_info 节点2] → 生成特效2配置
3. [数组收集节点] → 组合成数组
4. [add_effects 节点] → 添加到草稿
```

#### 静态配置场景(直接使用 add_effects):
```
1. [add_effects 节点] → 直接传入数组对象
```

## 设计参考

本工具的设计严格遵循以下参考资料:
1. **源码参考**: `tools/add_images/handler.py`, `tools/add_audios/handler.py`
2. **PR参考**: [PR #17](https://github.com/Gardene-el/Coze2JianYing/pull/17), [PR #25](https://github.com/Gardene-el/Coze2JianYing/pull/25)
3. **Issue参考**: [Issue #16](https://github.com/Gardene-el/Coze2JianYing/issues/16), [Issue #24](https://github.com/Gardene-el/Coze2JianYing/issues/24)
4. **数据结构**: `EffectSegmentConfig` in `data_structures/draft_generator_interface/models.py`

## 完整工作流示例

```python
# 步骤1: 创建草稿
from tools.create_draft.handler import handler as create_draft_handler
draft_result = create_draft_handler(MockArgs(CreateDraftInput(
    draft_name="特效演示草稿"
)))
draft_id = draft_result.draft_id

# 步骤2: 使用 make_effect_info 创建多个特效配置
from tools.make_effect_info.handler import handler as make_effect_info_handler

# 创建模糊特效
blur_effect = make_effect_info_handler(MockArgs(EffectInput(
    effect_type="模糊",
    start=0,
    end=3000,
    intensity=0.7
)))

# 创建锐化特效
sharpen_effect = make_effect_info_handler(MockArgs(EffectInput(
    effect_type="锐化",
    start=3000,
    end=6000,
    intensity=0.9
)))

# 步骤3: 收集特效配置到数组
effect_infos = [
    blur_effect.effect_info_string,
    sharpen_effect.effect_info_string
]

# 步骤4: 添加特效到草稿
from tools.add_effects.handler import handler as add_effects_handler
result = add_effects_handler(MockArgs(AddEffectsInput(
    draft_id=draft_id,
    effect_infos=effect_infos
)))

print(f"成功添加 {len(result.segment_ids)} 个特效")
print(f"特效ID: {result.segment_ids}")

# 步骤5: 导出草稿
from tools.export_drafts.handler import handler as export_drafts_handler
export_result = export_drafts_handler(MockArgs(ExportInput(
    draft_ids=[draft_id]
)))
```
