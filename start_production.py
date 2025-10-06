#!/usr/bin/env python3
"""
生產環境啟動腳本
用於 A2 Hosting 部署
"""
import os
import sys
from simple_chicken_web import app

if __name__ == '__main__':
    # 確保必要目錄存在
    if not os.path.exists('chicken_reports'):
        os.makedirs('chicken_reports')
    
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # 設定生產環境
    app.config['DEBUG'] = False
    app.config['TESTING'] = False
    
    print("🍗 雞排結帳系統 - 生產環境")
    print("=" * 50)
    print("✅ 系統已啟動")
    print("📱 請在瀏覽器中開啟您的網站")
    print("⏹️  按 Ctrl+C 停止服務")
    print("=" * 50)
    
    # 啟動應用程式
    app.run(host='0.0.0.0', port=5000, debug=False)
