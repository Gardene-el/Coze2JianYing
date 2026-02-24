"""通用数据模型 (Pydantic Common Types)。"""

from typing import Any, List, Tuple, Type, TypeVar

import pyJianYingDraft as draft
from pydantic import BaseModel, Field

ModelT = TypeVar("ModelT", bound=BaseModel)


def parse_common_model(model_cls: Type[ModelT], value: Any) -> ModelT:
    """兼容 Pydantic v1/v2 的通用模型解析。"""
    if isinstance(value, model_cls):
        return value
    if hasattr(model_cls, "model_validate"):
        return model_cls.model_validate(value)
    return model_cls.parse_obj(value)


class TimeRange(BaseModel):
    """时间范围模型（微秒）"""

    start: int = Field(..., description="开始时间（微秒）", ge=0)
    duration: int = Field(..., description="持续时长（微秒）", gt=0)


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


class TextStyle(BaseModel):
    """
    文本样式（镜像 pyJianYingDraft.TextStyle）
    对应 pyJianYingDraft 的 TextStyle 类，用于控制文本的样式属性
    """

    font_size: float = Field(8.0, description="字体大小（与剤映中定义一致）", gt=0)
    color: List[float] = Field([1.0, 1.0, 1.0], description="文字颜色 RGB (0.0-1.0)")
    alpha: float = Field(1.0, description="文字不透明度 0.0-1.0", ge=0.0, le=1.0)
    bold: bool = Field(False, description="是否加粗")
    italic: bool = Field(False, description="是否斜体")
    underline: bool = Field(False, description="是否下划线")
    align: int = Field(0, description="对齐方式: 0=左对齐, 1=居中, 2=右对齐", ge=0, le=2)
    vertical: bool = Field(False, description="是否竖排文本")
    letter_spacing: int = Field(0, description="字符间距（与剤映中定义一致）")
    line_spacing: int = Field(0, description="行间距（与剤映中定义一致）")
    auto_wrapping: bool = Field(False, description="是否自动换行（开启后 type 为 subtitle）")
    max_line_width: float = Field(0.82, description="每行最大宽度（占屏幕宽度比例 0-1）", ge=0.0, le=1.0)


class TextBorder(BaseModel):
    """文本描边参数（镜像 pyJianYingDraft.TextBorder）"""

    color: List[float] = Field([0.0, 0.0, 0.0], description="描边颜色 RGB (0.0-1.0)")
    alpha: float = Field(1.0, description="描边不透明度 0.0-1.0", ge=0.0, le=1.0)
    width: float = Field(40.0, description="描边宽度 0-100（与剤映中定义一致）", ge=0.0, le=100.0)


class TextShadow(BaseModel):
    """文本阴影参数（镜像 pyJianYingDraft.TextShadow）"""

    color: List[float] = Field([0.0, 0.0, 0.0], description="阴影颜色 RGB (0.0-1.0)")
    alpha: float = Field(0.9, description="阴影不透明度 0.0-1.0", ge=0.0, le=1.0)
    diffuse: float = Field(15.0, description="阴影扩散程度 0-100", ge=0.0, le=100.0)
    distance: float = Field(5.0, description="阴影距离 0-100", ge=0.0, le=100.0)
    angle: float = Field(-45.0, description="阴影角度 -180 到 180", ge=-180.0, le=180.0)


class TextBackground(BaseModel):
    """文本背景参数（镜像 pyJianYingDraft.TextBackground）"""

    color: str = Field(..., description="背景颜色，格式为 '#RRGGBB'")
    style: int = Field(1, description="背景样式 1 或 2", ge=1, le=2)
    alpha: float = Field(1.0, description="背景不透明度 0.0-1.0", ge=0.0, le=1.0)
    round_radius: float = Field(0.0, description="圆角半径 0-1", ge=0.0, le=1.0)
    height: float = Field(0.14, description="背景高度 0-1", ge=0.0, le=1.0)
    width: float = Field(0.14, description="背景宽度 0-1", ge=0.0, le=1.0)
    horizontal_offset: float = Field(0.5, description="水平偏移 0-1", ge=0.0, le=1.0)
    vertical_offset: float = Field(0.5, description="竖直偏移 0-1", ge=0.0, le=1.0)


