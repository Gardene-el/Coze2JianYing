# effect_infos

## 功能描述

将特效名称列表与时间线合并，生成 `add_effects` 工具所需的 `effect_infos` JSON 字符串。

纯计算工具，无网络请求，无文件 I/O。

## 输入参数

```python
class Input(NamedTuple):
    effects: str    # 特效名称数组，JSON 字符串，如 '["幻影","闪白"]'
    timelines: str  # 时间线 JSON 字符串，格式 '[{"start":…,"end":…},…]'
```

### 参数说明

| 参数        | 必填 | 说明                                               |
| ----------- | ---- | -------------------------------------------------- |
| `effects`   | ✅   | JSON 字符串，特效名称与 timelines 等长             |
| `timelines` | ✅   | 来自 `timelines/` 或 `audio_timelines/` 工具的输出 |

### 特效名称

特效名称对应 `pyJianYingDraft` 中 `VideoSceneEffectType` 的成员名（属性名）或显示名（`.value.name`）。

示例名称：`"幻影"`、`"闪白"`、`"模糊开场"`、`"镜头光晕"`

## 输出

```python
class Output(NamedTuple):
    effect_infos: str   # add_effects 所需的 JSON 字符串
    success: bool
    message: str
```

### 输出格式

```json
[
  { "effect_title": "幻影", "start": 0, "end": 2000000 },
  { "effect_title": "闪白", "start": 5000000, "end": 7000000 }
]
```

## 工作流衔接

```
timelines → effect_infos → add_effects
```
