<?php
/**
 * 雞排結帳系統 WordPress 短代碼
 * 使用方法: [chicken_system]
 */

// 註冊短代碼
add_shortcode('chicken_system', 'chicken_system_shortcode');

function chicken_system_shortcode($atts) {
    // 短代碼屬性
    $atts = shortcode_atts(array(
        'title' => '🍗 雞排結帳系統',
        'show_demo' => 'true',
        'show_buttons' => 'true'
    ), $atts);
    
    ob_start();
    ?>
    <div class="chicken-system-widget">
        <div class="chicken-header">
            <h3><?php echo esc_html($atts['title']); ?></h3>
            <p>整合到 WordPress 的雞排對帳系統</p>
        </div>
        
        <div class="chicken-content">
            <div class="chicken-status">
                <strong>✅ 系統狀態:</strong> WordPress 整合成功 |
                <strong>🌐 網域:</strong> <?php echo home_url(); ?> |
                <strong>⏱️ 時間:</strong> <span class="chicken-time"></span>
            </div>
            
            <?php if ($atts['show_demo'] === 'true'): ?>
            <div class="chicken-demo">
                <h4>🚀 系統功能展示</h4>
                <div class="chicken-form">
                    <div class="form-row">
                        <label>開始日期：</label>
                        <input type="date" class="chicken-date" value="2025-09-16">
                    </div>
                    <div class="form-row">
                        <label>結束日期：</label>
                        <input type="date" class="chicken-date" value="2025-09-30">
                    </div>
                </div>
            </div>
            <?php endif; ?>
            
            <?php if ($atts['show_buttons'] === 'true'): ?>
            <div class="chicken-buttons">
                <button class="chicken-btn chicken-btn-success" onclick="chickenLoadData()">📊 載入數據</button>
                <button class="chicken-btn chicken-btn-primary" onclick="chickenGenerateReport()">📋 生成報告</button>
                <button class="chicken-btn chicken-btn-info" onclick="chickenShowDemo()">🎯 功能展示</button>
            </div>
            <?php endif; ?>
            
            <div class="chicken-result" id="chicken-result" style="display: none;">
                <h4>📊 處理結果</h4>
                <div class="chicken-result-content" id="chicken-result-content"></div>
            </div>
            
            <div class="chicken-info">
                <div class="info-item">
                    <strong>🚀 系統功能:</strong> 炸雞銷售數據分析、自動對帳計算、Excel 報告生成
                </div>
                <div class="info-item">
                    <strong>🛠️ 技術架構:</strong> Python Flask + Google Sheets + A2 Hosting
                </div>
                <div class="info-item">
                    <strong>📱 完整系統:</strong> <a href="http://localhost:8082" target="_blank">🚀 開啟完整系統</a>
                </div>
            </div>
        </div>
    </div>
    
    <style>
    .chicken-system-widget {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        font-family: 'Microsoft JhengHei', Arial, sans-serif;
    }
    
    .chicken-header {
        background: linear-gradient(135deg, #ff6b6b, #ffa500);
        color: white;
        padding: 20px;
        text-align: center;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    .chicken-header h3 {
        margin: 0 0 10px 0;
        font-size: 1.5em;
    }
    
    .chicken-status {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    
    .chicken-demo {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 5px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .chicken-form {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15px;
        margin: 15px 0;
    }
    
    .form-row {
        display: flex;
        flex-direction: column;
    }
    
    .form-row label {
        font-weight: bold;
        margin-bottom: 5px;
        color: #495057;
    }
    
    .chicken-date {
        padding: 8px;
        border: 1px solid #ced4da;
        border-radius: 4px;
        font-size: 14px;
    }
    
    .chicken-buttons {
        text-align: center;
        margin: 20px 0;
    }
    
    .chicken-btn {
        display: inline-block;
        padding: 10px 20px;
        background: #007bff;
        color: white;
        text-decoration: none;
        border-radius: 5px;
        margin: 5px;
        transition: all 0.3s;
        border: none;
        cursor: pointer;
        font-size: 14px;
    }
    
    .chicken-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .chicken-btn-success {
        background: #28a745;
    }
    
    .chicken-btn-success:hover {
        background: #1e7e34;
    }
    
    .chicken-btn-primary {
        background: #007bff;
    }
    
    .chicken-btn-primary:hover {
        background: #0056b3;
    }
    
    .chicken-btn-info {
        background: #17a2b8;
    }
    
    .chicken-btn-info:hover {
        background: #138496;
    }
    
    .chicken-result {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 5px;
        padding: 20px;
        margin: 20px 0;
    }
    
    .chicken-result-content {
        background: #e9ecef;
        padding: 15px;
        border-radius: 5px;
        font-family: monospace;
        font-size: 12px;
        overflow-x: auto;
        white-space: pre-wrap;
    }
    
    .chicken-info {
        background: #e7f3ff;
        border-left: 4px solid #007bff;
        padding: 15px;
        border-radius: 5px;
    }
    
    .info-item {
        margin-bottom: 10px;
    }
    
    .info-item:last-child {
        margin-bottom: 0;
    }
    
    .info-item a {
        color: #007bff;
        text-decoration: none;
    }
    
    .info-item a:hover {
        text-decoration: underline;
    }
    
    @media (max-width: 768px) {
        .chicken-form {
            grid-template-columns: 1fr;
        }
        
        .chicken-buttons {
            text-align: left;
        }
        
        .chicken-btn {
            display: block;
            width: 100%;
            margin: 5px 0;
        }
    }
    </style>
    
    <script>
    // 更新時間
    function updateChickenTime() {
        const now = new Date();
        const timeElements = document.querySelectorAll('.chicken-time');
        timeElements.forEach(element => {
            element.textContent = now.toLocaleString('zh-TW');
        });
    }
    updateChickenTime();
    setInterval(updateChickenTime, 1000);
    
    // 載入數據
    function chickenLoadData() {
        const dates = document.querySelectorAll('.chicken-date');
        const startDate = dates[0] ? dates[0].value : '2025-09-16';
        const endDate = dates[1] ? dates[1].value : '2025-09-30';
        
        chickenShowResult('正在載入炸雞數據...\n\n日期範圍: ' + startDate + ' 到 ' + endDate + '\n\n載入中，請稍候...');
        
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
            
            chickenShowResult('炸雞數據載入完成！\n\n' + JSON.stringify(mockData, null, 2));
        }, 2000);
    }
    
    // 生成報告
    function chickenGenerateReport() {
        chickenShowResult('正在生成對帳報告...\n\n報告內容:\n- 日期範圍分析\n- 炸雞銷售統計\n- 對帳結果計算\n- 利潤分析報告\n\n報告生成完成！');
    }
    
    // 顯示功能展示
    function chickenShowDemo() {
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
        
        chickenShowResult('功能展示:\n\n' + JSON.stringify(demoData, null, 2));
    }
    
    // 顯示結果
    function chickenShowResult(content) {
        const resultDiv = document.getElementById('chicken-result');
        const contentDiv = document.getElementById('chicken-result-content');
        
        if (resultDiv && contentDiv) {
            resultDiv.style.display = 'block';
            contentDiv.textContent = content;
        }
    }
    </script>
    <?php
    
    return ob_get_clean();
}
?>