class CropSettings(BaseModel):
    """
    裁剪设置（镜像 pyJianYingDraft.CropSettings）
    对应 pyJianYingDraft 的 CropSettings 类，用于定义裁剪区域的四个角点坐标
    """

    upper_left_x: float = Field(
        0.0, description="左上角 X 坐标 (0.0-1.0)", ge=0.0, le=1.0
    )
    upper_left_y: float = Field(
        0.0, description="左上角 Y 坐标 (0.0-1.0)", ge=0.0, le=1.0
    )
    upper_right_x: float = Field(
        1.0, description="右上角 X 坐标 (0.0-1.0)", ge=0.0, le=1.0
    )
    upper_right_y: float = Field(
        0.0, description="右上角 Y 坐标 (0.0-1.0)", ge=0.0, le=1.0
    )
    lower_left_x: float = Field(
        0.0, description="左下角 X 坐标 (0.0-1.0)", ge=0.0, le=1.0
    )
    lower_left_y: float = Field(
        1.0, description="左下角 Y 坐标 (0.0-1.0)", ge=0.0, le=1.0
    )
    lower_right_x: float = Field(
        1.0, description="右下角 X 坐标 (0.0-1.0)", ge=0.0, le=1.0
    )
    lower_right_y: float = Field(
        1.0, description="右下角 Y 坐标 (0.0-1.0)", ge=0.0, le=1.0
    )


def to_draft_timerange(timerange: TimeRange) -> draft.Timerange:
    return draft.Timerange(timerange.start, timerange.duration)


def to_draft_clip_settings(clip_settings: ClipSettings) -> draft.ClipSettings:
    return draft.ClipSettings(
        alpha=clip_settings.alpha,
        rotation=clip_settings.rotation,
        scale_x=clip_settings.scale_x,
        scale_y=clip_settings.scale_y,
        transform_x=clip_settings.transform_x,
        transform_y=clip_settings.transform_y,
    )


def to_draft_crop_settings(crop_settings: CropSettings) -> draft.CropSettings:
    return draft.CropSettings(
        upper_left_x=crop_settings.upper_left_x,
        upper_left_y=crop_settings.upper_left_y,
        upper_right_x=crop_settings.upper_right_x,
        upper_right_y=crop_settings.upper_right_y,
        lower_left_x=crop_settings.lower_left_x,
        lower_left_y=crop_settings.lower_left_y,
        lower_right_x=crop_settings.lower_right_x,
        lower_right_y=crop_settings.lower_right_y,
    )


def _to_rgb(color: Any, default: Tuple[float, float, float]) -> Tuple[float, float, float]:
    if not isinstance(color, (list, tuple)) or len(color) < 3:
        return default
    return float(color[0]), float(color[1]), float(color[2])


def to_draft_text_style(text_style: TextStyle) -> draft.TextStyle:
    return draft.TextStyle(
        size=text_style.font_size,
        bold=text_style.bold,
        italic=text_style.italic,
        underline=text_style.underline,
        color=_to_rgb(text_style.color, (1.0, 1.0, 1.0)),
        alpha=text_style.alpha,
        align=text_style.align,
        vertical=text_style.vertical,
        letter_spacing=text_style.letter_spacing,
        line_spacing=text_style.line_spacing,
        auto_wrapping=text_style.auto_wrapping,
        max_line_width=text_style.max_line_width,
    )


def to_draft_text_border(text_border: TextBorder) -> draft.TextBorder:
    return draft.TextBorder(
        color=_to_rgb(text_border.color, (0.0, 0.0, 0.0)),
        alpha=text_border.alpha,
        width=text_border.width,
    )


def to_draft_text_shadow(text_shadow: TextShadow) -> draft.TextShadow:
    return draft.TextShadow(
        color=_to_rgb(text_shadow.color, (0.0, 0.0, 0.0)),
        alpha=text_shadow.alpha,
        diffuse=text_shadow.diffuse,
        distance=text_shadow.distance,
        angle=text_shadow.angle,
    )


def to_draft_text_background(text_background: TextBackground) -> draft.TextBackground:
    return draft.TextBackground(
        color=text_background.color,
        style=text_background.style,
        alpha=text_background.alpha,
        round_radius=text_background.round_radius,
        height=text_background.height,
        width=text_background.width,
        horizontal_offset=text_background.horizontal_offset,
        vertical_offset=text_background.vertical_offset,
    )
