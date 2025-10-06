<?php
/**
 * 雞排結帳系統 - PHP 代理
 * 用於在 A2 Hosting 上運行 Python Flask 應用程式
 */

// 設定錯誤報告
error_reporting(E_ALL);
ini_set('display_errors', 1);

// 設定時區
date_default_timezone_set('Asia/Taipei');

// 設定 Python 路徑
$python_path = '/usr/bin/python3';
$app_path = '/home/givingwi/simple_chicken_web.py';

// 檢查 Python 是否可用
if (!file_exists($python_path)) {
    die('Python 3 未安裝或路徑不正確');
}

// 檢查應用程式檔案是否存在
if (!file_exists($app_path)) {
    die('應用程式檔案不存在: ' . $app_path);
}

// 設定環境變數
putenv('FLASK_APP=simple_chicken_web.py');
putenv('FLASK_ENV=production');

// 處理請求
$request_uri = $_SERVER['REQUEST_URI'];
$request_method = $_SERVER['REQUEST_METHOD'];

// 如果是 API 請求，直接執行 Python 應用程式
if (strpos($request_uri, '/api/') !== false) {
    // 建立臨時檔案來傳遞請求資料
    $temp_file = tempnam(sys_get_temp_dir(), 'chicken_request');
    $request_data = [
        'method' => $request_method,
        'uri' => $request_uri,
        'get' => $_GET,
        'post' => $_POST,
        'headers' => getallheaders()
    ];
    file_put_contents($temp_file, json_encode($request_data));
    
    // 執行 Python 應用程式
    $command = "cd /home/givingwi && $python_path simple_chicken_web.py 2>&1";
    $output = shell_exec($command);
    
    // 清理臨時檔案
    unlink($temp_file);
    
    // 輸出結果
    echo $output;
    exit;
}

// 顯示主頁面
?>
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🍗 雞排結帳系統</title>
    <style>
        body {
            font-family: 'Microsoft JhengHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #ff6b6b, #ffa500);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
        }
        .content {
            padding: 30px;
        }
        .status {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 20px;
            margin: 20px 0;
        }
        .status h3 {
            color: #28a745;
            margin-top: 0;
        }
        .btn {
            display: inline-block;
            padding: 12px 24px;
            background: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 10px 5px;
            transition: background 0.3s;
        }
        .btn:hover {
            background: #0056b3;
        }
        .btn-success {
            background: #28a745;
        }
        .btn-success:hover {
            background: #1e7e34;
        }
        .info {
            background: #e7f3ff;
            border-left: 4px solid #007bff;
            padding: 15px;
            margin: 15px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍗 雞排結帳系統</h1>
            <p>自動化對帳管理系統</p>
        </div>
        
        <div class="content">
            <div class="status">
                <h3>✅ 系統狀態</h3>
                <p><strong>部署狀態:</strong> 已成功部署到 A2 Hosting</p>
                <p><strong>Python 版本:</strong> <?php echo shell_exec('python3 --version 2>&1'); ?></p>
                <p><strong>伺服器時間:</strong> <?php echo date('Y-m-d H:i:s'); ?></p>
                <p><strong>檔案路徑:</strong> <?php echo $app_path; ?></p>
            </div>
            
            <div class="info">
                <h4>📋 系統功能</h4>
                <ul>
                    <li>📊 炸雞銷售資料統計</li>
                    <li>💰 自動對帳計算</li>
                    <li>📄 Excel 報告生成</li>
                    <li>🏷️ 價格管理</li>
                    <li>📅 日期範圍查詢</li>
                </ul>
            </div>
            
            <div class="info">
                <h4>🔧 技術資訊</h4>
                <p><strong>後端:</strong> Python Flask</p>
                <p><strong>資料來源:</strong> Google Sheets</p>
                <p><strong>部署平台:</strong> A2 Hosting</p>
                <p><strong>網域:</strong> giving-wine.com</p>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="javascript:void(0)" onclick="testAPI()" class="btn btn-success">🧪 測試系統</a>
                <a href="javascript:void(0)" onclick="loadData()" class="btn">📊 載入資料</a>
                <a href="javascript:void(0)" onclick="generateReport()" class="btn">📄 生成報告</a>
            </div>
            
            <div id="result" style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; display: none;">
                <h4>📋 執行結果</h4>
                <pre id="result-content"></pre>
            </div>
        </div>
    </div>
    
    <script>
        function testAPI() {
            showResult('正在測試系統...');
            fetch('/api/test_data')
                .then(response => response.json())
                .then(data => {
                    showResult('測試成功！\n' + JSON.stringify(data, null, 2));
                })
                .catch(error => {
                    showResult('測試失敗：' + error.message);
                });
        }
        
        function loadData() {
            showResult('正在載入炸雞資料...');
            const today = new Date();
            const startDate = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
            const endDate = today;
            
            const startStr = startDate.toISOString().split('T')[0];
            const endStr = endDate.toISOString().split('T')[0];
            
            fetch(`/api/real_data?start_date=${startStr}&end_date=${endStr}`)
                .then(response => response.json())
                .then(data => {
                    showResult('資料載入成功！\n' + JSON.stringify(data, null, 2));
                })
                .catch(error => {
                    showResult('載入失敗：' + error.message);
                });
        }
        
        function generateReport() {
            showResult('正在生成對帳報告...');
            const today = new Date();
            const startDate = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
            const endDate = today;
            
            const startStr = startDate.toISOString().split('T')[0];
            const endStr = endDate.toISOString().split('T')[0];
            
            fetch('/api/generate_report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    start_date: startStr,
                    end_date: endStr
                })
            })
            .then(response => response.json())
            .then(data => {
                showResult('報告生成成功！\n' + JSON.stringify(data, null, 2));
            })
            .catch(error => {
                showResult('生成失敗：' + error.message);
            });
        }
        
        function showResult(content) {
            document.getElementById('result').style.display = 'block';
            document.getElementById('result-content').textContent = content;
        }
    </script>
</body>
</html>
