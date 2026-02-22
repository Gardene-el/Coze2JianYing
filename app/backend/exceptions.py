from __future__ import annotations

from enum import Enum


class CustomError(Enum):
    SUCCESS = (0, "成功", "Success")

    DRAFT_NOT_FOUND = (1001, "草稿不存在", "Draft not found")
    DRAFT_ALREADY_EXISTS = (1002, "草稿已存在", "Draft already exists")
    SEGMENT_NOT_FOUND = (1101, "片段不存在", "Segment not found")
    TRACK_NOT_FOUND = (1201, "轨道不存在", "Track not found")
    TRACK_TYPE_MISMATCH = (1202, "轨道类型不匹配", "Track type mismatch")
    INVALID_OPERATION = (1301, "不支持的操作", "Invalid operation")
    INVALID_SEGMENT_TYPE = (1302, "片段类型不合法", "Invalid segment type")

    PARAM_VALIDATION_FAILED = (1400, "参数验证失败", "Validation failed")
    UNAUTHORIZED = (1401, "未授权", "Unauthorized")
    FORBIDDEN = (1403, "禁止访问", "Forbidden")
    RESOURCE_NOT_FOUND = (1404, "资源不存在", "Resource not found")
    METHOD_NOT_ALLOWED = (1405, "请求方法不允许", "Method not allowed")
    TOO_MANY_REQUESTS = (1429, "请求过于频繁", "Too many requests")

    INTERNAL_SERVER_ERROR = (1500, "内部错误", "Internal error")
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
