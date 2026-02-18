"""
記帳工具 - Streamlit 網頁版
適合部署在 Streamlit Cloud 供個人使用
"""

VERSION = "1.1"

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
import matplotlib.pyplot as plt
from collections import defaultdict
import matplotlib
import matplotlib.font_manager as fm
from supabase import create_client, Client

# 配置 matplotlib 中文字體支援（兼容 Streamlit Cloud）
def setup_chinese_font():
    """設置 matplotlib 中文字體"""
    try:
        import matplotlib.font_manager as fm
        # 獲取系統可用字體
        available_fonts = set(f.name for f in fm.fontManager.ttflist)
        
        # 按優先順序嘗試中文字體
        chinese_fonts = ['Microsoft JhengHei', 'Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 
                        'Noto Sans CJK JP', 'Noto Sans CJK SC', 'WenQuanYi Micro Hei']
        
        selected_font = None
        for font in chinese_fonts:
            if font in available_fonts:
                selected_font = font
                break
        
        if selected_font:
            matplotlib.rcParams['font.sans-serif'] = [selected_font, 'DejaVu Sans', 'sans-serif']
        else:
            # 使用默認字體
            matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans', 'sans-serif']
        
        matplotlib.rcParams['axes.unicode_minus'] = False
    except Exception as e:
        # 如果設置失敗，使用默認配置
        matplotlib.rcParams['font.sans-serif'] = ['sans-serif']
        matplotlib.rcParams['axes.unicode_minus'] = False

# 初始化字體
setup_chinese_font()

# 頁面配置
st.set_page_config(
    page_title=f"💰 個人記帳工具 v{VERSION}",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 數據文件路徑
DATA_FILE = "accounting_data.json"

# 預設分類
EXPENSE_CATEGORIES = ["餐飲", "交通", "購物", "娛樂", "醫療", "教育", "住宿", "水電", "通訊", "其他"]
INCOME_CATEGORIES = ["薪水", "零用錢", "獎金", "投資收益", "兼職", "紅包", "退款", "其他"]
PAYMENT_METHODS = ["現金", "信用卡", "行動支付", "轉帳", "其他"]

# 密碼設定（請修改為您的密碼）
PASSWORD = "1234"  # 建議部署後改為更安全的密碼


def get_supabase_client():
    """獲取 Supabase 客戶端"""
    try:
        if "supabase_url" in st.secrets and "supabase_key" in st.secrets:
            url = st.secrets["supabase_url"]
            key = st.secrets["supabase_key"]
            return create_client(url, key)
        return None
    except Exception as e:
        st.error(f"Supabase 連接失敗：{str(e)}")
        return None


def load_data_from_supabase(client):
    """從 Supabase 載入數據"""
    try:
        response = client.table('accounting_records').select('*').order('created_at', desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"從 Supabase 讀取失敗：{str(e)}")
        return []


def save_record_to_supabase(client, record):
    """保存記錄到 Supabase"""
    try:
        # 移除 id，讓 Supabase 自動生成
        record_to_save = {k: v for k, v in record.items() if k != 'id'}
        response = client.table('accounting_records').insert(record_to_save).execute()
        return True
    except Exception as e:
        st.error(f"保存到 Supabase 失敗：{str(e)}")
        return False


def delete_records_from_supabase(client, record_ids):
    """從 Supabase 刪除記錄"""
    try:
        for record_id in record_ids:
            client.table('accounting_records').delete().eq('id', record_id).execute()
        return True
    except Exception as e:
        st.error(f"從 Supabase 刪除失敗：{str(e)}")
        return False


def check_password():
    """簡單的密碼驗證"""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    
    if not st.session_state.password_correct:
        st.markdown("### 🔐 請輸入密碼")
        password = st.text_input("密碼", type="password", key="password_input")
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            if st.button("登入", use_container_width=True):
                if password == PASSWORD:
                    st.session_state.password_correct = True
                    st.rerun()
                else:
                    st.error("❌ 密碼錯誤")
        with col2:
            st.info("💡 預設密碼: 1234")
        return False
    return True


def load_data():
    """載入數據（從 Supabase 或 JSON）"""
    # 檢查是否使用 Supabase
    if st.session_state.get("use_supabase", False):
        client = get_supabase_client()
        if client:
            return load_data_from_supabase(client)
    
    # 否則使用本地 JSON
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []


def save_data(records):
    """保存數據（到 Supabase 或 JSON）"""
    # 如果使用 Supabase，不需要這個函數（直接insert到supabase）
    if st.session_state.get("use_supabase", False):
        return True
    
    # 否則保存到本地 JSON
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"保存失敗：{str(e)}")
        return False


