"""
Easy API 数据模型 (Pydantic Schemas)

与 capcut-mate v1 路由参数结构对齐，提供简化的 add_xxs 系列接口。
主要差异：用 draft_id (UUID) 替代 draft_url (文件路径字符串)。

仅保留 8 个 add_xxs 路由所需的 Schema；
草稿管理（create/save）、计算类 Schema（timelines/*_infos）已移除。
"""

from typing import List, Optional

from pydantic import BaseModel, Field


# ────────────────────────────────────────────────────────────
# 公共子模型
# ────────────────────────────────────────────────────────────

class SegmentInfo(BaseModel):
    """片段时间信息"""
    id: str = Field(..., description="片段 ID")
    start: int = Field(..., description="开始时间（微秒）")
    end: int = Field(..., description="结束时间（微秒）")


class ShadowInfo(BaseModel):
    """文本阴影参数"""
    shadow_alpha: float = Field(default=1.0, ge=0.0, le=1.0, description="阴影不透明度 [0,1]")
    shadow_color: str = Field(default="#000000", description="阴影颜色（十六进制）")
    shadow_diffuse: float = Field(default=15.0, ge=0.0, le=100.0, description="阴影扩散 [0,100]")
    shadow_distance: float = Field(default=5.0, ge=0.0, le=100.0, description="阴影距离 [0,100]")
    shadow_angle: float = Field(default=-45.0, ge=-180.0, le=180.0, description="阴影角度 [-180,180]")


# ────────────────────────────────────────────────────────────
# 通用响应基类
# ────────────────────────────────────────────────────────────

class EasyBaseResponse(BaseModel):
    """Easy API 通用响应基类"""
    success: bool = Field(default=True, description="是否成功（始终 True）")
    message: str = Field(default="", description="附加说明")


# ────────────────────────────────────────────────────────────
# add_videos
# ────────────────────────────────────────────────────────────

class AddVideosRequest(BaseModel):
    draft_id: str = Field(..., description="草稿 ID（UUID）")
    video_infos: str = Field(..., description="视频信息列表 JSON 字符串")
    alpha: float = Field(default=1.0, description="全局透明度 [0,1]")
    scale_x: float = Field(default=1.0, description="X 轴缩放")
    scale_y: float = Field(default=1.0, description="Y 轴缩放")
    transform_x: int = Field(default=0, description="X 轴偏移（像素）")
    transform_y: int = Field(default=0, description="Y 轴偏移（像素）")


class AddVideosResponse(EasyBaseResponse):
    draft_id: str = Field(default="", description="草稿 ID")
    track_id: str = Field(default="", description="视频轨道 ID")
    video_ids: List[str] = Field(default=[], description="视频素材 ID 列表")
    segment_ids: List[str] = Field(default=[], description="片段 ID 列表")


# ────────────────────────────────────────────────────────────
# add_audios
# ────────────────────────────────────────────────────────────

class AddAudiosRequest(BaseModel):
    draft_id: str = Field(..., description="草稿 ID（UUID）")
    audio_infos: str = Field(..., description="音频信息列表 JSON 字符串")


class AddAudiosResponse(EasyBaseResponse):
    draft_id: str = Field(default="", description="草稿 ID")
    track_id: str = Field(default="", description="音频轨道 ID")
    audio_ids: List[str] = Field(default=[], description="音频素材 ID 列表")


# ────────────────────────────────────────────────────────────
# add_images
# ────────────────────────────────────────────────────────────

class AddImagesRequest(BaseModel):
    draft_id: str = Field(..., description="草稿 ID（UUID）")
    image_infos: str = Field(..., description="图片信息列表 JSON 字符串")
    alpha: float = Field(default=1.0, description="全局透明度 [0,1]")
    scale_x: float = Field(default=1.0, description="X 轴缩放")
    scale_y: float = Field(default=1.0, description="Y 轴缩放")
    transform_x: int = Field(default=0, description="X 轴偏移（像素）")
    transform_y: int = Field(default=0, description="Y 轴偏移（像素）")


class AddImagesResponse(EasyBaseResponse):
    draft_id: str = Field(default="", description="草稿 ID")
    track_id: str = Field(default="", description="图片轨道 ID")
    image_ids: List[str] = Field(default=[], description="图片素材 ID 列表")
    segment_ids: List[str] = Field(default=[], description="片段 ID 列表")
    segment_infos: List[SegmentInfo] = Field(default=[], description="片段信息列表")


# ────────────────────────────────────────────────────────────
# add_sticker
# ────────────────────────────────────────────────────────────

class AddStickerRequest(BaseModel):
    draft_id: str = Field(..., description="草稿 ID（UUID）")
    sticker_id: str = Field(..., description="贴纸资源 ID")
    start: int = Field(..., description="开始时间（微秒）")
    end: int = Field(..., description="结束时间（微秒）")
    scale: float = Field(default=1.0, description="缩放比例 [0.1,5.0]")
    transform_x: int = Field(default=0, description="X 轴偏移（像素）")
    transform_y: int = Field(default=0, description="Y 轴偏移（像素）")


