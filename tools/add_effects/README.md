# add_effects - 添加特效轨道工具

## 功能描述
将特效内容添加到现有草稿中，通过创建新的特效轨道。每次调用此工具都会创建一个包含所有特效片段的新轨道。

## 输入参数

### Input 类型定义
```python
class Input(NamedTuple):
    draft_id: str                               # 要修改的草稿UUID
    effects: List[Dict[str, Any]]               # 特效字典列表
    default_intensity: Optional[float] = 1.0   # 默认特效强度
    default_position_x: Optional[float] = None # 默认水平位置
    default_position_y: Optional[float] = None # 默认垂直位置
    default_scale: Optional[float] = 1.0       # 默认缩放因子
```

### 特效字典格式
每个特效必须包含以下字段：
```python
{
    "effect_type": str,             # 特效类型名称(必需)
    "start_time": int,              # 开始时间(毫秒，必需)
    "end_time": int,                # 结束时间(毫秒，必需)
    "intensity": float,             # 可选：特效强度(0-2)
    "position_x": float,            # 可选：水平位置
    "position_y": float,            # 可选：垂直位置
    "scale": float,                 # 可选：缩放因子(>0)
    "properties": Dict[str, Any]    # 可选：额外特效属性
}
```

### 参数说明

- **draft_id**: 目标草稿的UUID字符串，必需参数
- **effects**: 特效字典列表，必需参数，至少包含一个有效特效
- **default_intensity**: 默认特效强度，范围0-2，默认1.0
- **default_position_x**: 默认水平位置，如未指定则为None
- **default_position_y**: 默认垂直位置，如未指定则为None
- **default_scale**: 默认缩放因子，必须大于0，默认1.0

## 输出结果

### Output 类型定义
```python
class Output(NamedTuple):
    success: bool = True              # 操作成功状态
    message: str = "特效轨道添加成功"    # 状态消息
    track_index: int = -1             # 创建的轨道索引
    total_effects: int = 0            # 添加的特效总数
```

## 使用示例

### 基本用法
```json
{
  "tool": "add_effects",
  "input": {
    "draft_id": "uuid-of-draft",
    "effects": [
      {
        "effect_type": "光效闪烁",
        "start_time": 1000,
        "end_time": 3000
      },
      {
        "effect_type": "粒子爆炸",
        "start_time": 5000,
        "end_time": 7000
      }
    ]
  }
}
```

### 自定义特效参数
```json
{
  "tool": "add_effects",
  "input": {
    "draft_id": "uuid-of-draft",
    "effects": [
      {
        "effect_type": "光芒四射",
        "start_time": 2000,
        "end_time": 5000,
        "intensity": 1.5,
        "position_x": 0.5,
        "position_y": 0.3,
        "scale": 2.0
      },
      {
        "effect_type": "雨滴效果",
        "start_time": 6000,
        "end_time": 10000,
        "properties": {
          "drop_count": 200,
          "speed": 1.2,
          "opacity": 0.8
        }
      }
    ],
    "default_intensity": 1.0,
    "default_position_x": 0.5,
    "default_position_y": 0.5
  }
}
```

### 复杂特效组合
```json
{
  "tool": "add_effects",
  "input": {
    "draft_id": "uuid-of-draft",
    "effects": [
      {
        "effect_type": "烟花绽放",
        "start_time": 0,
        "end_time": 2000,
        "intensity": 1.8,
        "position_x": 0.3,
        "position_y": 0.2,
        "properties": {
          "color": "#FF6B6B",
          "particle_count": 150,
          "explosion_radius": 300
        }
      },
      {
        "effect_type": "光束扫描",
        "start_time": 1500,
        "end_time": 4000,
        "intensity": 1.2,
        "properties": {
          "beam_width": 50,
          "scan_speed": 2.0,
          "color": "#00D4FF"
        }
      }
    ]
  }
}
```

### 在Coze工作流中使用
```json
{
  "step": 5,
  "name": "添加视觉特效",
  "tool": "add_effects",
  "input": {
    "draft_id": "{{project_draft.draft_id}}",
    "effects": "{{user_input.effect_list}}",
    "default_intensity": "{{user_input.effect_strength}}"
  },
  "output_variable": "effects_added"
}
```

## 注意事项

### 输入验证
- draft_id必须是有效的UUID格式
- effects不能为空，必须包含至少一个有效特效
- 每个特效必须有effect_type、start_time、end_time字段
- end_time必须大于start_time
- intensity必须在0-2范围内
- scale必须是大于0的数值

### 特效时间管理
- 时间单位为毫秒
- 特效可以重叠显示
- 支持跨越其他轨道内容
- 自动更新草稿总时长

### 特效类型支持

#### 光效类特效
- **光芒四射**: 从中心向外辐射光线
- **光效闪烁**: 间歇性光效闪烁
- **光束扫描**: 光束移动扫描效果
- **霓虹发光**: 霓虹灯发光效果

#### 粒子类特效
- **粒子爆炸**: 粒子爆炸扩散效果
- **烟花绽放**: 烟花爆炸效果
- **雨滴效果**: 下雨粒子效果
- **雪花飘落**: 雪花飘落效果
- **火焰燃烧**: 火焰粒子效果

#### 动态类特效
- **镜头光晕**: 镜头光晕效果
- **动态模糊**: 运动模糊效果
- **震动效果**: 画面震动效果
- **缩放脉冲**: 脉冲式缩放效果

### 特效属性配置
特效的properties字段支持以下通用属性：
- **color**: 特效颜色 (十六进制格式)
- **opacity**: 透明度 (0-1)
- **speed**: 动画速度 (>0)
- **particle_count**: 粒子数量 (整数)
- **size**: 特效大小
- **duration_variation**: 持续时间变化

### 位置和变换
- **坐标系统**: 相对于视频画面
- **position_x/y**: 特效中心位置
- **scale**: 特效整体缩放
- **intensity**: 特效强度/不透明度

### 性能考虑
- 复杂特效会影响渲染性能
- 大量重叠特效可能造成性能问题
- 建议根据设备性能调整特效数量和复杂度
- 高强度特效建议限制同时播放数量

### 常见使用场景
- **节庆视频**: 烟花、彩带等庆祝特效
- **科技视频**: 光效、粒子等科技感特效
- **自然场景**: 雨雪、火焰等自然特效
- **转场增强**: 配合转场使用的装饰特效
- **重点突出**: 高亮、发光等强调特效

### 错误处理
- UUID格式验证失败会返回详细错误信息
- 草稿不存在会返回相应错误
- 特效格式验证失败会指出具体问题
- 时间范围验证失败会返回错误详情
- 参数超出范围会提供合理建议

## 相关工具

- `create_draft`: 创建新草稿
- `add_videos`: 添加视频轨道
- `add_audios`: 添加音频轨道
- `add_captions`: 添加字幕轨道
- `add_images`: 添加图片轨道
- `export_drafts`: 导出草稿数据