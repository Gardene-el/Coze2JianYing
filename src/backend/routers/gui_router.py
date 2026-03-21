"""
GUI 管理 API 路由

为 Electron 前端提供所有 /gui/* 端点：
  - 健康检查
  - 设置 CRUD
  - 草稿生成
  - 脚本格式化 / 验证 / 执行
  - 草稿回放
  - SSE 日志流

安全约束：/gui/script/execute 仅允许 127.0.0.1 / ::1 调用。
"""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.backend.core.settings_manager import get_settings_manager
from src.backend.DraftGenerator.draft_generator import DraftGenerator
from src.backend.utils.logger import logger
from src.backend.utils.sse_log import register_subscriber, unregister_subscriber

gui_router = APIRouter(tags=["GUI 管理"])


# ─── Pydantic 请求/响应模型 ───────────────────────────────────────────

class SettingsPayload(BaseModel):
    draft_folder: str = ""
    transfer_enabled: bool = False
    effective_output_path: Optional[str] = None
    effective_assets_base_path: Optional[str] = None


class GenerateDraftPayload(BaseModel):
    content: str


class ScriptPayload(BaseModel):
    script: str


class ExecutePayload(BaseModel):
    script: str


# ─── 健康检查 ─────────────────────────────────────────────────────────

@gui_router.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


# ─── 设置 ─────────────────────────────────────────────────────────────

@gui_router.get("/settings")
async def get_settings() -> Dict[str, Any]:
    return get_settings_manager().get_all()


@gui_router.put("/settings")
async def update_settings(payload: SettingsPayload) -> Dict[str, bool]:
    sm = get_settings_manager()
    sm.update(payload.model_dump())
    return {"ok": True}


@gui_router.post("/settings/detect-path")
async def detect_path() -> Dict[str, str]:
    _DEFAULT_DRAFT_PATHS = [
        r"C:\Users\{username}\AppData\Local\JianyingPro\User Data\Projects\com.lveditor.draft",
        r"C:\Users\{username}\AppData\Roaming\JianyingPro\User Data\Projects\com.lveditor.draft",
    ]
    username = os.environ.get("USERNAME") or os.environ.get("USER") or "User"
    for template in _DEFAULT_DRAFT_PATHS:
        candidate = template.format(username=username)
        if os.path.exists(candidate):
            return {"path": candidate}
    return {"path": ""}


# ─── 草稿生成 ──────────────────────────────────────────────────────────

