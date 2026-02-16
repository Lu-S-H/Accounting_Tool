"""
記帳工具 - Streamlit 網頁版
適合部署在 Streamlit Cloud 供個人使用
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
import matplotlib.pyplot as plt
from collections import defaultdict
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS', 'sans-serif']
matplotlib.rcParams['axes.unicode_minus'] = False

# 頁面配置
st.set_page_config(
    page_title="💰 個人記帳工具",
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
    """載入數據"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []


def save_data(records):
    """保存數據"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"保存失敗：{str(e)}")
        return False


def add_record(record_type, date_val, item, amount, payment, note):
    """新增記錄"""
    records = load_data()
    record = {
        "id": len(records) + 1,
        "type": record_type,
        "date": date_val.strftime("%Y-%m-%d"),
        "item": item,
        "amount": float(amount),
        "payment": payment,
        "note": note,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    records.append(record)
    if save_data(records):
        st.success(f"✅ {'支出' if record_type == 'expense' else '收入'}記錄已新增！")
        st.balloons()
        return True
    return False


def delete_records(indices_to_delete):
    """刪除記錄"""
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
            amount = st.number_input("金額 (NT$)", min_value=0.0, step=1.0, key="expense_amount")
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
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("總支出", f"NT$ {df['金額'].sum():,.2f}")
        with col2:
            st.metric("記錄筆數", len(df))
        with col3:
            st.metric("平均支出", f"NT$ {df['金額'].mean():,.2f}")
        
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
                format_func=lambda i: f"{records[i]['date']} - {records[i]['item']} - NT${records[i]['amount']:.2f}"
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
            amount = st.number_input("金額 (NT$)", min_value=0.0, step=1.0, key="income_amount")
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
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("總收入", f"NT$ {df['金額'].sum():,.2f}")
        with col2:
            st.metric("記錄筆數", len(df))
        with col3:
            st.metric("平均收入", f"NT$ {df['金額'].mean():,.2f}")
        
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
                format_func=lambda i: f"{records[i]['date']} - {records[i]['item']} - NT${records[i]['amount']:.2f}"
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
        st.metric("總支出", f"NT$ {total_expense:,.2f}", delta=None)
    with col2:
        st.metric("總收入", f"NT$ {total_income:,.2f}", delta=None)
    with col3:
        delta_color = "normal" if net_amount >= 0 else "inverse"
        st.metric(
            "淨收支",
            f"NT$ {net_amount:,.2f}",
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
                
                wedges, texts, autotexts = ax1.pie(
                    amounts,
                    labels=items,
                    autopct=lambda pct: f'{pct:.1f}%\nNT${pct*total_expense/100:.0f}',
                    colors=colors,
                    startangle=90,
                    textprops={'fontsize': 12, 'color': 'black', 'weight': 'bold'}
                )
                
                ax1.set_title(f'支出總計: NT${total_expense:,.2f}', fontsize=16, weight='bold', pad=20)
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
                
                wedges, texts, autotexts = ax2.pie(
                    amounts,
                    labels=items,
                    autopct=lambda pct: f'{pct:.1f}%\nNT${pct*total_income/100:.0f}',
                    colors=colors,
                    startangle=90,
                    textprops={'fontsize': 12, 'color': 'black', 'weight': 'bold'}
                )
                
                ax2.set_title(f'收入總計: NT${total_income:,.2f}', fontsize=16, weight='bold', pad=20)
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


def main():
    """主程式"""
    # 檢查密碼
    if not check_password():
        return
    
    # 側邊欄
    with st.sidebar:
        st.title("💰 個人記帳工具")
        st.markdown("---")
        
        page = st.radio(
            "選擇功能",
            ["💸 支出記帳", "💰 收入記帳", "📊 統計分析"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # 顯示總覽統計
        st.subheader("📈 總覽")
        all_records = load_data()
        expense_total = sum(r["amount"] for r in all_records if r.get("type", "expense") == "expense")
        income_total = sum(r["amount"] for r in all_records if r.get("type") == "income")
        
        st.metric("累計支出", f"NT$ {expense_total:,.2f}")
        st.metric("累計收入", f"NT$ {income_total:,.2f}")
        st.metric("淨收支", f"NT$ {income_total - expense_total:,.2f}")
        
        st.markdown("---")
        st.caption("© 2026 個人記帳工具")
        
        # 登出按鈕
        if st.button("🚪 登出", use_container_width=True):
            st.session_state.password_correct = False
            st.rerun()
    
    # 主要內容
    if page == "💸 支出記帳":
        expense_page()
    elif page == "💰 收入記帳":
        income_page()
    else:
        statistics_page()


if __name__ == "__main__":
    main()
