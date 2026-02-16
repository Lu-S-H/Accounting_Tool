"""
記帳工具 - 現代化UI介面
使用 customtkinter 實現美觀的介面設計
"""

import customtkinter as ctk
from tkinter import ttk, messagebox, Toplevel
from datetime import datetime, date
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import json
import os
from collections import defaultdict
from tkcalendar import Calendar

# 設置外觀模式和顏色主題
ctk.set_appearance_mode("light")  # 可選: "light", "dark", "system"
ctk.set_default_color_theme("blue")  # 可選: "blue", "green", "dark-blue"


class AccountingApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("💰 記帳工具")
        self.root.geometry("1200x700")
        
        # 數據存儲
        self.data_file = "accounting_data.json"
        self.records = self.load_data()
        
        # 消費方式選項
        self.payment_methods = ["現金", "信用卡", "行動支付", "轉帳", "其他"]
        
        # 項目分類選項
        self.expense_categories = ["餐飲", "交通", "購物", "娛樂", "醫療", "教育", "住宿", "水電", "通訊", "其他"]
        self.income_categories = ["薪水", "零用錢", "獎金", "投資收益", "兼職", "紅包", "退款", "其他"]
        
        # 選中的日期
        self.selected_date_expense = date.today()
        self.selected_date_income = date.today()
        
        # 日曆視窗控制
        self.calendar_window = None
        
        # 創建UI
        self.create_ui()
        
    def create_ui(self):
        """創建主要UI介面"""
        # 標題列
        self.create_title()
        
        # 創建分頁系統
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # 添加分頁
        self.tab_expense = self.tabview.add("支出記帳")
        self.tab_income = self.tabview.add("收入記帳")
        self.tab_statistics = self.tabview.add("統計分析")
        
        # 創建支出記帳頁面
        self.create_expense_tab()
        
        # 創建收入記帳頁面
        self.create_income_tab()
        
        # 創建統計頁面
        self.create_statistics_tab()
        
    def create_title(self):
        """創建標題列"""
        title_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="💰 個人記帳工具",
            font=ctk.CTkFont(size=32, weight="bold")
        )
        title_label.pack()
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="輕鬆管理您的每一筆收支",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle_label.pack()
        
    def create_expense_tab(self):
        """創建支出記帳頁面"""
        # 輸入表單區域
        self.create_expense_form()
        
        # 記帳紀錄區域
        self.create_expense_records_display()
    
    def create_income_tab(self):
        """創建收入記帳頁面"""
        # 輸入表單區域
        self.create_income_form()
        
        # 記帳紀錄區域
        self.create_income_records_display()
        
    def create_expense_form(self):
        """創建支出輸入表單"""
        form_frame = ctk.CTkFrame(self.tab_expense)
        form_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # 標題
        form_title = ctk.CTkLabel(
            form_frame,
            text="新增支出",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        form_title.grid(row=0, column=0, columnspan=5, pady=(10, 15), sticky="w", padx=10)
        
        # 日期選擇
        date_label = ctk.CTkLabel(form_frame, text="日期:", font=ctk.CTkFont(size=14))
        date_label.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="e")
        
        # 使用按鈕樣式的日期選擇器
        self.expense_date_button = ctk.CTkButton(
            form_frame,
            text=date.today().strftime("%Y-%m-%d"),
            command=lambda: self.open_calendar('expense'),
            width=150,
            height=28,
            anchor="w"
        )
        self.expense_date_button.grid(row=1, column=1, padx=5, pady=10, sticky="w")
        
        # 項目
        item_label = ctk.CTkLabel(form_frame, text="項目:", font=ctk.CTkFont(size=14))
        item_label.grid(row=1, column=2, padx=(20, 5), pady=10, sticky="e")
        
        # 項目下拉選單（預設分類）
        self.expense_item_var = ctk.StringVar(value=self.expense_categories[0])
        self.expense_item_menu = ctk.CTkOptionMenu(
            form_frame,
            values=self.expense_categories,
            variable=self.expense_item_var,
            width=150
        )
        self.expense_item_menu.grid(row=1, column=3, padx=5, pady=10, sticky="w")
        
        # 金額
        amount_label = ctk.CTkLabel(form_frame, text="金額:", font=ctk.CTkFont(size=14))
        amount_label.grid(row=2, column=0, padx=(10, 5), pady=10, sticky="e")
        
        self.expense_amount_entry = ctk.CTkEntry(form_frame, placeholder_text="例：100", width=150)
        self.expense_amount_entry.grid(row=2, column=1, padx=5, pady=10, sticky="w")
        
        # 消費方式
        payment_label = ctk.CTkLabel(form_frame, text="消費方式:", font=ctk.CTkFont(size=14))
        payment_label.grid(row=2, column=2, padx=(20, 5), pady=10, sticky="e")
        
        self.expense_payment_var = ctk.StringVar(value=self.payment_methods[0])
        self.expense_payment_menu = ctk.CTkOptionMenu(
            form_frame,
            values=self.payment_methods,
            variable=self.expense_payment_var,
            width=150
        )
        self.expense_payment_menu.grid(row=2, column=3, padx=5, pady=10, sticky="w")
        
        # 備註
        note_label = ctk.CTkLabel(form_frame, text="備註:", font=ctk.CTkFont(size=14))
        note_label.grid(row=3, column=0, padx=(10, 5), pady=10, sticky="e")
        
        self.expense_note_entry = ctk.CTkEntry(form_frame, placeholder_text="選填", width=400)
        self.expense_note_entry.grid(row=3, column=1, columnspan=3, padx=5, pady=10, sticky="w")
        
        # 按鈕區域
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=4, column=0, columnspan=5, pady=15)
        
        add_button = ctk.CTkButton(
            button_frame,
            text="➕ 新增支出",
            command=self.add_expense_record,
            width=120,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        add_button.pack(side="left", padx=5)
        
        clear_button = ctk.CTkButton(
            button_frame,
            text="🔄 清空表單",
            command=self.clear_expense_form,
            width=120,
            height=35,
            fg_color="gray",
            hover_color="darkgray"
        )
        clear_button.pack(side="left", padx=5)
        
    def create_expense_records_display(self):
        """創建支出紀錄顯示區域"""
        records_frame = ctk.CTkFrame(self.tab_expense)
        records_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        # 標題和工具列
        header_frame = ctk.CTkFrame(records_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        records_title = ctk.CTkLabel(
            header_frame,
            text="支出紀錄",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        records_title.pack(side="left")
        
        delete_button = ctk.CTkButton(
            header_frame,
            text="🗑️ 刪除選中",
            command=lambda: self.delete_record('expense'),
            width=100,
            height=30,
            fg_color="red",
            hover_color="darkred"
        )
        delete_button.pack(side="right", padx=5)
        
        # 創建Treeview
        tree_frame = ctk.CTkFrame(records_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        # 創建滾動條
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        # 創建Treeview
        columns = ("日期", "項目", "金額", "消費方式", "備註")
        self.expense_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            height=15
        )
        scrollbar.config(command=self.expense_tree.yview)
        
        # 設置列標題
        self.expense_tree.heading("日期", text="日期")
        self.expense_tree.heading("項目", text="項目")
        self.expense_tree.heading("金額", text="金額 (NT$)")
        self.expense_tree.heading("消費方式", text="消費方式")
        self.expense_tree.heading("備註", text="備註")
        
        # 設置列寬
        self.expense_tree.column("日期", width=100, anchor="center")
        self.expense_tree.column("項目", width=150, anchor="w")
        self.expense_tree.column("金額", width=100, anchor="e")
        self.expense_tree.column("消費方式", width=100, anchor="center")
        self.expense_tree.column("備註", width=300, anchor="w")
        
        # 設置樣式
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                       background="white",
                       foreground="black",
                       rowheight=35,
                       fieldbackground="white",
                       font=("Microsoft JhengHei", 14))
        style.configure("Treeview.Heading",
                       font=("Microsoft JhengHei", 15, "bold"),
                       background="#3B8ED0",
                       foreground="white")
        style.map("Treeview", background=[("selected", "#3B8ED0")])
        
        # 綁定點擊事件以支援取消選取
        self.expense_tree.bind("<Button-1>", lambda e: self.on_tree_click(e, self.expense_tree))
        
        self.expense_tree.pack(fill="both", expand=True)
        
        # 載入現有記錄
        self.refresh_expense_records()
        
    def create_statistics_tab(self):
        """創建統計分析頁面"""
        # 控制面板
        control_frame = ctk.CTkFrame(self.tab_statistics)
        control_frame.pack(fill="x", padx=20, pady=20)
        
        # 標題
        stats_title = ctk.CTkLabel(
            control_frame,
            text="📊 支出統計分析",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        stats_title.pack(pady=(10, 15))
        
        # 日期篩選選項
        filter_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        filter_frame.pack(pady=10)
        
        filter_label = ctk.CTkLabel(
            filter_frame,
            text="統計範圍:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        filter_label.grid(row=0, column=0, padx=10, pady=5)
        
        # 快速選項
        self.filter_var = ctk.StringVar(value="當月")
        quick_filters = ["當日", "當月", "當年", "自訂"]
        
        for i, filter_option in enumerate(quick_filters):
            radio = ctk.CTkRadioButton(
                filter_frame,
                text=filter_option,
                variable=self.filter_var,
                value=filter_option,
                command=self.on_filter_change,
                font=ctk.CTkFont(size=13)
            )
            radio.grid(row=0, column=i+1, padx=10, pady=5)
        
        # 自訂日期範圍
        custom_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        custom_frame.pack(pady=10)
        
        start_label = ctk.CTkLabel(custom_frame, text="開始日期:", font=ctk.CTkFont(size=13))
        start_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.start_date_entry = ctk.CTkEntry(custom_frame, placeholder_text="YYYY-MM-DD", width=120)
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        end_label = ctk.CTkLabel(custom_frame, text="結束日期:", font=ctk.CTkFont(size=13))
        end_label.grid(row=0, column=2, padx=(20, 5), pady=5)
        
        self.end_date_entry = ctk.CTkEntry(custom_frame, placeholder_text="YYYY-MM-DD", width=120)
        self.end_date_entry.grid(row=0, column=3, padx=5, pady=5)
        
        update_button = ctk.CTkButton(
            custom_frame,
            text="🔍 更新統計",
            command=self.update_statistics,
            width=100,
            height=30
        )
        update_button.grid(row=0, column=4, padx=10, pady=5)
        
        # 圖表顯示區域
        self.chart_frame = ctk.CTkFrame(self.tab_statistics)
        self.chart_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # 初始化統計
        self.update_statistics()
        
    def on_filter_change(self):
        """當篩選選項改變時"""
        if self.filter_var.get() != "自訂":
            self.update_statistics()
    
    def on_tree_click(self, event, tree):
        """處理表格點擊事件，支援取消選取"""
        region = tree.identify("region", event.x, event.y)
        if region == "cell":
            item = tree.identify_row(event.y)
            if item in tree.selection():
                tree.selection_remove(item)
                return "break"
    
    def open_calendar(self, calendar_type):
        """打開日曆選擇對話框"""
        # 如果已有日曆視窗打開，將其置於最前
        if self.calendar_window is not None and self.calendar_window.winfo_exists():
            self.calendar_window.lift()
            self.calendar_window.focus_force()
            return
        
        # 創建頂層窗口
        self.calendar_window = Toplevel(self.root)
        self.calendar_window.title("選擇日期")
        self.calendar_window.geometry("600x600")
        self.calendar_window.resizable(False, False)
        
        # 使窗口居中
        self.calendar_window.update_idletasks()
        x = (self.calendar_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.calendar_window.winfo_screenheight() // 2) - (600 // 2)
        self.calendar_window.geometry(f"600x600+{x}+{y}")
        
        # 獲取對應的日期
        if calendar_type == 'expense':
            current_date = self.selected_date_expense
        else:
            current_date = self.selected_date_income
        
        # 創建日曆
        cal = Calendar(
            self.calendar_window,
            selectmode='day',
            year=current_date.year,
            month=current_date.month,
            day=current_date.day,
            date_pattern='yyyy-mm-dd',
            font=('Microsoft JhengHei', 18),
            showweeknumbers=False
        )
        cal.pack(padx=20, pady=20, fill="both", expand=True)
        
        def select_date():
            selected = cal.selection_get()
            if calendar_type == 'expense':
                self.selected_date_expense = selected
                self.expense_date_button.configure(text=selected.strftime("%Y-%m-%d"))
            else:
                self.selected_date_income = selected
                self.income_date_button.configure(text=selected.strftime("%Y-%m-%d"))
            self.calendar_window.destroy()
            self.calendar_window = None
        
        def on_close():
            self.calendar_window.destroy()
            self.calendar_window = None
        
        # 確認按鈕
        confirm_btn = ctk.CTkButton(
            self.calendar_window,
            text="確認",
            command=select_date,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        confirm_btn.pack(pady=20)
        
        # 綁定關閉事件
        self.calendar_window.protocol("WM_DELETE_WINDOW", on_close)
    
    def add_expense_record(self):
        """新增支出記錄"""
        try:
            # 獲取輸入值
            date_str = self.selected_date_expense.strftime("%Y-%m-%d")
            item = self.expense_item_var.get().strip()
            amount_str = self.expense_amount_entry.get().strip()
            payment = self.expense_payment_var.get()
            note = self.expense_note_entry.get().strip()
            
            # 驗證輸入
            if not date_str or not item or not amount_str:
                messagebox.showwarning("輸入錯誤", "請填寫日期、項目和金額！")
                return
            
            # 驗證日期格式
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("日期錯誤", "日期格式錯誤！請使用 YYYY-MM-DD 格式")
                return
            
            # 驗證金額
            try:
                amount = float(amount_str)
                if amount <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("金額錯誤", "請輸入有效的金額（正數）！")
                return
            
            # 創建記錄
            record = {
                "id": len(self.records) + 1,
                "type": "expense",
                "date": date_str,
                "item": item,
                "amount": amount,
                "payment": payment,
                "note": note,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 添加到記錄列表
            self.records.append(record)
            
            # 保存數據
            self.save_data()
            
            # 刷新顯示
            self.refresh_expense_records()
            
            # 清空表單
            self.clear_expense_form()
            
            messagebox.showinfo("成功", "支出記錄已新增！")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"新增記錄時發生錯誤：{str(e)}")
    
    def delete_record(self, record_type):
        """刪除選中的記錄"""
        if record_type == 'expense':
            tree = self.expense_tree
        else:
            tree = self.income_tree
        
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("未選擇", "請先選擇要刪除的記錄！")
            return
        
        if messagebox.askyesno("確認刪除", "確定要刪除選中的記錄嗎？"):
            for item in selected:
                values = tree.item(item)["values"]
                # 根據日期、項目、金額和類型找到記錄
                self.records = [r for r in self.records 
                              if not (r.get("type", "expense") == record_type and
                                     r["date"] == values[0] and 
                                     r["item"] == values[1] and 
                                     r["amount"] == float(values[2]))]
            
            self.save_data()
            if record_type == 'expense':
                self.refresh_expense_records()
            else:
                self.refresh_income_records()
            messagebox.showinfo("成功", "記錄已刪除！")
    
    def clear_expense_form(self):
        """清空支出表單"""
        self.selected_date_expense = date.today()
        self.expense_date_button.configure(text=date.today().strftime("%Y-%m-%d"))
        self.expense_item_var.set(self.expense_categories[0])
        self.expense_amount_entry.delete(0, "end")
        self.expense_payment_var.set(self.payment_methods[0])
        self.expense_note_entry.delete(0, "end")
    
    def refresh_expense_records(self):
        """刷新支出記錄顯示"""
        # 清空現有顯示
        for item in self.expense_tree.get_children():
            self.expense_tree.delete(item)
        
        # 篩選支出記錄並按日期排序（最新的在前）
        expense_records = [r for r in self.records if r.get("type", "expense") == "expense"]
        sorted_records = sorted(expense_records, key=lambda x: x["date"], reverse=True)
        
        # 添加記錄
        for record in sorted_records:
            self.expense_tree.insert("", "end", values=(
                record["date"],
                record["item"],
                f"{record['amount']:.2f}",
                record["payment"],
                record["note"]
            ))
    
    def create_income_form(self):
        """創建收入輸入表單"""
        form_frame = ctk.CTkFrame(self.tab_income)
        form_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # 標題
        form_title = ctk.CTkLabel(
            form_frame,
            text="新增收入",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        form_title.grid(row=0, column=0, columnspan=5, pady=(10, 15), sticky="w", padx=10)
        
        # 日期選擇
        date_label = ctk.CTkLabel(form_frame, text="日期:", font=ctk.CTkFont(size=14))
        date_label.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="e")
        
        # 使用按鈕樣式的日期選擇器
        self.income_date_button = ctk.CTkButton(
            form_frame,
            text=date.today().strftime("%Y-%m-%d"),
            command=lambda: self.open_calendar('income'),
            width=150,
            height=28,
            anchor="w"
        )
        self.income_date_button.grid(row=1, column=1, padx=5, pady=10, sticky="w")
        
        # 項目
        item_label = ctk.CTkLabel(form_frame, text="項目:", font=ctk.CTkFont(size=14))
        item_label.grid(row=1, column=2, padx=(20, 5), pady=10, sticky="e")
        
        # 項目下拉選單（預設分類）
        self.income_item_var = ctk.StringVar(value=self.income_categories[0])
        self.income_item_menu = ctk.CTkOptionMenu(
            form_frame,
            values=self.income_categories,
            variable=self.income_item_var,
            width=150
        )
        self.income_item_menu.grid(row=1, column=3, padx=5, pady=10, sticky="w")
        
        # 金額
        amount_label = ctk.CTkLabel(form_frame, text="金額:", font=ctk.CTkFont(size=14))
        amount_label.grid(row=2, column=0, padx=(10, 5), pady=10, sticky="e")
        
        self.income_amount_entry = ctk.CTkEntry(form_frame, placeholder_text="例：5000", width=150)
        self.income_amount_entry.grid(row=2, column=1, padx=5, pady=10, sticky="w")
        
        # 收入方式
        payment_label = ctk.CTkLabel(form_frame, text="收入方式:", font=ctk.CTkFont(size=14))
        payment_label.grid(row=2, column=2, padx=(20, 5), pady=10, sticky="e")
        
        self.income_payment_var = ctk.StringVar(value=self.payment_methods[0])
        self.income_payment_menu = ctk.CTkOptionMenu(
            form_frame,
            values=self.payment_methods,
            variable=self.income_payment_var,
            width=150
        )
        self.income_payment_menu.grid(row=2, column=3, padx=5, pady=10, sticky="w")
        
        # 備註
        note_label = ctk.CTkLabel(form_frame, text="備註:", font=ctk.CTkFont(size=14))
        note_label.grid(row=3, column=0, padx=(10, 5), pady=10, sticky="e")
        
        self.income_note_entry = ctk.CTkEntry(form_frame, placeholder_text="選填", width=400)
        self.income_note_entry.grid(row=3, column=1, columnspan=3, padx=5, pady=10, sticky="w")
        
        # 按鈕區域
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=4, column=0, columnspan=5, pady=15)
        
        add_button = ctk.CTkButton(
            button_frame,
            text="➕ 新增收入",
            command=self.add_income_record,
            width=120,
            height=35,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        add_button.pack(side="left", padx=5)
        
        clear_button = ctk.CTkButton(
            button_frame,
            text="🔄 清空表單",
            command=self.clear_income_form,
            width=120,
            height=35,
            fg_color="gray",
            hover_color="darkgray"
        )
        clear_button.pack(side="left", padx=5)
    
    def create_income_records_display(self):
        """創建收入紀錄顯示區域"""
        records_frame = ctk.CTkFrame(self.tab_income)
        records_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        # 標題和工具列
        header_frame = ctk.CTkFrame(records_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        records_title = ctk.CTkLabel(
            header_frame,
            text="收入紀錄",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        records_title.pack(side="left")
        
        delete_button = ctk.CTkButton(
            header_frame,
            text="🗑️ 刪除選中",
            command=lambda: self.delete_record('income'),
            width=100,
            height=30,
            fg_color="red",
            hover_color="darkred"
        )
        delete_button.pack(side="right", padx=5)
        
        # 創建Treeview
        tree_frame = ctk.CTkFrame(records_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        # 創建滾動條
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side="right", fill="y")
        
        # 創建Treeview
        columns = ("日期", "項目", "金額", "收入方式", "備註")
        self.income_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            height=15
        )
        scrollbar.config(command=self.income_tree.yview)
        
        # 設置列標題
        self.income_tree.heading("日期", text="日期")
        self.income_tree.heading("項目", text="項目")
        self.income_tree.heading("金額", text="金額 (NT$)")
        self.income_tree.heading("收入方式", text="收入方式")
        self.income_tree.heading("備註", text="備註")
        
        # 設置列寬
        self.income_tree.column("日期", width=100, anchor="center")
        self.income_tree.column("項目", width=150, anchor="w")
        self.income_tree.column("金額", width=100, anchor="e")
        self.income_tree.column("收入方式", width=100, anchor="center")
        self.income_tree.column("備註", width=300, anchor="w")
        
        # 綁定點擊事件以支援取消選取
        self.income_tree.bind("<Button-1>", lambda e: self.on_tree_click(e, self.income_tree))
        
        self.income_tree.pack(fill="both", expand=True)
        
        # 載入現有記錄
        self.refresh_income_records()
    
    def add_income_record(self):
        """新增收入記錄"""
        try:
            # 獲取輸入值
            date_str = self.selected_date_income.strftime("%Y-%m-%d")
            item = self.income_item_var.get().strip()
            amount_str = self.income_amount_entry.get().strip()
            payment = self.income_payment_var.get()
            note = self.income_note_entry.get().strip()
            
            # 驗證輸入
            if not date_str or not item or not amount_str:
                messagebox.showwarning("輸入錯誤", "請填寫日期、項目和金額！")
                return
            
            # 驗證日期格式
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("日期錯誤", "日期格式錯誤！請使用 YYYY-MM-DD 格式")
                return
            
            # 驗證金額
            try:
                amount = float(amount_str)
                if amount <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("金額錯誤", "請輸入有效的金額（正數）！")
                return
            
            # 創建記錄
            record = {
                "id": len(self.records) + 1,
                "type": "income",
                "date": date_str,
                "item": item,
                "amount": amount,
                "payment": payment,
                "note": note,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 添加到記錄列表
            self.records.append(record)
            
            # 保存數據
            self.save_data()
            
            # 刷新顯示
            self.refresh_income_records()
            
            # 清空表單
            self.clear_income_form()
            
            messagebox.showinfo("成功", "收入記錄已新增！")
            
        except Exception as e:
            messagebox.showerror("錯誤", f"新增記錄時發生錯誤：{str(e)}")
    
    def clear_income_form(self):
        """清空收入表單"""
        self.selected_date_income = date.today()
        self.income_date_button.configure(text=date.today().strftime("%Y-%m-%d"))
        self.income_item_var.set(self.income_categories[0])
        self.income_amount_entry.delete(0, "end")
        self.income_payment_var.set(self.payment_methods[0])
        self.income_note_entry.delete(0, "end")
    
    def refresh_income_records(self):
        """刷新收入記錄顯示"""
        # 清空現有顯示
        for item in self.income_tree.get_children():
            self.income_tree.delete(item)
        
        # 篩選收入記錄並按日期排序（最新的在前）
        income_records = [r for r in self.records if r.get("type") == "income"]
        sorted_records = sorted(income_records, key=lambda x: x["date"], reverse=True)
        
        # 添加記錄
        for record in sorted_records:
            self.income_tree.insert("", "end", values=(
                record["date"],
                record["item"],
                f"{record['amount']:.2f}",
                record["payment"],
                record["note"]
            ))
    
    def update_statistics(self):
        """更新統計圖表"""
        # 清空現有圖表
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        # 獲取篩選範圍
        filter_type = self.filter_var.get()
        today = date.today()
        
        if filter_type == "當日":
            start_date = end_date = today
        elif filter_type == "當月":
            start_date = date(today.year, today.month, 1)
            # 下個月的第一天減一天 = 本月最後一天
            if today.month == 12:
                end_date = date(today.year, 12, 31)
            else:
                next_month = date(today.year, today.month + 1, 1)
                end_date = date(next_month.year, next_month.month, next_month.day - 1) if next_month.day > 1 else today
            end_date = today  # 簡化為今天
        elif filter_type == "當年":
            start_date = date(today.year, 1, 1)
            end_date = today
        else:  # 自訂
            try:
                start_date = datetime.strptime(self.start_date_entry.get().strip(), "%Y-%m-%d").date()
                end_date = datetime.strptime(self.end_date_entry.get().strip(), "%Y-%m-%d").date()
            except:
                messagebox.showerror("日期錯誤", "請輸入有效的日期範圍（YYYY-MM-DD）！")
                return
        
        # 篩選記錄
        filtered_records = [
            r for r in self.records
            if start_date <= datetime.strptime(r["date"], "%Y-%m-%d").date() <= end_date
        ]
        
        if not filtered_records:
            no_data_label = ctk.CTkLabel(
                self.chart_frame,
                text="📊 此期間沒有記帳記錄",
                font=ctk.CTkFont(size=18),
                text_color="gray"
            )
            no_data_label.pack(expand=True)
            return
        
        # 分別統計支出和收入
        expense_records = [r for r in filtered_records if r.get("type", "expense") == "expense"]
        income_records = [r for r in filtered_records if r.get("type") == "income"]
        
        # 統計支出各項目的金額
        expense_totals = defaultdict(float)
        for record in expense_records:
            expense_totals[record["item"]] += record["amount"]
        
        # 統計收入各項目的金額
        income_totals = defaultdict(float)
        for record in income_records:
            income_totals[record["item"]] += record["amount"]
        
        # 計算總金額
        total_expense = sum(expense_totals.values())
        total_income = sum(income_totals.values())
        
        # 創建圖表（支出和收入並排顯示）
        fig = Figure(figsize=(14, 7), dpi=100)
        
        period_str = f"{start_date} 至 {end_date}"
        
        # 如果有支出記錄
        if expense_totals:
            ax1 = fig.add_subplot(121)
            
            # 準備數據
            items = list(expense_totals.keys())
            amounts = list(expense_totals.values())
            
            # 繪製圓餅圖
            colors = plt.cm.Set3(range(len(items)))
            wedges, texts, autotexts = ax1.pie(
                amounts,
                labels=items,
                autopct=lambda pct: f'{pct:.1f}%\nNT${pct*total_expense/100:.0f}',
                colors=colors,
                startangle=90
            )
            
            # 設置文字樣式
            for text in texts:
                text.set_fontsize(13)
                text.set_fontfamily('Microsoft JhengHei')
                text.set_color('black')
                text.set_fontweight('bold')
            for autotext in autotexts:
                autotext.set_color('black')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(11)
                autotext.set_fontfamily('Microsoft JhengHei')
            
            # 設置標題
            ax1.set_title(f'支出統計\n總計: NT${total_expense:,.2f}',
                        fontsize=16, fontweight='bold', fontfamily='Microsoft JhengHei', pad=20)
            ax1.axis('equal')
        
        # 如果有收入記錄
        if income_totals:
            ax2 = fig.add_subplot(122) if expense_totals else fig.add_subplot(111)
            
            # 準備數據
            items = list(income_totals.keys())
            amounts = list(income_totals.values())
            
            # 繪製圓餅圖
            colors = plt.cm.Pastel1(range(len(items)))
            wedges, texts, autotexts = ax2.pie(
                amounts,
                labels=items,
                autopct=lambda pct: f'{pct:.1f}%\nNT${pct*total_income/100:.0f}',
                colors=colors,
                startangle=90
            )
            
            # 設置文字樣式
            for text in texts:
                text.set_fontsize(13)
                text.set_fontfamily('Microsoft JhengHei')
                text.set_color('black')
                text.set_fontweight('bold')
            for autotext in autotexts:
                autotext.set_color('black')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(11)
                autotext.set_fontfamily('Microsoft JhengHei')
            
            # 設置標題
            ax2.set_title(f'收入統計\n總計: NT${total_income:,.2f}',
                        fontsize=16, fontweight='bold', fontfamily='Microsoft JhengHei', pad=20)
            ax2.axis('equal')
        
        # 添加總標題
        net_amount = total_income - total_expense
        net_text = f"淨收入: NT${net_amount:,.2f}" if net_amount >= 0 else f"淨支出: NT${-net_amount:,.2f}"
        fig.suptitle(f'{period_str}\n{net_text}',
                    fontsize=18, fontweight='bold', fontfamily='Microsoft JhengHei')
        
        # 嵌入到tkinter
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
    def load_data(self):
        """從文件載入數據"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_data(self):
        """保存數據到文件"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("保存錯誤", f"保存數據時發生錯誤：{str(e)}")
    
    def run(self):
        """運行應用程式"""
        self.root.mainloop()


def main():
    """主程式入口"""
    app = AccountingApp()
    app.run()


if __name__ == "__main__":
    main()
