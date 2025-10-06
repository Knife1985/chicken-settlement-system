<?php
header('Content-Type: text/html; charset=UTF-8');
?>
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🍗 雞排結帳系統 - PHP 測試</title>
    <style>
        body {
            font-family: 'Microsoft JhengHei', Arial, sans-serif;
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
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #ff6b6b, #ffa500);
            color: white;
            padding: 30px;
            text-align: center;
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
        .btn {
            display: inline-block;
            padding: 12px 24px;
            background: #28a745;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 10px 5px;
            transition: all 0.3s;
        }
        .btn:hover {
            background: #1e7e34;
            transform: translateY(-2px);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🍗 雞排結帳系統</h1>
            <p>PHP 測試頁面 - 如果看到這個，表示 PHP 檔案可以正常顯示！</p>
        </div>
        <div class="content">
            <div class="status">
                <strong>✅ 系統狀態:</strong> PHP 檔案測試成功 |
                <strong>🌐 網域:</strong> giving-wine.com |
                <strong>⏱️ 時間:</strong> <?php echo date('Y-m-d H:i:s'); ?>
            </div>
            
            <h3>🚀 測試成功！</h3>
            <p>如果您能看到這個頁面正常顯示（不是 base64 編碼），表示：</p>
            <ul>
                <li>✅ PHP 檔案可以正常運行</li>
                <li>✅ 伺服器支援 PHP</li>
                <li>✅ 檔案上傳功能正常</li>
                <li>✅ 網址可以正常訪問</li>
            </ul>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="http://localhost:8082" target="_blank" class="btn">🚀 開啟完整系統</a>
            </div>
        </div>
    </div>
</body>
</html>
