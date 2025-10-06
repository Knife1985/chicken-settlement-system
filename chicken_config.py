"""
炸雞對帳系統設定檔
專門處理炸雞品項的對帳設定
"""
import os
from datetime import datetime, timedelta

# Google Sheets 設定
GOOGLE_SHEETS_CONFIG = {
    # 您的 Google Sheet ID
    'SHEET_ID': '1wweNNyclcNn1g_uGj3IBA56OaRrJlAMsr2uxeCB2IZs',
    # 主要資料工作表名稱
    'MAIN_SHEET_NAME': '表單回應 1',
    # 設定工作表名稱（炸雞品項價格設定）
    'SETTINGS_SHEET_NAME': '設定',
    # 資料範圍
    'DATA_RANGE': 'A1:Z1000',
    # 設定範圍
    'SETTINGS_RANGE': 'A1:Z100',
    # 認證檔案路徑
    'CREDENTIALS_FILE': 'credentials.json',
    # Token 檔案路徑
    'TOKEN_FILE': 'token.json'
}

# 對帳設定
SETTLEMENT_CONFIG = {
    # 結算週期 (天數)
    'SETTLEMENT_PERIOD_DAYS': 14,
    # 結算開始日期 (YYYY-MM-DD 格式，或 None 表示從今天開始)
    'START_DATE': None,
    # 是否自動執行結算
    'AUTO_SETTLEMENT': True,
    # 結算時間 (24小時制，例如: "09:00")
    'SETTLEMENT_TIME': '09:00'
}

# 炸雞品項設定（預設價格，會從「設定」工作表讀取實際價格）
# 格式：{品項名稱: {'cost': 成本, 'price': 售價}}
CHICKEN_PRODUCTS_CONFIG = {
    '雞排': {'cost': 80, 'price': 170},
    '地瓜': {'cost': 35, 'price': 75},
    '棒腿': {'cost': 80, 'price': 170},
    '雞翅': {'cost': 105, 'price': 180},
    '雞腿': {'cost': 80, 'price': 170},
    '雞塊': {'cost': 60, 'price': 120},
    '雞米花': {'cost': 50, 'price': 100},
    '雞柳條': {'cost': 70, 'price': 140},
    '雞胸肉': {'cost': 75, 'price': 150},
    '雞胗': {'cost': 40, 'price': 80},
    '雞心': {'cost': 45, 'price': 90},
    '雞脖子': {'cost': 30, 'price': 60}
}

# 欄位對應設定（根據您的實際 Google Sheet 格式調整）
COLUMN_MAPPING = {
    '時間戳記': 'A',     # 時間戳記欄位
    '填表人': 'B',       # 填表人欄位
    '日期': 'C',         # 日期欄位
    '營業總額': 'D',     # 營業總額欄位
    '現金': 'E',         # 現金欄位
    '刷卡': 'F',         # 刷卡欄位
    '文化幣': 'G',       # 文化幣欄位
    '其他': 'H',         # 其他欄位
    '照片連結': 'I',     # 帳條照片連結欄位
    '特殊交接事項': 'J', # 特殊交接事項欄位
    '營業總額2': 'K',   # 重複的營業總額欄位
    # 炸雞品項欄位（需要根據您的實際欄位調整）
    '炸物的訂購_雞排': 'L',      # 雞排訂購數量
    '炸物的訂購_地瓜': 'M',      # 地瓜訂購數量
    '炸物的訂購_棒腿': 'N',      # 棒腿訂購數量
    '炸物的訂購_雞翅': 'O'       # 雞翅訂購數量
}

# 炸雞品項欄位對應（從 Google Sheet 欄位名稱對應到品項名稱）
CHICKEN_COLUMN_MAPPING = {
    '炸物的訂購_雞排': '雞排',
    '炸物的訂購_地瓜': '地瓜',
    '炸物的訂購_棒腿': '棒腿',
    '炸物的訂購_雞翅': '雞翅'
}

# 報告設定
REPORT_CONFIG = {
    # 報告輸出目錄
    'OUTPUT_DIR': 'chicken_reports',
    # 報告檔案格式 ('excel', 'csv', 'json')
    'FORMAT': 'excel',
    # 是否包含詳細明細
    'INCLUDE_DETAILS': True,
    # 是否包含圖表
    'INCLUDE_CHARTS': True
}

# 通知設定
NOTIFICATION_CONFIG = {
    # 是否啟用通知
    'ENABLED': True,
    # 通知方式 ('email', 'console', 'file')
    'METHOD': 'console',
    # Email 設定 (如果使用 email 通知)
    'EMAIL': {
        'SMTP_SERVER': 'smtp.gmail.com',
        'SMTP_PORT': 587,
        'SENDER_EMAIL': 'your_email@gmail.com',
        'SENDER_PASSWORD': 'your_app_password',
        'RECIPIENT_EMAIL': 'chicken_boss@gmail.com'  # 炸雞老闆的 Email
    }
}

# 日誌設定
LOGGING_CONFIG = {
    'LEVEL': 'INFO',
    'FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'FILE': 'chicken_settlement.log'
}
