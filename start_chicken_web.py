#!/usr/bin/env python3
"""
炸雞對帳系統網頁啟動腳本
"""
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def main():
    """主函數"""
    print("🍗 炸雞對帳系統")
    print("=" * 50)
    print()
    
    # 檢查必要檔案
    required_files = [
        'chicken_web_interface.py',
        'templates/chicken_index.html',
        'chicken_settlement_calculator.py',
        'chicken_report_generator.py',
        'chicken_config.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ 缺少必要檔案：")
        for file in missing_files:
            print(f"   - {file}")
        print()
        print("請確保所有檔案都存在後再執行此腳本")
        return
    
    print("✅ 所有必要檔案都存在")
    print()
    
    # 啟動網頁服務
    print("🌐 正在啟動炸雞對帳網頁服務...")
    print("📱 網頁地址: http://localhost:8081")
    print("⏹️  按 Ctrl+C 停止服務")
    print()
    
    try:
        # 啟動網頁服務
        process = subprocess.Popen([sys.executable, 'chicken_web_interface.py'])
        
        # 等待一下讓服務啟動
        time.sleep(3)
        
        # 自動開啟瀏覽器
        print("🚀 正在開啟瀏覽器...")
        webbrowser.open('http://localhost:8081')
        
        print("✅ 炸雞對帳網頁服務已啟動！")
        print("💡 如果瀏覽器沒有自動開啟，請手動前往: http://localhost:8081")
        print()
        print("📋 使用說明：")
        print("1. 在網頁中選擇日期範圍")
        print("2. 點擊「載入炸雞資料」查看炸雞銷售統計")
        print("3. 點擊「生成對帳報告」建立炸雞對帳報告")
        print("4. 查看「炸雞老闆應付金額」")
        print("5. 點擊「下載報告」下載 Excel 檔案")
        print()
        
        # 等待用戶中斷
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n⏹️  正在停止服務...")
            process.terminate()
            process.wait()
            print("✅ 服務已停止")
            
    except Exception as error:
        print(f"❌ 啟動失敗: {error}")
        return

if __name__ == "__main__":
    main()