@gui_router.post("/draft/generate")
async def generate_draft(payload: GenerateDraftPayload) -> Dict[str, Any]:
    logger.info("开始生成草稿...")
    try:
        gen = DraftGenerator()
        paths: List[str] = await asyncio.to_thread(gen.generate, payload.content)
        logger.info("草稿生成成功，共 %d 个文件: %s", len(paths), paths)
        return {"paths": paths}
    except Exception as exc:
        logger.error("草稿生成失败: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ─── 脚本处理辅助函数（从 ScriptExecutorPage 迁移） ─────────────────────

def _decode_escaped_string(s: str) -> str:
    for escaped, unescaped in [
        (r"\n", "\n"),
        (r"\t", "\t"),
        (r"\r", "\r"),
        (r"\"", '"'),
        (r"\'", "'"),
    ]:
        s = s.replace(escaped, unescaped)
    return s


def _extract_script_from_input(content: str) -> str:
    """提取并解码脚本内容（支持 JSON 包装和转义字符串）。"""
    content = content.strip()
    try:
        data = json.loads(content)
        if isinstance(data, dict) and "output" in data:
            return _decode_escaped_string(data["output"])
    except json.JSONDecodeError:
        pass
    if r"\n" in content or "\\n" in content:
        return _decode_escaped_string(content)
    return content


def _preprocess_script(script_content: str) -> str:
    """在用户脚本前注入标准导入，并包装成 async main()。"""
    preamble = """\
import sys
import asyncio
from pathlib import Path
from types import SimpleNamespace

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.backend.services.easy import *  # noqa: F401,F403
from src.backend.services.basic import *  # noqa: F401,F403
from src.backend.core.common_types import *  # noqa: F401,F403

CustomNamespace = SimpleNamespace
"""
    script_content = script_content.strip().strip('"').strip("'")

    import_lines: List[str] = []
    code_lines: List[str] = []
    for line in script_content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            import_lines.append(line)
        elif not stripped or stripped.startswith("#"):
            (import_lines if not code_lines else code_lines).append(line)
        else:
            code_lines.append(line)

    user_imports = "\n".join(import_lines)
    user_code = "\n".join(code_lines)
    indented = "\n".join(
        "    " + line if line.strip() else line for line in user_code.split("\n")
    )

    return (
        f"{preamble}\n"
        f"{user_imports}\n"
        f"async def main():\n"
        f"{indented}\n\n"
        f'if __name__ == "__main__":\n'
        f"    asyncio.run(main())\n"
    )


# ─── 脚本端点 ─────────────────────────────────────────────────────────

@gui_router.post("/script/format")
async def format_script(payload: ScriptPayload) -> Dict[str, str]:
    try:
        result = _extract_script_from_input(payload.script)
        return {"formatted": result}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@gui_router.post("/script/validate")
async def validate_script(payload: ScriptPayload) -> Dict[str, Any]:
    try:
        processed = _preprocess_script(_extract_script_from_input(payload.script))
        compile(processed, "<script>", "exec")
        return {"valid": True}
    except SyntaxError as exc:
        return {"valid": False, "error": f"第 {exc.lineno} 行: {exc.msg}"}
    except Exception as exc:
        return {"valid": False, "error": str(exc)}


@gui_router.post("/script/execute")
async def execute_script(payload: ExecutePayload, request: Request) -> Dict[str, bool]:
    # 安全约束：仅允许本地请求执行任意脚本
    client_host = request.client.host if request.client else ""
    if client_host not in ("127.0.0.1", "::1", "localhost"):
        raise HTTPException(status_code=403, detail="只允许本地连接执行脚本")

    def _run() -> None:
        script_content = _extract_script_from_input(payload.script)
        processed = _preprocess_script(script_content)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            exec(processed, {"__name__": "__main__", "__file__": "<script>"})  # noqa: S102
        finally:
            loop.close()

    logger.info("开始执行脚本...")
    try:
        await asyncio.to_thread(_run)
        logger.info("脚本执行成功")
        return {"ok": True}
    except Exception as exc:
        logger.error("脚本执行失败: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ─── 草稿回放 ─────────────────────────────────────────────────────────

@gui_router.get("/replay/{draft_id}")
async def replay_draft(draft_id: str) -> Dict[str, Any]:
    sm = get_settings_manager()
    from src.backend.config import get_config
    output_path = sm.get("effective_output_path") or get_config().drafts_dir
    draft_dir = Path(output_path) / draft_id

    if not draft_dir.exists():
        raise HTTPException(status_code=404, detail=f"草稿 {draft_id} 不存在")

    meta_file = draft_dir / "draft_meta_info.json"
    if not meta_file.exists():
        json_files = list(draft_dir.glob("*.json"))
        if not json_files:
            raise HTTPException(status_code=404, detail="未找到草稿文件")
        meta_file = json_files[0]

    try:
        with open(meta_file, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ─── SSE 日志流 ───────────────────────────────────────────────────────

@gui_router.get("/logs/stream")
async def logs_stream() -> StreamingResponse:
    async def event_generator():
        q: asyncio.Queue[str] = asyncio.Queue(maxsize=500)
        register_subscriber(q)
        logger.info("SSE 日志客户端已连接")
        try:
            while True:
                try:
                    msg = await asyncio.wait_for(q.get(), timeout=20.0)
                    # Escape newlines so a multiline message stays as one SSE event
                    safe_msg = msg.replace("\n", "\\n")
                    yield f"data: {safe_msg}\n\n"
                except asyncio.TimeoutError:
                    # Keep-alive comment prevents browser/proxy timeouts
                    yield ": keep-alive\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            unregister_subscriber(q)
            logger.info("SSE 日志客户端已断开")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
