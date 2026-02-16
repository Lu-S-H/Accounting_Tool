# 📱 Streamlit 記帳工具部署說明

## 🎯 功能特色

✅ **完整功能**
- 支出記帳（預設10種分類）
- 收入記帳（預設8種分類）
- 統計圓餅圖（支出/收入並列顯示）
- 資料自動保存（JSON格式）
- 密碼保護功能

✅ **手機友善**
- 響應式設計，自動適應手機螢幕
- iPhone/Android 都可使用
- 可加入主畫面，像 App 一樣使用

---

## 🚀 本地測試

### 1. 安裝依賴
```bash
pip install streamlit pandas matplotlib
```

### 2. 運行程式
```bash
streamlit run streamlit_app.py
```

### 3. 開啟瀏覽器
程式會自動開啟瀏覽器，預設網址：
```
http://localhost:8501
```

### 4. 登入
- 預設密碼：`1234`
- 建議修改程式中的密碼（第29行）

---

## ☁️ 部署到 Streamlit Cloud

### 步驟 1：準備 GitHub 倉庫

1. 在 GitHub 創建新倉庫（例如：`my-accounting-app`）

2. 上傳以下文件：
   - `streamlit_app.py`（主程式）
   - `requirements.txt`（依賴套件）
   - 選擇性：`.gitignore`（避免上傳資料檔）

3. 建議的 `.gitignore` 內容：
```
accounting_data.json
__pycache__/
*.pyc
.DS_Store
```

### 步驟 2：部署到 Streamlit Cloud

1. 前往 [Streamlit Cloud](https://streamlit.io/cloud)

2. 點擊 **"New app"**

3. 連接您的 GitHub 帳號

4. 選擇倉庫和分支：
   - Repository: `your-username/my-accounting-app`
   - Branch: `main`
   - Main file path: `streamlit_app.py`

5. 點擊 **"Deploy"**

6. 等待約 2-3 分鐘，應用程式就會上線！

### 步驟 3：獲取網址

部署完成後，您會得到一個網址，例如：
```
https://your-username-my-accounting-app-streamlit-app-xxxxx.streamlit.app
```

---

## 📱 在 iPhone 上使用

### 方法 1：瀏覽器開啟
直接用 Safari 或 Chrome 開啟部署後的網址

### 方法 2：加入主畫面（推薦）

1. 用 Safari 開啟您的應用網址

2. 點擊底部的**分享按鈕** 📤

3. 選擇 **"加入主畫面"**

4. 自訂圖示名稱（例如：記帳本）

5. 點擊 **"加入"**

6. 現在主畫面上就有捷徑了！ 🎉

---

## 🔐 修改密碼

### 在程式中修改
打開 `streamlit_app.py`，找到第 29 行：

```python
PASSWORD = "1234"  # 修改這裡
```

改為您的密碼：
```python
PASSWORD = "your_secure_password"
```

### 使用環境變數（更安全）

在 Streamlit Cloud 中設定環境變數：

1. 進入應用設定頁面
2. 點擊 **"Secrets"**
3. 添加：
```toml
PASSWORD = "your_secure_password"
```

4. 修改程式碼第 29 行：
```python
PASSWORD = st.secrets.get("PASSWORD", "1234")
```

---

## 💾 資料持久化

### 在 Streamlit Cloud 上的注意事項

⚠️ **重要**：Streamlit Cloud 的檔案系統是暫時的，應用重啟後會遺失資料！

### 解決方案（選擇一個）

#### 方案 1：使用 Google Sheets（推薦）
- 安裝 `gspread` 套件
- 連接 Google Sheets API
- 資料直接寫入雲端試算表
- 永久保存，不會遺失

#### 方案 2：使用 SQLite + GitHub
- 定期自動 commit 資料檔到 GitHub
- 需要設定 GitHub token

#### 方案 3：使用資料庫服務
- PostgreSQL（Supabase 免費方案）
- MongoDB（MongoDB Atlas 免費方案）

**目前版本使用本地 JSON 檔案**，適合本地測試或短期使用。

---

## 🎨 自訂設定

### 修改分類

編輯程式中的分類列表（第 20-22 行）：

```python
EXPENSE_CATEGORIES = ["餐飲", "交通", ...]  # 支出分類
INCOME_CATEGORIES = ["薪水", "零用錢", ...]  # 收入分類
PAYMENT_METHODS = ["現金", "信用卡", ...]    # 付款方式
```

### 修改外觀

Streamlit 支援自訂主題，在專案根目錄創建 `.streamlit/config.toml`：

```toml
[theme]
primaryColor = "#3B8ED0"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

---

## 📊 功能說明

### 支出記帳
- 選擇日期、項目、金額、付款方式
- 可添加備註
- 即時顯示統計：總支出、筆數、平均

### 收入記帳
- 同支出記帳功能
- 獨立的收入類別

### 統計分析
- 快速篩選：當日/當月/當年/自訂
- 支出/收入圓餅圖並列
- 顯示淨收支
- 明細列表可查看

---

## ❓ 常見問題

### Q: 密碼忘記了怎麼辦？
A: 修改程式碼中的 PASSWORD 變數，重新部署即可。

### Q: 可以多人使用嗎？
A: 目前是單用戶設計。如需多用戶，需要添加資料庫和用戶系統。

### Q: 資料會不會遺失？
A: 在 Streamlit Cloud 上，應用重啟會遺失資料。建議連接 Google Sheets 或資料庫。

### Q: 可以匯出資料嗎？
A: 可以在程式中添加 CSV 匯出功能（下載按鈕）。

### Q: 手機使用順暢嗎？
A: 非常順暢！UI 已針對手機優化。

---

## 🔄 更新應用

當您修改程式碼並 push 到 GitHub 後：
- Streamlit Cloud 會自動偵測到更新
- 自動重新部署（約 1-2 分鐘）
- 無需手動操作

---

## 📞 支援

如有問題，可以：
1. 查看 [Streamlit 官方文檔](https://docs.streamlit.io)
2. 查看 [Streamlit Community](https://discuss.streamlit.io)

---

## 🎉 開始使用

```bash
# 本地測試
streamlit run streamlit_app.py

# 登入密碼
1234
```

祝您記帳愉快！ 💰✨
