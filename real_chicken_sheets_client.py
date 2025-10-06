"""
真實炸雞 Google Sheets 客戶端
讀取真實的 Google Sheet 資料並轉換為炸雞銷售格式
"""
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import logging
from chicken_sheets_client import ChickenSheetsClient

logger = logging.getLogger(__name__)

class RealChickenSheetsClient:
    """真實炸雞 Google Sheets 客戶端"""
    
    def __init__(self, sheet_id: str, credentials_file: str = 'credentials.json', token_file: str = 'token.pickle'):
        """
        初始化客戶端
        
        Args:
            sheet_id (str): Google Sheet ID
            credentials_file (str): 認證檔案路徑
            token_file (str): Token 檔案路徑
        """
        self.sheet_id = sheet_id
        self.sheets_client = ChickenSheetsClient(credentials_file, token_file, sheet_id)
    
    def read_chicken_sales_data(self, main_sheet_name: str = '表單回應 1', 
                               settings_sheet_name: str = '設定',
                               data_range: str = 'A1:Z1000',
                               settings_range: str = 'A1:Z100') -> pd.DataFrame:
        """
        讀取炸雞銷售資料
        
        Args:
            main_sheet_name (str): 主要資料工作表名稱
            settings_sheet_name (str): 設定工作表名稱
            data_range (str): 資料範圍
            settings_range (str): 設定範圍
            
        Returns:
            pd.DataFrame: 炸雞銷售資料
        """
        try:
            # 使用 ChickenSheetsClient 的 get_chicken_sales_data 方法
            logger.info("正在讀取炸雞銷售資料...")
            chicken_data = self.sheets_client.get_chicken_sales_data()
            
            if chicken_data.empty:
                logger.warning("沒有讀取到炸雞銷售資料")
                return pd.DataFrame()
            
            logger.info(f"成功讀取 {len(chicken_data)} 筆炸雞銷售資料")
            return chicken_data
            
        except Exception as error:
            logger.error(f"讀取炸雞銷售資料時發生錯誤: {error}")
            raise
    
    def _convert_to_chicken_sales_format(self, main_data: pd.DataFrame, 
                                       settings_data: pd.DataFrame) -> pd.DataFrame:
        """
        將主要資料轉換為炸雞銷售格式
        
        Args:
            main_data (pd.DataFrame): 主要資料
            settings_data (pd.DataFrame): 設定資料
            
        Returns:
            pd.DataFrame: 炸雞銷售格式資料
        """
        try:
            chicken_sales_list = []
            
            # 處理設定資料，建立品項價格對應
            price_mapping = self._parse_settings_data(settings_data)
            
            # 處理主要資料中的炸雞品項欄位
            chicken_columns = [
                '炸物的訂購_雞排',
                '炸物的訂購_地瓜', 
                '炸物的訂購_棒腿',
                '炸物的訂購_雞翅'
            ]
            
            # 品項名稱對應
            item_mapping = {
                '炸物的訂購_雞排': '雞排',
                '炸物的訂購_地瓜': '地瓜',
                '炸物的訂購_棒腿': '棒腿', 
                '炸物的訂購_雞翅': '雞翅'
            }
            
            for _, row in main_data.iterrows():
                # 取得日期
                date_value = row.get('日期', '')
                if pd.isna(date_value) or date_value == '':
                    continue
                
                try:
                    # 轉換日期格式
                    if isinstance(date_value, str):
                        date_obj = pd.to_datetime(date_value, errors='coerce')
                    else:
                        date_obj = date_value
                    
                    if pd.isna(date_obj):
                        continue
                        
                except:
                    continue
                
                # 處理每個炸雞品項
                for col in chicken_columns:
                    if col in row and not pd.isna(row[col]) and str(row[col]).strip() != '':
                        quantity_str = str(row[col]).strip()
                        
                        # 處理數量（將「一份」轉換為 1）
                        if quantity_str == '一份':
                            quantity = 1
                        else:
                            try:
                                quantity = int(quantity_str)
                            except:
                                continue
                        
                        if quantity > 0:
                            item_name = item_mapping.get(col, col)
                            
                            # 取得價格設定
                            price_info = price_mapping.get(item_name, {'cost': 0, 'price': 0})
                            
                            chicken_sales_list.append({
                                '日期': date_obj,
                                '品項': item_name,
                                '數量': quantity,
                                '單價': price_info['price'],
                                '成本': price_info['cost'],
                                '小計': quantity * price_info['price'],
                                '成本小計': quantity * price_info['cost']
                            })
            
            if not chicken_sales_list:
                logger.warning("沒有找到有效的炸雞銷售資料")
                return pd.DataFrame()
            
            result_df = pd.DataFrame(chicken_sales_list)
            logger.info(f"成功轉換 {len(result_df)} 筆炸雞銷售資料")
            return result_df
            
        except Exception as error:
            logger.error(f"轉換炸雞銷售格式時發生錯誤: {error}")
            raise
    
    def _parse_settings_data(self, settings_data: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        解析設定資料，建立品項價格對應
        
        Args:
            settings_data (pd.DataFrame): 設定資料
            
        Returns:
            Dict[str, Dict[str, float]]: 品項價格對應
        """
        try:
            price_mapping = {}
            
            if settings_data.empty:
                logger.warning("設定資料為空，使用預設價格")
                return price_mapping
            
            # 假設設定資料格式：
            # A 欄：品項名稱
            # B 欄：品項名稱（重複）
            # C 欄：成本
            # D 欄：售價
            
            for _, row in settings_data.iterrows():
                item_name = str(row.iloc[0]).strip() if not pd.isna(row.iloc[0]) else ''
                if item_name and item_name != 'nan':
                    try:
                        cost = float(row.iloc[2]) if not pd.isna(row.iloc[2]) else 0
                        price = float(row.iloc[3]) if not pd.isna(row.iloc[3]) else 0
                        
                        price_mapping[item_name] = {
                            'cost': cost,
                            'price': price
                        }
                        
                        logger.info(f"設定品項 {item_name}: 成本 {cost}, 售價 {price}")
                        
                    except (ValueError, IndexError) as e:
                        logger.warning(f"解析品項 {item_name} 價格時發生錯誤: {e}")
                        continue
            
            logger.info(f"成功解析 {len(price_mapping)} 個品項的價格設定")
            return price_mapping
            
        except Exception as error:
            logger.error(f"解析設定資料時發生錯誤: {error}")
            return {}
    
    def get_available_dates(self, main_sheet_name: str = '表單回應 1') -> List[datetime]:
        """
        取得可用的日期列表
        
        Args:
            main_sheet_name (str): 主要資料工作表名稱
            
        Returns:
            List[datetime]: 可用日期列表
        """
        try:
            # 使用 get_chicken_sales_data 取得資料
            data = self.sheets_client.get_chicken_sales_data()
            
            if data.empty or '日期' not in data.columns:
                return []
            
            # 取得唯一日期並排序
            dates = sorted(data['日期'].dropna().unique().tolist())
            logger.info(f"找到 {len(dates)} 個可用日期")
            return dates
            
        except Exception as error:
            logger.error(f"取得可用日期時發生錯誤: {error}")
            return []



