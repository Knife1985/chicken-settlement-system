#!/usr/bin/env python3
"""
WSGI 應用程式入口點
用於 A2 Hosting 部署
"""
import sys
import os

# 添加專案目錄到 Python 路徑
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# 設定環境變數
os.environ.setdefault('FLASK_APP', 'simple_chicken_web.py')
os.environ.setdefault('FLASK_ENV', 'production')

# 導入應用程式
from simple_chicken_web import app

# WSGI 應用程式物件
application = app

if __name__ == "__main__":
    application.run()
