"""
簡化版炸雞對帳系統網頁介面
直接讀取 Google Sheet 公開資料，不需要 API 認證
"""
from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from datetime import datetime, timedelta
import os
import json
import numpy as np
from chicken_settlement_calculator import ChickenSettlementCalculator
from chicken_report_generator import ChickenReportGenerator
from chicken_config import CHICKEN_PRODUCTS_CONFIG, GOOGLE_SHEETS_CONFIG
from direct_sheets_reader import DirectSheetsReader
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_pandas_types(obj):
    """轉換 pandas 數據類型為 Python 原生類型，以便 JSON 序列化"""
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict('records')
    elif isinstance(obj, pd.Series):
        return obj.to_dict()
    elif isinstance(obj, dict):
        return {key: convert_pandas_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_pandas_types(item) for item in obj]
    else:
        return obj

app = Flask(__name__)

# 全域變數
calculator = ChickenSettlementCalculator(CHICKEN_PRODUCTS_CONFIG)
report_generator = ChickenReportGenerator("chicken_reports")
sheets_reader = DirectSheetsReader(GOOGLE_SHEETS_CONFIG['SHEET_ID'])

@app.route('/')
def index():
    """首頁"""
    return render_template('chicken_index.html')

@app.route('/api/real_data')
def get_real_data():
    """取得真實 Google Sheet 資料"""
    try:
        # 取得日期參數
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 讀取真實的 Google Sheet 資料，使用最新價格設定
        import json
        with open('chicken_prices.json', 'r', encoding='utf-8') as f:
            prices = json.load(f)
        
        # 讀取主要資料
        main_data = sheets_reader.read_sheet_as_csv('0')
        
        # 使用最新價格轉換資料
        df = sheets_reader._convert_to_chicken_sales_format_with_prices(main_data, prices)
        
        if df.empty:
            return jsonify({
                'success': False, 
                'error': '沒有找到炸雞銷售資料，請檢查 Google Sheet 中是否有炸雞品項的銷售記錄'
            })
        
        # 根據日期篩選資料
        if start_date and end_date:
            df['日期'] = pd.to_datetime(df['日期'])
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            df = df[(df['日期'] >= start_date) & (df['日期'] <= end_date)]
            logger.info(f"根據日期篩選資料: {start_date.date()} 到 {end_date.date()}")
        else:
            # 如果沒有提供日期參數，使用預設的最近一週
            df['日期'] = pd.to_datetime(df['日期'])
            today = pd.Timestamp.now()
            one_week_ago = today - pd.Timedelta(days=7)
            df = df[(df['日期'] >= one_week_ago) & (df['日期'] <= today)]
            logger.info(f"使用預設日期篩選: {one_week_ago.date()} 到 {today.date()}")
        
        # 處理資料
        processed_df = calculator.process_chicken_sales_data(df)
        
        # 計算各種摘要
        daily_summary = calculator.calculate_daily_chicken_summary(processed_df)
        product_summary = calculator.calculate_chicken_product_summary(processed_df)
        settlement_info = calculator.calculate_chicken_settlement(processed_df)
        
        # 為每日摘要添加成本資訊
        if not daily_summary.empty and '成本小計' in processed_df.columns:
            daily_cost_summary = processed_df.groupby('日期').agg({
                '成本小計': 'sum'
            }).reset_index()
            daily_summary = daily_summary.merge(daily_cost_summary, on='日期', how='left')
            daily_summary['總成本'] = daily_summary['成本小計'].fillna(0)
        
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
        
        # 生成文字摘要
        text_summary = calculator.generate_text_settlement_summary(df, start_date, end_date)
        
        result = {
            'success': True,
            'data': {
                'daily_summary': daily_summary_dict,
                'product_summary': product_summary_dict,
                'settlement_info': settlement_info_dict,
                'raw_data': raw_data_dict,
                '文字摘要': text_summary
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
        # 取得日期參數
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 建立測試資料（使用當前日期範圍）
        from datetime import datetime, timedelta
        today = datetime.now()
        test_dates = []
        for i in range(7):  # 最近7天
            date = today - timedelta(days=i)
            test_dates.append(date.strftime('%Y-%m-%d'))
        
        # 確保所有陣列長度一致
        items = ['雞排', '雞翅', '雞腿', '雞排', '雞塊', '雞米花', '雞排', '雞柳條', '雞排', '雞翅']
        quantities = [10, 5, 3, 8, 4, 6, 12, 2, 15, 7]
        prices = [65, 25, 55, 65, 40, 35, 65, 45, 65, 25]
        amounts = [650, 125, 165, 520, 160, 210, 780, 90, 975, 175]
        
        # 重複資料以匹配日期長度
        all_dates = test_dates + test_dates[:3]  # 10個日期
        all_items = items
        all_quantities = quantities
        all_prices = prices
        all_amounts = amounts
        
        test_data = {
            '日期': all_dates,
            '品項': all_items,
            '數量': all_quantities,
            '單價': all_prices,
            '小計': all_amounts
        }
        
        df = pd.DataFrame(test_data)
        df['日期'] = pd.to_datetime(df['日期'])
        
        # 根據日期篩選資料
        if start_date and end_date:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            df = df[(df['日期'] >= start_date) & (df['日期'] <= end_date)]
            logger.info(f"測試資料根據日期篩選: {start_date.date()} 到 {end_date.date()}")
        else:
            # 如果沒有提供日期參數，使用預設的最近一週
            today = pd.Timestamp.now()
            one_week_ago = today - pd.Timedelta(days=7)
            df = df[(df['日期'] >= one_week_ago) & (df['日期'] <= today)]
            logger.info(f"測試資料使用預設日期篩選: {one_week_ago.date()} 到 {today.date()}")
        
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
        
        # 讀取真實資料
        df = sheets_reader.read_chicken_sales_data()
        settlement_report = calculator.generate_chicken_settlement_report(df, start_date, end_date)
        
        # 生成 Excel 報告
        excel_file = report_generator.generate_excel_report(settlement_report)
        
        # 轉換所有數據類型以確保 JSON 序列化成功
        report_data = convert_pandas_types(settlement_report)
        
        return jsonify({
            'success': True,
            'message': '炸雞對帳報告生成成功',
            'excel_file': excel_file,
            'report_data': {
                '期間': report_data['期間'],
                '總銷售金額': report_data['總銷售金額'],
                '總銷售數量': report_data['總銷售數量'],
                '炸雞老闆應付金額': report_data['炸雞老闆應付金額'],
                '成本比例': report_data['成本比例'],
                '利潤': report_data['利潤']
            }
        })
        
    except Exception as error:
        logger.error(f"生成報告時發生錯誤: {error}")
        return jsonify({'success': False, 'error': str(error)})

@app.route('/api/current_prices')
def get_current_prices():
    """取得目前價格設定"""
    try:
        from persistent_price_config import get_chicken_prices
        prices = get_chicken_prices()
        return jsonify({'success': True, 'prices': prices})
    except Exception as error:
        logger.error(f"取得目前價格時發生錯誤: {error}")
        return jsonify({'success': False, 'error': str(error)})

@app.route('/api/update_price', methods=['POST'])
def update_price():
    """更新價格設定"""
    try:
        data = request.json
        item = data['item']
        cost = float(data['cost'])
        price = float(data['price'])
        
        from persistent_price_config import update_chicken_prices
        update_chicken_prices(item, cost, price)
        
        return jsonify({'success': True, 'message': f'{item} 價格已更新'})
    except Exception as error:
        logger.error(f"更新價格時發生錯誤: {error}")
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
    
    print("🍗 啟動簡化版炸雞對帳系統網頁介面...")
    print("📱 請在瀏覽器中開啟: http://localhost:8082")
    print("⏹️  按 Ctrl+C 停止服務")
    
    app.run(debug=True, host='0.0.0.0', port=8082)
