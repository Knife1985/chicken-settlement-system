# 炸雞對帳系統

這是一個自動化的炸雞銷售對帳系統，可以從 Google Sheets 讀取銷售資料，並每兩週自動生成對帳報告。

## 功能特色

- 🔗 **Google Sheets 整合**: 直接從 Google Sheets 讀取銷售資料
- 📊 **自動計算**: 自動計算各品項銷售金額和數量
- 📅 **定期結算**: 每兩週自動執行對帳結算
- 📈 **詳細報告**: 生成 Excel、CSV 等多種格式的對帳報告
- 🔔 **通知功能**: 支援 Email、控制台等多種通知方式
- ⚙️ **靈活設定**: 可自訂品項單價、結算週期等參數

## 系統需求

- Python 3.7+
- Google Sheets API 存取權限
- 網路連線

## 安裝步驟

### 1. 安裝相依套件

```bash
pip install -r requirements.txt
```

### 2. 設定 Google Sheets API

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Google Sheets API
4. 建立服務帳戶並下載認證檔案
5. 將認證檔案重新命名為 `credentials.json` 並放在專案根目錄
6. 將服務帳戶的 Email 加入您的 Google Sheet 的編輯者權限

### 3. 設定 Google Sheet

建立一個 Google Sheet，包含以下欄位：

| 日期 | 品項 | 數量 | 單價 | 備註 |
|------|------|------|------|------|
| 2024-01-01 | 雞排 | 10 | 65 | |
| 2024-01-01 | 雞翅 | 5 | 25 | |
| ... | ... | ... | ... | ... |

### 4. 修改設定檔

編輯 `config.py` 檔案，設定以下參數：

```python
# Google Sheets 設定
GOOGLE_SHEETS_CONFIG = {
    'SHEET_ID': 'your_google_sheet_id_here',  # 替換為您的 Google Sheet ID
    'SHEET_NAME': '銷售記錄',  # 工作表名稱
    'DATA_RANGE': 'A1:Z1000',  # 資料範圍
}

# 品項設定
PRODUCTS_CONFIG = {
    '雞排': 65,
    '雞翅': 25,
    '雞腿': 55,
    '雞塊': 40,
    '雞米花': 35,
    '雞柳條': 45
}
```

## 使用方法

### 手動執行對帳

```bash
# 執行最近兩週的對帳
python main.py --mode manual

# 執行指定日期範圍的對帳
python main.py --mode manual --start-date 2024-01-01 --end-date 2024-01-14

# 執行指定開始日期和天數的對帳
python main.py --mode manual --start-date 2024-01-01 --days 14
```

### 自動排程模式

```bash
# 啟動自動排程（每兩週執行一次）
python main.py --mode auto
```

### 測試模式

```bash
# 測試系統功能
python main.py --mode test
```

## 設定說明

### 結算週期設定

在 `config.py` 中修改 `SETTLEMENT_CONFIG`：

```python
SETTLEMENT_CONFIG = {
    'SETTLEMENT_PERIOD_DAYS': 14,  # 結算週期（天數）
    'START_DATE': None,  # 結算開始日期，None 表示從今天開始
    'AUTO_SETTLEMENT': True,  # 是否啟用自動結算
    'SETTLEMENT_TIME': '09:00'  # 結算執行時間
}
```

### 品項單價設定

在 `config.py` 中修改 `PRODUCTS_CONFIG`：

```python
PRODUCTS_CONFIG = {
    '雞排': 65,
    '雞翅': 25,
    '雞腿': 55,
    # 添加更多品項...
}
```

### 通知設定

在 `config.py` 中修改 `NOTIFICATION_CONFIG`：

```python
NOTIFICATION_CONFIG = {
    'ENABLED': True,  # 是否啟用通知
    'METHOD': 'console',  # 通知方式: 'console', 'email', 'file'
    'EMAIL': {
        'SMTP_SERVER': 'smtp.gmail.com',
        'SMTP_PORT': 587,
        'SENDER_EMAIL': 'your_email@gmail.com',
        'SENDER_PASSWORD': 'your_app_password',
        'RECIPIENT_EMAIL': 'boss_email@gmail.com'
    }
}
```

## 報告格式

系統會生成以下格式的報告：

### Excel 報告
- 結算摘要工作表
- 品項摘要工作表（含圖表）
- 每日摘要工作表
- 詳細資料工作表

### CSV 報告
- 品項銷售摘要的 CSV 格式

### 文字報告
- 簡潔的文字格式摘要

## 檔案結構

```
雞排自動結帳/
├── main.py                    # 主程式
├── config.py                  # 設定檔
├── google_sheets_client.py    # Google Sheets API 客戶端
├── settlement_calculator.py   # 對帳計算器
├── report_generator.py        # 報告生成器
├── settlement_scheduler.py    # 排程器
├── requirements.txt           # 相依套件
├── credentials.json           # Google API 認證檔案
├── token.json                 # Google API Token（自動生成）
├── reports/                   # 報告輸出目錄
└── README.md                  # 說明文件
```

## 常見問題

### Q: 如何取得 Google Sheet ID？
A: 從 Google Sheet 的 URL 中複製 ID，例如：
`https://docs.google.com/spreadsheets/d/1ABC123.../edit`
ID 就是 `1ABC123...` 這部分。

### Q: 如何設定 Email 通知？
A: 需要設定 Gmail 的應用程式密碼，並在 `config.py` 中填入正確的 SMTP 設定。

### Q: 可以修改結算週期嗎？
A: 可以，在 `config.py` 中修改 `SETTLEMENT_PERIOD_DAYS` 參數。

### Q: 如何添加新的品項？
A: 在 `config.py` 的 `PRODUCTS_CONFIG` 中添加新的品項和單價。

## 授權

本專案採用 MIT 授權條款。

## 支援

如有問題或建議，請聯繫開發團隊。