def add_record(record_type, date_val, item, amount, payment, note):
    """新增記錄"""
    record = {
        "type": record_type,
        "date": date_val.strftime("%Y-%m-%d"),
        "item": item,
        "amount": int(amount),
        "payment": payment,
        "note": note,
        "created_at": datetime.now().isoformat()
    }
    
    # 使用 Supabase
    if st.session_state.get("use_supabase", False):
        client = get_supabase_client()
        if client and save_record_to_supabase(client, record):
            st.success(f"✅ {'支出' if record_type == 'expense' else '收入'}記錄已新增到 Supabase！")
            st.balloons()
            return True
        return False
    
    # 使用本地 JSON
    records = load_data()
    record["id"] = len(records) + 1
    records.append(record)
    if save_data(records):
        st.success(f"✅ {'支出' if record_type == 'expense' else '收入'}記錄已新增！")
        st.balloons()
        return True
    return False


def delete_records(indices_to_delete):
    """刪除記錄"""
    # 使用 Supabase
    if st.session_state.get("use_supabase", False):
        client = get_supabase_client()
        if client:
            records = load_data()
            record_ids = [records[i]['id'] for i in indices_to_delete if i < len(records)]
            if delete_records_from_supabase(client, record_ids):
                st.success(f"✅ 已從 Supabase 刪除 {len(indices_to_delete)} 筆記錄")
                return True
        return False
    
    # 使用本地 JSON
    records = load_data()
    records = [r for i, r in enumerate(records) if i not in indices_to_delete]
    if save_data(records):
        st.success(f"✅ 已刪除 {len(indices_to_delete)} 筆記錄")
        return True
    return False


def get_filtered_records(record_type, start_date=None, end_date=None):
    """獲取篩選後的記錄"""
    records = load_data()
    filtered = [r for r in records if r.get("type", "expense") == record_type]
    
    if start_date and end_date:
        filtered = [
            r for r in filtered
            if start_date <= datetime.strptime(r["date"], "%Y-%m-%d").date() <= end_date
        ]
    
    return filtered