class AddStickerResponse(EasyBaseResponse):
    draft_id: str = Field(default="", description="草稿 ID")
    sticker_id: str = Field(default="", description="贴纸资源 ID")
    track_id: str = Field(default="", description="贴纸轨道 ID")
    segment_id: str = Field(default="", description="片段 ID")
    duration: int = Field(default=0, description="时长（微秒）")


# ────────────────────────────────────────────────────────────
# add_keyframes
# ────────────────────────────────────────────────────────────

class AddKeyframesRequest(BaseModel):
    draft_id: str = Field(..., description="草稿 ID（UUID）")
    keyframes: str = Field(..., description="关键帧列表 JSON 字符串")


class AddKeyframesResponse(EasyBaseResponse):
    draft_id: str = Field(default="", description="草稿 ID")
    keyframes_added: int = Field(default=0, description="成功添加的关键帧数量")
    affected_segments: List[str] = Field(default=[], description="受影响的片段 ID 列表")


# ────────────────────────────────────────────────────────────
# add_captions
# ────────────────────────────────────────────────────────────

class AddCaptionsRequest(BaseModel):
    draft_id: str = Field(..., description="草稿 ID（UUID）")
    captions: str = Field(..., description="字幕信息列表 JSON 字符串")
    text_color: str = Field(default="#ffffff", description="文本颜色（十六进制）")
    border_color: Optional[str] = Field(default=None, description="边框颜色（十六进制）")
    alignment: int = Field(default=1, ge=0, le=5, description="对齐方式 (0-5)")
    alpha: float = Field(default=1.0, ge=0.0, le=1.0, description="透明度 [0,1]")
    font: Optional[str] = Field(default=None, description="字体名称")
    font_size: int = Field(default=15, ge=1, description="字体大小")
    letter_spacing: Optional[float] = Field(default=None, description="字间距")
    line_spacing: Optional[float] = Field(default=None, description="行间距")
    scale_x: float = Field(default=1.0, description="水平缩放")
    scale_y: float = Field(default=1.0, description="垂直缩放")
    transform_x: float = Field(default=0.0, description="水平位移")
    transform_y: float = Field(default=0.0, description="垂直位移")
    style_text: bool = Field(default=False, description="是否使用富文本样式")
    underline: bool = Field(default=False, description="下划线")
    italic: bool = Field(default=False, description="斜体")
    bold: bool = Field(default=False, description="加粗")
    has_shadow: bool = Field(default=False, description="启用阴影")
    shadow_info: Optional[ShadowInfo] = Field(default=None, description="阴影参数")


class AddCaptionsResponse(EasyBaseResponse):
    draft_id: str = Field(default="", description="草稿 ID")
    track_id: str = Field(default="", description="字幕轨道 ID")
    text_ids: List[str] = Field(default=[], description="文本素材 ID 列表")
    segment_ids: List[str] = Field(default=[], description="片段 ID 列表")
    segment_infos: List[SegmentInfo] = Field(default=[], description="片段信息列表")


# ────────────────────────────────────────────────────────────
# add_effects
# ────────────────────────────────────────────────────────────

class AddEffectsRequest(BaseModel):
    draft_id: str = Field(..., description="草稿 ID（UUID）")
    effect_infos: str = Field(..., description="特效信息列表 JSON 字符串")


class AddEffectsResponse(EasyBaseResponse):
    draft_id: str = Field(default="", description="草稿 ID")
    track_id: str = Field(default="", description="特效轨道 ID")
    effect_ids: List[str] = Field(default=[], description="特效素材 ID 列表")
    segment_ids: List[str] = Field(default=[], description="片段 ID 列表")


# ────────────────────────────────────────────────────────────
# add_masks
# ────────────────────────────────────────────────────────────

class AddMasksRequest(BaseModel):
    draft_id: str = Field(..., description="草稿 ID（UUID）")
    segment_ids: List[str] = Field(..., description="要应用遮罩的片段 ID 列表")
    name: str = Field(default="线性", description="遮罩类型名称")
    X: int = Field(default=0, description="中心 X 坐标（像素）")
    Y: int = Field(default=0, description="中心 Y 坐标（像素）")
    width: int = Field(default=512, description="遮罩宽度（像素）")
    height: int = Field(default=512, description="遮罩高度（像素）")
    feather: int = Field(default=0, description="羽化程度 [0,100]")
    rotation: int = Field(default=0, description="旋转角度（度）")
    invert: bool = Field(default=False, description="是否反转遮罩")
    roundCorner: int = Field(default=0, description="圆角半径 [0,100]")


class AddMasksResponse(EasyBaseResponse):
    draft_id: str = Field(default="", description="草稿 ID")
    masks_added: int = Field(default=0, description="成功添加的遮罩数量")
    affected_segments: List[str] = Field(default=[], description="受影响的片段 ID 列表")
    mask_ids: List[str] = Field(default=[], description="遮罩 ID 列表")


# (计算类 Schema 已移除，请使用 coze_plugin/easy_aux_tools 中对应的 Coze 工具)
