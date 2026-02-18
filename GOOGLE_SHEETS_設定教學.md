# 📊 Google Sheets 連動設定教學

## 🎯 功能說明

現在您的記帳工具支援：
- ✅ **本地 JSON 模式**：資料儲存在本地（預設）
- ✅ **Google Sheets 模式**：資料即時同步到 Google Sheets
- ✅ **一鍵切換**：隨時在兩種模式間切換
- ✅ **資料遷移**：可將本地資料複製到 Google Sheets

---

## 🚀 快速設定指南

### 步驟 1：創建 Google Cloud 專案（5 分鐘）

1. 前往 [Google Cloud Console](https://console.cloud.google.com)

2. 點擊頂部的「選取專案」→「新增專案」
   - 專案名稱：例如 `my-accounting-tool`
   - 點擊「建立」

3. 等待專案創建完成

### 步驟 2：啟用 API（2 分鐘）

1. 在左側選單中，點擊「API 和服務」→「程式庫」

2. 搜尋並啟用以下兩個 API：
   - ✅ **Google Sheets API**
   - ✅ **Google Drive API**

3. 每個 API 都點擊「啟用」按鈕

### 步驟 3：創建服務帳號（5 分鐘）

1. 在左側選單中，點擊「API 和服務」→「憑證」

2. 點擊「建立憑證」→「服務帳號」

3. 填寫資訊：
   - 服務帳號名稱：例如 `accounting-service`
   - 服務帳號 ID：會自動產生
   - 說明：選填
   - 點擊「建立並繼續」

4. 授予權限：
   - 角色：選擇「編輯者」
   - 點擊「繼續」→「完成」

5. 下載金鑰檔案：
   - 找到剛創建的服務帳號
   - 點擊右側的「⋮」→「管理金鑰」
   - 點擊「新增金鑰」→「建立新的金鑰」
   - 選擇「JSON」格式
   - 點擊「建立」→ 金鑰檔案會自動下載

⚠️ **重要**：妥善保管這個 JSON 檔案，不要分享給他人！

### 步驟 4：創建 Google Sheet（1 分鐘）

1. 前往 [Google Sheets](https://sheets.google.com)

2. 點擊「+」創建新的試算表

3. 命名試算表（例如：我的記帳本）

4. **複製網址**（整個網址都要）
   ```
   https://docs.google.com/spreadsheets/d/1a2b3c4d5e6f7g8h9i0j/edit
   ```

### 步驟 5：分享 Sheet 給服務帳號（2 分鐘）

1. 打開剛下載的 JSON 金鑰檔案（用記事本或文字編輯器）

2. 找到 `client_email` 這一行，複製 email 地址
   ```json
   "client_email": "accounting-service@my-project.iam.gserviceaccount.com"
   ```

3. 回到 Google Sheet，點擊右上角的「共用」按鈕

4. 貼上服務帳號的 email

5. 權限設為「編輯者」

6. **取消勾選**「通知使用者」（因為這是機器人帳號）

7. 點擊「共用」

✅ 完成！Google Sheet 已準備好了

---

## 🔐 配置憑證

### 方法 A：在 Streamlit Cloud 上（推薦）

1. 部署應用到 Streamlit Cloud

2. 進入應用管理頁面

3. 點擊「⚙️ Settings」→「Secrets」

4. 打開您的 JSON 金鑰檔案，複製**全部內容**

5. 在 Secrets 編輯器中，貼上以下格式：

```toml
[gcp_service_account]
type = "service_account"
project_id = "你的專案ID"
private_key_id = "你的私鑰ID"
private_key = "-----BEGIN PRIVATE KEY-----\n你的私鑰內容\n-----END PRIVATE KEY-----\n"
client_email = "你的服務帳號email"
client_id = "你的客戶端ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "你的憑證URL"
```

⚠️ **注意**：`private_key` 中的 `\n` 要保留！

6. 點擊「Save」

7. 應用會自動重啟

### 方法 B：在本地測試

1. 在專案資料夾中創建 `.streamlit` 資料夾

2. 在 `.streamlit` 資料夾中創建 `secrets.toml` 檔案

3. 貼上與上面相同的內容

4. 確保 `.streamlit/secrets.toml` 已加入 `.gitignore`（不要上傳到 Git）

---

## 📱 使用 Google Sheets 模式

### 連接到 Google Sheets

1. 打開應用，登入

2. 點擊側邊欄的「⚙️ 系統設定」

3. 在「Google Sheet 網址」欄位貼上您的 Sheet 網址

4. 點擊「🔗 連接 Google Sheets」

5. 看到「✅ 成功連接」訊息即表示完成

6. 側邊欄會顯示「📊 資料：Google Sheets」

### 新增記錄

現在當您新增支出或收入記錄時：
- 資料會**即時寫入** Google Sheets
- 在「記帳記錄」工作表中可以看到
- 不會再寫入本地 JSON 檔案

### 查看資料

在 Google Sheet 中，您會看到：
- **記帳記錄** 工作表（自動創建）
- 8 個欄位：ID、類型、日期、項目、金額、付款方式、備註、建立時間
- 所有記錄按新增順序排列

### 中斷連接

如果想切回本地模式：
1. 進入「⚙️ 系統設定」
2. 點擊「🔌 中斷連接」
3. 回到本地 JSON 模式

---

## 📦 資料遷移

### 從本地遷移到 Google Sheets

1. 確保已連接 Google Sheets

2. 進入「⚙️ 系統設定」

3. 點擊「🔄 本地→Sheets」

4. 系統會顯示本地有多少筆記錄

5. 點擊「確認遷移」

6. 等待完成（每秒約 1-2 筆，避免超過 API 限制）

### 匯出為 CSV

隨時可以將資料匯出：
1. 進入「⚙️ 系統設定」
2. 點擊「📤 匯出到 CSV」
3. 點擊「⬇️ 下載 CSV」
4. 檔案會下載到您的電腦

---

## 🎨 Google Sheets 的優勢

### ✅ 優點

1. **雲端備份**：資料永不遺失
2. **多裝置同步**：手機、電腦都能看
3. **進階分析**：用 Google Sheets 強大的公式和圖表
4. **資料透視表**：輕鬆製作複雜的統計報表
5. **共享**：可以分享給家人或會計師
6. **匯出方便**：Excel、PDF 等格式隨意匯出
7. **版本歷史**：可以還原到任何時間點

### ⚠️ 注意事項

1. **API 限制**：
   - 每分鐘最多 60 次請求
   - 每天最多 25,000 次請求
   - 正常使用完全夠用

2. **延遲**：
   - 比本地模式稍慢（約 1-2 秒）
   - 網路不穩可能失敗

3. **隱私**：
   - 資料存在 Google 雲端
   - 服務帳號可以存取您的 Sheet
   - 請妥善保管 JSON 金鑰

---

## 🔧 進階使用

### 在 Google Sheets 中手動編輯

您可以直接在 Google Sheet 中修改資料：
- 編輯金額、項目、備註等
- 應用程式會讀取最新資料
- ⚠️ 不要刪除標題列
- ⚠️ 不要更改欄位順序

### 創建自訂圖表

在 Google Sheet 中：
1. 選取資料範圍
2. 插入 → 圖表
3. 自訂圓餅圖、折線圖、長條圖等
4. 永久保存在 Sheet 中

### 設定公式

例如計算月平均支出：
```
=AVERAGEIFS(E:E, B:B, "expense", C:C, ">="&DATE(2026,1,1))
```

### 自動化通知

使用 Google Apps Script：
- 每日支出總結 email
- 超過預算時發送通知
- 定期報表生成

---

## ❓ 常見問題

### Q1: 憑證配置失敗？
**A:** 
- 確認 JSON 格式正確（不能有多餘逗號）
- 確認 `private_key` 中的 `\n` 都保留
- 在本地測試時，確認檔案路徑正確

### Q2: 連接失敗「403 權限錯誤」？
**A:**
- 確認 Sheet 已分享給服務帳號 email
- 確認權限設為「編輯者」
- 確認 API 已啟用

### Q3: 能否多人共用一個 Sheet？
**A:**
- 可以！多個部署都用同一個 Sheet URL
- 但建議每人有自己的應用實例
- 或在 Sheet 中用不同工作表區分

### Q4: 本地資料會遺失嗎？
**A:**
- 不會！本地 JSON 檔案保持不變
- 只是新記錄會寫入 Google Sheets
- 可隨時切回本地模式

### Q5: API 配額不夠怎麼辦？
**A:**
- 免費配額對個人使用綽綽有餘
- 每天 25,000 次 = 每秒可執行約 290 次
- 如真的不夠，可申請提高配額

### Q6: 資料安全嗎？
**A:**
- Google Sheets 使用業界標準加密
- 服務帳號只能存取您分享的 Sheet
- JSON 金鑰存在 Streamlit Secrets（加密）
- 建議定期備份

---

## 🎉 完成！

設定完成後，您就擁有：
- 💰 美觀的記帳網頁介面
- ☁️ 雲端自動備份
- 📊 強大的 Google Sheets 分析能力
- 📱 iPhone/Android 隨時隨地記帳

享受您的雲端記帳體驗吧！ ✨

---

## 📞 需要協助？

如果遇到問題：
1. 檢查本文檔的常見問題
2. 查看 [Google Sheets API 文檔](https://developers.google.com/sheets/api)
3. 查看 [gspread 文檔](https://docs.gspread.org)

祝記帳愉快！ 💰
