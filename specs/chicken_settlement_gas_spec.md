# Spec：雞排對帳系統 Google Apps Script 版本

## 摘要
將現有的雞排對帳系統（含 Google Sheets 整合、文字摘要、複製功能）重新包裝成部署於 Google Apps Script（GAS）的網路服務。最終成果為一個可在瀏覽器操作的對帳工具，支援從 Google Sheets 讀取資料、生成每日明細的文字報告、匯出 Excel、並提供複製摘要功能；同時保留排程自動結算與通知能力。

## 目標
- ✅ 在 GAS 上建立可公開使用的 Web App，提供與現行 `index.html` 一致的互動介面與摘要格式。
- ✅ 移植既有 Python 模組的計算邏輯，確保每日明細、品項對帳與計算式一致。
- ✅ 支援直接讀取 Google Sheets，無需額外後端或伺服器。
- ✅ 保留報告輸出（Excel/CSV）與手動複製摘要功能。
- ✅ 提供自動排程（Time-driven Trigger）每日/每兩週自動結算並寄送通知。

## 非目標
- ❌ 不支援非 Google 帳號存取（GAS 限制）。
- ❌ 不支援離線使用。
- ❌ 不重新開發自訂認證後台或會員系統。

## 使用情境 / User Stories
1. **店長匯入對帳**：店長開啟 Web App → 選擇結算期間 → 按下「載入炸雞數據」→ 立即顯示每日明細、品項摘要與應付金額 → 一鍵複製摘要貼到 LINE。
2. **會計下載報告**：會計於月底登入 → 指定日期範圍 → 下載 Excel 對帳報告以備份。
3. **自動提醒**：每兩週自動執行結算 → 寄送文字摘要與報告連結至設定的 Email。

## 現況與差距
- **現有實作**：Python Flask + 靜態版 `index.html`（Vercel）提供模擬資料；`chicken_settlement_calculator.py` 具完整結算邏輯。
- **差距**：
  - 最新部署為純前端 Mock 資料，缺少真實 Google Sheets 讀寫。
  - Python 環境無法直接搬到 GAS，需要以 Apps Script（基於 JavaScript）重寫主要邏輯。
  - 自動排程需改用 GAS Trigger。

### 既有雲端設定
- Google Sheet：
  - `1wweNNyclcNn1g_uGj3IBA56OaRrJlAMsr2uxeCB2IZs`（來源帳號擁有，實際資料分頁 `表單回應1` 等；已共享給分析帳號閱讀）
  - `1i3K-MA764j2JoaVZEbgzH_eD8xWbbbOTsEpZTcJaE24`（原始備援表單，可視需要保留）
- 服務帳戶：`chicken-settlement-sa@chicken-settlement.iam.gserviceaccount.com`（已被加入該 Sheet 的編輯權限）
- 憑證檔：本地 `credentials.json`（與 `.gitignore` 一併更新，避免 commit），待 `token.json` 首次授權後自動生成

## 系統設計概要
### 架構圖（文字描述）
- **前端 UI**：HTML/CSS/JS，部署在 GAS Web App。負責輸入日期、觸發結算、顯示文字摘要、提供複製按鈕與下載報告。
- **Apps Script 服務端**：
  - `doGet()`: 回傳前端頁面。
  - `doPost()`: 接收前端請求（日期範圍、動作類型），呼叫計算模組。
  - `SettlementService`: 將原 Python 計算流程（資料處理、每日明細、品項摘要、文字總結）改寫成 JS。
  - `SheetsClient`: 讀取 Google Sheets 資料範圍，輸出 JSON。
  - `ReportGenerator`: 使用 Google Workspace API / DriveApp 匯出 Excel、CSV。
  - `Notifier`: 寄送 email（GmailApp / MailApp）。
  - `Triggers`: Time-driven trigger 呼叫 `runScheduledSettlement()`。

### 資料流程
1. 前端送出日期範圍 → `google.script.run.generateSettlement(startDate, endDate)`
2. Apps Script 讀取 Google Sheets → 執行計算 → 回傳 JSON 結果。
3. 前端渲染：
   - 文字摘要（每日明細 + 總計 + 計算式）
   - 品項對帳表
   - 複製按鈕
4. 下載報告：前端呼叫 `google.script.run.exportReport(...)` → 產生檔案於 Google Drive → 回傳分享連結。
5. 排程：Trigger 定期執行 → 產生報告、寄送通知。

## 功能需求
### F1：即時對帳摘要
- 輸入開始、結束日期（必填，預設最近 14 日）。
- 從 Google Sheets 指定工作表讀取欄位：日期、品項、數量、單價、備註。
- 計算每日明細（含品項、數量、進價）、每日總計、品項總表、計算式、應付金額。
- 以原備份 ASCII 文字格式顯示，並保留複製按鈕。
- 若同一天有多筆回應，僅取「時間戳記較新的最後一筆」資料入帳（避免手動更正造成日期錯位）。
- 解析日期時優先使用工作表顯示文字（避免時區及 Google Sheet 底層格式造成日期往前一天的平移），必要時再落回序號或字串解析，最終以 `{year, month, day}` 形式比對與分組以確保每日明細與總計一致。

