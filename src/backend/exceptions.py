from __future__ import annotations

from enum import Enum


class CustomError(Enum):
    SUCCESS = (0, "成功", "Success")

    DRAFT_NOT_FOUND = (1001, "草稿不存在", "Draft not found")
    DRAFT_ALREADY_EXISTS = (1002, "草稿已存在", "Draft already exists")
    INVALID_DRAFT_URL = (1003, "无效的草稿URL", "Invalid draft URL")
    DRAFT_CREATE_FAILED = (1004, "草稿创建失败", "Draft creation failed")
    SEGMENT_NOT_FOUND = (1101, "片段不存在", "Segment not found")
    TRACK_NOT_FOUND = (1201, "轨道不存在", "Track not found")
    TRACK_TYPE_MISMATCH = (1202, "轨道类型不匹配", "Track type mismatch")
    INVALID_OPERATION = (1301, "不支持的操作", "Invalid operation")
    INVALID_SEGMENT_TYPE = (1302, "片段类型不合法", "Invalid segment type")

    PARAM_VALIDATION_FAILED = (1400, "参数验证失败", "Validation failed")
    INVALID_VIDEO_INFO = (1408, "视频参数无效", "Invalid video info")
    INVALID_IMAGE_INFO = (1409, "图片参数无效", "Invalid image info")
    INVALID_EFFECT_INFO = (1410, "特效参数无效", "Invalid effect info")
    INVALID_MASK_INFO = (1411, "遮罩参数无效", "Invalid mask info")
    INVALID_KEYFRAME_INFO = (1412, "关键帧参数无效", "Invalid keyframe info")
    INVALID_AUDIO_INFO = (1406, "音频参数无效", "Invalid audio info")
    INVALID_CAPTION_INFO = (1407, "字幕参数无效", "Invalid caption info")
    UNAUTHORIZED = (1401, "未授权", "Unauthorized")
    FORBIDDEN = (1403, "禁止访问", "Forbidden")
    RESOURCE_NOT_FOUND = (1404, "资源不存在", "Resource not found")
    METHOD_NOT_ALLOWED = (1405, "请求方法不允许", "Method not allowed")
    TOO_MANY_REQUESTS = (1429, "请求过于频繁", "Too many requests")

    INTERNAL_SERVER_ERROR = (1500, "内部错误", "Internal error")
    VIDEO_ADD_FAILED = (1507, "视频添加失败", "Video add failed")
    IMAGE_ADD_FAILED = (1508, "图片添加失败", "Image add failed")
    EFFECT_NOT_FOUND = (1509, "特效不存在", "Effect not found")
    EFFECT_ADD_FAILED = (1510, "特效添加失败", "Effect add failed")
    MASK_NOT_FOUND = (1511, "遮罩不存在", "Mask not found")
    MASK_ADD_FAILED = (1512, "遮罩添加失败", "Mask add failed")
    KEYFRAME_ADD_FAILED = (1513, "关键帧添加失败", "Keyframe add failed")
    AUDIO_ADD_FAILED = (1505, "音频添加失败", "Audio add failed")
    CAPTION_ADD_FAILED = (1506, "字幕添加失败", "Caption add failed")
    BAD_GATEWAY = (1502, "网关错误", "Bad gateway")
    SERVICE_UNAVAILABLE = (1503, "服务不可用", "Service unavailable")
    GATEWAY_TIMEOUT = (1504, "网关超时", "Gateway timeout")

    def __init__(self, code: int, cn_message: str, en_message: str) -> None:
        self.code = code
        self.cn_message = cn_message
        self.en_message = en_message

    def as_dict(self, detail: str = "", lang: str = "zh") -> dict:
        message = self.cn_message if lang == "zh" else self.en_message
        if detail:
            message += f" ({detail})"
        return {"code": self.code, "message": message}


class CustomException(Exception):
    def __init__(self, err: CustomError, detail: str = "") -> None:
        self.err = err
        self.detail = detail
        super().__init__(err.cn_message)
