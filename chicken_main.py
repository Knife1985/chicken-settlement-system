"""
炸雞對帳系統主程式
專門處理炸雞品項的對帳功能
"""
import argparse
import logging
import sys
import pandas as pd
from datetime import datetime, timedelta
from chicken_sheets_client import ChickenSheetsClient
from chicken_settlement_calculator import ChickenSettlementCalculator
from chicken_report_generator import ChickenReportGenerator
from chicken_config import (
    GOOGLE_SHEETS_CONFIG, 
    CHICKEN_PRODUCTS_CONFIG, 
    LOGGING_CONFIG
)

# 設定日誌
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['LEVEL']),
    format=LOGGING_CONFIG['FORMAT'],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG['FILE'], encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """主程式入口"""
    parser = argparse.ArgumentParser(description='🍗 炸雞對帳系統')
    parser.add_argument('--mode', choices=['manual', 'test'], default='manual',
                       help='執行模式: manual=手動執行, test=測試模式')
    parser.add_argument('--start-date', type=str, help='開始日期 (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='結束日期 (YYYY-MM-DD)')
    parser.add_argument('--days', type=int, default=14, help='結算天數 (預設14天)')
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'test':
            # 測試模式
            print("🍗 執行炸雞對帳測試模式...")
            test_chicken_settlement()
            
        elif args.mode == 'manual':
            # 手動執行模式
            print("🍗 執行手動炸雞對帳...")
            
            # 建立 Google Sheets 客戶端
            print("正在連接 Google Sheets...")
            sheets_client = ChickenSheetsClient(
                credentials_file=GOOGLE_SHEETS_CONFIG['CREDENTIALS_FILE'],
                token_file=GOOGLE_SHEETS_CONFIG['TOKEN_FILE'],
                sheet_id=GOOGLE_SHEETS_CONFIG['SHEET_ID']
            )
            
            # 取得炸雞品項價格
            chicken_prices = sheets_client.get_chicken_prices()
            print(f"✅ 成功載入 {len(chicken_prices)} 個炸雞品項價格")
            
            # 建立計算器和報告生成器
            calculator = ChickenSettlementCalculator(chicken_prices)
            report_generator = ChickenReportGenerator()
            
            # 計算日期範圍
            if args.start_date and args.end_date:
                start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
                end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
            elif args.start_date:
                start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
                end_date = start_date + timedelta(days=args.days - 1)
            else:
                # 使用預設日期（最近兩週）
                end_date = datetime.now()
                start_date = end_date - timedelta(days=args.days)
            
            print(f"對帳期間: {start_date.date()} 至 {end_date.date()}")
            
            # 讀取炸雞銷售資料
            print("正在讀取炸雞銷售資料...")
            chicken_df = sheets_client.get_chicken_sales_data()
            
            if chicken_df.empty:
                print("❌ 沒有讀取到任何炸雞銷售資料")
                print("請檢查 Google Sheet 中是否有炸雞品項的銷售記錄")
                return
            
            print(f"✅ 成功讀取 {len(chicken_df)} 筆炸雞銷售資料")
            
            # 生成對帳報告
            print("正在生成炸雞對帳報告...")
            settlement_report = calculator.generate_chicken_settlement_report(
                chicken_df, start_date, end_date
            )
            
            # 生成報告檔案
            print("正在生成報告檔案...")
            excel_file = report_generator.generate_excel_report(settlement_report)
            text_report = report_generator.generate_text_report(settlement_report)
            
            # 顯示結果
            print("\n" + "="*60)
            print("🍗 炸雞對帳執行成功！")
            print("="*60)
            print(f"📊 總銷售金額: ${settlement_report['總銷售金額']:,}")
            print(f"🍗 總銷售數量: {settlement_report['總銷售數量']:,} 份")
            print(f"📋 總訂單數: {settlement_report['總訂單數']:,} 筆")
            print(f"🏷️  品項種類: {settlement_report['品項種類']} 種")
            print(f"💰 平均單價: ${settlement_report['平均單價']:.2f}")
            print("")
            print("🍗 炸雞老闆對帳明細:")
            print(f"   應付金額: ${settlement_report['炸雞老闆應付金額']:,}")
            print(f"   成本比例: {settlement_report['成本比例']*100:.1f}%")
            print(f"   利潤: ${settlement_report['利潤']:,}")
            print("")
            print(f"📄 Excel 報告: {excel_file}")
            print("="*60)
            
    except KeyboardInterrupt:
        print("\n程式被使用者中斷")
        sys.exit(0)
    except Exception as error:
        logger.error(f"程式執行時發生錯誤: {error}")
        print(f"❌ 程式執行失敗: {error}")
        sys.exit(1)

def test_chicken_settlement():
    """測試炸雞對帳系統功能"""
    try:
        print("🧪 測試炸雞對帳系統...")
        
        # 建立測試資料
        test_data = {
            '日期': [
                '2025-04-29', '2025-04-29', '2025-04-30', '2025-04-30', '2025-05-01',
                '2025-05-01', '2025-05-02', '2025-05-02', '2025-05-03', '2025-05-03'
            ],
            '品項': [
                '雞排', '雞翅', '雞排', '雞腿', '雞排',
                '雞塊', '雞排', '雞米花', '雞排', '雞柳條'
            ],
            '數量': [10, 5, 8, 3, 12, 4, 15, 6, 9, 2],
            '單價': [65, 25, 65, 55, 65, 40, 65, 35, 65, 45],
            '小計': [650, 125, 520, 165, 780, 160, 975, 210, 585, 90]
        }
        
        df = pd.DataFrame(test_data)
        df['日期'] = pd.to_datetime(df['日期'])
        
        print(f"✅ 測試資料建立完成，共 {len(df)} 筆資料")
        
        # 建立計算器
        calculator = ChickenSettlementCalculator(CHICKEN_PRODUCTS_CONFIG)
        
        # 處理資料
        processed_df = calculator.process_chicken_sales_data(df)
        print(f"✅ 資料處理完成，有效資料 {len(processed_df)} 筆")
        
        # 計算對帳報告
        start_date = datetime(2025, 4, 29)
        end_date = datetime(2025, 5, 3)
        
        settlement_report = calculator.generate_chicken_settlement_report(
            df, start_date, end_date
        )
        
        print(f"✅ 對帳報告生成完成")
        print(f"📊 總銷售金額: ${settlement_report['總銷售金額']:,}")
        print(f"🍗 總銷售數量: {settlement_report['總銷售數量']:,} 份")
        print(f"💰 炸雞老闆應付金額: ${settlement_report['炸雞老闆應付金額']:,}")
        print(f"💵 利潤: ${settlement_report['利潤']:,}")
        
        # 測試報告生成
        print("\n測試報告生成...")
        report_generator = ChickenReportGenerator("test_chicken_reports")
        
        excel_file = report_generator.generate_excel_report(settlement_report, "test_chicken_settlement.xlsx")
        print(f"✅ Excel 報告已生成: {excel_file}")
        
        text_report = report_generator.generate_text_report(settlement_report)
        print("\n📄 文字報告內容：")
        print(text_report)
        
        print("\n✅ 測試完成！")
        
    except Exception as error:
        print(f"❌ 測試失敗: {error}")
        logger.error(f"測試時發生錯誤: {error}")

if __name__ == "__main__":
    main()
