#!/usr/bin/env python3
"""
雞排結帳系統 - 簡化版
專為 A2 Hosting 部署設計
"""
import os
import sys
import json
import pandas as pd
from datetime import datetime, timedelta
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 設定路徑
sys.path.insert(0, '/home/givingwi')

# 導入模組
try:
    from chicken_settlement_calculator import ChickenSettlementCalculator
    from chicken_report_generator import ChickenReportGenerator
    from direct_sheets_reader import DirectSheetsReader
    from chicken_config import CHICKEN_PRODUCTS_CONFIG, GOOGLE_SHEETS_CONFIG
except ImportError as e:
    logger.error(f"模組導入失敗: {e}")
    # 使用基本設定
    CHICKEN_PRODUCTS_CONFIG = {
        '雞排': 65,
        '雞翅': 25,
        '棒腿': 55,
        '地瓜': 35
    }
    GOOGLE_SHEETS_CONFIG = {
        'SHEET_ID': '1wweNNyclcNn1g_uGj3IBA56OaRrJlAMsr2uxeCB2IZs'
    }

def get_test_data():
    """取得測試資料"""
    try:
        # 建立測試資料
        test_data = {
            '日期': [
                '2025-04-29', '2025-04-29', '2025-04-29', '2025-04-30', '2025-04-30',
                '2025-04-30', '2025-05-01', '2025-05-01', '2025-05-02', '2025-05-02',
                '2025-05-02', '2025-05-03', '2025-05-03', '2025-05-04', '2025-05-04',
                '2025-05-05', '2025-05-05', '2025-05-06', '2025-05-06', '2025-05-07'
            ],
            '品項': [
                '雞排', '雞翅', '雞腿', '雞排', '雞塊',
                '雞米花', '雞排', '雞柳條', '雞排', '雞翅',
                '雞腿', '雞排', '雞塊', '雞排', '雞米花',
                '雞排', '雞翅', '雞腿', '雞排', '雞塊'
            ],
            '數量': [10, 5, 3, 8, 4, 6, 12, 2, 15, 7, 4, 9, 3, 11, 5, 8, 6, 2, 13, 4],
            '單價': [65, 25, 55, 65, 40, 35, 65, 45, 65, 25, 55, 65, 40, 65, 35, 65, 25, 55, 65, 40],
            '小計': [650, 125, 165, 520, 160, 210, 780, 90, 975, 175, 220, 585, 120, 715, 175, 520, 150, 110, 845, 160]
        }
        
        df = pd.DataFrame(test_data)
        df['日期'] = pd.to_datetime(df['日期'])
        
        return df
        
    except Exception as error:
        logger.error(f"建立測試資料時發生錯誤: {error}")
        return pd.DataFrame()

def get_real_data(start_date=None, end_date=None):
    """取得真實資料"""
    try:
        # 讀取 Google Sheets 資料
        sheets_reader = DirectSheetsReader(GOOGLE_SHEETS_CONFIG['SHEET_ID'])
        df = sheets_reader.read_chicken_sales_data()
        
        if df.empty:
            logger.warning("沒有讀取到真實資料，使用測試資料")
            return get_test_data()
        
        # 根據日期篩選
        if start_date and end_date:
            df['日期'] = pd.to_datetime(df['日期'])
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            df = df[(df['日期'] >= start_date) & (df['日期'] <= end_date)]
        
        return df
        
    except Exception as error:
        logger.error(f"取得真實資料時發生錯誤: {error}")
        return get_test_data()

def calculate_settlement(df):
    """計算對帳"""
    try:
        calculator = ChickenSettlementCalculator(CHICKEN_PRODUCTS_CONFIG)
        processed_df = calculator.process_chicken_sales_data(df)
        
        # 計算摘要
        daily_summary = calculator.calculate_daily_chicken_summary(processed_df)
        product_summary = calculator.calculate_chicken_product_summary(processed_df)
        settlement_info = calculator.calculate_chicken_settlement(processed_df)
        
        return {
            'daily_summary': daily_summary.to_dict('records'),
            'product_summary': product_summary.to_dict('records'),
            'settlement_info': settlement_info.to_dict(),
            'raw_data': processed_df.head(10).to_dict('records')
        }
        
    except Exception as error:
        logger.error(f"計算對帳時發生錯誤: {error}")
        return {}

def generate_report(start_date, end_date):
    """生成報告"""
    try:
        # 取得資料
        df = get_real_data(start_date, end_date)
        
        if df.empty:
            return {'success': False, 'error': '沒有資料可生成報告'}
        
        # 計算對帳
        calculator = ChickenSettlementCalculator(CHICKEN_PRODUCTS_CONFIG)
        start_date_obj = pd.to_datetime(start_date)
        end_date_obj = pd.to_datetime(end_date)
        
        settlement_report = calculator.generate_chicken_settlement_report(df, start_date_obj, end_date_obj)
        
        # 生成 Excel 報告
        report_generator = ChickenReportGenerator("chicken_reports")
        excel_file = report_generator.generate_excel_report(settlement_report)
        
        return {
            'success': True,
            'message': '炸雞對帳報告生成成功',
            'excel_file': excel_file,
            'report_data': settlement_report
        }
        
    except Exception as error:
        logger.error(f"生成報告時發生錯誤: {error}")
        return {'success': False, 'error': str(error)}

def main():
    """主函數"""
    print("Content-Type: application/json; charset=utf-8")
    print()
    
    try:
        # 取得請求方法
        method = os.environ.get('REQUEST_METHOD', 'GET')
        
        # 取得查詢參數
        query_string = os.environ.get('QUERY_STRING', '')
        params = {}
        if query_string:
            for param in query_string.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value
        
        # 處理不同的請求
        if 'test_data' in params:
            # 測試資料
            df = get_test_data()
            result = calculate_settlement(df)
            result['success'] = True
            result['data_type'] = 'test'
            
        elif 'real_data' in params:
            # 真實資料
            start_date = params.get('start_date')
            end_date = params.get('end_date')
            df = get_real_data(start_date, end_date)
            result = calculate_settlement(df)
            result['success'] = True
            result['data_type'] = 'real'
            
        elif method == 'POST':
            # POST 請求（生成報告）
            content_length = int(os.environ.get('CONTENT_LENGTH', 0))
            if content_length > 0:
                post_data = sys.stdin.read(content_length)
                try:
                    data = json.loads(post_data)
                    start_date = data.get('start_date')
                    end_date = data.get('end_date')
                    result = generate_report(start_date, end_date)
                except json.JSONDecodeError:
                    result = {'success': False, 'error': '無效的 JSON 資料'}
            else:
                result = {'success': False, 'error': '沒有 POST 資料'}
        else:
            # 預設回應
            result = {
                'success': True,
                'message': '雞排結帳系統 API',
                'endpoints': [
                    '?test_data=1 - 取得測試資料',
                    '?real_data=1&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD - 取得真實資料',
                    'POST / - 生成報告'
                ]
            }
        
        # 輸出 JSON 回應
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as error:
        logger.error(f"主函數執行時發生錯誤: {error}")
        error_result = {
            'success': False,
            'error': str(error),
            'message': '系統發生錯誤'
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
