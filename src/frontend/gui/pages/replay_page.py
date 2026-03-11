import json
import threading
import urllib.request
import urllib.error
import customtkinter as ctk
from tkinter import messagebox

from src.frontend.gui.base_page import BasePage
from src.backend.core.settings_manager import get_settings_manager

class ReplayPage(BasePage):
    """回放查看页面 —— 通过 draft_id 向 Cloudflare Worker 拉取调用回放"""

    def __init__(self, parent):
        self.settings = get_settings_manager()
        self._fetch_thread = None
        self._is_fetching = False
        super().__init__(parent, "回放查看")

    # ------------------------------------------------------------------ #
    # UI 构建
    # ------------------------------------------------------------------ #

    def _create_widgets(self):
        title_font = ctk.CTkFont(family="Microsoft YaHei", size=26, weight="bold")
        label_font = ctk.CTkFont(family="Microsoft YaHei", size=13)
        btn_font = ctk.CTkFont(family="Microsoft YaHei", size=14, weight="bold")
        mono_font = ctk.CTkFont(family="Consolas", size=13)

        # 主容器
        main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=("white", "#2D2D2D"))
        main_frame.pack(fill="both", expand=True, padx=8, pady=(8, 4))

        # ── 标题 ──────────────────────────────────────────────────────────
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=25, pady=(25, 5))
        ctk.CTkLabel(header_frame, text="回放查看", font=title_font).pack(side="left")

        ctk.CTkLabel(
            main_frame,
            text="输入草稿 ID，从系统设置中配置的 Worker 拉取调用回放",
            text_color="gray",
            font=label_font,
        ).pack(anchor="w", padx=25, pady=(0, 15))

        # ── 底部：先 pack 防止被挤出视图 ─────────────────────────────────
        self.status_label = ctk.CTkLabel(
            main_frame, text="状态: 就绪", text_color="gray", font=label_font
        )
        self.status_label.pack(side="bottom", pady=(5, 20))

        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", padx=25, pady=(10, 5))

        self.fetch_btn = ctk.CTkButton(
            btn_frame,
            text="拉取回放",
            command=self._on_fetch,
            height=45,
            corner_radius=8,
            font=btn_font,
            fg_color="#0067C0",
            hover_color="#005A9E",
        )
        self.fetch_btn.pack(side="left", padx=(0, 10), expand=True, fill="x")

        self.clear_btn = ctk.CTkButton(
            btn_frame,
            text="清空结果",
            command=self._clear_result,
            height=45,
            corner_radius=8,
            font=btn_font,
            fg_color=("gray75", "gray25"),
            text_color=("gray10", "gray90"),
            hover_color=("gray65", "gray35"),
        )
        self.clear_btn.pack(side="left", expand=True, fill="x")

        # ── 输入区域 ──────────────────────────────────────────────────────
        input_frame = ctk.CTkFrame(main_frame, fg_color=("gray97", "#363636"), corner_radius=10)
        input_frame.pack(fill="x", padx=25, pady=(0, 12))

        # Worker URL：跳转到系统设置配置
        url_row = ctk.CTkFrame(input_frame, fg_color="transparent")
        url_row.pack(fill="x", padx=15, pady=(12, 4))
        ctk.CTkLabel(url_row, text="Worker URL:", font=label_font, width=110, anchor="w").pack(side="left")
        self.worker_url_label = ctk.CTkLabel(
            url_row,
            text=self.settings.get("relay_worker_url", ""),
            text_color=("gray40", "gray70"),
            font=ctk.CTkFont(family="Consolas", size=12),
            anchor="w",
        )
        self.worker_url_label.pack(side="left", padx=(8, 0))
        ctk.CTkButton(
            url_row,
            text="切换 Worker 服务器",
            command=self._go_to_worker_settings,
            height=28,
            corner_radius=6,
            fg_color="transparent",
            border_width=1,
            border_color=("gray60", "gray50"),
            text_color=("gray20", "gray80"),
            hover_color=("gray80", "gray30"),
            font=ctk.CTkFont(family="Microsoft YaHei", size=12),
        ).pack(side="right", padx=(8, 0))

        # Draft ID
        draft_row = ctk.CTkFrame(input_frame, fg_color="transparent")
        draft_row.pack(fill="x", padx=15, pady=(4, 15))
        ctk.CTkLabel(draft_row, text="草稿 ID:", font=label_font, width=110, anchor="w").pack(side="left")

        self.draft_id_var = ctk.StringVar()
        self.draft_id_entry = ctk.CTkEntry(
            draft_row,
            textvariable=self.draft_id_var,
            placeholder_text="virtual_draft_id（如 draft_1710000000000_12345）",
            corner_radius=8,
            fg_color=("white", "#3B3B3B"),
            border_color=("gray70", "gray40"),
        )
        self.draft_id_entry.pack(side="left", fill="x", expand=True, padx=(8, 0))

        # ── 结果区域 ──────────────────────────────────────────────────────
        result_label_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        result_label_frame.pack(fill="x", padx=25, pady=(0, 4))

        ctk.CTkLabel(
            result_label_frame, text="回放数据", font=ctk.CTkFont(family="Microsoft YaHei", size=14, weight="bold")
        ).pack(side="left")

        self.call_count_label = ctk.CTkLabel(
            result_label_frame, text="", text_color="gray", font=label_font
        )
        self.call_count_label.pack(side="left", padx=(10, 0))

        self.result_textbox = ctk.CTkTextbox(
            main_frame,
            font=mono_font,
            fg_color=("gray97", "#383838"),
            corner_radius=8,
            wrap="none",
        )
        self.result_textbox.pack(fill="both", expand=True, padx=25, pady=(0, 8))
        self.result_textbox.configure(state="disabled")

    # ------------------------------------------------------------------ #
    # 事件处理
    # ------------------------------------------------------------------ #

    def _on_fetch(self):
        if self._is_fetching:
            return

        worker_url = self.settings.get("relay_worker_url", "").strip().rstrip("/")
        draft_id = self.draft_id_var.get().strip()

        if not worker_url:
            messagebox.showwarning("未配置 Worker URL", "请先在系统设置的「云服务设置」中填写 Worker URL。", parent=self)
            return
        if not draft_id:
            messagebox.showwarning("缺少草稿 ID", "请填写要查询的草稿 ID。", parent=self)
            return

        self._set_fetching(True)
        self._fetch_thread = threading.Thread(
            target=self._fetch_replay,
            args=(worker_url, draft_id),
            daemon=True,
        )
        self._fetch_thread.start()

    def _fetch_replay(self, worker_url: str, draft_id: str):
        """在子线程中执行 HTTP GET，完成后回调到主线程更新 UI。"""
        url = f"{worker_url}/replay/{draft_id}"
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8")
            data = json.loads(body)
            self.after(0, self._on_fetch_success, data)
        except urllib.error.HTTPError as e:
            err_body = ""
            try:
                err_body = e.read().decode("utf-8")
            except Exception:
                pass
            self.after(0, self._on_fetch_error, f"HTTP {e.code}: {e.reason}\n{err_body}")
        except urllib.error.URLError as e:
            self.after(0, self._on_fetch_error, f"网络错误: {e.reason}")
        except Exception as e:
            self.after(0, self._on_fetch_error, f"未知错误: {e}")

    def _on_fetch_success(self, data: dict):
        total = data.get("total", 0)
        calls = data.get("calls", [])
        segment_ids = data.get("segment_ids", [])

        # 汇总信息
        summary = {
            "virtual_draft_id": data.get("virtual_draft_id"),
            "total_calls": total,
            "segment_count": len(segment_ids),
            "segment_ids": segment_ids,
        }
        lines = [
            "// ── 摘要 " + "─" * 60,
            json.dumps(summary, ensure_ascii=False, indent=2),
            "",
            "// ── 调用列表 " + "─" * 55,
        ]
        for i, call in enumerate(calls, 1):
            lines.append(f"// [{i}/{total}]")
            lines.append(json.dumps(call, ensure_ascii=False, indent=2))
            lines.append("")

        self._set_result("\n".join(lines))
        self.call_count_label.configure(text=f"共 {total} 条调用，{len(segment_ids)} 个片段")
        self._set_status(f"拉取成功：{total} 条调用记录", "green")
        self._set_fetching(False)

    def _on_fetch_error(self, message: str):
        self._set_status(f"拉取失败：{message}", "red")
        self._set_fetching(False)

    def _clear_result(self):
        self._set_result("")
        self.call_count_label.configure(text="")
        self._set_status("状态: 就绪", "gray")

    # ------------------------------------------------------------------ #
    # 辅助方法
    # ------------------------------------------------------------------ #

    def _set_fetching(self, fetching: bool):
        self._is_fetching = fetching
        state = "disabled" if fetching else "normal"
        self.fetch_btn.configure(state=state)
        if fetching:
            self._set_status("正在拉取…", "orange")

    def _set_status(self, text: str, color: str = "gray"):
        self.status_label.configure(text=f"状态: {text}", text_color=color)

    def _set_result(self, text: str):
        self.result_textbox.configure(state="normal")
        self.result_textbox.delete("0.0", "end")
        if text:
            self.result_textbox.insert("0.0", text)
        self.result_textbox.configure(state="disabled")

    def _go_to_worker_settings(self):
        """跳转到系统设置页"""
        self.winfo_toplevel().select_frame_by_name("settings")

    def update_settings(self):
        """切换到本页时刷新 Worker URL 显示标签"""
        self.worker_url_label.configure(text=self.settings.get("relay_worker_url", ""))
