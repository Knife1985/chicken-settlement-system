"""
炸雞對帳系統設定檔
"""
import os
from datetime import datetime, timedelta

# Google Sheets 設定
GOOGLE_SHEETS_CONFIG = {
    # 您的 Google Sheet ID
    'SHEET_ID': '1wweNNyclcNn1g_uGj3IBA56OaRrJlAMsr2uxeCB2IZs',
    # 工作表名稱
    'SHEET_NAME': '表單回應 1',
    # 資料範圍 (例如: A1:Z1000)
    'DATA_RANGE': 'A1:Z1000',
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

# 品項設定 (根據您的實際業務調整)
PRODUCTS_CONFIG = {
    # 由於您的資料是營業總額而非具體品項，這裡設定為整體營業
    '總營業額': 1,  # 用於計算總額
    '現金收入': 1,  # 現金部分
    '刷卡收入': 1,  # 刷卡部分
    '文化幣收入': 1, # 文化幣部分
    '其他收入': 1    # 其他收入部分
}

# 欄位對應設定 (根據您的實際 Google Sheet 格式調整)
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
    '營業總額2': 'K'    # 重複的營業總額欄位
}

# 報告設定
REPORT_CONFIG = {
    # 報告輸出目錄
    'OUTPUT_DIR': 'reports',
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
        'RECIPIENT_EMAIL': 'boss_email@gmail.com'
    }
}

# 日誌設定
LOGGING_CONFIG = {
    'LEVEL': 'INFO',
    'FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'FILE': 'settlement.log'
}


