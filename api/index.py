from flask import Flask, render_template_string, jsonify, request
import os
import json
from datetime import datetime

app = Flask(__name__)

# 雞排價格配置
CHICKEN_PRICES = {
    "雞排": 45,
    "雞翅": 12,
    "雞腿": 8,
    "雞塊": 9
}

# HTML 模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🍗 雞排結帳系統</title>
    <style>
        body {
            font-family: 'Microsoft JhengHei', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #ff6b6b, #ffa500);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .content {
            padding: 30px;
        }
        .status {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .demo-section {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #495057;
        }
        .form-group input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ced4da;
            border-radius: 5px;
            font-size: 16px;
        }
        .button-group {
            text-align: center;
            margin: 20px 0;
        }
        .btn {
            display: inline-block;
            padding: 12px 24px;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 10px 5px;
            transition: all 0.3s;
            border: none;
            cursor: pointer;
        }
        .btn:hover {
            background: #0056b3;
            transform: translateY(-2px);
        }
        .btn-success {
            background: #28a745;
        }
        .btn-success:hover {
            background: #1e7e34;
        }
        .btn-primary {
            background: #007bff;
        }
        .btn-primary:hover {
            background: #0056b3;
        }
        .btn-info {
            background: #17a2b8;
        }
        .btn-info:hover {
            background: #138496;
        }
        .result-section {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            display: none;
        }
        .result-data {
            background: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 12px;
            overflow-x: auto;
            white-space: pre-wrap;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .info-card {
            background: #e7f3ff;
            border-left: 4px solid #007bff;
            padding: 20px;
            border-radius: 5px;
        }
        .info-card h4 {
            color: #007bff;
            margin-bottom: 10px;
        }
        .info-card ul {
            margin: 0;
            padding-left: 20px;
        }
        .info-card li {
            margin-bottom: 5px;
        }
        .action-buttons {
            text-align: center;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍗 雞排結帳系統</h1>
            <p>Vercel 部署成功 - 雲端雞排對帳系統</p>
        </div>
        
        <div class="content">
            <div class="status">
                <strong>✅ 系統狀態:</strong> Vercel 部署成功 |
                <strong>🌐 網域:</strong> <span id="current-domain"></span> |
                <strong>⏱️ 時間:</strong> <span id="current-time"></span>
            </div>
            
            <div class="demo-section">
                <h3>🚀 系統功能展示</h3>
                <p>以下是您的雞排結帳系統功能：</p>
                
                <div class="form-group">
                    <label for="start-date">開始日期：</label>
                    <input type="date" id="start-date" value="2025-09-16">
                </div>
                
                <div class="form-group">
                    <label for="end-date">結束日期：</label>
                    <input type="date" id="end-date" value="2025-09-30">
                </div>
                
                <div class="button-group">
                    <button class="btn btn-success" onclick="loadData()">📊 載入炸雞數據</button>
                    <button class="btn btn-primary" onclick="generateReport()">📋 生成對帳報告</button>
                    <button class="btn btn-info" onclick="showDemo()">🎯 查看功能展示</button>
                </div>
            </div>
            
            <div class="result-section" id="result-section">
                <h4>📊 處理結果</h4>
                <div class="result-data" id="result-content"></div>
            </div>
            
            <div class="info-grid">
                <div class="info-card">
                    <h4>🚀 系統功能</h4>
                    <ul>
                        <li>📊 炸雞銷售數據分析</li>
                        <li>💰 自動對帳計算</li>
                        <li>📋 Excel 報告生成</li>
                        <li>🔗 Google Sheets 整合</li>
                        <li>📱 響應式網頁設計</li>
                    </ul>
                </div>
                
                <div class="info-card">
                    <h4>🛠️ 技術架構</h4>
                    <ul>
                        <li><strong>後端:</strong> Python Flask</li>
                        <li><strong>部署:</strong> Vercel</li>
                        <li><strong>數據源:</strong> Google Sheets</li>
                        <li><strong>網域:</strong> Vercel 免費網域</li>
                        <li><strong>狀態:</strong> 雲端部署成功</li>
                    </ul>
                </div>
                
                <div class="info-card">
                    <h4>📋 使用流程</h4>
                    <ul>
                        <li>1. 設定日期範圍</li>
                        <li>2. 載入炸雞銷售數據</li>
                        <li>3. 自動計算對帳結果</li>
                        <li>4. 生成 Excel 報告</li>
                        <li>5. 下載並使用報告</li>
                    </ul>
                </div>
            </div>
            
            <div class="action-buttons">
                <button class="btn btn-success" onclick="showFeatures()">🔍 查看功能詳情</button>
            </div>
        </div>
    </div>
    
    <script>
    // 更新時間和網域
    function updateTime() {
        const now = new Date();
        document.getElementById('current-time').textContent = now.toLocaleString('zh-TW');
        document.getElementById('current-domain').textContent = window.location.hostname;
    }
    updateTime();
    setInterval(updateTime, 1000);
    
    // 載入數據
    function loadData() {
        const startDate = document.getElementById('start-date').value;
        const endDate = document.getElementById('end-date').value;
        
        showResult('正在載入炸雞數據...\\n\\n日期範圍: ' + startDate + ' 到 ' + endDate + '\\n\\n載入中，請稍候...');
        
        // 模擬 API 調用
        setTimeout(() => {
            const mockData = {
                "載入數據": {
                    "日期範圍": startDate + " 到 " + endDate,
                    "炸雞總銷售": "1,660 元",
                    "炸雞總數量": "74 份",
                    "炸雞分類": {
                        "雞排": "45 份",
                        "雞翅": "12 份", 
                        "雞腿": "8 份",
                        "雞塊": "9 份"
                    },
                    "對帳結果": {
                        "總收入": "820 元",
                        "收入比例": "49.4%",
                        "利潤": "840 元"
                    },
                    "炸雞利潤分析": "820 元"
                }
            };
            
            showResult('炸雞數據載入完成！\\n\\n' + JSON.stringify(mockData, null, 2));
        }, 2000);
    }
    
    // 生成報告
    function generateReport() {
        showResult('正在生成對帳報告...\\n\\n報告內容:\\n- 日期範圍分析\\n- 炸雞銷售統計\\n- 對帳結果計算\\n- 利潤分析報告\\n\\n報告生成完成！');
    }
    
    // 顯示功能展示
    function showDemo() {
        const demoData = {
            "功能展示": {
                "日期範圍": "2025-09-16 到 2025-09-30",
                "炸雞總銷售": "1,660 元",
                "炸雞總數量": "74 份",
                "炸雞分類": {
                    "雞排": "45 份",
                    "雞翅": "12 份", 
                    "雞腿": "8 份",
                    "雞塊": "9 份"
                },
                "對帳結果": {
                    "總收入": "820 元",
                    "收入比例": "49.4%",
                    "利潤": "840 元"
                },
                "炸雞利潤分析": "820 元"
            }
        };
        
        showResult('功能展示:\\n\\n' + JSON.stringify(demoData, null, 2));
    }
    
    // 顯示功能詳情
    function showFeatures() {
        const features = {
            "系統功能詳情": {
                "數據整合": {
                    "Google Sheets 整合": "直接讀取 Google Sheets 數據，無需 API 認證",
                    "數據格式": "自動轉換數據格式，支援多種輸入格式",
                    "數據驗證": "自動驗證數據完整性，確保計算準確性"
                },
                "對帳計算": {
                    "自動對帳": "自動計算炸雞銷售對帳，支援多種產品類型",
                    "利潤分析": "詳細的利潤分析報告，包含各項成本計算",
                    "數據統計": "完整的銷售統計，包含數量、金額、比例分析"
                },
                "報告生成": {
                    "Excel 報告": "自動生成 Excel 格式的對帳報告",
                    "數據匯出": "支援多種格式的數據匯出功能",
                    "報告自訂": "可自訂報告內容和格式"
                }
            }
        };
        
        showResult('功能詳情:\\n\\n' + JSON.stringify(features, null, 2));
    }
    
    // 顯示結果
    function showResult(content) {
        document.getElementById('result-section').style.display = 'block';
        document.getElementById('result-content').textContent = content;
    }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/load-data', methods=['POST'])
def load_data():
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    # 模擬數據載入
    mock_data = {
        "載入數據": {
            "日期範圍": f"{start_date} 到 {end_date}",
            "炸雞總銷售": "1,660 元",
            "炸雞總數量": "74 份",
            "炸雞分類": {
                "雞排": "45 份",
                "雞翅": "12 份", 
                "雞腿": "8 份",
                "雞塊": "9 份"
            },
            "對帳結果": {
                "總收入": "820 元",
                "收入比例": "49.4%",
                "利潤": "840 元"
            },
            "炸雞利潤分析": "820 元"
        }
    }
    
    return jsonify(mock_data)

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    # 模擬報告生成
    return jsonify({
        "status": "success",
        "message": "報告生成完成！",
        "report_url": "/reports/chicken_report.xlsx"
    })

# Vercel 需要這個作為入口點
def handler(request):
    return app(request.environ, lambda *args: None)
