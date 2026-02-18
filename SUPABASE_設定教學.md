# Supabase 設定教學

本記帳工具使用 Supabase 作為雲端資料庫，實現多裝置同步和資料備份功能。

## 🌟 為什麼選擇 Supabase？

- ✅ **完全免費**：500MB 資料庫空間（足夠使用數年）
- ✅ **無需信用卡**：使用 GitHub 帳號即可註冊
- ✅ **即時同步**：多裝置自動更新資料
- ✅ **安全可靠**：PostgreSQL 資料庫，企業級安全
- ✅ **視覺化管理**：網頁介面直接查看和編輯資料

---

## 📋 設定步驟

### 步驟 1：註冊 Supabase 帳號

1. 前往 [Supabase 官網](https://supabase.com)
2. 點擊右上角 **"Start your project"** 或 **"Sign In"**
3. 選擇 **"Continue with GitHub"** 使用 GitHub 帳號登入
4. 授權 Supabase 存取您的 GitHub 帳號

> 💡 如果沒有 GitHub 帳號，可以先到 [GitHub](https://github.com) 免費註冊

---

### 步驟 2：創建新專案

1. 登入後點擊 **"New Project"**
2. 選擇或創建一個 **Organization**（組織）
3. 填寫專案資訊：
   - **Name**：例如 `accounting-tool`（專案名稱）
   - **Database Password**：設定一個強密碼（請記住此密碼）
   - **uH2zVR#3/8wCeHT**
   - **Region**：選擇 **Singapore (Southeast Asia)** （離台灣最近）
   - **Pricing Plan**：選擇 **Free** （免費方案）
4. 點擊 **"Create new project"**
5. 等待約 1-2 分鐘讓專案初始化完成

---

### 步驟 3：創建資料表

1. 專案創建完成後，點擊左側選單的 **"Table Editor"**
2. 點擊 **"Create a new table"**
3. 設定表格資訊：
   - **Name**：`accounting_records` （必須使用此名稱）
   - **Description**：記帳記錄
   - 勾選 **"Enable Row Level Security (RLS)"** （先不勾選，簡化設定）

4. 新增以下欄位（Columns）：

| Column name | Type    | Default value | Primary | Allow nullable |
|-------------|---------|---------------|---------|----------------|
| id          | int8    | AUTO          | ✓       | ✗              |
| type        | text    | -             |         | ✗              |
| date        | text    | -             |         | ✗              |
| item        | text    | -             |         | ✗              |
| amount      | float8  | -             |         | ✗              |
| payment     | text    | -             |         | ✗              |
| note        | text    | -             |         | ✓              |
| created_at  | timestamptz | now() | | ✗ |

5. 點擊 **"Save"** 完成表格創建

> 💡 `id` 和 `created_at` 會自動生成，無需手動輸入

---

### 步驟 4：取得 API 金鑰

1. 點擊左側選單的 **"Project Settings"** （齒輪圖示）
2. 選擇 **"API"** 分頁
3. 找到兩個重要資訊：
   - **Project URL**：例如 `https://xxxxxxxxxxxxx.supabase.co`
   - **anon public** key：一長串 JWT token（以 `eyJ` 開頭）
4. 點擊右側複製按鈕，分別複製這兩個值並保存

---

### 步驟 5：設定 Streamlit Secrets

#### 在 Streamlit Cloud 部署時：

1. 進入 [Streamlit Cloud](https://share.streamlit.io)
2. 找到您的應用，點擊右側的 **⋮** → **Settings**
3. 選擇 **"Secrets"** 分頁
4. 在編輯器中貼上以下內容（替換成您的實際值）：

```toml
supabase_url = "https://xxxxxxxxxxxxx.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6..."
```

5. 點擊 **"Save"**
6. Streamlit 會自動重新啟動應用

#### 在本地開發時：

1. 在專案資料夾中創建 `.streamlit` 資料夾（如果不存在）
2. 在 `.streamlit` 資料夾中創建 `secrets.toml` 檔案
3. 貼上相同的內容：

```toml
supabase_url = "https://xxxxxxxxxxxxx.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

4. 保存檔案並重啟 Streamlit 應用

> ⚠️ **重要**：`.streamlit/secrets.toml` 不應該提交到 Git（已在 `.gitignore` 中排除）

---

### 步驟 6：啟用 Supabase 連接

1. 在應用中點擊左側選單的 **"⚙️ 系統設定"**
2. 確認顯示 **"✅ Supabase 憑證已配置"**
3. 點擊 **"🔗 啟用 Supabase"** 按鈕
4. 等待連接測試完成
5. 看到 **"✅ 成功連接到 Supabase！"** 表示設定成功 🎉

---

## 🔄 資料遷移

如果您之前使用本地 JSON 儲存資料，可以將資料遷移到 Supabase：

1. 進入 **"⚙️ 系統設定"** 頁面
2. 在 **"📦 資料遷移"** 區塊
3. 點擊 **"🔄 本地→Supabase"** 按鈕
4. 確認遷移數量無誤後，點擊 **"確認遷移"**
5. 等待遷移完成

---

## 📊 查看資料

您可以直接在 Supabase 網頁介面查看資料：

1. 前往 Supabase 專案
2. 點擊左側 **"Table Editor"**
3. 選擇 `accounting_records` 表格
4. 即可查看所有記帳記錄

---

## 🔧 常見問題

### Q1: 連接失敗怎麼辦？

**檢查清單：**
- ✓ Supabase 專案是否已完成初始化（約 2 分鐘）
- ✓ `accounting_records` 表格是否已創建
- ✓ API URL 和 Key 是否正確複製（注意不要有多餘空格）
- ✓ Streamlit secrets 格式是否正確
- ✓ Streamlit 應用是否已重啟

### Q2: 啟用 Supabase 後，為什麼資料還是本地的？

**原因說明：**
- 啟用 Supabase 後，應用會**從 Supabase 讀取資料**
- 如果 Supabase 資料表是空的，當然看不到資料！
- 本地的 JSON 資料不會自動上傳到 Supabase

**解決方法：**

**方法 1：遷移舊資料（如果之前有本地資料）**
1. 進入 **"⚙️ 系統設定"**
2. 在 **"📦 資料遷移"** 區塊
3. 點擊 **"🔄 本地→Supabase"** 按鈕
4. 點擊 **"確認遷移"**
5. 等待遷移完成後，重新整理頁面

**方法 2：新增新資料**
- 啟用 Supabase 後，新增的資料會自動儲存到 Supabase
- 回到記帳頁面新增一筆測試記錄
- 前往 Supabase 網頁介面查看是否已上傳成功

**方法 3：檢查 Supabase 資料表**
1. 前往 Supabase 專案
2. 點擊 **"Table Editor"** → **"accounting_records"**
3. 確認資料表中是否有資料
4. 如果是空的，需要先遷移或新增資料

**驗證連接成功：**
- 左側欄下方應顯示 **"📊 資料：Supabase 雲端"**（而非「本地 JSON」）
- 系統設定頁面顯示 **"連接狀態：已連接"**
- 新增一筆記錄，到 Supabase 網頁確認是否出現

### Q3: 如何切換回本地模式？

1. 進入 **"⚙️ 系統設定"**
2. 點擊 **"🔌 停用 Supabase"**
3. 資料會自動切換回本地 JSON 檔案

### Q4: Supabase 免費方案有什麼限制？

- 500MB 資料庫空間（約可儲存 50 萬筆記錄）
- 每月 500MB 資料傳輸
- API 請求無限制
- 適合個人使用，完全夠用！

### Q5: 資料會同步到多個裝置嗎？

是的！只要在不同裝置上都啟用 Supabase 連接，資料會即時同步。

### Q6: 如何備份資料？

1. 進入 **"⚙️ 系統設定"**
2. 點擊 **"📤 匯出到 CSV"**
3. 下載 CSV 檔案作為備份

---

## 🎯 下一步

設定完成後，您可以：
- ✅ 在 iPhone 或任何裝置上使用記帳工具
- ✅ 資料自動同步到雲端
- ✅ 隨時隨地查看和編輯記帳記錄
- ✅ 使用統計功能分析支出和收入

---

## 📚 參考資源

- [Supabase 官方文件](https://supabase.com/docs)
- [Supabase 資料庫指南](https://supabase.com/docs/guides/database)
- [Streamlit Secrets 管理](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)

---

**設定過程中遇到問題？** 歡迎在專案 Issues 中提問！
