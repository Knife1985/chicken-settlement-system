#!/bin/bash
# 雞排結帳系統 - A2 Hosting 部署腳本

echo "🍗 雞排結帳系統部署腳本"
echo "================================"

# 設定變數
DOMAIN="giving-wine.com"
USERNAME="givingwi"
DEPLOY_DIR="/home/givingwi/public_html/chicken_system"

echo "📋 部署資訊："
echo "   網域: $DOMAIN"
echo "   使用者: $USERNAME"
echo "   部署目錄: $DEPLOY_DIR"
echo ""

# 建立部署目錄
echo "📁 建立部署目錄..."
mkdir -p $DEPLOY_DIR
mkdir -p $DEPLOY_DIR/chicken_reports
mkdir -p $DEPLOY_DIR/templates

# 設定權限
echo "🔐 設定檔案權限..."
chmod 755 $DEPLOY_DIR
chmod 755 $DEPLOY_DIR/chicken_reports
chmod 644 $DEPLOY_DIR/*.py
chmod 644 $DEPLOY_DIR/*.json
chmod 644 $DEPLOY_DIR/*.txt
chmod 644 $DEPLOY_DIR/.htaccess

# 設定 Python 環境
echo "🐍 設定 Python 環境..."
cd $DEPLOY_DIR

# 檢查 Python 版本
python3 --version

# 安裝套件
echo "📦 安裝 Python 套件..."
pip3 install --user -r requirements.txt

echo "✅ 部署完成！"
echo ""
echo "🌐 系統網址: https://$DOMAIN/chicken_system/"
echo "📱 請在瀏覽器中測試系統功能"
echo ""
echo "🔧 如果遇到問題，請檢查："
echo "   1. Python 版本是否為 3.8+"
echo "   2. 所有套件是否正確安裝"
echo "   3. 檔案權限是否正確"
echo "   4. Google Sheets 設定是否正確"
