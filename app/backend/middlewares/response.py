"""
统一响应中间件：
- 成功：{"code":0,"message":"成功","data":{...}}
- 失败：{"code":<非0>,"message":"错误说明"}
- HTTP 始终返回 200
"""
from __future__ import annotations

import json
from http import HTTPStatus
from typing import Any, Dict

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.backend.exceptions import CustomError, CustomException
from app.backend.utils.logger import get_logger

logger = get_logger(__name__)


class ResponseMiddleware(BaseHTTPMiddleware):
    _HTTP_ERROR_MAP: Dict[int, CustomError] = {
        400: CustomError.PARAM_VALIDATION_FAILED,
        401: CustomError.UNAUTHORIZED,
        403: CustomError.FORBIDDEN,
        404: CustomError.RESOURCE_NOT_FOUND,
        405: CustomError.METHOD_NOT_ALLOWED,
        422: CustomError.PARAM_VALIDATION_FAILED,
        429: CustomError.TOO_MANY_REQUESTS,
        500: CustomError.INTERNAL_SERVER_ERROR,
        502: CustomError.BAD_GATEWAY,
        503: CustomError.SERVICE_UNAVAILABLE,
        504: CustomError.GATEWAY_TIMEOUT,
    }

    async def dispatch(self, request: Request, call_next):
        lang = self._resolve_lang(request)
        try:
            response = await call_next(request)
            return await self._normalize_response(response, lang)
        except CustomException as exc:
            logger.warning("业务异常: code=%s detail=%s", exc.err.code, exc.detail)
            return JSONResponse(status_code=200, content=exc.err.as_dict(detail=exc.detail, lang=lang))
        except Exception as exc:
            logger.exception("响应中间件捕获异常: %s", exc)
            err = CustomError.INTERNAL_SERVER_ERROR
            detail = str(exc) or (err.cn_message if lang == "zh" else err.en_message)
            return JSONResponse(status_code=200, content=err.as_dict(detail=detail, lang=lang))

    @staticmethod
    def _resolve_lang(request: Request) -> str:
        header = (request.headers.get("accept-language") or "").lower()
        return "zh" if "zh" in header else "en"

    def _error_response(self, err: CustomError, lang: str, detail: str = "") -> JSONResponse:
        return JSONResponse(status_code=200, content=err.as_dict(detail=detail, lang=lang))

    async def _normalize_response(self, response: Response, lang: str) -> Response:
        body = await self._read_response_body(response)
        payload = self._try_parse_json(body)

        if isinstance(payload, dict) and "code" in payload and "message" in payload:
            return JSONResponse(status_code=200, content=payload)

        if response.status_code == 422:
            message = self._format_422_message(payload, lang)
            return self._error_response(self._HTTP_ERROR_MAP[422], lang, message)

        if response.status_code != 200:
            err = self._HTTP_ERROR_MAP.get(response.status_code, CustomError.INTERNAL_SERVER_ERROR)
            message = self._extract_error_message(payload)
            if not message:
                try:
                    message = HTTPStatus(response.status_code).phrase
                except ValueError:
                    message = err.cn_message if lang == "zh" else err.en_message
            return self._error_response(err, lang, message)

        if payload is None:
            return response

        return JSONResponse(
            status_code=200,
            content={
                **CustomError.SUCCESS.as_dict(lang=lang),
                "data": payload,
            },
        )

    @staticmethod
    async def _read_response_body(response: Response) -> str:
        body = b""
        if hasattr(response, "body_iterator") and response.body_iterator is not None:
            async for chunk in response.body_iterator:
                body += chunk
        elif getattr(response, "body", None) is not None:
            body = response.body
        return body.decode("utf-8", errors="replace") if body else ""

    @staticmethod
    def _try_parse_json(body: str) -> Any:
        if not body:
            return None
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return None

    def _format_422_message(self, payload: Any, lang: str) -> str:
        if not isinstance(payload, dict):
            return (
                CustomError.PARAM_VALIDATION_FAILED.cn_message
                if lang == "zh"
                else CustomError.PARAM_VALIDATION_FAILED.en_message
            )
        details = payload.get("detail")
        if not isinstance(details, list):
            return (
                CustomError.PARAM_VALIDATION_FAILED.cn_message
                if lang == "zh"
                else CustomError.PARAM_VALIDATION_FAILED.en_message
            )
        messages = []
        for item in details:
            if not isinstance(item, dict):
                continue
            loc = ".".join(str(x) for x in item.get("loc", []) if x != "body")
            msg = item.get("msg") or ""
            messages.append(f"{loc}: {msg}" if loc else msg)
        default_msg = (
            CustomError.PARAM_VALIDATION_FAILED.cn_message
            if lang == "zh"
            else CustomError.PARAM_VALIDATION_FAILED.en_message
        )
        return "; ".join(m for m in messages if m) or default_msg

    @staticmethod
    def _extract_error_message(payload: Any) -> str:
        if isinstance(payload, dict):
            for key in ("message", "detail", "error"):
                value = payload.get(key)
                if isinstance(value, str) and value:
                    return value
                if isinstance(value, list) and value:
                    return "; ".join(str(v) for v in value)
        if isinstance(payload, str):
            return payload
        return ""

