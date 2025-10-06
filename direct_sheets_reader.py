"""
直接讀取 Google Sheet 公開資料
不需要 API 認證，直接從公開的 CSV 連結讀取
"""
import pandas as pd
import requests
from typing import Dict, List, Optional
import logging
from io import StringIO

logger = logging.getLogger(__name__)

class DirectSheetsReader:
    """直接讀取 Google Sheet 公開資料"""
    
    def __init__(self, sheet_id: str):
        """
        初始化讀取器
        
        Args:
            sheet_id (str): Google Sheet ID
        """
        self.sheet_id = sheet_id
        self.base_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export"
    
    def read_sheet_as_csv(self, sheet_name: str = None, gid: str = "0") -> pd.DataFrame:
        """
        讀取 Google Sheet 為 CSV 格式
        
        Args:
            sheet_name (str): 工作表名稱（可選）
            gid (str): 工作表 ID，預設為 "0"（第一個工作表）
            
        Returns:
            pd.DataFrame: 讀取的資料
        """
        try:
            # 使用正確的公開 Google Sheet CSV 匯出 URL 格式
            # 對於公開的 Google Sheet，使用這個格式
            url = f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/gviz/tq?tqx=out:csv&gid={gid}"
            
            logger.info(f"正在讀取 Google Sheet: {url}")
            
            # 發送請求，設定適當的 headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # 讀取 CSV 資料
            csv_data = StringIO(response.text)
            df = pd.read_csv(csv_data)
            
            logger.info(f"成功讀取 {len(df)} 筆資料，{len(df.columns)} 個欄位")
            logger.info(f"欄位名稱: {list(df.columns)}")
            
            return df
            
        except Exception as error:
            logger.error(f"讀取 Google Sheet 時發生錯誤: {error}")
            logger.error(f"回應狀態碼: {response.status_code if 'response' in locals() else 'N/A'}")
            logger.error(f"回應內容: {response.text[:500] if 'response' in locals() else 'N/A'}")
            raise
    
    def get_available_sheets(self) -> List[Dict[str, str]]:
        """
        取得可用的工作表列表
        
        Returns:
            List[Dict[str, str]]: 工作表資訊列表
        """
        try:
            # 嘗試讀取第一個工作表來取得基本資訊
            df = self.read_sheet_as_csv()
            
            # 這裡可以根據實際需求擴展，取得所有工作表資訊
            sheets_info = [
                {
                    'name': '表單回應 1',
                    'gid': '0',
                    'rows': len(df),
                    'columns': len(df.columns)
                }
            ]
            
            return sheets_info
            
        except Exception as error:
            logger.error(f"取得工作表資訊時發生錯誤: {error}")
            return []
    
    def read_chicken_sales_data(self, main_sheet_gid: str = "0", 
                               settings_sheet_gid: str = "1") -> pd.DataFrame:
        """
        讀取炸雞銷售資料
        
        Args:
            main_sheet_gid (str): 主要資料工作表 ID
            settings_sheet_gid (str): 設定工作表 ID
            
        Returns:
            pd.DataFrame: 炸雞銷售資料
        """
        try:
            # 讀取主要資料
            logger.info("正在讀取主要資料工作表...")
            main_data = self.read_sheet_as_csv(gid=main_sheet_gid)
            
            if main_data.empty:
                logger.warning("主要資料工作表為空")
                return pd.DataFrame()
            
            # 動態載入最新的價格設定
            try:
                # 直接讀取 JSON 檔案以獲取最新價格
                import json
                import os
                price_file = 'chicken_prices.json'
                if os.path.exists(price_file):
                    with open(price_file, 'r', encoding='utf-8') as f:
                        prices = json.load(f)
                    logger.info("成功載入最新價格設定")
                    # 轉換為炸雞銷售格式，使用最新價格
                    chicken_data = self._convert_to_chicken_sales_format_with_prices(main_data, prices)
                else:
                    logger.warning("價格設定檔案不存在，使用預設價格")
                    settings_data = pd.DataFrame()
                    chicken_data = self._convert_to_chicken_sales_format(main_data, settings_data)
            except Exception as error:
                logger.warning(f"載入價格設定失敗，使用預設價格: {error}")
                settings_data = pd.DataFrame()
                chicken_data = self._convert_to_chicken_sales_format(main_data, settings_data)
            
            logger.info(f"成功轉換 {len(chicken_data)} 筆炸雞銷售資料")
            return chicken_data
            
        except Exception as error:
            logger.error(f"讀取炸雞銷售資料時發生錯誤: {error}")
            raise
    
    def _convert_to_chicken_sales_format_with_prices(self, main_data: pd.DataFrame, 
                                                   prices: dict) -> pd.DataFrame:
        """
        使用提供的價格設定轉換為炸雞銷售格式
        """
        chicken_sales_list = []
        
        # 品項名稱對應
        item_mapping = {
            '炸物的訂購 [雞排]': '雞排',
            '炸物的訂購 [地瓜]': '地瓜',
            '炸物的訂購 [棒腿*2]': '棒腿', 
            '炸物的訂購 [雞翅 *3]': '雞翅'
        }
        
        # 炸雞品項欄位
        chicken_columns = [
            '炸物的訂購 [雞排]',
            '炸物的訂購 [地瓜]', 
            '炸物的訂購 [棒腿*2]',
            '炸物的訂購 [雞翅 *3]'
        ]
        
        # 先按日期分組，只取每個日期的最新記錄
        if '時間戳記' in main_data.columns:
            # 按日期分組，取每個日期的最新記錄（時間戳記最大的）
            # 處理中文時間格式
            main_data['時間戳記'] = pd.to_datetime(main_data['時間戳記'], format='%Y/%m/%d 下午 %I:%M:%S', errors='coerce')
            # 如果下午格式失敗，嘗試上午格式
            mask = main_data['時間戳記'].isna()
            main_data.loc[mask, '時間戳記'] = pd.to_datetime(main_data.loc[mask, '時間戳記'], format='%Y/%m/%d 上午 %I:%M:%S', errors='coerce')
            
            # 過濾掉時間戳記為 NaN 的記錄
            valid_data = main_data.dropna(subset=['時間戳記'])
            if not valid_data.empty:
                latest_records = valid_data.groupby('日期').apply(lambda x: x.loc[x['時間戳記'].idxmax()]).reset_index(drop=True)
            else:
                latest_records = main_data
        else:
            # 如果沒有時間戳記欄位，直接使用原始資料
            latest_records = main_data
        
        for _, row in latest_records.iterrows():
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
                
                # 處理每個炸雞品項欄位
                for col in chicken_columns:
                    if col not in row:
                        continue
                    
                    quantity_str = str(row[col]).strip()
                    if quantity_str and quantity_str != 'nan' and quantity_str != '':
                        # 處理數量格式（例如："3份" -> 3）
                        if '份' in quantity_str:
                            quantity_str = quantity_str.replace('份', '')
                        
                        try:
                            quantity = int(quantity_str)
                        except:
                            continue
                        
                        if quantity > 0:
                            item_name = item_mapping.get(col, col)
                            
                            # 使用提供的價格設定
                            price_info = prices.get(item_name, {'cost': 0, 'price': 0})
                            
                            chicken_sales_list.append({
                                '日期': date_obj,
                                '品項': item_name,
                                '數量': quantity,
                                '單價': price_info['price'],
                                '成本': price_info['cost'],
                                '小計': quantity * price_info['price'],
                                '成本小計': quantity * price_info['cost']
                            })
            
            except Exception as error:
                logger.warning(f"處理資料行時發生錯誤: {error}")
                continue
        
        if not chicken_sales_list:
            logger.warning("沒有找到有效的炸雞銷售資料")
            return pd.DataFrame()
        
        result_df = pd.DataFrame(chicken_sales_list)
        logger.info(f"成功轉換 {len(result_df)} 筆炸雞銷售資料")
        return result_df

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
            
            # 顯示主要資料的欄位，幫助除錯
            logger.info(f"主要資料欄位: {list(main_data.columns)}")
            logger.info(f"主要資料前5行:")
            logger.info(f"{main_data.head()}")
            
            # 處理主要資料中的炸雞品項欄位（根據實際欄位名稱）
            chicken_columns = [
                '炸物的訂購 [雞排]',
                '炸物的訂購 [地瓜]', 
                '炸物的訂購 [棒腿*2]',
                '炸物的訂購 [雞翅 *3]'
            ]
            
            # 品項名稱對應
            item_mapping = {
                '炸物的訂購 [雞排]': '雞排',
                '炸物的訂購 [地瓜]': '地瓜',
                '炸物的訂購 [棒腿*2]': '棒腿', 
                '炸物的訂購 [雞翅 *3]': '雞翅'
            }
            
            # 先按日期分組，只取每個日期的最新記錄
            if '時間戳記' in main_data.columns:
                # 按日期分組，取每個日期的最新記錄（時間戳記最大的）
                # 處理中文時間格式
                main_data['時間戳記'] = pd.to_datetime(main_data['時間戳記'], format='%Y/%m/%d 下午 %I:%M:%S', errors='coerce')
                # 如果下午格式失敗，嘗試上午格式
                mask = main_data['時間戳記'].isna()
                main_data.loc[mask, '時間戳記'] = pd.to_datetime(main_data.loc[mask, '時間戳記'], format='%Y/%m/%d 上午 %I:%M:%S', errors='coerce')
                
                # 過濾掉時間戳記為 NaN 的記錄
                valid_data = main_data.dropna(subset=['時間戳記'])
                if not valid_data.empty:
                    latest_records = valid_data.groupby('日期').apply(lambda x: x.loc[x['時間戳記'].idxmax()]).reset_index(drop=True)
                else:
                    latest_records = main_data
            else:
                # 如果沒有時間戳記欄位，直接使用原始資料
                latest_records = main_data
            
            for _, row in latest_records.iterrows():
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
                        
                        # 處理數量（將「X份」轉換為數字）
                        if '份' in quantity_str:
                            try:
                                # 提取數字部分
                                quantity = int(quantity_str.replace('份', ''))
                            except:
                                continue
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
                logger.warning("設定資料為空，使用手動價格設定")
                # 使用手動價格設定
                from persistent_price_config import get_chicken_prices
                price_mapping = get_chicken_prices()
                return price_mapping
            
            # 顯示設定資料的欄位，幫助除錯
            logger.info(f"設定資料欄位: {list(settings_data.columns)}")
            logger.info(f"設定資料內容:")
            logger.info(f"{settings_data}")
            
            # 假設設定資料格式：
            # A 欄：品項名稱
            # B 欄：品項名稱（重複）
            # C 欄：成本
            # D 欄：售價
            
            for _, row in settings_data.iterrows():
                # 跳過第一行（標題行）
                if pd.isna(row.iloc[0]) or str(row.iloc[0]).strip() == '':
                    continue
                    
                item_name = str(row.iloc[0]).strip()
                if item_name and item_name != 'nan' and not item_name.startswith('品項'):
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
