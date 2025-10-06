"""
炸雞對帳系統網頁介面
專門處理炸雞品項的對帳功能
"""
from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from datetime import datetime, timedelta
import os
import json
from chicken_settlement_calculator import ChickenSettlementCalculator
from chicken_report_generator import ChickenReportGenerator
from chicken_config import CHICKEN_PRODUCTS_CONFIG, GOOGLE_SHEETS_CONFIG
from real_chicken_sheets_client import RealChickenSheetsClient
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 全域變數
calculator = ChickenSettlementCalculator(CHICKEN_PRODUCTS_CONFIG)
report_generator = ChickenReportGenerator("chicken_reports")

# 嘗試建立 Google Sheets 客戶端，如果失敗則使用測試模式
sheets_client = None
try:
    if os.path.exists(GOOGLE_SHEETS_CONFIG['CREDENTIALS_FILE']):
        sheets_client = RealChickenSheetsClient(
            GOOGLE_SHEETS_CONFIG['SHEET_ID'],
            GOOGLE_SHEETS_CONFIG['CREDENTIALS_FILE']
        )
        logger.info("Google Sheets 客戶端初始化成功")
    else:
        logger.warning("Google API 認證檔案不存在，將使用測試模式")
except Exception as error:
    logger.warning(f"無法初始化 Google Sheets 客戶端: {error}，將使用測試模式")

@app.route('/')
def index():
    """首頁"""
    return render_template('chicken_index.html')

@app.route('/api/real_data')
def get_real_data():
    """取得真實 Google Sheet 資料"""
    try:
        # 讀取真實的 Google Sheet 資料
        df = sheets_client.read_chicken_sales_data(
            GOOGLE_SHEETS_CONFIG['MAIN_SHEET_NAME'],
            GOOGLE_SHEETS_CONFIG['SETTINGS_SHEET_NAME'],
            GOOGLE_SHEETS_CONFIG['DATA_RANGE'],
            GOOGLE_SHEETS_CONFIG['SETTINGS_RANGE']
        )
        
        if df.empty:
            return jsonify({
                'success': False, 
                'error': '沒有找到炸雞銷售資料，請檢查 Google Sheet 中是否有炸雞品項的銷售記錄'
            })
        
        # 處理資料
        processed_df = calculator.process_chicken_sales_data(df)
        
        # 計算各種摘要
        daily_summary = calculator.calculate_daily_chicken_summary(processed_df)
        product_summary = calculator.calculate_chicken_product_summary(processed_df)
        settlement_info = calculator.calculate_chicken_settlement(processed_df)
        
        # 轉換為 JSON 格式，處理 int64 序列化問題
        daily_summary_dict = daily_summary.astype(str).to_dict('records')
        product_summary_dict = product_summary.astype(str).to_dict('records')
        
        # 處理 settlement_info 中的數值
        settlement_info_dict = {}
        for key, value in settlement_info.items():
            if pd.isna(value):
                settlement_info_dict[key] = 0
            else:
                settlement_info_dict[key] = float(value)
        
        # 處理原始資料
        raw_data_dict = processed_df.head(10).astype(str).to_dict('records')
        
        result = {
            'success': True,
            'data': {
                'daily_summary': daily_summary_dict,
                'product_summary': product_summary_dict,
                'settlement_info': settlement_info_dict,
                'raw_data': raw_data_dict
            }
        }
        
        return jsonify(result)
        
    except Exception as error:
        logger.error(f"取得真實資料時發生錯誤: {error}")
        return jsonify({'success': False, 'error': str(error)})

@app.route('/api/test_data')
def get_test_data():
    """取得測試資料（備用）"""
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
        processed_df = calculator.process_chicken_sales_data(df)
        
        # 計算各種摘要
        start_date = datetime(2025, 4, 29)
        end_date = datetime(2025, 5, 7)
        
        daily_summary = calculator.calculate_daily_chicken_summary(processed_df)
        product_summary = calculator.calculate_chicken_product_summary(processed_df)
        settlement_info = calculator.calculate_chicken_settlement(processed_df)
        
        # 轉換為 JSON 格式，處理 int64 序列化問題
        daily_summary_dict = daily_summary.astype(str).to_dict('records')
        product_summary_dict = product_summary.astype(str).to_dict('records')
        
        # 處理 settlement_info 中的數值
        settlement_info_dict = {}
        for key, value in settlement_info.items():
            if pd.isna(value):
                settlement_info_dict[key] = 0
            else:
                settlement_info_dict[key] = float(value)
        
        # 處理原始資料
        raw_data_dict = processed_df.head(10).astype(str).to_dict('records')
        
        result = {
            'success': True,
            'data': {
                'daily_summary': daily_summary_dict,
                'product_summary': product_summary_dict,
                'settlement_info': settlement_info_dict,
                'raw_data': raw_data_dict
            }
        }
        
        return jsonify(result)
        
    except Exception as error:
        logger.error(f"取得測試資料時發生錯誤: {error}")
        return jsonify({'success': False, 'error': str(error)})

@app.route('/api/generate_report', methods=['POST'])
def generate_report():
    """生成對帳報告"""
    try:
        data = request.json
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
        
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
        settlement_report = calculator.generate_chicken_settlement_report(df, start_date, end_date)
        
        # 生成 Excel 報告
        excel_file = report_generator.generate_excel_report(settlement_report)
        
        return jsonify({
            'success': True,
            'message': '炸雞對帳報告生成成功',
            'excel_file': excel_file,
            'report_data': {
                '期間': settlement_report['期間'],
                '總銷售金額': settlement_report['總銷售金額'],
                '總銷售數量': settlement_report['總銷售數量'],
                '炸雞老闆應付金額': settlement_report['炸雞老闆應付金額'],
                '成本比例': settlement_report['成本比例'],
                '利潤': settlement_report['利潤']
            }
        })
        
    except Exception as error:
        logger.error(f"生成報告時發生錯誤: {error}")
        return jsonify({'success': False, 'error': str(error)})

@app.route('/api/download_report/<filename>')
def download_report(filename):
    """下載報告檔案"""
    try:
        file_path = os.path.join('chicken_reports', filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'success': False, 'error': '檔案不存在'})
    except Exception as error:
        logger.error(f"下載報告時發生錯誤: {error}")
        return jsonify({'success': False, 'error': str(error)})

if __name__ == '__main__':
    # 確保 reports 目錄存在
    if not os.path.exists('chicken_reports'):
        os.makedirs('chicken_reports')
    
    # 確保 templates 目錄存在
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("🍗 啟動炸雞對帳系統網頁介面...")
    print("📱 請在瀏覽器中開啟: http://localhost:8081")
    print("⏹️  按 Ctrl+C 停止服務")
    
    app.run(debug=True, host='0.0.0.0', port=8081)