### F2：報告輸出
- 產出 Excel（含結算摘要、品項摘要、每日摘要、明細）。
- 產出 CSV（品項摘要）。
- 生成檔案儲存在 Google Drive 指定資料夾，提供下載/分享連結。

### F3：自動排程與通知
- Time-driven Trigger 預設每 14 天執行，時間可設定。
- 執行時自動抓取最新資料，產出報告，將文字摘要與報告連結寄送至設定 Email。
- 可手動在 UI 觸發同樣流程。

### F4：系統設定
- 可於 Apps Script Properties 設定：
  - Google Sheet ID、工作表名稱、資料範圍。
  - 品項與進價（JSON）。
  - Email 通知設定。
  - 報告輸出資料夾 ID。
- 提供 UI 按鈕顯示目前設定摘要（唯讀）。

## 非功能需求
- 使用者需登入 Google 帳號才可存取（GAS 限制）。
- 回應時間 < 5 秒（以 2000 筆資料為基準）。
- 文字摘要格式 100% 符合備份版本（包含每日明細、計算式）。
- 程式碼以 TypeScript for GAS 維護（可用 clasp 開發），並具單元測試。

## 技術規格
- **語言**：Google Apps Script（TypeScript 編譯）、HTML/CSS/JavaScript。
- **資料來源**：Google Sheets。
- **檔案儲存**：Google Drive。
- **通知**：GmailApp / MailApp。
- **框架**：Apps Script 原生（無需外部框架）。
- **版本控管**：持續使用 GitHub，同步 GAS 程式碼（使用 `clasp` CLI）。
- **表單分頁對應**：系統會以「去除空白、變小寫」的方式比對工作表名稱，避免前端設定與實際分頁存在全形/半形或空格差異而讀不到資料。
- **本機工具**：
  - Node.js v25.1.0（含 npm 11.6.2，透過 Homebrew 安裝 `brew install node`）
  - Google `clasp` CLI 3.1.1（`npm install -g @google/clasp`）
  - 已啟用 Google Apps Script API（<https://script.google.com/home/usersettings>）

## 開發計畫
### 里程碑與預估時程
1. **M1：需求確認與環境設定（1 週）**
   - 建立 GAS 專案與 Web App 範本（需啟用 Apps Script API、安裝 Node.js/npm 與 `clasp`）。
   - 設定 clasp 與 GitHub 同步流程（`clasp login`、`clasp create`、`clasp push`）。
   - 匯整品項成本與報表範例。
2. **M2：核心計算模組移植（2 週）**
   - 將 `chicken_settlement_calculator.py` 轉寫成 Apps Script。
   - 覆蓋：資料清洗、每日/品項摘要、文字報告、Excel 結構。
   - 撰寫單元測試驗證與 Python 結果一致。
3. **M3：前端整合與互動流程（1 週）**
   - 將現行 `index.html` UI 轉為 GAS 前端。
   - 完成 `google.script.run` 呼叫與結果呈現。
   - 確認複製按鈕在 GAS 環境可用。
4. **M4：報告匯出與自動排程（1 週）**
   - 實作報告匯出、Google Drive 儲存、連結回傳。
   - 建立 Time-driven Trigger、Email 通知。
5. **M5：驗收與部署（1 週）**
   - 整體整合測試、壓力測試。
   - 完成使用手冊與部署流程文件。
   - 釋出正式 Web App URL。

### 交付項目
- GAS 程式碼（clasp 專案結構）。
- `appsscript.json` 設定檔。
- 前端 HTML/CSS/JS。
- 部署說明檔（含 Node.js/npm 安裝、`clasp` 操作、Apps Script API 啟用、跨帳號表單分享注意事項）。
- 測試報告（含與 Python 版比對）。
- 使用手冊與部署說明（含權限設定、Trigger 設定）。

## 測試計畫
- 單元測試：計算模組各函式（每日摘要、品項摘要、文字輸出）。
- 整合測試：模擬 date range→ API → 回傳 JSON → 前端渲染。
- 回歸測試：確保文字摘要與舊備份逐字一致（可比對字串）。
- 排程測試：使用 GAS Test Trigger 驗證報告產出與 Email 通知。

## 風險與緩解
- **Apps Script 執行時間限制**：分批讀取資料、必要時採分頁；報告匯出改排程背景執行。
- **Excel 產生受限**：若 GAS 轉 Excel 複雜，改用 Google Sheet 報告模板並提供下載格式。
- **權限設定困難**：提供詳細部署文件，包含 OAuth 範圍、分享設定（跨帳號表單需授權來源帳號共享讀取）。
- **文字格式差異**：撰寫自動化比對腳本，確保輸出與 Python 版一致。

## 開放議題
- 是否需要提供 LINE Notify 等更多通知管道？
- 報告是否要支援多幣別或多店面合併？
- 是否保留 Python 版作為備援？需要同步資料嗎？

---
**負責人**：待指派  
**狀態**：草稿（需與利害關係人審閱）  
**最後更新**：2025-11-10