def expense_page():
    """支出記帳頁面"""
    st.header("💸 支出記帳")
    
    # 輸入表單
    with st.form("expense_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date_val = st.date_input("日期", value=date.today(), key="expense_date")
            item = st.selectbox("項目", EXPENSE_CATEGORIES, key="expense_item")
        
        with col2:
            amount = st.number_input("金額 (NT$)", min_value=0, step=1, key="expense_amount")
            payment = st.selectbox("消費方式", PAYMENT_METHODS, key="expense_payment")
        
        with col3:
            note = st.text_input("備註（選填）", key="expense_note")
            st.write("")  # 空行對齊
            submit = st.form_submit_button("➕ 新增支出", use_container_width=True, type="primary")
        
        if submit:
            if amount <= 0:
                st.error("❌ 請輸入有效的金額")
            else:
                add_record("expense", date_val, item, amount, payment, note)
                st.rerun()
    
    st.divider()
    
    # 顯示記錄
    st.subheader("📋 支出紀錄")
    
    records = get_filtered_records("expense")
    
    if records:
        # 轉換為 DataFrame
        df = pd.DataFrame(records)
        df = df[["date", "item", "amount", "payment", "note"]]
        df.columns = ["日期", "項目", "金額", "消費方式", "備註"]
        df = df.sort_values("日期", ascending=False).reset_index(drop=True)
        
        # 顯示統計
        col1, col2 = st.columns(2)
        with col1:
            st.metric("總支出", f"NT$ {int(df['金額'].sum()):,}")
        with col2:
            st.metric("記錄筆數", len(df))
        
        st.dataframe(
            df,
            use_container_width=True,
            height=400,
            hide_index=False
        )
        
        # 刪除功能
        with st.expander("🗑️ 刪除記錄"):
            st.warning("⚠️ 刪除操作無法復原，請謹慎操作")
            delete_indices = st.multiselect(
                "選擇要刪除的記錄（可多選）",
                options=range(len(records)),
                format_func=lambda i: f"{records[i]['date']} - {records[i]['item']} - NT${int(records[i]['amount']):,}"
            )
            if st.button("確認刪除", type="secondary"):
                if delete_indices:
                    if delete_records(delete_indices):
                        st.rerun()
    else:
        st.info("📝 尚無支出記錄，請開始記帳吧！")


def income_page():
    """收入記帳頁面"""
    st.header("💰 收入記帳")
    
    # 輸入表單
    with st.form("income_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            date_val = st.date_input("日期", value=date.today(), key="income_date")
            item = st.selectbox("項目", INCOME_CATEGORIES, key="income_item")
        
        with col2:
            amount = st.number_input("金額 (NT$)", min_value=0, step=1, key="income_amount")
            payment = st.selectbox("收入方式", PAYMENT_METHODS, key="income_payment")
        
        with col3:
            note = st.text_input("備註（選填）", key="income_note")
            st.write("")  # 空行對齊
            submit = st.form_submit_button("➕ 新增收入", use_container_width=True, type="primary")
        
        if submit:
            if amount <= 0:
                st.error("❌ 請輸入有效的金額")
            else:
                add_record("income", date_val, item, amount, payment, note)
                st.rerun()
    
    st.divider()
    
    # 顯示記錄
    st.subheader("📋 收入紀錄")
    
    records = get_filtered_records("income")
    
    if records:
        # 轉換為 DataFrame
        df = pd.DataFrame(records)
        df = df[["date", "item", "amount", "payment", "note"]]
        df.columns = ["日期", "項目", "金額", "收入方式", "備註"]
        df = df.sort_values("日期", ascending=False).reset_index(drop=True)
        
        # 顯示統計
        col1, col2 = st.columns(2)
        with col1:
            st.metric("總收入", f"NT$ {int(df['金額'].sum()):,}")
        with col2:
            st.metric("記錄筆數", len(df))
        
        st.dataframe(
            df,
            use_container_width=True,
            height=400,
            hide_index=False
        )
        
        # 刪除功能
        with st.expander("🗑️ 刪除記錄"):
            st.warning("⚠️ 刪除操作無法復原，請謹慎操作")
            delete_indices = st.multiselect(
                "選擇要刪除的記錄（可多選）",
                options=range(len(records)),
                format_func=lambda i: f"{records[i]['date']} - {records[i]['item']} - NT${int(records[i]['amount']):,}"
            )
            if st.button("確認刪除", type="secondary"):
                if delete_indices:
                    if delete_records(delete_indices):
                        st.rerun()
    else:
        st.info("📝 尚無收入記錄，請開始記帳吧！")


def statistics_page():
    """統計分析頁面"""
    st.header("📊 統計分析")
    
    # 日期範圍選擇
    col1, col2, col3 = st.columns([2, 2, 3])
    
    with col1:
        filter_type = st.selectbox(
            "統計範圍",
            ["當日", "當月", "當年", "自訂"],
            key="filter_type"
        )
    
    today = date.today()
    
    if filter_type == "當日":
        start_date = end_date = today
    elif filter_type == "當月":
        start_date = date(today.year, today.month, 1)
        end_date = today
    elif filter_type == "當年":
        start_date = date(today.year, 1, 1)
        end_date = today
    else:  # 自訂
        with col2:
            start_date = st.date_input("開始日期", value=today.replace(day=1))
        with col3:
            end_date = st.date_input("結束日期", value=today)
    
    st.divider()
    
    # 獲取篩選後的記錄
    expense_records = get_filtered_records("expense", start_date, end_date)
    income_records = get_filtered_records("income", start_date, end_date)
    
    # 計算統計
    total_expense = sum(r["amount"] for r in expense_records)
    total_income = sum(r["amount"] for r in income_records)
    net_amount = total_income - total_expense
    
    # 顯示總覽
    st.subheader(f"📅 {start_date} 至 {end_date}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("總支出", f"NT$ {int(total_expense):,}", delta=None)
    with col2:
        st.metric("總收入", f"NT$ {int(total_income):,}", delta=None)
    with col3:
        delta_color = "normal" if net_amount >= 0 else "inverse"
        st.metric(
            "淨收支",
            f"NT$ {int(net_amount):,}",
            delta=f"{'盈餘' if net_amount >= 0 else '赤字'}"
        )
    
    st.divider()
    
    # 圓餅圖
    if expense_records or income_records:
        col1, col2 = st.columns(2)
        
        # 支出圓餅圖
        with col1:
            if expense_records:
                st.subheader("💸 支出統計")
                expense_totals = defaultdict(float)
                for r in expense_records:
                    expense_totals[r["item"]] += r["amount"]
                
                fig1, ax1 = plt.subplots(figsize=(8, 8))
                items = list(expense_totals.keys())
                amounts = list(expense_totals.values())
                colors = plt.cm.Set3(range(len(items)))
                
                # 設置字體屬性
                font_prop = {'family': matplotlib.rcParams['font.sans-serif'][0], 
                            'size': 12, 'weight': 'bold'}
                
                wedges, texts, autotexts = ax1.pie(
                    amounts,
                    labels=items,
                    autopct=lambda pct: f'{pct:.1f}%\nNT${pct*total_expense/100:.0f}',
                    colors=colors,
                    startangle=90,
                    textprops=font_prop
                )
                
                # 設置標題字體
                ax1.set_title(f'支出總計: NT${int(total_expense):,}', 
                            fontsize=16, weight='bold', pad=20,
                            fontfamily=matplotlib.rcParams['font.sans-serif'][0])
                st.pyplot(fig1)
                plt.close()
            else:
                st.info("此期間無支出記錄")
        
        # 收入圓餅圖
        with col2:
            if income_records:
                st.subheader("💰 收入統計")
                income_totals = defaultdict(float)
                for r in income_records:
                    income_totals[r["item"]] += r["amount"]
                
                fig2, ax2 = plt.subplots(figsize=(8, 8))
                items = list(income_totals.keys())
                amounts = list(income_totals.values())
                colors = plt.cm.Pastel1(range(len(items)))
                
                # 設置字體屬性
                font_prop = {'family': matplotlib.rcParams['font.sans-serif'][0], 
                            'size': 12, 'weight': 'bold'}
                
                wedges, texts, autotexts = ax2.pie(
                    amounts,
                    labels=items,
                    autopct=lambda pct: f'{pct:.1f}%\nNT${pct*total_income/100:.0f}',
                    colors=colors,
                    startangle=90,
                    textprops=font_prop
                )
                
                # 設置標題字體
                ax2.set_title(f'收入總計: NT${int(total_income):,}', 
                            fontsize=16, weight='bold', pad=20,
                            fontfamily=matplotlib.rcParams['font.sans-serif'][0])
                st.pyplot(fig2)
                plt.close()
            else:
                st.info("此期間無收入記錄")
        
        # 詳細列表
        st.divider()
        st.subheader("📝 明細列表")
        
        tab1, tab2 = st.tabs(["支出明細", "收入明細"])
        
        with tab1:
            if expense_records:
                df_expense = pd.DataFrame(expense_records)
                df_expense = df_expense[["date", "item", "amount", "payment", "note"]]
                df_expense.columns = ["日期", "項目", "金額", "消費方式", "備註"]
                df_expense = df_expense.sort_values("日期", ascending=False)
                st.dataframe(df_expense, use_container_width=True, hide_index=True)
            else:
                st.info("此期間無支出記錄")
        
        with tab2:
            if income_records:
                df_income = pd.DataFrame(income_records)
                df_income = df_income[["date", "item", "amount", "payment", "note"]]
                df_income.columns = ["日期", "項目", "金額", "收入方式", "備註"]
                df_income = df_income.sort_values("日期", ascending=False)
                st.dataframe(df_income, use_container_width=True, hide_index=True)
            else:
                st.info("此期間無收入記錄")
    else:
        st.info("📊 此期間沒有記帳記錄")


def settings_page():
    """設定頁面"""
    st.header("⚙️ 系統設定")
    
    st.subheader("📊 Supabase 雲端資料庫")
    
    # 檢查是否已配置憑證
    has_credentials = "supabase_url" in st.secrets and "supabase_key" in st.secrets
    
    if has_credentials:
        st.success("✅ Supabase 憑證已配置")
        
        # 顯示當前狀態
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "連接狀態",
                "已連接" if st.session_state.get("use_supabase", False) else "未連接"
            )
        with col2:
            if st.session_state.get("use_supabase", False):
                st.metric("資料來源", "Supabase")
            else:
                st.metric("資料來源", "本地 JSON")
        
        st.divider()
        
        # Supabase 連接管理
        st.markdown("### 🔗 連接管理")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔗 啟用 Supabase", use_container_width=True, type="primary"):
                with st.spinner("正在測試連接..."):
                    try:
                        client = get_supabase_client()
                        # 測試連接
                        response = client.table('accounting_records').select('count').execute()
                        st.session_state.use_supabase = True
                        st.success(f"✅ 成功連接到 Supabase！")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ 連接失敗: {str(e)}")
        
        with col2:
            if st.button("🔌 停用 Supabase", use_container_width=True):
                st.session_state.use_supabase = False
                st.success("✅ 已停用 Supabase，切換回本地模式")
                st.rerun()
        
        # 顯示教學
        with st.expander("📖 如何設定 Supabase？"):
            st.markdown("""
            ### 步驟 1：創建 Supabase 專案
            1. 前往 [Supabase](https://supabase.com)
            2. 使用 GitHub 帳號免費註冊（無需信用卡）
            3. 點擊 "New Project" 創建新專案
            4. 設定專案名稱、資料庫密碼、選擇區域（建議選 Singapore）
            5. 等待專案創建完成（約 2 分鐘）
            
            ### 步驟 2：創建資料表
            1. 進入專案後，點擊左側 "Table Editor"
            2. 點擊 "Create a new table"
            3. 表格名稱輸入：`accounting_records`
            4. 新增以下欄位：
               - `type` (text)
               - `date` (text)
               - `item` (text)
               - `amount` (float8 或 numeric)
               - `payment` (text)
               - `note` (text)
            5. 保持 `id` 和 `created_at` 自動生成
            
            ### 步驟 3：取得 API 金鑰
            1. 點擊左側 "Project Settings" → "API"
            2. 找到 "Project URL" 和 "anon public" key
            3. 複製這兩個值
            
            ### 步驟 4：設定 Streamlit Secrets
            **在 Streamlit Cloud：**
            1. 進入應用設定 → Secrets
            2. 貼上：
            ```toml
            supabase_url = "你的 Project URL"
            supabase_key = "你的 anon key"
            ```
            
            **本地測試：**
            1. 創建 `.streamlit/secrets.toml`
            2. 貼上相同內容
            
            ### 步驟 5：啟用連接
            1. 點擊上方「啟用 Supabase」按鈕
            2. 完成！資料將自動同步到雲端
            
            ### ✨ Supabase 優勢
            - ✅ **完全免費**：500MB 資料庫空間
            - ✅ **無需信用卡**：GitHub 登入即可使用
            - ✅ **即時同步**：多裝置自動更新
            - ✅ **資料安全**：PostgreSQL 資料庫
            - ✅ **視覺化管理**：網頁介面直接查看資料
            """)
        
        # 資料遷移
        st.divider()
        st.markdown("### 📦 資料遷移")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📤 匯出到 CSV", use_container_width=True):
                records = load_data()
                if records:
                    df = pd.DataFrame(records)
                    csv = df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="⬇️ 下載 CSV",
                        data=csv,
                        file_name=f"accounting_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.info("沒有資料可匯出")
        
        with col2:
            if st.button("🔄 本地→Supabase", use_container_width=True):
                if st.session_state.get("use_supabase", False):
                    # 從本地JSON讀取並上傳到Supabase
                    if os.path.exists(DATA_FILE):
                        with open(DATA_FILE, 'r', encoding='utf-8') as f:
                            local_records = json.load(f)
                        
                        if local_records:
                            st.info(f"找到 {len(local_records)} 筆本地記錄")
                            if st.button("確認遷移", type="primary"):
                                with st.spinner("正在遷移..."):
                                    client = get_supabase_client()
                                    if client:
                                        success_count = 0
                                        for record in local_records:
                                            if save_record_to_supabase(client, record):
                                                success_count += 1
                                        st.success(f"✅ 遷移完成！成功上傳 {success_count}/{len(local_records)} 筆記錄")
                                    else:
                                        st.error("❌ 無法連接到 Supabase")
                        else:
                            st.info("本地沒有資料")
                    else:
                        st.info("找不到本地資料檔案")
                else:
                    st.warning("⚠️ 請先啟用 Supabase")
        
    else:
        st.warning("⚠️ 尚未配置 Supabase 憑證")
        st.info("""
        ### 如何配置憑證？
        
        **在 Streamlit Cloud 上：**
        1. 進入應用設定
        2. 點擊 Secrets
        3. 貼上您的 Supabase 憑證
        
        **在本地測試：**
        1. 創建 `.streamlit/secrets.toml` 檔案
        2. 貼上憑證內容
        
        **憑證格式範例：**
        ```toml
        supabase_url = "https://xxxxxxxxxxxxx.supabase.co"
        supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        ```
        
        **取得憑證步驟：**
        1. 前往 [Supabase](https://supabase.com) 註冊（免費）
        2. 創建新專案
        3. 進入 Project Settings → API
        4. 複製 "Project URL" 和 "anon public" key
        5. 貼上到上方格式中
        """)


def main():
    """主程式"""
    # 檢查密碼
    if not check_password():
        return
    
    # 側邊欄
    with st.sidebar:
        st.title(f"💰 個人記帳工具 v{VERSION}")
        st.markdown("---")
        
        page = st.radio(
            "選擇功能",
            ["💸 支出記帳", "💰 收入記帳", "📊 統計分析", "⚙️ 系統設定"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # 顯示總覽統計
        st.subheader("📈 總覽")
        all_records = load_data()
        expense_total = sum(r["amount"] for r in all_records if r.get("type", "expense") == "expense")
        income_total = sum(r["amount"] for r in all_records if r.get("type") == "income")
        
        st.metric("累計支出", f"NT$ {int(expense_total):,}")
        st.metric("累計收入", f"NT$ {int(income_total):,}")
        st.metric("淨收支", f"NT$ {int(income_total - expense_total):,}")
        
        # 顯示資料來源
        if st.session_state.get("use_supabase", False):
            st.success("📊 資料：Supabase 雲端")
        else:
            st.info("📊 資料：本地 JSON")
        
        st.markdown("---")
        st.caption(f"© 2026 個人記帳工具 v{VERSION}")
        
        # 登出按鈕
        if st.button("🚪 登出", use_container_width=True):
            st.session_state.password_correct = False
            st.rerun()
    
    # 主要內容
    if page == "💸 支出記帳":
        expense_page()
    elif page == "💰 收入記帳":
        income_page()
    elif page == "📊 統計分析":
        statistics_page()
    else:
        settings_page()


if __name__ == "__main__":
    main()
