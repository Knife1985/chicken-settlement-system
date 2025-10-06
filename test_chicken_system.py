"""
炸雞對帳系統測試工具
不需要 Google API 認證的測試工具
"""
import pandas as pd
from datetime import datetime, timedelta
from chicken_settlement_calculator import ChickenSettlementCalculator
from chicken_report_generator import ChickenReportGenerator
from chicken_config import CHICKEN_PRODUCTS_CONFIG, GOOGLE_SHEETS_CONFIG

def create_sample_chicken_data():
    """建立範例炸雞銷售資料來測試系統"""
    print("🍗 建立範例炸雞銷售資料...")
    
    # 建立範例資料
    sample_data = {
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
    
    df = pd.DataFrame(sample_data)
    df['日期'] = pd.to_datetime(df['日期'])
    
    print(f"✅ 範例資料建立完成，共 {len(df)} 筆資料")
    print()
    
    # 顯示資料預覽
    print("📋 資料預覽：")
    print(df.head(10))
    print()
    
    return df

def test_chicken_calculator(df):
    """測試炸雞計算器功能"""
    print("🧮 測試炸雞對帳計算器...")
    
    # 建立計算器
    calculator = ChickenSettlementCalculator(CHICKEN_PRODUCTS_CONFIG)
    
    # 處理資料
    processed_df = calculator.process_chicken_sales_data(df)
    print(f"✅ 資料處理完成，有效資料 {len(processed_df)} 筆")
    print()
    
    # 顯示處理後的資料
    print("📊 處理後的資料預覽：")
    print(processed_df.head())
    print()
    
    # 計算品項摘要
    product_summary = calculator.calculate_chicken_product_summary(processed_df)
    print("🍗 炸雞品項銷售摘要：")
    print(product_summary)
    print()
    
    # 計算每日摘要
    daily_summary = calculator.calculate_daily_chicken_summary(processed_df)
    print("📅 每日炸雞銷售摘要：")
    print(daily_summary.head())
    print()
    
    # 計算對帳資訊
    settlement_info = calculator.calculate_chicken_settlement(processed_df)
    print("💰 炸雞對帳資訊：")
    for key, value in settlement_info.items():
        print(f"  {key}: {value}")
    print()
    
    return processed_df, product_summary, daily_summary, settlement_info

def test_report_generator(processed_df, product_summary, daily_summary, settlement_info):
    """測試報告生成器"""
    print("📄 測試炸雞對帳報告生成器...")
    
    # 建立報告生成器
    report_generator = ChickenReportGenerator("test_chicken_reports")
    
    # 建立測試報告資料
    start_date = datetime(2025, 4, 29)
    end_date = datetime(2025, 5, 7)
    
    settlement_report = {
        '期間': f"{start_date.date()} 至 {end_date.date()}",
        '總銷售金額': settlement_info['總銷售金額'],
        '總銷售數量': settlement_info['總銷售數量'],
        '總訂單數': settlement_info['總訂單數'],
        '品項種類': settlement_info['品項種類'],
        '平均單價': settlement_info['平均單價'],
        '炸雞老闆應付金額': settlement_info['炸雞老闆應付金額'],
        '成本比例': settlement_info['成本比例'],
        '利潤': settlement_info['利潤'],
        '品項摘要': product_summary,
        '每日摘要': daily_summary,
        '詳細資料': processed_df
    }
    
    # 生成文字報告
    print("📝 生成文字報告...")
    text_report = report_generator.generate_text_report(settlement_report)
    print("文字報告內容：")
    print(text_report)
    print()
    
    # 生成 Excel 報告
    print("📊 生成 Excel 報告...")
    try:
        excel_file = report_generator.generate_excel_report(settlement_report, "test_chicken_settlement_report.xlsx")
        print(f"✅ Excel 報告已生成: {excel_file}")
    except Exception as error:
        print(f"❌ Excel 報告生成失敗: {error}")
    
    print()

def show_expected_format():
    """顯示期望的 Google Sheet 格式"""
    print("📋 您的 Google Sheet 應該包含的炸雞品項欄位：")
    print("=" * 60)
    print()
    print("根據您的 Google Sheet，系統會從以下欄位讀取炸雞銷售資料：")
    print()
    print("| 欄位名稱 | 品項 | 說明 |")
    print("|----------|------|------|")
    print("| 炸物的訂購_雞排 | 雞排 | 雞排訂購數量 |")
    print("| 炸物的訂購_地瓜 | 地瓜 | 地瓜訂購數量 |")
    print("| 炸物的訂購_棒腿 | 棒腿 | 棒腿訂購數量 |")
    print("| 炸物的訂購_雞翅 | 雞翅 | 雞翅訂購數量 |")
    print()
    print("📝 系統功能：")
    print("• 自動從 Google Sheet 讀取炸雞品項銷售數量")
    print("• 從「設定」工作表讀取炸雞品項價格")
    print("• 計算各品項的銷售金額和總計")
    print("• 計算需要付給炸雞老闆的金額")
    print("• 生成詳細的對帳報告")
    print()
    print("⚙️ 系統設定：")
    print(f"• Google Sheet ID: {GOOGLE_SHEETS_CONFIG['SHEET_ID']}")
    print(f"• 主要資料工作表: {GOOGLE_SHEETS_CONFIG['MAIN_SHEET_NAME']}")
    print(f"• 設定工作表: {GOOGLE_SHEETS_CONFIG['SETTINGS_SHEET_NAME']}")
    print(f"• 炸雞品項價格: {CHICKEN_PRODUCTS_CONFIG}")
    print()

def main():
    """主函數"""
    print("🧪 炸雞對帳系統測試工具")
    print("=" * 60)
    print()
    
    # 顯示期望格式
    show_expected_format()
    
    # 建立範例資料
    df = create_sample_chicken_data()
    
    # 測試計算器
    processed_df, product_summary, daily_summary, settlement_info = test_chicken_calculator(df)
    
    # 測試報告生成器
    test_report_generator(processed_df, product_summary, daily_summary, settlement_info)
    
    print("✅ 測試完成！")
    print()
    print("💡 下一步：")
    print("1. 確認您的 Google Sheet 中有炸雞品項的銷售欄位")
    print("2. 在「設定」工作表中設定炸雞品項價格")
    print("3. 下載 credentials.json 檔案到專案目錄")
    print("4. 執行 python chicken_main.py --mode test 測試實際資料")
    print("5. 執行 python chicken_main.py --mode manual 進行實際對帳")

if __name__ == "__main__":
    main()
