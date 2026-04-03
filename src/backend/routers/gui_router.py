"""
GUI 管理 API 路由

为 Electron 前端提供所有 /gui/* 端点：
  - 健康检查
  - 设置 CRUD
  - 草稿生成
  - 脚本格式化 / 验证 / 执行
  - 草稿回放 / 拉取执行
  - SSE 日志流

安全约束：/gui/script/execute 和 /gui/replay/execute 仅允许 127.0.0.1 / ::1 调用。
"""
from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests as _http  # sync HTTP client (project dep), used for replay self-calls
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.backend.core.settings_manager import get_settings_manager
from src.backend.DraftGenerator.draft_generator import DraftGenerator
from src.backend.utils.logger import logger
from src.backend.utils.sse_log import register_subscriber, unregister_subscriber

# ─── 安全依赖：仅允许本机请求访问 /gui/* ────────────────────────────────

def _require_localhost(request: Request) -> None:
    """拒绝所有非本机来源的请求，防止外部进程调用 GUI 内部端点。"""
    host = request.client.host if request.client else ""
    if host not in ("127.0.0.1", "::1", "localhost"):
        raise HTTPException(status_code=403, detail="/gui/* 端点仅限本机访问")


gui_router = APIRouter(tags=["GUI 管理"], dependencies=[Depends(_require_localhost)])


# ─── Pydantic 请求/响应模型 ───────────────────────────────────────────

class SettingsPayload(BaseModel):
    draft_folder: Optional[str] = None


class ReplayExecutePayload(BaseModel):
    worker_url: str  # e.g. "https://api.garden-eel.com/coze2jianying"
    draft_id: str    # virtual draft ID recorded by Coze2JianYing-Capture


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
    sm.update(payload.model_dump(exclude_none=True))
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
    draft_folder = get_settings_manager().require("draft_folder")
    try:
        gen = DraftGenerator(output_base_dir=draft_folder)
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


_LEGACY_PREAMBLE = """\
import sys
import asyncio
from pathlib import Path
from types import SimpleNamespace

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.backend.api.legacy import *  # noqa: F401,F403

CustomNamespace = SimpleNamespace
"""

