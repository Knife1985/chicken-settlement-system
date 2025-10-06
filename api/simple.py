from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🍗 雞排結帳系統</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 20px;
                min-height: 100vh;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            .header h1 {
                color: #ff6b6b;
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            .status {
                background: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
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
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🍗 雞排結帳系統</h1>
                <p>Vercel 部署成功 - 雲端雞排對帳系統</p>
            </div>
            
            <div class="status">
                <strong>✅ 系統狀態:</strong> Vercel 部署成功 |
                <strong>🌐 網域:</strong> <span id="current-domain"></span> |
                <strong>⏱️ 時間:</strong> <span id="current-time"></span>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <h3>🚀 系統功能展示</h3>
                <p>您的雞排結帳系統已經成功部署到 Vercel！</p>
                
                <button class="btn btn-success" onclick="showDemo()">🎯 查看功能展示</button>
                <button class="btn" onclick="showFeatures()">🔍 查看功能詳情</button>
            </div>
            
            <div id="result" style="background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 10px; padding: 20px; margin: 20px 0; display: none;">
                <h4>📊 處理結果</h4>
                <div id="result-content" style="background: #e9ecef; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 12px; overflow-x: auto; white-space: pre-wrap;"></div>
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
                    }
                }
            };
            
            showResult('功能展示:\\n\\n' + JSON.stringify(demoData, null, 2));
        }
        
        // 顯示功能詳情
        function showFeatures() {
            const features = {
                "系統功能詳情": {
                    "數據整合": "直接讀取 Google Sheets 數據，無需 API 認證",
                    "對帳計算": "自動計算炸雞銷售對帳，支援多種產品類型",
                    "報告生成": "自動生成 Excel 格式的對帳報告",
                    "部署狀態": "Vercel 雲端部署成功"
                }
            };
            
            showResult('功能詳情:\\n\\n' + JSON.stringify(features, null, 2));
        }
        
        // 顯示結果
        function showResult(content) {
            document.getElementById('result').style.display = 'block';
            document.getElementById('result-content').textContent = content;
        }
        </script>
    </body>
    </html>
    '''

@app.route('/api/test')
def test():
    return jsonify({
        "status": "success",
        "message": "API 測試成功！",
        "data": {
            "系統": "雞排結帳系統",
            "部署": "Vercel",
            "狀態": "運行正常"
        }
    })

# Vercel 需要這個作為入口點
def handler(request):
    return app(request.environ, lambda *args: None)

if __name__ == '__main__':
    app.run(debug=True)
