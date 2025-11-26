# -*- coding: utf-8 -*-
"""
主 GUI 应用程序
基于 CustomTkinter 的现代化界面
"""

import os
import sys
import threading
from datetime import datetime
from tkinter import messagebox
from typing import Dict, List

import customtkinter as ctk

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.db_manager import get_db_manager
from src.database.models import EmailAccount, BankCard, GmailAccount, VirtualIdentity
from src.email_handler.receiver import EmailReceiver
from src.utils.email_configs import get_email_config_manager
from src.utils.browser_config import get_browser_config_manager
from src.utils.logger import get_logger
from src.utils.totp_authenticator import TOTPAuthenticator


class MainApplication(ctk.CTk):
    """主应用程序窗口"""

    def __init__(self):
        super().__init__()

        # 配置窗口
        self.title("Python 自动化工具集")
        self.geometry("1200x800")

        # 设置主题
        ctk.set_appearance_mode("dark")  # 可选: "light", "dark", "system"
        ctk.set_default_color_theme("blue")  # 可选: "blue", "green", "dark-blue"

        # 初始化日志
        self.logger = get_logger()
        self.logger.info("应用程序启动")

        # 初始化数据库
        self.db = get_db_manager()
        self.logger.info("数据库初始化完成")

        # 初始化邮箱配置管理器
        self.email_config_mgr = get_email_config_manager(self.db)
        self.email_config_mgr.initialize_default_configs()
        self.logger.info("邮箱配置管理器初始化完成")

        # 初始化浏览器配置管理器
        self.browser_config_mgr = get_browser_config_manager()
        self.logger.info("浏览器配置管理器初始化完成")

        # 创建主布局
        self.setup_ui()

        # 运行状态
        self.is_running = False

    def setup_ui(self):
        """设置 UI 布局"""

        # 配置网格权重
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 创建侧边栏
        self.create_sidebar()

        # 创建状态栏（必须在 create_main_content 之前，因为 show_page 会调用 update_status）
        self.create_statusbar()

        # 创建主内容区域
        self.create_main_content()

    def create_sidebar(self):
        """创建侧边栏导航"""

        # 侧边栏框架
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(10, weight=1)

        # 标题
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="🚀 自动化工具",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 导航按钮
        self.nav_buttons = {}

        buttons_config = [
            ("🏠 主页", "home", 1),
            ("🏊 资料池", "pool", 2),
            ("🧪 功能测试", "functional_test", 3),
            ("🤖 自动化操作", "automation", 4),
            ("⚙️ 设置", "settings", 6),
        ]

        for text, key, row in buttons_config:
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                command=lambda k=key: self.show_page(k),
                height=40,
                font=ctk.CTkFont(size=14),
            )
            btn.grid(row=row, column=0, padx=20, pady=10, sticky="ew")
            self.nav_buttons[key] = btn

        # 主题切换
        self.appearance_mode_label = ctk.CTkLabel(
            self.sidebar_frame, text="外观模式:", anchor="w"
        )
        self.appearance_mode_label.grid(row=11, column=0, padx=20, pady=(10, 0))

        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode,
        )
        self.appearance_mode_optionemenu.grid(row=12, column=0, padx=20, pady=(10, 10))
        self.appearance_mode_optionemenu.set("Dark")

        # 版本信息
        self.version_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="版本 1.0.0",
            font=ctk.CTkFont(size=10),
            text_color="gray",
        )
        self.version_label.grid(row=13, column=0, padx=20, pady=(10, 20))

    def create_main_content(self):
        """创建主内容区域"""

        # 主内容框架
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # 创建不同页面的容器
        self.pages = {}
        self.create_home_page()
        self.create_pool_page()
        self.create_functional_test_page()
        self.create_automation_page()
        # self.create_email_page()
        # self.create_receive_page()
        # self.create_web_page()
        # self.create_sheets_page()
        # self.create_gmail_page()
        # self.create_accounts_page()
        self.create_settings_page()

        # 默认显示主页
        self.show_page("home")

    def create_home_page(self):
        """创建主页"""

        page = ctk.CTkFrame(self.main_frame)
        self.pages["home"] = page

        # 标题
        title = ctk.CTkLabel(
            page,
            text="欢迎使用 Python 自动化工具集",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title.pack(pady=(40, 20))

        # 描述
        desc = ctk.CTkLabel(
            page,
            text="一个集成了网页操作、邮件发送、Google API 等功能的自动化工具",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        desc.pack(pady=(0, 40))

        # 功能卡片容器
        cards_frame = ctk.CTkFrame(page, fg_color="transparent")
        cards_frame.pack(fill="both", expand=True, padx=40)

        # 配置网格
        for i in range(3):
            cards_frame.grid_columnconfigure(i, weight=1)

        # 功能卡片
        cards = [
            ("📧 邮件发送", "发送文本和HTML邮件\n支持附件、抄送密送", "email"),
            ("🌐 网页采集", "自动化网页操作\n数据采集和截图", "web"),
            ("⚙️ 配置管理", "系统设置和配置\n个性化定制", "settings"),
        ]

        for idx, (title, desc, page_key) in enumerate(cards):
            row = idx // 3
            col = idx % 3

            card = ctk.CTkFrame(cards_frame)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            card_title = ctk.CTkLabel(
                card, text=title, font=ctk.CTkFont(size=18, weight="bold")
            )
            card_title.pack(pady=(20, 10))

            card_desc = ctk.CTkLabel(
                card, text=desc, font=ctk.CTkFont(size=12), text_color="gray"
            )
            card_desc.pack(pady=(0, 10))

            card_btn = ctk.CTkButton(
                card,
                text="打开",
                command=lambda k=page_key: self.show_page(k),
                width=100,
            )
            card_btn.pack(pady=(10, 20))

    def create_pool_page(self):
        """创建资料池页面"""
        page = ctk.CTkFrame(self.main_frame)
        self.pages["pool"] = page

        # 页面标题
        title = ctk.CTkLabel(
            page, text="🏊 资料池", font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(20, 10))

        # 创建 TabView
        self.pool_tabview = ctk.CTkTabview(page)
        self.pool_tabview.pack(fill="both", expand=True, padx=20, pady=10)

        # 添加 Tab
        self.pool_tabview.add("全新 Gmail 池")
        self.pool_tabview.add("银行账户池")
        self.pool_tabview.add("可用 Gmail 池")
        self.pool_tabview.add("虚拟资料池")

        # 初始化各个 Tab 的内容
        self.create_new_gmail_tab(self.pool_tabview.tab("全新 Gmail 池"))
        self.create_bank_card_tab(self.pool_tabview.tab("银行账户池"))
        self.create_old_gmail_tab(self.pool_tabview.tab("可用 Gmail 池"))
        self.create_virtual_identity_tab(self.pool_tabview.tab("虚拟资料池"))

    def create_new_gmail_tab(self, parent):
        """创建全新 Gmail 池 Tab 内容"""
        # 左右分栏
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        # 左侧：列表
        left_frame = ctk.CTkFrame(parent)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        ctk.CTkLabel(left_frame, text="全新 Gmail 列表", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.new_gmail_list = ctk.CTkScrollableFrame(left_frame)
        self.new_gmail_list.pack(fill="both", expand=True, padx=5, pady=5)
        
        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="刷新", command=self.refresh_new_gmail_list, width=80).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="新建", command=self.clear_new_gmail_form, width=80).pack(side="left", padx=5)

        # 右侧：编辑表单
        right_frame = ctk.CTkFrame(parent)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        ctk.CTkLabel(right_frame, text="账户详情", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        form_scroll = ctk.CTkScrollableFrame(right_frame)
        form_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        # 表单字段
        self.ng_email = self._create_entry(form_scroll, "邮箱地址:")
        self.ng_password = self._create_entry(form_scroll, "密码:")
        self.ng_2fa = self._create_entry(form_scroll, "2FA 密钥 (可选):")
        self.ng_rec_email = self._create_entry(form_scroll, "辅助邮箱 (可选):")
        self.ng_rec_pwd = self._create_entry(form_scroll, "辅助邮箱密码 (可选):")
        
        # 保存/删除按钮
        action_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=5, pady=10)
        
        ctk.CTkButton(action_frame, text="保存", command=self.save_new_gmail, fg_color="green").pack(side="left", padx=5, expand=True)
        ctk.CTkButton(action_frame, text="删除", command=self.delete_new_gmail, fg_color="red").pack(side="left", padx=5, expand=True)

        self.current_new_gmail_id = None
        self.refresh_new_gmail_list()

    def create_bank_card_tab(self, parent):
        """创建银行账户池 Tab 内容"""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        # 左侧列表
        left_frame = ctk.CTkFrame(parent)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        ctk.CTkLabel(left_frame, text="银行卡列表", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.bank_card_list = ctk.CTkScrollableFrame(left_frame)
        self.bank_card_list.pack(fill="both", expand=True, padx=5, pady=5)
        
        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="刷新", command=self.refresh_bank_card_list, width=80).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="新建", command=self.clear_bank_card_form, width=80).pack(side="left", padx=5)

        # 右侧表单
        right_frame = ctk.CTkFrame(parent)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        ctk.CTkLabel(right_frame, text="银行卡详情", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        form_scroll = ctk.CTkScrollableFrame(right_frame)
        form_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        self.bc_bank_name = self._create_entry(form_scroll, "银行名称:")
        self.bc_card_number = self._create_entry(form_scroll, "卡号:")
        self.bc_holder = self._create_entry(form_scroll, "持卡人姓名:")
        self.bc_expiry = self._create_entry(form_scroll, "过期日期 (MM/YY):")
        self.bc_cvv = self._create_entry(form_scroll, "CVV:")
        self.bc_pin = self._create_entry(form_scroll, "PIN/密码:")
        self.bc_notes = self._create_entry(form_scroll, "备注:")

        action_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=5, pady=10)
        ctk.CTkButton(action_frame, text="保存", command=self.save_bank_card, fg_color="green").pack(side="left", padx=5, expand=True)
        ctk.CTkButton(action_frame, text="删除", command=self.delete_bank_card, fg_color="red").pack(side="left", padx=5, expand=True)

        self.current_bank_card_id = None
        self.refresh_bank_card_list()

    def create_old_gmail_tab(self, parent):
        """创建可用 Gmail 池 Tab 内容 (复用部分逻辑)"""
        # 这里其实可以复用 Accounts Page 的逻辑，或者简单展示
        # 为了保持一致性，我们做一个类似的列表+详情结构
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        left_frame = ctk.CTkFrame(parent)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        ctk.CTkLabel(left_frame, text="可用邮箱列表", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.old_gmail_list = ctk.CTkScrollableFrame(left_frame)
        self.old_gmail_list.pack(fill="both", expand=True, padx=5, pady=5)
        
        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="刷新", command=self.refresh_old_gmail_list, width=80).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="新建", command=self.clear_old_gmail_form, width=80).pack(side="left", padx=5)

        right_frame = ctk.CTkFrame(parent)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        ctk.CTkLabel(right_frame, text="账户详情", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        form_scroll = ctk.CTkScrollableFrame(right_frame)
        form_scroll.pack(fill="both", expand=True, padx=5, pady=5)

        self.og_email = self._create_entry(form_scroll, "邮箱地址:")
        self.og_password = self._create_entry(form_scroll, "授权码:")
        self.og_2fa = self._create_entry(form_scroll, "2FA 密钥:")

        action_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        action_frame.pack(fill="x", padx=5, pady=10)
        ctk.CTkButton(action_frame, text="保存", command=self.save_old_gmail, fg_color="green").pack(side="left", padx=5, expand=True)
        ctk.CTkButton(action_frame, text="删除", command=self.delete_old_gmail, fg_color="red").pack(side="left", padx=5, expand=True)

        self.current_old_gmail_id = None
        self.refresh_old_gmail_list()

    def _create_entry(self, parent, label_text):
        """辅助方法：创建带标签的输入框"""
        ctk.CTkLabel(parent, text=label_text, anchor="w").pack(fill="x", padx=5, pady=(10, 0))
        entry = ctk.CTkEntry(parent)
        entry.pack(fill="x", padx=5, pady=(0, 5))
        return entry

    # --- 全新 Gmail 逻辑 ---
    def refresh_new_gmail_list(self):
        for widget in self.new_gmail_list.winfo_children():
            widget.destroy()
        accounts = self.db.get_all_gmail_accounts()
        for acc in accounts:
            btn = ctk.CTkButton(
                self.new_gmail_list, 
                text=f"{acc.email_address}", 
                command=lambda a=acc: self.load_new_gmail(a),
                fg_color="transparent", border_width=1, text_color=("gray10", "gray90")
            )
            btn.pack(fill="x", padx=2, pady=2)

    def load_new_gmail(self, account):
        self.current_new_gmail_id = account.id
        self.ng_email.delete(0, "end"); self.ng_email.insert(0, account.email_address)
        self.ng_password.delete(0, "end"); self.ng_password.insert(0, account.password)
        self.ng_2fa.delete(0, "end"); self.ng_2fa.insert(0, account.twofa_secret or "")
        self.ng_rec_email.delete(0, "end"); self.ng_rec_email.insert(0, account.recovery_email or "")
        self.ng_rec_pwd.delete(0, "end"); self.ng_rec_pwd.insert(0, account.recovery_password or "")

    def clear_new_gmail_form(self):
        self.current_new_gmail_id = None
        for entry in [self.ng_email, self.ng_password, self.ng_2fa, self.ng_rec_email, self.ng_rec_pwd]:
            entry.delete(0, "end")

    def save_new_gmail(self):
        acc = GmailAccount(
            id=self.current_new_gmail_id,
            email_address=self.ng_email.get(),
            password=self.ng_password.get(),
            twofa_secret=self.ng_2fa.get(),
            recovery_email=self.ng_rec_email.get(),
            recovery_password=self.ng_rec_pwd.get()
        )
        if self.current_new_gmail_id:
            self.db.update_gmail_account(acc)
        else:
            self.db.add_gmail_account(acc)
        self.refresh_new_gmail_list()
        self.update_status("全新 Gmail 保存成功")

    def delete_new_gmail(self):
        if self.current_new_gmail_id:
            if messagebox.askyesno("确认", "确定删除该账户？"):
                self.db.delete_gmail_account(self.current_new_gmail_id)
                self.clear_new_gmail_form()
                self.refresh_new_gmail_list()

    # --- 银行卡逻辑 ---
    def refresh_bank_card_list(self):
        for widget in self.bank_card_list.winfo_children():
            widget.destroy()
        cards = self.db.get_all_bank_cards()
        for card in cards:
            btn = ctk.CTkButton(
                self.bank_card_list, 
                text=f"{card.bank_name} - {card.cardholder_name}", 
                command=lambda c=card: self.load_bank_card(c),
                fg_color="transparent", border_width=1, text_color=("gray10", "gray90")
            )
            btn.pack(fill="x", padx=2, pady=2)

    def load_bank_card(self, card):
        self.current_bank_card_id = card.id
        self.bc_bank_name.delete(0, "end"); self.bc_bank_name.insert(0, card.bank_name)
        self.bc_card_number.delete(0, "end"); self.bc_card_number.insert(0, card.card_number)
        self.bc_holder.delete(0, "end"); self.bc_holder.insert(0, card.cardholder_name)
        self.bc_expiry.delete(0, "end"); self.bc_expiry.insert(0, card.expiry_date)
        self.bc_cvv.delete(0, "end"); self.bc_cvv.insert(0, card.cvv or "")
        self.bc_pin.delete(0, "end"); self.bc_pin.insert(0, card.pin or "")
        self.bc_notes.delete(0, "end"); self.bc_notes.insert(0, card.notes or "")

    def clear_bank_card_form(self):
        self.current_bank_card_id = None
        for entry in [self.bc_bank_name, self.bc_card_number, self.bc_holder, self.bc_expiry, self.bc_cvv, self.bc_pin, self.bc_notes]:
            entry.delete(0, "end")

    def save_bank_card(self):
        card = BankCard(
            id=self.current_bank_card_id,
            bank_name=self.bc_bank_name.get(),
            card_number=self.bc_card_number.get(),
            cardholder_name=self.bc_holder.get(),
            expiry_date=self.bc_expiry.get(),
            cvv=self.bc_cvv.get(),
            pin=self.bc_pin.get(),
            notes=self.bc_notes.get()
        )
        if self.current_bank_card_id:
            self.db.update_bank_card(card)
        else:
            self.db.add_bank_card(card)
        self.refresh_bank_card_list()
        self.update_status("银行卡保存成功")

    def delete_bank_card(self):
        if self.current_bank_card_id:
            if messagebox.askyesno("确认", "确定删除该银行卡？"):
                self.db.delete_bank_card(self.current_bank_card_id)
                self.clear_bank_card_form()
                self.refresh_bank_card_list()

    # --- 原有 Gmail 逻辑 ---
    def refresh_old_gmail_list(self):
        for widget in self.old_gmail_list.winfo_children():
            widget.destroy()
        accounts = self.db.get_all_email_accounts()
        for acc in accounts:
            btn = ctk.CTkButton(
                self.old_gmail_list, 
                text=f"{acc.email_address}", 
                command=lambda a=acc: self.load_old_gmail(a),
                fg_color="transparent", border_width=1, text_color=("gray10", "gray90")
            )
            btn.pack(fill="x", padx=2, pady=2)

    def load_old_gmail(self, account):
        self.current_old_gmail_id = account.id
        self.og_email.delete(0, "end"); self.og_email.insert(0, account.email_address)
        self.og_password.delete(0, "end"); self.og_password.insert(0, account.password)
        self.og_2fa.delete(0, "end"); self.og_2fa.insert(0, account.twofa_secret or "")

    def clear_old_gmail_form(self):
        self.current_old_gmail_id = None
        for entry in [self.og_email, self.og_password, self.og_2fa]:
            entry.delete(0, "end")

    def save_old_gmail(self):
        acc = EmailAccount(
            id=self.current_old_gmail_id,
            email_address=self.og_email.get(),
            password=self.og_password.get(),
            twofa_secret=self.og_2fa.get()
        )
        if self.current_old_gmail_id:
            self.db.update_email_account(acc)
        else:
            self.db.add_email_account(acc)
        self.refresh_old_gmail_list()
        self.refresh_accounts_list() # 同时刷新主账户页面的列表
        self.update_status("原有 Gmail 保存成功")

    def delete_old_gmail(self):
        if self.current_old_gmail_id:
            if messagebox.askyesno("确认", "确定删除该账户？"):
                self.db.delete_email_account(self.current_old_gmail_id)
                self.clear_old_gmail_form()
                self.refresh_old_gmail_list()
                self.refresh_accounts_list()

    def create_functional_test_page(self):
        """创建功能测试页面"""
        page = ctk.CTkFrame(self.main_frame)
        self.pages["functional_test"] = page

        # 页面标题
        title = ctk.CTkLabel(
            page, text="🧪 功能测试", font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(20, 10))

        # 创建 TabView
        self.func_tabview = ctk.CTkTabview(page)
        self.func_tabview.pack(fill="both", expand=True, padx=20, pady=10)

        # 添加 Tab
        self.func_tabview.add("邮件发送")
        self.func_tabview.add("邮件接收")
        self.func_tabview.add("网页采集")

        # 初始化各个 Tab 的内容
        self.setup_email_send_tab(self.func_tabview.tab("邮件发送"))
        self.setup_email_receive_tab(self.func_tabview.tab("邮件接收"))
        self.setup_web_scraping_tab(self.func_tabview.tab("网页采集"))

    def setup_email_send_tab(self, parent):
        """创建邮件发送 Tab 内容"""
        # 表单容器
        form_frame = ctk.CTkFrame(parent)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 账户选择区域
        account_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        account_frame.grid(row=0, column=0, columnspan=2, pady=(20, 10), sticky="ew", padx=20)

        ctk.CTkLabel(
            account_frame,
            text="发件人账户:",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(side="left", padx=(0, 10))

        # 获取已保存的账户
        saved_accounts = self.db.get_all_email_accounts()
        # 过滤出有邮箱地址的账户
        self.email_accounts_map = {acc.email_address: acc for acc in saved_accounts if acc.email_address}
        account_names = ["请选择账户"] + list(self.email_accounts_map.keys())

        self.selected_email_account_var = ctk.StringVar(value="请选择账户")
        self.email_account_menu = ctk.CTkOptionMenu(
            account_frame,
            values=account_names,
            variable=self.selected_email_account_var,
            width=300,
            height=35,
        )
        self.email_account_menu.pack(side="left", padx=5)
        
        ctk.CTkButton(
            account_frame,
            text="刷新列表",
            command=self.refresh_email_send_accounts,
            width=80,
            height=35,
        ).pack(side="left", padx=10)

        # 邮件内容区域
        mail_label = ctk.CTkLabel(
            form_frame, text="邮件内容", font=ctk.CTkFont(size=16, weight="bold")
        )
        mail_label.grid(
            row=1, column=0, columnspan=2, pady=(20, 10), sticky="w", padx=20
        )

        # 收件人
        ctk.CTkLabel(form_frame, text="收件人:").grid(
            row=2, column=0, padx=20, pady=10, sticky="w"
        )
        self.recipient_entry = ctk.CTkEntry(
            form_frame, width=300, placeholder_text="recipient@example.com"
        )
        self.recipient_entry.grid(row=2, column=1, padx=20, pady=10, sticky="ew")

        # 主题
        ctk.CTkLabel(form_frame, text="主题:").grid(
            row=3, column=0, padx=20, pady=10, sticky="w"
        )
        self.subject_entry = ctk.CTkEntry(
            form_frame, width=300, placeholder_text="邮件主题"
        )
        self.subject_entry.grid(row=3, column=1, padx=20, pady=10, sticky="ew")

        # 邮件正文
        ctk.CTkLabel(form_frame, text="正文:").grid(
            row=4, column=0, padx=20, pady=10, sticky="nw"
        )
        self.body_textbox = ctk.CTkTextbox(form_frame, width=300, height=150)
        self.body_textbox.grid(row=4, column=1, padx=20, pady=10, sticky="ew")

        # 按钮区域
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)

        self.send_email_btn = ctk.CTkButton(
            button_frame,
            text="发送邮件",
            command=self.send_email_functional,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.send_email_btn.pack(side="left", padx=10)

        self.clear_email_btn = ctk.CTkButton(
            button_frame,
            text="清空",
            command=self.clear_email_form,
            width=100,
            height=40,
            fg_color="gray",
        )
        self.clear_email_btn.pack(side="left", padx=10)

        # 配置列权重
        form_frame.grid_columnconfigure(1, weight=1)

    def refresh_email_send_accounts(self):
        """刷新邮件发送页面的账户列表"""
        saved_accounts = self.db.get_all_email_accounts()
        self.email_accounts_map = {acc.email_address: acc for acc in saved_accounts if acc.email_address}
        account_names = ["请选择账户"] + list(self.email_accounts_map.keys())
        self.email_account_menu.configure(values=account_names)
        self.selected_email_account_var.set("请选择账户")
        self.update_status("账户列表已刷新")

    def send_email_functional(self):
        """功能测试页面：发送邮件"""
        self.update_status("正在发送邮件...")
        
        # 获取选中的账户
        selected_email = self.selected_email_account_var.get()
        if selected_email == "请选择账户":
            messagebox.showwarning("提示", "请先选择发件人账户")
            return
            
        account = self.email_accounts_map.get(selected_email)
        if not account:
            messagebox.showerror("错误", "账户信息无效")
            return

        # 获取表单数据
        recipient = self.recipient_entry.get()
        subject = self.subject_entry.get()
        body = self.body_textbox.get("1.0", "end-1c")

        if not all([recipient, subject]):
            messagebox.showerror("错误", "请填写收件人和主题")
            return

        # 获取SMTP配置
        email_type = account.get_email_type()
        smtp_server, smtp_port = self.email_config_mgr.get_smtp_config(email_type)
        
        if not smtp_server:
            messagebox.showerror("错误", f"未找到 {email_type} 的SMTP配置")
            return

        # 在线程中发送
        def send_task():
            try:
                from src.email_handler.sender import EmailSender
                
                sender = EmailSender(
                    smtp_server=smtp_server,
                    smtp_port=smtp_port,
                    sender_email=account.email_address,
                    sender_password=account.password,
                    use_tls=True
                )
                
                recipients = [r.strip() for r in recipient.split(",")]
                success = sender.send_simple_email(recipients, subject, body)
                
                if success:
                    self.after(0, lambda: messagebox.showinfo("成功", "邮件发送成功！"))
                    self.after(0, lambda: self.update_status("邮件发送成功"))
                else:
                    self.after(0, lambda: messagebox.showerror("失败", "邮件发送失败"))
                    self.after(0, lambda: self.update_status("邮件发送失败"))
                    
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("错误", f"发送出错: {str(e)}"))
                self.logger.error(f"发送邮件错误: {e}")

        thread = threading.Thread(target=send_task, daemon=True)
        thread.start()

    def setup_email_receive_tab(self, parent):
        """创建邮件接收 Tab 内容"""
        # 配置网格
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=2)
        parent.grid_rowconfigure(0, weight=1)

        # 左侧控制面板
        control_frame = ctk.CTkFrame(parent)
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # 账户选择区域
        account_section = ctk.CTkFrame(control_frame)
        account_section.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            account_section, text="选择账户", font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # 获取已保存的邮箱账户
        saved_accounts = self.db.get_all_email_accounts()
        account_options = ["请选择账户"] + [acc.email_address for acc in saved_accounts]

        self.receive_account_var = ctk.StringVar(value="请选择账户")
        self.receive_account_menu = ctk.CTkOptionMenu(
            account_section,
            values=account_options,
            variable=self.receive_account_var,
            width=280,
            height=35,
        )
        self.receive_account_menu.pack(padx=10, pady=(0, 10), fill="x")

        # 获取设置区域
        settings_section = ctk.CTkFrame(control_frame)
        settings_section.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            settings_section, text="获取设置", font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

        # 邮件数量
        count_frame = ctk.CTkFrame(settings_section, fg_color="transparent")
        count_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(count_frame, text="获取数量:").pack(side="left", padx=(0, 10))
        self.email_count_var = ctk.StringVar(value="10")
        count_options = ["5", "10", "20", "50", "100"]
        self.email_count_menu = ctk.CTkOptionMenu(
            count_frame, values=count_options, variable=self.email_count_var, width=100
        )
        self.email_count_menu.pack(side="left")

        # 只获取未读
        self.unread_only_var = ctk.BooleanVar(value=False)
        self.unread_only_checkbox = ctk.CTkCheckBox(
            settings_section,
            text="只获取未读邮件",
            variable=self.unread_only_var,
            font=ctk.CTkFont(size=13),
        )
        self.unread_only_checkbox.pack(anchor="w", padx=10, pady=10)

        # 文件夹选择
        folder_frame = ctk.CTkFrame(settings_section, fg_color="transparent")
        folder_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(folder_frame, text="邮件夹:").pack(side="left", padx=(0, 10))
        self.email_folder_var = ctk.StringVar(value="INBOX")
        self.email_folder_entry = ctk.CTkEntry(
            folder_frame, textvariable=self.email_folder_var, width=150
        )
        self.email_folder_entry.pack(side="left")

        # 按钮区域
        button_section = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_section.pack(fill="x", padx=20, pady=20)

        self.fetch_emails_btn = ctk.CTkButton(
            button_section,
            text="📥 获取邮件",
            command=self.fetch_emails,
            width=280,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.fetch_emails_btn.pack(pady=5)

        self.refresh_accounts_btn = ctk.CTkButton(
            button_section,
            text="🔄 刷新账户列表",
            command=self.refresh_receive_accounts,
            width=280,
            height=35,
            fg_color="gray",
        )
        self.refresh_accounts_btn.pack(pady=5)

        # 状态信息
        self.receive_status_label = ctk.CTkLabel(
            control_frame, text="", font=ctk.CTkFont(size=11), text_color="gray"
        )
        self.receive_status_label.pack(pady=10)

        # 右侧邮件列表区域
        list_frame = ctk.CTkFrame(parent)
        list_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(1, weight=1)

        # 列表标题
        list_title = ctk.CTkLabel(
            list_frame, text="邮件列表", font=ctk.CTkFont(size=16, weight="bold")
        )
        list_title.grid(row=0, column=0, pady=10, padx=20, sticky="w")

        # 邮件列表（可滚动）
        self.email_list_frame = ctk.CTkScrollableFrame(list_frame)
        self.email_list_frame.grid(
            row=1, column=0, padx=10, pady=(0, 10), sticky="nsew"
        )
        self.email_list_frame.grid_columnconfigure(0, weight=1)

        # 初始提示
        initial_label = ctk.CTkLabel(
            self.email_list_frame,
            text="请选择账户并点击「获取邮件」",
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        initial_label.grid(row=0, column=0, pady=50)

        # 邮件详情区域
        detail_frame = ctk.CTkFrame(parent)
        detail_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        detail_frame.grid_columnconfigure(0, weight=1)
        detail_frame.grid_rowconfigure(1, weight=1)

        # 详情标题
        detail_title = ctk.CTkLabel(
            detail_frame, text="邮件详情", font=ctk.CTkFont(size=16, weight="bold")
        )
        detail_title.grid(row=0, column=0, pady=10, padx=20, sticky="w")

        # 详情显示
        self.email_detail_textbox = ctk.CTkTextbox(detail_frame, wrap="word")
        self.email_detail_textbox.grid(
            row=1, column=0, padx=10, pady=(0, 10), sticky="nsew"
        )
        self.email_detail_textbox.insert("1.0", "选择一封邮件查看详情...")
        self.email_detail_textbox.configure(state="disabled")

        # 存储当前邮件列表
        self.current_emails: List[Dict] = []

    def setup_web_scraping_tab(self, parent):
        """创建网页采集 Tab 内容"""
        # 表单容器
        form_frame = ctk.CTkFrame(parent)
        form_frame.pack(fill="both", expand=True, padx=40, pady=20)

        # URL 输入
        ctk.CTkLabel(form_frame, text="目标 URL:", font=ctk.CTkFont(size=14)).grid(
            row=0, column=0, padx=20, pady=10, sticky="w"
        )
        self.url_entry = ctk.CTkEntry(
            form_frame, width=400, placeholder_text="https://example.com"
        )
        self.url_entry.grid(row=0, column=1, padx=20, pady=10, sticky="ew")

        # 浏览器选择
        ctk.CTkLabel(form_frame, text="浏览器:", font=ctk.CTkFont(size=14)).grid(
            row=1, column=0, padx=20, pady=10, sticky="w"
        )
        self.browser_var = ctk.StringVar(value="chrome")
        browser_options = ctk.CTkSegmentedButton(
            form_frame, values=["chrome", "firefox", "edge"], variable=self.browser_var
        )
        browser_options.grid(row=1, column=1, padx=20, pady=10, sticky="w")

        # 无头模式
        self.headless_var = ctk.BooleanVar(value=False)
        headless_checkbox = ctk.CTkCheckBox(
            form_frame, text="无头模式（后台运行）", variable=self.headless_var
        )
        headless_checkbox.grid(row=2, column=1, padx=20, pady=10, sticky="w")

        # 操作选择
        ctk.CTkLabel(form_frame, text="操作:", font=ctk.CTkFont(size=14)).grid(
            row=3, column=0, padx=20, pady=10, sticky="w"
        )

        operations_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        operations_frame.grid(row=3, column=1, padx=20, pady=10, sticky="w")

        self.screenshot_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            operations_frame, text="截图", variable=self.screenshot_var
        ).pack(side="left", padx=(0, 20))

        self.get_title_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            operations_frame, text="获取标题", variable=self.get_title_var
        ).pack(side="left", padx=(0, 20))

        self.get_links_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            operations_frame, text="提取链接", variable=self.get_links_var
        ).pack(side="left")

        # 结果显示区域
        ctk.CTkLabel(form_frame, text="执行结果:", font=ctk.CTkFont(size=14)).grid(
            row=4, column=0, padx=20, pady=10, sticky="nw"
        )
        self.web_result_textbox = ctk.CTkTextbox(form_frame, width=400, height=200)
        self.web_result_textbox.grid(row=4, column=1, padx=20, pady=10, sticky="ew")

        # 按钮区域
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)

        self.run_web_btn = ctk.CTkButton(
            button_frame,
            text="开始执行",
            command=self.run_web_automation,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.run_web_btn.pack(side="left", padx=10)

        self.stop_web_btn = ctk.CTkButton(
            button_frame,
            text="停止",
            command=self.stop_web_automation,
            width=100,
            height=40,
            fg_color="red",
            state="disabled",
        )
        self.stop_web_btn.pack(side="left", padx=10)

        # 配置列权重
        form_frame.grid_columnconfigure(1, weight=1)

    def create_automation_page(self):
        """创建自动化操作页面"""
        page = ctk.CTkFrame(self.main_frame)
        self.pages["automation"] = page

        # 页面标题
        title = ctk.CTkLabel(
            page, text="🤖 自动化操作", font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(20, 10))

        # 创建 TabView
        self.auto_tabview = ctk.CTkTabview(page)
        self.auto_tabview.pack(fill="both", expand=True, padx=20, pady=10)

        # 添加 Tab
        self.auto_tabview.add("获取邮箱授权码")
        self.auto_tabview.add("Gmail 注册")
        self.auto_tabview.add("生成虚拟信息")

        # 初始化各个 Tab 的内容
        self.setup_get_auth_code_tab(self.auto_tabview.tab("获取邮箱授权码"))
        self.setup_gmail_registration_tab(self.auto_tabview.tab("Gmail 注册"))
        self.setup_identity_generator_tab(self.auto_tabview.tab("生成虚拟信息"))

    def setup_get_auth_code_tab(self, parent):
        """创建获取邮箱授权码 Tab 内容"""
        # 表单容器
        form_frame = ctk.CTkFrame(parent)
        form_frame.pack(fill="both", expand=True, padx=40, pady=20)

        ctk.CTkLabel(form_frame, text="此功能将自动化登录邮箱并获取授权码", font=ctk.CTkFont(size=14)).pack(pady=20)
        
        ctk.CTkButton(form_frame, text="开始获取", command=lambda: messagebox.showinfo("提示", "功能开发中...")).pack(pady=10)

    def setup_gmail_registration_tab(self, parent):
        """创建 Gmail 注册 Tab 内容"""
        # 表单容器
        form_frame = ctk.CTkFrame(parent)
        form_frame.pack(fill="both", expand=True, padx=40, pady=20)

        ctk.CTkLabel(form_frame, text="自动化注册 Gmail 账户", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            form_frame, 
            text="注意：由于 Google 的反自动化机制，通常需要手机号验证。\n此脚本将自动填写表单，但在手机验证步骤可能需要人工干预。", 
            font=ctk.CTkFont(size=12),
            text_color="orange"
        ).pack(pady=(0, 20))

        # 选项
        self.reg_headless_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(form_frame, text="无头模式 (后台运行，不推荐)", variable=self.reg_headless_var).pack(pady=10)

        # 身份来源选项
        self.identity_source_var = ctk.StringVar(value="random")
        
        identity_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        identity_frame.pack(pady=10)
        
        ctk.CTkLabel(identity_frame, text="身份信息来源:").pack(side="left", padx=(0, 10))
        
        ctk.CTkRadioButton(
            identity_frame, 
            text="随机生成", 
            variable=self.identity_source_var, 
            value="random"
        ).pack(side="left", padx=10)
        
        ctk.CTkRadioButton(
            identity_frame, 
            text="使用虚拟身份库", 
            variable=self.identity_source_var, 
            value="virtual"
        ).pack(side="left", padx=10)

        # 按钮
        self.run_reg_btn = ctk.CTkButton(
            form_frame, 
            text="开始注册", 
            command=self.run_gmail_registration,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.run_reg_btn.pack(pady=20)

        # 结果日志
        self.reg_log_textbox = ctk.CTkTextbox(form_frame, height=200)
        self.reg_log_textbox.pack(pady=10, fill="both", expand=True)

    def run_gmail_registration(self):
        """运行 Gmail 注册"""
        self.run_reg_btn.configure(state="disabled")
        self.reg_log_textbox.delete("1.0", "end")
        self.reg_log_textbox.insert("end", "正在启动注册流程...\n")
        
        # 获取选项
        identity_source = self.identity_source_var.get()
        
        def reg_task():
            try:
                from src.web_automation.gmail_registration import GmailRegistrator
                
                identity = None
                if identity_source == "virtual":
                    self.after(0, lambda: self.reg_log_textbox.insert("end", "正在获取未使用的虚拟身份...\n"))
                    identity = self.db.get_unused_virtual_identity()
                    if not identity:
                        self.after(0, lambda: self.reg_log_textbox.insert("end", "错误: 没有可用的虚拟身份！请先生成。\n"))
                        self.after(0, lambda: messagebox.showwarning("提示", "没有可用的虚拟身份！请先在'虚拟身份生成'标签页生成。"))
                        return
                    self.after(0, lambda: self.reg_log_textbox.insert("end", f"使用身份: {identity.full_name}\n"))
                
                registrator = GmailRegistrator(headless=self.reg_headless_var.get())
                success, msg = registrator.register_new_account(identity=identity)
                
                self.after(0, lambda: self.reg_log_textbox.insert("end", f"\n结果: {'成功' if success else '未完成'}\n"))
                self.after(0, lambda: self.reg_log_textbox.insert("end", f"详情: {msg}\n"))
                
                if success:
                    if identity:
                        self.db.mark_virtual_identity_as_used(identity.id)
                        self.after(0, lambda: self.reg_log_textbox.insert("end", "已标记身份为已使用。\n"))
                        
                    self.after(0, lambda: messagebox.showinfo("成功", "注册成功并已保存！"))
                    # 刷新全新 Gmail 池列表
                    self.after(0, self.refresh_new_gmail_list)
                else:
                    self.after(0, lambda: messagebox.showwarning("提示", f"注册未完成: {msg}"))
                    
            except Exception as e:
                self.after(0, lambda: self.reg_log_textbox.insert("end", f"\n错误: {str(e)}\n"))
                self.logger.error(f"Gmail 注册错误: {e}")
            finally:
                self.after(0, lambda: self.run_reg_btn.configure(state="normal"))

        thread = threading.Thread(target=reg_task, daemon=True)
        thread.start()


    def setup_identity_generator_tab(self, parent):
        """创建虚拟信息生成 Tab 内容"""
        # 表单容器
        form_frame = ctk.CTkFrame(parent)
        form_frame.pack(fill="both", expand=True, padx=40, pady=20)

        ctk.CTkLabel(form_frame, text="自动化生成虚拟身份信息", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            form_frame, 
            text="数据来源: haoweichi.com\n将自动抓取数据并存入虚拟资料池", 
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=(0, 20))

        # 设置区域
        settings_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        settings_frame.pack(pady=10)

        ctk.CTkLabel(settings_frame, text="生成数量:").pack(side="left", padx=10)
        self.gen_count_entry = ctk.CTkEntry(settings_frame, width=100)
        self.gen_count_entry.insert(0, "1")
        self.gen_count_entry.pack(side="left", padx=10)

        self.gen_headless_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(settings_frame, text="后台运行 (无头模式)", variable=self.gen_headless_var).pack(side="left", padx=20)

        # 按钮
        self.run_gen_btn = ctk.CTkButton(
            form_frame, 
            text="开始生成", 
            command=self.run_identity_generation,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.run_gen_btn.pack(pady=20)

        # 结果日志
        self.gen_log_textbox = ctk.CTkTextbox(form_frame, height=200)
        self.gen_log_textbox.pack(pady=10, fill="both", expand=True)

    def run_identity_generation(self):
        """运行身份生成"""
        try:
            count = int(self.gen_count_entry.get())
            if count < 1:
                messagebox.showerror("错误", "数量必须大于0")
                return
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return

        self.run_gen_btn.configure(state="disabled")
        self.gen_log_textbox.delete("1.0", "end")
        self.gen_log_textbox.insert("end", f"准备生成 {count} 个虚拟身份...\n")
        
        def gen_task():
            try:
                from src.web_automation.identity_generator import IdentityGenerator
                
                def log_callback(msg):
                    self.after(0, lambda: self.gen_log_textbox.insert("end", f"{msg}\n"))
                    self.after(0, lambda: self.gen_log_textbox.see("end"))

                generator = IdentityGenerator(headless=self.gen_headless_var.get())
                identities = generator.generate_identities(count=count, callback=log_callback)
                
                # 保存到数据库
                success_count = 0
                for identity in identities:
                    try:
                        self.db.add_virtual_identity(identity)
                        success_count += 1
                    except Exception as e:
                        log_callback(f"保存数据库失败: {str(e)}")

                self.after(0, lambda: messagebox.showinfo("完成", f"生成完成！\n成功保存: {success_count}/{count}"))
                self.after(0, lambda: self.gen_log_textbox.insert("end", f"\n任务结束。成功保存 {success_count} 个身份。\n"))
                
                # 刷新资料池页面
                self.after(0, self.refresh_virtual_identity_list)
                    
            except Exception as e:
                self.after(0, lambda: self.gen_log_textbox.insert("end", f"\n错误: {str(e)}\n"))
                self.logger.error(f"身份生成错误: {e}")
            finally:
                self.after(0, lambda: self.run_gen_btn.configure(state="normal"))

        thread = threading.Thread(target=gen_task, daemon=True)
        thread.start()




    def create_virtual_identity_tab(self, parent):
        """创建虚拟资料池 Tab 内容"""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        # 左侧列表
        left_frame = ctk.CTkFrame(parent)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        ctk.CTkLabel(left_frame, text="虚拟身份列表", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.virtual_identity_list = ctk.CTkScrollableFrame(left_frame)
        self.virtual_identity_list.pack(fill="both", expand=True, padx=5, pady=5)
        
        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="刷新", command=self.refresh_virtual_identity_list, width=80).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="删除", command=self.delete_virtual_identity, width=80, fg_color="red").pack(side="left", padx=5)

        # 右侧详情
        right_frame = ctk.CTkFrame(parent)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        
        ctk.CTkLabel(right_frame, text="身份详情", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.vi_detail_textbox = ctk.CTkTextbox(right_frame, wrap="word")
        self.vi_detail_textbox.pack(fill="both", expand=True, padx=5, pady=5)

        self.current_virtual_identity_id = None
        self.refresh_virtual_identity_list()

    def refresh_virtual_identity_list(self):
        for widget in self.virtual_identity_list.winfo_children():
            widget.destroy()
        identities = self.db.get_all_virtual_identities()
        for identity in identities:
            btn = ctk.CTkButton(
                self.virtual_identity_list, 
                text=f"{identity.first_name} {identity.last_name}", 
                command=lambda i=identity: self.load_virtual_identity(i),
                fg_color="transparent", border_width=1, text_color=("gray10", "gray90")
            )
            btn.pack(fill="x", padx=2, pady=2)

    def load_virtual_identity(self, identity):
        self.current_virtual_identity_id = identity.id
        self.vi_detail_textbox.delete("1.0", "end")
        
        detail = f"姓名: {identity.first_name} {identity.last_name}\n"
        detail += f"性别: {identity.gender}\n"
        detail += f"出生日期: {identity.birthday}\n"
        detail += f"地址: {identity.street_address}, {identity.city}, {identity.state} {identity.zip_code}\n"
        detail += f"电话: {identity.phone}\n"
        detail += f"SSN: {identity.ssn}\n"
        detail += f"邮箱: {identity.temp_email}\n"
        detail += f"用户名: {identity.username}\n"
        detail += f"密码: {identity.password}\n"
        detail += f"生成时间: {identity.created_at}\n"
        detail += f"是否使用: {'是' if identity.is_used else '否'}\n"
        
        self.vi_detail_textbox.insert("1.0", detail)

    def delete_virtual_identity(self):
        if self.current_virtual_identity_id:
            if messagebox.askyesno("确认", "确定删除该身份信息？"):
                self.db.delete_virtual_identity(self.current_virtual_identity_id)
                self.vi_detail_textbox.delete("1.0", "end")
                self.current_virtual_identity_id = None
                self.refresh_virtual_identity_list()

    def create_settings_page(self):
        """创建设置页面"""

        page = ctk.CTkScrollableFrame(self.main_frame)
        self.pages["settings"] = page

        # 页面标题
        title = ctk.CTkLabel(
            page, text="⚙️ 系统设置", font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(pady=(20, 30))

        # 设置容器
        settings_frame = ctk.CTkFrame(page)
        settings_frame.pack(fill="both", expand=True, padx=40, pady=20)

        # ==================== 邮箱服务器配置 ====================
        ctk.CTkLabel(
            settings_frame,
            text="📧 邮箱服务器配置",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, pady=(20, 10), sticky="w", padx=20)

        # 说明文字
        ctk.CTkLabel(
            settings_frame,
            text="管理全局的SMTP和IMAP服务器配置，所有账户将使用这些配置",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).grid(row=1, column=0, columnspan=3, pady=(0, 10), sticky="w", padx=20)

        # 邮箱类型选择
        ctk.CTkLabel(settings_frame, text="邮箱类型:", font=ctk.CTkFont(size=14)).grid(
            row=2, column=0, padx=20, pady=10, sticky="w"
        )

        email_types = self.email_config_mgr.get_email_types()
        self.settings_email_type_var = ctk.StringVar(
            value=email_types[0] if email_types else "Gmail"
        )
        email_type_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=email_types,
            variable=self.settings_email_type_var,
            command=self.on_settings_email_type_change,
            width=200,
        )
        email_type_menu.grid(row=2, column=1, padx=20, pady=10, sticky="w")

        # SMTP服务器
        ctk.CTkLabel(
            settings_frame, text="SMTP服务器:", font=ctk.CTkFont(size=14)
        ).grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.settings_smtp_entry = ctk.CTkEntry(settings_frame, width=300)
        self.settings_smtp_entry.grid(row=3, column=1, padx=20, pady=10, sticky="w")

        # SMTP端口
        ctk.CTkLabel(settings_frame, text="SMTP端口:", font=ctk.CTkFont(size=14)).grid(
            row=4, column=0, padx=20, pady=10, sticky="w"
        )
        self.settings_smtp_port_entry = ctk.CTkEntry(settings_frame, width=150)
        self.settings_smtp_port_entry.grid(
            row=4, column=1, padx=20, pady=10, sticky="w"
        )

        # IMAP服务器
        ctk.CTkLabel(
            settings_frame, text="IMAP服务器:", font=ctk.CTkFont(size=14)
        ).grid(row=5, column=0, padx=20, pady=10, sticky="w")
        self.settings_imap_entry = ctk.CTkEntry(settings_frame, width=300)
        self.settings_imap_entry.grid(row=5, column=1, padx=20, pady=10, sticky="w")

        # IMAP端口
        ctk.CTkLabel(settings_frame, text="IMAP端口:", font=ctk.CTkFont(size=14)).grid(
            row=6, column=0, padx=20, pady=10, sticky="w"
        )
        self.settings_imap_port_entry = ctk.CTkEntry(settings_frame, width=150)
        self.settings_imap_port_entry.grid(
            row=6, column=1, padx=20, pady=10, sticky="w"
        )

        # 使用TLS
        self.settings_use_tls_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            settings_frame, text="使用TLS加密", variable=self.settings_use_tls_var
        ).grid(row=7, column=1, padx=20, pady=10, sticky="w")

        # 配置描述
        ctk.CTkLabel(settings_frame, text="描述:", font=ctk.CTkFont(size=14)).grid(
            row=8, column=0, padx=20, pady=10, sticky="w"
        )
        self.settings_description_entry = ctk.CTkEntry(settings_frame, width=300)
        self.settings_description_entry.grid(
            row=8, column=1, padx=20, pady=10, sticky="w"
        )

        # 邮箱配置按钮
        email_config_btn_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        email_config_btn_frame.grid(row=9, column=0, columnspan=3, pady=20)

        ctk.CTkButton(
            email_config_btn_frame,
            text="💾 保存配置",
            command=self.save_email_config,
            width=120,
            height=35,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            email_config_btn_frame,
            text="🔄 重置默认",
            command=self.reset_email_config,
            width=120,
            height=35,
            fg_color="orange",
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            email_config_btn_frame,
            text="📤 导出配置",
            command=self.export_email_configs,
            width=120,
            height=35,
            fg_color="green",
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            email_config_btn_frame,
            text="📥 导入配置",
            command=self.import_email_configs,
            width=120,
            height=35,
            fg_color="blue",
        ).pack(side="left", padx=5)

        # 分隔线
        separator1 = ctk.CTkFrame(settings_frame, height=2, fg_color="gray30")
        separator1.grid(row=10, column=0, columnspan=3, sticky="ew", padx=20, pady=20)

        # ==================== 通用设置 ====================
        ctk.CTkLabel(
            settings_frame, text="⚙️ 通用设置", font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=11, column=0, columnspan=3, pady=(20, 10), sticky="w", padx=20)

        # 日志级别
        ctk.CTkLabel(settings_frame, text="日志级别:", font=ctk.CTkFont(size=14)).grid(
            row=12, column=0, padx=20, pady=10, sticky="w"
        )
        self.log_level_var = ctk.StringVar(value="INFO")
        log_level_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            variable=self.log_level_var,
        )
        log_level_menu.grid(row=12, column=1, padx=20, pady=10, sticky="w")

        # 自动保存
        self.auto_save_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            settings_frame, text="自动保存配置", variable=self.auto_save_var
        ).grid(row=13, column=1, padx=20, pady=10, sticky="w")

        # 分隔线
        separator2 = ctk.CTkFrame(settings_frame, height=2, fg_color="gray30")
        separator2.grid(row=14, column=0, columnspan=3, sticky="ew", padx=20, pady=20)

        # ==================== 路径设置 ====================
        ctk.CTkLabel(
            settings_frame, text="📁 路径设置", font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=15, column=0, columnspan=3, pady=(20, 10), sticky="w", padx=20)

        # 输出目录
        ctk.CTkLabel(settings_frame, text="输出目录:", font=ctk.CTkFont(size=14)).grid(
            row=16, column=0, padx=20, pady=10, sticky="w"
        )
        output_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        output_frame.grid(row=16, column=1, padx=20, pady=10, sticky="ew")

        self.output_dir_entry = ctk.CTkEntry(
            output_frame, width=300, placeholder_text="output/"
        )
        self.output_dir_entry.pack(side="left", padx=(0, 10))

        ctk.CTkButton(output_frame, text="浏览", width=80).pack(side="left")

        # 日志目录
        ctk.CTkLabel(settings_frame, text="日志目录:", font=ctk.CTkFont(size=14)).grid(
            row=17, column=0, padx=20, pady=10, sticky="w"
        )
        log_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        log_frame.grid(row=17, column=1, padx=20, pady=10, sticky="ew")

        self.log_dir_entry = ctk.CTkEntry(
            log_frame, width=300, placeholder_text="logs/"
        )
        self.log_dir_entry.pack(side="left", padx=(0, 10))

        ctk.CTkButton(log_frame, text="浏览", width=80).pack(side="left")

        # 分隔线
        separator3 = ctk.CTkFrame(settings_frame, height=2, fg_color="gray30")
        separator3.grid(row=18, column=0, columnspan=3, sticky="ew", padx=20, pady=20)

        # ==================== 浏览器设置 ====================
        ctk.CTkLabel(
            settings_frame, text="🌐 浏览器设置", font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=19, column=0, columnspan=3, pady=(20, 10), sticky="w", padx=20)

        # 启用指纹
        self.enable_fingerprint_var = ctk.BooleanVar(value=self.browser_config_mgr.get("enable_fingerprint", True))
        ctk.CTkCheckBox(
            settings_frame, text="启用浏览器指纹 (随机User-Agent和窗口大小)", variable=self.enable_fingerprint_var
        ).grid(row=20, column=1, padx=20, pady=10, sticky="w")

        # 分隔线
        separator4 = ctk.CTkFrame(settings_frame, height=2, fg_color="gray30")
        separator4.grid(row=21, column=0, columnspan=3, sticky="ew", padx=20, pady=20)

        # ==================== 关于信息 ====================
        ctk.CTkLabel(
            settings_frame, text="ℹ️ 关于", font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=22, column=0, columnspan=3, pady=(20, 10), sticky="w", padx=20)

        about_text = """
Python 自动化工具集 v1.0.0

功能特性:
• 网页自动化操作
• 邮件发送（SMTP 和 Gmail API）
• 邮件接收（IMAP）
• Google Sheets 数据处理
• 完善的日志系统
• 全局邮箱配置管理
• 浏览器指纹随机化

开发: Python + CustomTkinter
许可证: MIT License
        """

        about_label = ctk.CTkLabel(
            settings_frame, text=about_text, font=ctk.CTkFont(size=12), justify="left"
        )
        about_label.grid(row=23, column=0, columnspan=3, padx=20, pady=10, sticky="w")

        # 按钮区域
        button_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        button_frame.grid(row=24, column=0, columnspan=3, pady=30)

        ctk.CTkButton(
            button_frame,
            text="保存所有设置",
            command=self.save_settings,
            width=150,
            height=40,
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            text="重置所有设置",
            command=self.reset_settings,
            width=150,
            height=40,
            fg_color="gray",
        ).pack(side="left", padx=10)

        # 加载当前邮箱配置
        self.load_current_email_config()

    def create_statusbar(self):
        """创建状态栏"""

        self.statusbar = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.statusbar.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 10))

        self.status_label = ctk.CTkLabel(
            self.statusbar, text="就绪", font=ctk.CTkFont(size=11)
        )
        self.status_label.pack(side="left", padx=10)

        self.time_label = ctk.CTkLabel(
            self.statusbar,
            text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            font=ctk.CTkFont(size=11),
        )
        self.time_label.pack(side="right", padx=10)

        # 更新时间
        self.update_time()

    def update_time(self):
        """更新状态栏时间"""
        self.time_label.configure(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.after(1000, self.update_time)

    def show_page(self, page_name):
        """显示指定页面"""

        # 隐藏所有页面
        for page in self.pages.values():
            page.grid_forget()

        # 显示目标页面
        if page_name in self.pages:
            self.pages[page_name].grid(row=0, column=0, sticky="nsew")
            self.update_status(f"已切换到: {page_name}")
            self.logger.info(f"切换页面: {page_name}")

    def change_appearance_mode(self, mode):
        """切换外观模式"""
        ctk.set_appearance_mode(mode.lower())
        self.logger.info(f"外观模式已切换: {mode}")

    def update_status(self, message):
        """更新状态栏消息"""
        self.status_label.configure(text=message)
        self.logger.info(message)

    # ==================== 功能实现方法 ====================

    def send_email(self):
        """发送邮件"""
        self.update_status("正在发送邮件...")

        # 获取表单数据
        smtp_server = self.smtp_server_entry.get()
        smtp_port = self.smtp_port_entry.get()
        sender_email = self.sender_email_entry.get()
        sender_password = self.sender_password_entry.get()
        recipient = self.recipient_entry.get()
        subject = self.subject_entry.get()
        body = self.body_textbox.get("1.0", "end-1c")

        # 验证输入
        if not all(
            [smtp_server, smtp_port, sender_email, sender_password, recipient, subject]
        ):
            messagebox.showerror("错误", "请填写所有必填字段！")
            self.update_status("发送失败：缺少必填字段")
            return

        # 验证端口号
        try:
            port = int(smtp_port)
        except ValueError:
            messagebox.showerror("错误", "端口号必须是数字！")
            self.update_status("发送失败：端口号格式错误")
            return

        # 在线程中发送邮件，避免界面冻结
        def send_task():
            try:
                from src.email_handler.sender import EmailSender

                # 创建邮件发送器
                sender = EmailSender(
                    smtp_server=smtp_server,
                    smtp_port=port,
                    sender_email=sender_email,
                    sender_password=sender_password,
                    use_tls=True,
                )

                # 发送邮件
                recipients = [r.strip() for r in recipient.split(",")]
                success = sender.send_simple_email(recipients, subject, body)

                # 更新UI（需要在主线程中）
                if success:
                    self.after(0, lambda: messagebox.showinfo("成功", "邮件发送成功！"))
                    self.after(0, lambda: self.update_status("邮件发送成功"))
                    self.logger.info(f"邮件发送成功到: {recipient}")
                else:
                    self.after(
                        0,
                        lambda: messagebox.showerror(
                            "失败", "邮件发送失败，请检查配置和网络连接"
                        ),
                    )
                    self.after(0, lambda: self.update_status("邮件发送失败"))
                    self.logger.error(f"邮件发送失败到: {recipient}")

            except Exception as e:
                error_msg = f"发送邮件时出错: {str(e)}"
                self.after(0, lambda: messagebox.showerror("错误", error_msg))
                self.after(0, lambda: self.update_status("邮件发送出错"))
                self.logger.error(error_msg)

        # 启动发送线程
        thread = threading.Thread(target=send_task, daemon=True)
        thread.start()
        self.logger.info(f"开始发送邮件到: {recipient}")

    def load_saved_email_account(self, email_address: str):
        """从数据库加载已保存的邮箱账户"""
        if email_address == "手动配置":
            return

        # 根据邮箱地址获取账户
        account = self.db.get_email_account_by_address(email_address)
        if not account:
            messagebox.showerror("错误", f"未找到账户: {email_address}")
            return

        # 获取邮箱类型
        email_type = account.get_email_type()

        # 从全局配置获取 SMTP 配置
        smtp_server, smtp_port = self.email_config_mgr.get_smtp_config(email_type)

        # 填充表单
        self.smtp_server_entry.delete(0, "end")
        self.smtp_server_entry.insert(0, smtp_server)

        self.smtp_port_entry.delete(0, "end")
        self.smtp_port_entry.insert(0, str(smtp_port))

        self.sender_email_entry.delete(0, "end")
        self.sender_email_entry.insert(0, account.email_address)

        self.sender_password_entry.delete(0, "end")
        self.sender_password_entry.insert(0, account.password)

        self.update_status(f"已加载账户: {email_address}")
        self.logger.info(f"从数据库加载邮箱账户: {email_address}")

        # 更新最后使用时间
        if account.id is not None:
            self.db.update_last_used(account.id)

    def set_gmail_config(self):
        """设置Gmail快捷配置"""
        self.smtp_server_entry.delete(0, "end")
        self.smtp_server_entry.insert(0, "smtp.gmail.com")
        self.smtp_port_entry.delete(0, "end")
        self.smtp_port_entry.insert(0, "587")
        self.load_account_var.set("手动配置")
        self.update_status("已设置Gmail配置 (需要使用应用专用密码)")
        messagebox.showinfo(
            "Gmail 配置说明",
            "Gmail SMTP已配置！\n\n"
            "重要提示：\n"
            "1. 不能使用Gmail登录密码\n"
            "2. 必须开启两步验证\n"
            "3. 使用应用专用密码\n\n"
            "获取应用专用密码：\n"
            "访问: https://myaccount.google.com/apppasswords\n"
            "生成16位密码后填入密码框\n\n"
            "提示: 可以在「账户管理」页面保存配置",
        )

    def set_qq_config(self):
        """设置QQ邮箱快捷配置"""
        self.smtp_server_entry.delete(0, "end")
        self.smtp_server_entry.insert(0, "smtp.qq.com")
        self.smtp_port_entry.delete(0, "end")
        self.smtp_port_entry.insert(0, "587")
        self.load_account_var.set("手动配置")
        self.update_status("已设置QQ邮箱配置 (需要使用授权码)")
        messagebox.showinfo(
            "QQ邮箱配置说明",
            "QQ邮箱SMTP已配置！\n\n"
            "重要提示：\n"
            "1. 不能使用QQ密码\n"
            "2. 必须使用授权码\n\n"
            "获取授权码：\n"
            "登录QQ邮箱 -> 设置 -> 账户\n"
            "-> 开启SMTP服务 -> 生成授权码\n\n"
            "提示: 可以在「账户管理」页面保存配置",
        )

    def clear_email_form(self):
        """清空邮件表单"""
        self.recipient_entry.delete(0, "end")
        self.subject_entry.delete(0, "end")
        self.body_textbox.delete("1.0", "end")
        self.update_status("表单已清空")

    # ==================== 账户管理功能 ====================

    def refresh_accounts_list(self):
        """刷新账户列表"""
        # 清空现有列表
        for widget in self.accounts_listbox.winfo_children():
            widget.destroy()

        # 获取所有账户
        accounts = self.db.get_all_email_accounts()

        if not accounts:
            no_account_label = ctk.CTkLabel(
                self.accounts_listbox,
                text="暂无账户\n点击「新建」添加",
                text_color="gray",
                font=ctk.CTkFont(size=12),
            )
            no_account_label.pack(pady=20)
            return

        # 显示账户列表
        for account in accounts:
            # 获取邮箱类型
            email_type = account.get_email_type()

            # 创建账户项
            item_frame = ctk.CTkFrame(self.accounts_listbox)
            item_frame.pack(fill="x", padx=5, pady=5)

            # 邮箱信息
            info_label = ctk.CTkLabel(
                item_frame,
                text=f"📧 {account.email_address}\n类型: {email_type}",
                anchor="w",
                font=ctk.CTkFont(size=11),
            )
            info_label.pack(side="left", padx=10, pady=5, fill="x", expand=True)

            # 2FA 标记
            if account.twofa_secret:
                twofa_label = ctk.CTkLabel(
                    item_frame, text="🔐", font=ctk.CTkFont(size=12)
                )
                twofa_label.pack(side="right", padx=5)

            # 加载按钮
            load_btn = ctk.CTkButton(
                item_frame,
                text="编辑",
                width=60,
                height=28,
                command=lambda aid=account.id: self.load_account(aid),
            )
            load_btn.pack(side="right", padx=5, pady=5)

        self.update_status(f"已加载 {len(accounts)} 个账户")

    def add_new_account(self):
        """添加新账户"""
        self.current_account_id = None
        self.clear_account_form()
        self.update_status("请填写新账户信息")

    def clear_account_form(self):
        """清空账户表单"""
        self.current_account_id = None
        self.acc_email_entry.delete(0, "end")
        self.acc_password_entry.delete(0, "end")
        self.acc_twofa_entry.delete(0, "end")

    def load_account(self, account_id: int):
        """加载账户到表单"""
        account = self.db.get_email_account(account_id)
        if not account:
            messagebox.showerror("错误", "账户不存在！")
            return

        self.current_account_id = account_id

        # 填充表单
        self.acc_email_entry.delete(0, "end")
        self.acc_email_entry.insert(0, account.email_address)

        self.acc_password_entry.delete(0, "end")
        self.acc_password_entry.insert(0, account.password)

        self.acc_twofa_entry.delete(0, "end")
        self.acc_twofa_entry.insert(0, account.twofa_secret or "")

        # 显示邮箱类型（自动推断）
        email_type = account.get_email_type()
        self.update_status(f"已加载账户: {account.email_address} ({email_type})")

        # 如果有 2FA 密钥，自动显示验证码
        if account.twofa_secret:
            self.show_totp_code()
        else:
            self.stop_totp_countdown()

    def save_account(self):
        """保存账户"""
        # 验证输入
        email_address = self.acc_email_entry.get().strip()
        password = self.acc_password_entry.get().strip()
        twofa_secret = self.acc_twofa_entry.get().strip()

        if not email_address or not password:
            messagebox.showerror("错误", "邮箱地址和密码不能为空！")
            return

        # 验证邮箱格式
        if "@" not in email_address:
            messagebox.showerror("错误", "请输入有效的邮箱地址！")
            return

        # 创建账户对象
        account = EmailAccount(
            id=self.current_account_id,
            email_address=email_address,
            password=password,
            twofa_secret=twofa_secret if twofa_secret else None,
        )

        try:
            if self.current_account_id:
                # 更新现有账户
                success = self.db.update_email_account(account)
                if success:
                    messagebox.showinfo("成功", "账户已更新！")
                    email_type = account.get_email_type()
                    self.update_status(f"账户已更新: {email_address} ({email_type})")
                else:
                    messagebox.showerror("错误", "更新失败！")
            else:
                # 添加新账户
                account_id = self.db.add_email_account(account)
                self.current_account_id = account_id
                messagebox.showinfo("成功", "账户已保存！")
                email_type = account.get_email_type()
                self.update_status(f"账户已保存: {email_address} ({email_type})")

            # 刷新列表
            self.refresh_accounts_list()

        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
            self.logger.error(f"保存账户失败: {str(e)}")

    def delete_account(self):
        """删除账户"""
        if not self.current_account_id:
            messagebox.showwarning("提示", "请先选择要删除的账户！")
            return

        # 确认删除
        account = self.db.get_email_account(self.current_account_id)
        if not account:
            messagebox.showerror("错误", "账户不存在！")
            return

        confirm = messagebox.askyesno(
            "确认删除",
            f"确定要删除账户「{account.email_address}」吗？\n此操作不可恢复！",
        )

        if confirm:
            try:
                success = self.db.delete_email_account(self.current_account_id)
                if success:
                    messagebox.showinfo("成功", "账户已删除！")
                    self.update_status(f"账户已删除: {account.email_address}")
                    self.current_account_id = None
                    self.clear_account_form()
                    self.refresh_accounts_list()
                else:
                    messagebox.showerror("错误", "删除失败！")
            except Exception as e:
                messagebox.showerror("错误", f"删除失败: {str(e)}")
                self.logger.error(f"删除账户失败: {str(e)}")

    def test_account(self):
        """测试账户连接（简化版）"""
        # 获取表单数据
        email_address = self.acc_email_entry.get().strip()
        password = self.acc_password_entry.get().strip()

        if not email_address or not password:
            messagebox.showerror("错误", "请填写邮箱地址和密码！")
            return

        # 创建临时账户对象
        account = EmailAccount(email_address=email_address, password=password)

        # 获取邮箱类型
        email_type = account.get_email_type()

        if email_type == "其他":
            messagebox.showwarning(
                "提示",
                f"无法自动识别邮箱类型: {email_address}\n请在全局配置中添加该邮箱类型的配置",
            )
            return

        # 从全局配置获取 SMTP 配置
        smtp_server, smtp_port = self.email_config_mgr.get_smtp_config(email_type)

        if not smtp_server:
            messagebox.showerror(
                "错误",
                f"{email_type} 邮箱配置不存在！\n请先在「⚙️ 设置」中配置 {email_type} 的 SMTP 服务器",
            )
            return

        # 在新线程中测试连接
        def test_task():
            try:
                # 尝试连接
                import smtplib

                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(email_address, password)

                # 成功
                self.after(
                    0,
                    lambda: messagebox.showinfo(
                        "成功",
                        f"✓ 连接成功！\n\n"
                        f"邮箱: {email_address}\n"
                        f"类型: {email_type}\n"
                        f"SMTP: {smtp_server}:{smtp_port}",
                    ),
                )
                self.after(0, lambda: self.update_status("✓ 测试连接成功"))

            except Exception as e:
                self.after(
                    0,
                    lambda: messagebox.showerror(
                        "连接失败",
                        f"✗ 无法连接到 SMTP 服务器\n\n"
                        f"错误: {str(e)}\n\n"
                        f"提示:\n"
                        f"1. 检查邮箱地址和密码是否正确\n"
                        f"2. Gmail/QQ/163等需要使用授权码\n"
                        f"3. 检查网络连接",
                    ),
                )
                self.after(0, lambda: self.update_status("✗ 测试连接失败"))

        import threading

        thread = threading.Thread(target=test_task, daemon=True)
        thread.start()
        self.update_status("正在测试连接...")

    def run_web_automation(self):
        """运行网页自动化"""
        self.update_status("正在执行网页自动化...")
        self.run_web_btn.configure(state="disabled")
        self.stop_web_btn.configure(state="normal")

        url = self.url_entry.get()

        if not url:
            messagebox.showerror("错误", "请输入目标 URL！")
            self.run_web_btn.configure(state="normal")
            self.stop_web_btn.configure(state="disabled")
            return

        # TODO: 实现实际的网页自动化逻辑
        # 使用线程避免界面冻结
        def automation_task():
            try:
                self.web_result_textbox.insert("end", f"正在打开: {url}\n")
                self.web_result_textbox.insert("end", "浏览器启动成功\n")
                self.web_result_textbox.insert("end", "页面加载完成\n")

                if self.screenshot_var.get():
                    self.web_result_textbox.insert(
                        "end", "截图已保存到 output/screenshot.png\n"
                    )

                if self.get_title_var.get():
                    self.web_result_textbox.insert("end", "页面标题: Example Domain\n")

                self.web_result_textbox.insert("end", "\n✓ 执行完成\n")
                self.update_status("网页自动化执行完成")

            except Exception as e:
                self.web_result_textbox.insert("end", f"\n✗ 错误: {str(e)}\n")
                self.logger.error(f"网页自动化错误: {e}")
            finally:
                self.run_web_btn.configure(state="normal")
                self.stop_web_btn.configure(state="disabled")

        thread = threading.Thread(target=automation_task)
        thread.daemon = True
        thread.start()

    def stop_web_automation(self):
        """停止网页自动化"""
        self.update_status("正在停止...")
        self.run_web_btn.configure(state="normal")
        self.stop_web_btn.configure(state="disabled")

    def on_sheets_operation_change(self, value):
        """Sheets 操作改变时的回调"""
        if value == "read":
            self.sheets_data_textbox.configure(state="disabled")
        else:
            self.sheets_data_textbox.configure(state="normal")

    def run_sheets_operation(self):
        """执行 Sheets 操作"""
        self.update_status("正在执行 Google Sheets 操作...")

        spreadsheet_id = self.spreadsheet_id_entry.get()
        range_name = self.sheet_range_entry.get()
        operation = self.sheets_operation_var.get()

        if not spreadsheet_id or not range_name:
            messagebox.showerror("错误", "请填写电子表格 ID 和范围！")
            return

        # TODO: 实现实际的 Sheets 操作
        result_text = f"操作: {operation}\n"
        result_text += f"电子表格 ID: {spreadsheet_id}\n"
        result_text += f"范围: {range_name}\n\n"
        result_text += "✓ 操作完成（占位符）\n"

        self.sheets_result_textbox.delete("1.0", "end")
        self.sheets_result_textbox.insert("1.0", result_text)
        self.update_status("Sheets 操作完成")

    def get_gmail_messages(self):
        """获取 Gmail 邮件"""
        self.update_status("正在获取 Gmail 邮件...")

        max_results = self.gmail_max_results.get() or "10"

        # TODO: 实现实际的 Gmail 读取逻辑
        result_text = f"正在获取最新 {max_results} 封邮件...\n\n"
        result_text += "示例邮件列表:\n"
        result_text += (
            "1. 主题: 欢迎使用\n   发件人: admin@example.com\n   日期: 2024-01-01\n\n"
        )
        result_text += (
            "2. 主题: 系统通知\n   发件人: system@example.com\n   日期: 2024-01-02\n\n"
        )
        result_text += "✓ 获取完成（占位符）\n"

        self.gmail_result_textbox.delete("1.0", "end")
        self.gmail_result_textbox.insert("1.0", result_text)
        self.update_status("Gmail 邮件获取完成")

    def send_gmail(self):
        """发送 Gmail"""
        self.update_status("正在发送 Gmail...")

        to = self.gmail_to_entry.get()
        subject = self.gmail_subject_entry.get()
        body = self.gmail_body_textbox.get("1.0", "end-1c")

        if not all([to, subject, body]):
            messagebox.showerror("错误", "请填写所有必填字段！")
            return

        # TODO: 实现实际的 Gmail 发送逻辑
        messagebox.showinfo("提示", f"Gmail 发送功能待实现\n收件人: {to}")
        self.update_status("Gmail 发送完成（占位符）")

    def load_current_email_config(self):
        """加载当前选择的邮箱配置"""
        email_type = self.settings_email_type_var.get()
        config = self.email_config_mgr.get_config(email_type)

        if config:
            self.settings_smtp_entry.delete(0, "end")
            self.settings_smtp_entry.insert(0, config.get("smtp_server", ""))

            self.settings_smtp_port_entry.delete(0, "end")
            self.settings_smtp_port_entry.insert(0, str(config.get("smtp_port", 587)))

            self.settings_imap_entry.delete(0, "end")
            self.settings_imap_entry.insert(0, config.get("imap_server", ""))

            self.settings_imap_port_entry.delete(0, "end")
            self.settings_imap_port_entry.insert(0, str(config.get("imap_port", 993)))

            self.settings_use_tls_var.set(config.get("use_tls", True))

            self.settings_description_entry.delete(0, "end")
            self.settings_description_entry.insert(0, config.get("description", ""))

    def on_settings_email_type_change(self, choice: str):
        """设置页面邮箱类型改变时加载配置"""
        self.load_current_email_config()
        self.update_status(f"已加载 {choice} 配置")

    def save_email_config(self):
        """保存邮箱配置"""
        email_type = self.settings_email_type_var.get()
        smtp_server = self.settings_smtp_entry.get().strip()
        smtp_port_str = self.settings_smtp_port_entry.get().strip()
        imap_server = self.settings_imap_entry.get().strip()
        imap_port_str = self.settings_imap_port_entry.get().strip()
        description = self.settings_description_entry.get().strip()

        # 验证输入
        if not all([smtp_server, smtp_port_str, imap_server, imap_port_str]):
            messagebox.showerror("错误", "请填写完整的服务器配置信息！")
            return

        try:
            smtp_port = int(smtp_port_str)
            imap_port = int(imap_port_str)
        except ValueError:
            messagebox.showerror("错误", "端口必须是数字！")
            return

        # 保存配置
        success = self.email_config_mgr.save_config(
            email_type=email_type,
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            imap_server=imap_server,
            imap_port=imap_port,
            use_tls=self.settings_use_tls_var.get(),
            description=description,
        )

        if success:
            messagebox.showinfo("成功", f"{email_type} 邮箱配置已保存！")
            self.update_status(f"{email_type} 配置已保存")
            self.logger.info(f"保存邮箱配置: {email_type}")
        else:
            messagebox.showerror("错误", "保存配置失败！")

    def reset_email_config(self):
        """重置邮箱配置为默认值"""
        email_type = self.settings_email_type_var.get()

        result = messagebox.askyesno(
            "确认", f"确定要将 {email_type} 配置重置为默认值吗？"
        )

        if result:
            success = self.email_config_mgr.reset_to_default(email_type)
            if success:
                self.load_current_email_config()
                messagebox.showinfo("成功", f"{email_type} 配置已重置为默认值！")
                self.update_status(f"{email_type} 配置已重置")
                self.logger.info(f"重置邮箱配置: {email_type}")
            else:
                messagebox.showerror("错误", "重置失败！该邮箱类型没有默认配置。")

    def export_email_configs(self):
        """导出所有邮箱配置"""
        from tkinter import filedialog

        filepath = filedialog.asksaveasfilename(
            title="导出邮箱配置",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
        )

        if filepath:
            success = self.email_config_mgr.export_configs(filepath)
            if success:
                messagebox.showinfo("成功", f"配置已导出到:\n{filepath}")
                self.update_status("邮箱配置已导出")
                self.logger.info(f"导出邮箱配置: {filepath}")
            else:
                messagebox.showerror("错误", "导出配置失败！")

    def import_email_configs(self):
        """导入邮箱配置"""
        from tkinter import filedialog

        filepath = filedialog.askopenfilename(
            title="导入邮箱配置",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
        )

        if filepath:
            result = messagebox.askyesno("确认", "导入配置将覆盖现有配置，确定继续吗？")

            if result:
                success = self.email_config_mgr.import_configs(filepath)
                if success:
                    self.email_config_mgr.clear_cache()
                    self.load_current_email_config()
                    messagebox.showinfo("成功", "配置已成功导入！")
                    self.update_status("邮箱配置已导入")
                    self.logger.info(f"导入邮箱配置: {filepath}")
                else:
                    messagebox.showerror("错误", "导入配置失败！")

    def save_settings(self):
        """保存设置"""
        # 保存浏览器配置
        browser_config = {
            "enable_fingerprint": self.enable_fingerprint_var.get(),
            "headless": False, # 默认值，可以在UI中添加更多设置
            "browser_type": "chrome"
        }
        self.browser_config_mgr.save_config(browser_config)
        
        messagebox.showinfo("提示", "设置已保存！")
        self.logger.info("设置已保存")

    def reset_settings(self):
        """重置设置"""
        result = messagebox.askyesno("确认", "确定要重置所有设置为默认值吗？")
        if result:
            # 重置浏览器配置
            default_browser_config = self.browser_config_mgr.get_default_config()
            self.browser_config_mgr.save_config(default_browser_config)
            self.enable_fingerprint_var.set(default_browser_config["enable_fingerprint"])
            
            self.logger.info("设置已重置")
            self.log_level_var.set("INFO")
            self.auto_save_var.set(True)
            self.output_dir_entry.delete(0, "end")
            self.output_dir_entry.insert(0, "output/")
            self.log_dir_entry.delete(0, "end")
            self.log_dir_entry.insert(0, "logs/")
            messagebox.showinfo("提示", "设置已重置为默认值！")
            self.update_status("设置已重置")

    def refresh_receive_accounts(self):
        """刷新邮件接收的账户列表"""
        saved_accounts = self.db.get_all_email_accounts()
        account_options = ["请选择账户"] + [acc.email_address for acc in saved_accounts]

        self.receive_account_menu.configure(values=account_options)
        self.receive_account_var.set("请选择账户")
        self.update_status("账户列表已刷新")

    def fetch_emails(self):
        """获取邮件列表"""
        # 获取选中的账户
        selected = self.receive_account_var.get()

        if selected == "请选择账户":
            messagebox.showwarning("提示", "请先选择一个邮箱账户")
            return

        # 从数据库获取账户信息
        # selected 就是 email_address
        account = self.db.get_email_account_by_address(selected)

        if not account:
            messagebox.showerror("错误", "未找到账户信息")
            return

        # 获取设置
        limit = int(self.email_count_var.get())
        unread_only = self.unread_only_var.get()
        folder = self.email_folder_var.get()

        # 更新状态
        self.receive_status_label.configure(text="正在连接服务器...")
        self.fetch_emails_btn.configure(state="disabled", text="正在获取...")

        # 在后台线程执行
        def fetch_task():
            try:
                # 创建接收器
                # 获取邮箱类型和IMAP配置
                email_type = account.get_email_type()
                imap_server, imap_port = self.email_config_mgr.get_imap_config(
                    email_type
                )

                receiver = EmailReceiver(
                    imap_server=imap_server,
                    imap_port=imap_port,
                    email_address=account.email_address,
                    password=account.password,
                )

                # 连接服务器
                if not receiver.connect():
                    self.after(
                        0,
                        lambda: messagebox.showerror(
                            "错误", "连接IMAP服务器失败，请检查账户配置"
                        ),
                    )
                    return

                self.after(
                    0,
                    lambda: self.receive_status_label.configure(text="正在获取邮件..."),
                )

                # 获取邮件
                if unread_only:
                    emails = receiver.get_unread_emails(limit=limit)
                else:
                    emails = receiver.fetch_emails(
                        criteria="ALL", folder=folder, limit=limit
                    )

                # 断开连接
                receiver.disconnect()

                # 更新UI
                self.after(0, lambda: self.display_emails(emails))

                # 更新状态
                status_msg = f"成功获取 {len(emails)} 封邮件"
                if unread_only:
                    status_msg += " (未读)"
                self.after(
                    0, lambda: self.receive_status_label.configure(text=status_msg)
                )
                self.after(0, lambda: self.update_status(status_msg))

            except Exception as e:
                error_msg = f"获取邮件失败: {str(e)}"
                self.after(0, lambda: messagebox.showerror("错误", error_msg))
                self.after(
                    0, lambda: self.receive_status_label.configure(text="获取失败")
                )
                self.logger.error(error_msg)
            finally:
                self.after(
                    0,
                    lambda: self.fetch_emails_btn.configure(
                        state="normal", text="📥 获取邮件"
                    ),
                )

        # 启动线程
        thread = threading.Thread(target=fetch_task, daemon=True)
        thread.start()

    def display_emails(self, emails: List[Dict]):
        """显示邮件列表"""
        # 清空现有列表
        for widget in self.email_list_frame.winfo_children():
            widget.destroy()

        # 保存邮件列表
        self.current_emails = emails

        if not emails:
            no_email_label = ctk.CTkLabel(
                self.email_list_frame,
                text="没有找到邮件",
                font=ctk.CTkFont(size=14),
                text_color="gray",
            )
            no_email_label.grid(row=0, column=0, pady=50)
            return

        # 显示每封邮件
        for idx, email in enumerate(emails):
            email_item = self.create_email_item(email, idx)
            email_item.grid(row=idx, column=0, padx=10, pady=5, sticky="ew")

    def create_email_item(self, email: Dict, index: int):
        """创建邮件列表项"""
        item_frame = ctk.CTkFrame(self.email_list_frame, fg_color=("gray85", "gray20"))
        item_frame.grid_columnconfigure(1, weight=1)

        # 序号
        index_label = ctk.CTkLabel(
            item_frame,
            text=f"{index + 1}",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=30,
        )
        index_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        # 发件人
        from_text = email.get("from", "未知")
        if len(from_text) > 30:
            from_text = from_text[:27] + "..."
        from_label = ctk.CTkLabel(
            item_frame, text=f"来自: {from_text}", font=ctk.CTkFont(size=12), anchor="w"
        )
        from_label.grid(row=0, column=1, padx=10, pady=(10, 2), sticky="w")

        # 主题
        subject_text = email.get("subject", "无主题")
        if len(subject_text) > 40:
            subject_text = subject_text[:37] + "..."
        subject_label = ctk.CTkLabel(
            item_frame,
            text=subject_text,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        )
        subject_label.grid(row=1, column=1, padx=10, pady=(2, 10), sticky="w")

        # 日期
        date_text = email.get("date", "")
        if len(date_text) > 20:
            date_text = date_text[:17] + "..."
        date_label = ctk.CTkLabel(
            item_frame, text=date_text, font=ctk.CTkFont(size=10), text_color="gray"
        )
        date_label.grid(row=0, column=2, padx=10, pady=10)

        # 附件标识
        if email.get("has_attachments", False):
            attachment_label = ctk.CTkLabel(
                item_frame, text="📎", font=ctk.CTkFont(size=14)
            )
            attachment_label.grid(row=1, column=2, padx=10, pady=10)

        # 查看详情按钮
        view_btn = ctk.CTkButton(
            item_frame,
            text="查看",
            command=lambda e=email: self.show_email_detail(e),
            width=60,
            height=28,
        )
        view_btn.grid(row=0, column=3, rowspan=2, padx=10, pady=10)

        return item_frame

    def show_email_detail(self, email: Dict):
        """显示邮件详情"""
        self.email_detail_textbox.configure(state="normal")
        self.email_detail_textbox.delete("1.0", "end")

        # 格式化邮件详情
        detail_text = f"""
╔══════════════════════════════════════════════════════════════╗
  邮件详情
╚══════════════════════════════════════════════════════════════╝

📧 主题: {email.get("subject", "无主题")}

👤 发件人: {email.get("from", "未知")}

📅 日期: {email.get("date", "未知")}

📎 附件: {"是 (" + ", ".join(email.get("attachments", [])) + ")" if email.get("has_attachments", False) else "否"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 正文内容:

{email.get("body", "无内容")}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        self.email_detail_textbox.insert("1.0", detail_text)
        self.email_detail_textbox.configure(state="disabled")
        self.update_status(f"正在查看邮件: {email.get('subject', '无主题')}")

    def on_closing(self):
        """窗口关闭事件"""
        self.logger.info("应用程序关闭")
        self.destroy()


def main():
    """主函数"""
    app = MainApplication()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()


if __name__ == "__main__":
    main()