_CURRENT_PREAMBLE = """\
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

# 旧版脚本的特征导入前缀（来自 main 分支时代的 Coze 插件）
_LEGACY_IMPORT_PATTERNS = (
    "from app.schemas.segment_schemas",
    "from app.backend.schemas.segment_schemas",
    "from app.schemas import",
    "from app.backend.schemas import",
)


def _is_legacy_script(content: str) -> bool:
    """检测脚本是否为旧版 Coze 插件生成的格式。"""
    return any(pat in content for pat in _LEGACY_IMPORT_PATTERNS)


def _preprocess_script(script_content: str) -> str:
    """在用户脚本前注入标准导入，并包装成 async main()。
    自动检测旧版脚本（from app.schemas.segment_schemas import *）并切换到兼容 preamble。
    """
    script_content = script_content.strip().strip('"').strip("'")

    is_legacy = _is_legacy_script(script_content)
    preamble = _LEGACY_PREAMBLE if is_legacy else _CURRENT_PREAMBLE

    import_lines: List[str] = []
    code_lines: List[str] = []
    for line in script_content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            # 旧版模式下，过滤掉 legacy 导入行（compat 已全部提供）
            if is_legacy and any(pat in stripped for pat in _LEGACY_IMPORT_PATTERNS):
                continue
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
async def execute_script(payload: ExecutePayload) -> Dict[str, bool]:
    # 安全约束已由路由器级依赖 _require_localhost 统一处理
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


# ─── 回放执行辅助 ─────────────────────────────────────────────────────

# 产生 segment_ids 列表的 easy API 动作集合
_EASY_MULTI_SEGMENT_ACTIONS = frozenset(
    {"add_videos", "add_audios", "add_captions", "add_images", "add_effects"}
)


def _replace_ids_in_str(s: str, id_map: Dict[str, str]) -> str:
    """将路径字符串中出现的所有虚拟 ID 替换为真实 ID。"""
    for virt, real in id_map.items():
        s = s.replace(virt, real)
    return s


def _resolve_ids(value: Any, id_map: Dict[str, str]) -> Any:
    """递归地将 payload 中所有虚拟 ID 替换为真实 ID。
    对于内嵌 JSON 字符串（如 add_keyframes 的 keyframes 字段）也会递归处理。
    """
    if isinstance(value, str):
        if value in id_map:
            return id_map[value]
        # 对内嵌 JSON 字符串（以 [ 或 { 开头）也做递归替换
        stripped = value.strip()
        if stripped and stripped[0] in ("[", "{"):
            try:
                inner = json.loads(stripped)
                resolved = _resolve_ids(inner, id_map)
                return json.dumps(resolved, ensure_ascii=False)
            except (json.JSONDecodeError, ValueError):
                pass
        return value
    elif isinstance(value, list):
        return [_resolve_ids(v, id_map) for v in value]
    elif isinstance(value, dict):
        return {k: _resolve_ids(v, id_map) for k, v in value.items()}
    return value


def _run_replay(worker_url: str, draft_id: str, self_port: int) -> Dict[str, Any]:
    """同步执行录制回放（在线程池中运行，不阻塞事件循环）。

    流程：
      1. 从 Capture Worker 拉取调用记录
      2. 按 created_at 升序排列，建立 easy API 虚拟 segment ID 队列
      3. 逐条调用本地后端，维护 virtual_id → real_id 映射
      4. 返回执行统计
    """
    local_base = f"http://127.0.0.1:{self_port}"

    # ── 1. 从 Worker 拉取录制数据 ──────────────────────────────
    base = worker_url.rstrip("/")
    try:
        resp = _http.get(f"{base}/replay/{draft_id}", timeout=30)
        resp.raise_for_status()
    except _http.exceptions.RequestException as exc:
        raise RuntimeError(f"拉取 Worker 数据失败: {exc}") from exc

    data: Dict[str, Any] = resp.json()
    if data.get("code", 0) != 0:
        raise RuntimeError(f"Worker 返回错误: {data.get('message', '未知错误')}")

    calls: List[Dict[str, Any]] = sorted(
        data.get("calls", []), key=lambda c: c.get("created_at", 0)
    )

    if not calls:
        return {"calls_executed": 0, "message": "无可执行的调用记录"}

    # ── 2. 预处理：收集 easy API 合成记录，建立 action → 虚拟 seg ID 队列 ──
    # easy API (add_videos 等) 在 Worker 侧会为每个产生的 segment 插入一条
    # action="easy_{parent}_segment" 的合成记录，用于关联关系追踪。
    # 回放时需要按顺序将这些虚拟 ID 映射到 easy API 返回的真实 segment_ids。
    easy_id_queues: Dict[str, List[str]] = {}
    for call in calls:
        action: str = call.get("action", "")
        if action.startswith("easy_") and action.endswith("_segment"):
            # "easy_add_videos_segment" → parent "add_videos"
            parent = action[5:-8]
            produced_id: Optional[str] = call.get("produced_virtual_id")
            if produced_id:
                easy_id_queues.setdefault(parent, []).append(produced_id)

    # ── 3. 主循环：逐条调用本地 API ───────────────────────────
    session = _http.Session()
    id_map: Dict[str, str] = {}  # virtual_id → real_id
    executed = 0

    for call in calls:
        action = call.get("action", "")

        # 跳过合成记录——它们只是 Capture 的内部追踪记录，不对应真实 API 调用
        if action.startswith("easy_") and action.endswith("_segment"):
            continue

        path: str = call.get("path", "")
        payload_json: Optional[str] = call.get("payload_json")
        payload: Dict[str, Any] = json.loads(payload_json) if payload_json else {}

        # 替换路径和 payload 中的虚拟 ID
        real_path = _replace_ids_in_str(path, id_map)
        real_payload = _resolve_ids(payload, id_map)

        # 调用本地 API
        url = f"{local_base}{real_path}"
        try:
            r = session.post(url, json=real_payload, timeout=60)
            result: Dict[str, Any] = r.json()
        except _http.exceptions.RequestException as exc:
            raise RuntimeError(f"调用 {real_path} 时连接失败: {exc}") from exc

        if result.get("code", 0) != 0:
            raise RuntimeError(
                f"调用 {action} ({real_path}) 失败: {result.get('message', '未知错误')}"
            )

        # ── 维护 virtual → real ID 映射 ──────────────────────
        produced_vid: Optional[str] = call.get("produced_virtual_id")
        produced_type: Optional[str] = call.get("produced_id_type")

        if produced_vid and produced_type == "draft":
            real_id = result.get("draft_id")
            if real_id:
                id_map[produced_vid] = real_id
                logger.info("回放映射: 虚拟 draft %s → 真实 %s", produced_vid, real_id)

        elif produced_vid and produced_type == "segment":
            real_id = result.get("segment_id")
            if real_id:
                id_map[produced_vid] = real_id
                logger.info("回放映射: 虚拟 segment %s → 真实 %s", produced_vid, real_id)

        elif action in _EASY_MULTI_SEGMENT_ACTIONS:
            # easy API 返回 segment_ids 列表，按顺序映射到虚拟 ID 队列
            seg_ids: List[str] = result.get("segment_ids", [])
            virtual_segs = easy_id_queues.get(action, [])
            mapped_count = min(len(seg_ids), len(virtual_segs))
            for i in range(mapped_count):
                id_map[virtual_segs[i]] = seg_ids[i]
                logger.info(
                    "回放映射: 虚拟 segment %s → 真实 %s (via %s)",
                    virtual_segs[i], seg_ids[i], action,
                )
            easy_id_queues[action] = virtual_segs[mapped_count:]

        executed += 1
        logger.info("回放 [%d]: %s → %s 成功", executed, action, real_path)

    logger.info("回放完成，共执行 %d 条调用", executed)
    return {"ok": True, "calls_executed": executed}


@gui_router.post("/replay/execute")
async def execute_replay(payload: ReplayExecutePayload, request: Request) -> Dict[str, Any]:
    """从 Capture Worker 拉取并执行录制的调用序列。

    与粘贴脚本、粘贴草稿相同的一次性执行模式：
      - 调用方负责在执行前启动 Python 后端（通过 useEnsureBackend）
      - 执行完成后调用方卸载组件自动回收后端

    安全约束：仅允许本地请求调用。
    """
    client_host = request.client.host if request.client else ""
    if client_host not in ("127.0.0.1", "::1", "localhost"):
        raise HTTPException(status_code=403, detail="只允许本地连接执行回放")

    if not payload.worker_url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="无效的 Worker URL，必须以 http:// 或 https:// 开头")

    if not payload.draft_id.strip():
        raise HTTPException(status_code=400, detail="draft_id 不能为空")

    # 从请求自身推断后端运行端口（避免硬编码）
    self_port: int = request.url.port or 20211

    logger.info("开始执行回放: worker=%s draft=%s port=%d", payload.worker_url, payload.draft_id, self_port)

    try:
        result = await asyncio.to_thread(
            _run_replay,
            payload.worker_url,
            payload.draft_id.strip(),
            self_port,
        )
        return result
    except Exception as exc:
        logger.error("回放执行失败: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ─── 草稿回放 ─────────────────────────────────────────────────────────

@gui_router.get("/replay/{draft_id}")
async def replay_draft(draft_id: str) -> Dict[str, Any]:
    draft_folder = get_settings_manager().require("draft_folder")
    draft_dir = Path(draft_folder) / draft_id

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
