"""
手動價格設定檔
讓您可以手動設定炸雞品項的成本和售價
"""
import pandas as pd
from datetime import datetime
from typing import Dict

# 手動設定的炸雞品項價格
# 格式：{品項名稱: {'cost': 成本, 'price': 售價}}
MANUAL_CHICKEN_PRICES = {
    '雞排': {'cost': 80, 'price': 170},
    '地瓜': {'cost': 35, 'price': 75}, 
    '棒腿': {'cost': 80, 'price': 170},
    '雞翅': {'cost': 105, 'price': 180}
}

def get_chicken_prices() -> Dict[str, Dict[str, float]]:
    """
    取得炸雞品項價格設定
    
    Returns:
        Dict[str, Dict[str, float]]: 品項價格對應
    """
    return MANUAL_CHICKEN_PRICES.copy()

def update_chicken_prices(item_name: str, cost: float, price: float) -> None:
    """
    更新炸雞品項價格
    
    Args:
        item_name (str): 品項名稱
        cost (float): 成本
        price (float): 售價
    """
    MANUAL_CHICKEN_PRICES[item_name] = {'cost': cost, 'price': price}

def print_current_prices() -> None:
    """顯示目前的價格設定"""
    print("🍗 目前炸雞品項價格設定：")
    print("=" * 50)
    for item, prices in MANUAL_CHICKEN_PRICES.items():
        print(f"{item}: 成本 ${prices['cost']}, 售價 ${prices['price']}")
    print()

def create_price_input_interface() -> None:
    """建立價格輸入介面"""
    print("🍗 炸雞品項價格設定介面")
    print("=" * 50)
    print("請輸入各品項的成本和售價（按 Enter 跳過不修改）")
    print()
    
    for item, prices in MANUAL_CHICKEN_PRICES.items():
        print(f"📝 {item} 目前設定：成本 ${prices['cost']}, 售價 ${prices['price']}")
        
        try:
            cost_input = input(f"請輸入 {item} 的新成本（目前：${prices['cost']}）: ").strip()
            if cost_input:
                new_cost = float(cost_input)
                MANUAL_CHICKEN_PRICES[item]['cost'] = new_cost
                
            price_input = input(f"請輸入 {item} 的新售價（目前：${prices['price']}）: ").strip()
            if price_input:
                new_price = float(price_input)
                MANUAL_CHICKEN_PRICES[item]['price'] = new_price
                
        except ValueError:
            print("❌ 輸入格式錯誤，保持原設定")
        
        print()

if __name__ == "__main__":
    print_current_prices()
    create_price_input_interface()
    print("✅ 價格設定完成！")
    print_current_prices()


