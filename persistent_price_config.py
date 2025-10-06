"""
持久化價格設定檔
將價格設定保存到 JSON 檔案中
"""
import json
import os
from typing import Dict

# 價格設定檔案路徑
PRICE_CONFIG_FILE = 'chicken_prices.json'

# 預設價格設定
DEFAULT_PRICES = {
    '雞排': {'cost': 80, 'price': 170},
    '地瓜': {'cost': 35, 'price': 75}, 
    '棒腿': {'cost': 80, 'price': 170},
    '雞翅': {'cost': 105, 'price': 180}
}

def load_prices() -> Dict[str, Dict[str, float]]:
    """
    從檔案載入價格設定
    
    Returns:
        Dict[str, Dict[str, float]]: 品項價格對應
    """
    if os.path.exists(PRICE_CONFIG_FILE):
        try:
            with open(PRICE_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            print("❌ 讀取價格設定檔案失敗，使用預設價格")
            return DEFAULT_PRICES.copy()
    else:
        print("📝 價格設定檔案不存在，使用預設價格")
        return DEFAULT_PRICES.copy()

def save_prices(prices: Dict[str, Dict[str, float]]) -> None:
    """
    儲存價格設定到檔案
    
    Args:
        prices (Dict[str, Dict[str, float]]): 品項價格對應
    """
    try:
        with open(PRICE_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(prices, f, ensure_ascii=False, indent=2)
        print("✅ 價格設定已儲存")
    except Exception as e:
        print(f"❌ 儲存價格設定失敗: {e}")

def get_chicken_prices() -> Dict[str, Dict[str, float]]:
    """
    取得炸雞品項價格設定
    
    Returns:
        Dict[str, Dict[str, float]]: 品項價格對應
    """
    return load_prices()

def update_chicken_prices(item_name: str, cost: float, price: float) -> None:
    """
    更新炸雞品項價格
    
    Args:
        item_name (str): 品項名稱
        cost (float): 成本
        price (float): 售價
    """
    prices = load_prices()
    prices[item_name] = {'cost': cost, 'price': price}
    save_prices(prices)

def print_current_prices() -> None:
    """顯示目前的價格設定"""
    prices = load_prices()
    print("🍗 目前炸雞品項價格設定：")
    print("=" * 50)
    for item, price_info in prices.items():
        print(f"{item}: 成本 ${price_info['cost']}, 售價 ${price_info['price']}")
    print()

def create_price_input_interface() -> None:
    """建立價格輸入介面"""
    print("🍗 炸雞品項價格設定介面")
    print("=" * 50)
    print("請輸入各品項的成本和售價（按 Enter 跳過不修改）")
    print()
    
    prices = load_prices()
    
    for item, price_info in prices.items():
        print(f"📝 {item} 目前設定：成本 ${price_info['cost']}, 售價 ${price_info['price']}")
        
        try:
            cost_input = input(f"請輸入 {item} 的新成本（目前：${price_info['cost']}）: ").strip()
            if cost_input:
                new_cost = float(cost_input)
                prices[item]['cost'] = new_cost
                
            price_input = input(f"請輸入 {item} 的新售價（目前：${price_info['price']}）: ").strip()
            if price_input:
                new_price = float(price_input)
                prices[item]['price'] = new_price
                
        except ValueError:
            print("❌ 輸入格式錯誤，保持原設定")
        
        print()
    
    # 儲存更新後的價格
    save_prices(prices)

if __name__ == "__main__":
    print_current_prices()
    create_price_input_interface()
    print("✅ 價格設定完成！")
    print_current_prices()


