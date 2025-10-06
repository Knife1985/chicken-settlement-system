"""
炸雞對帳系統 Google Sheets 客戶端
專門處理炸雞品項的 Google Sheets 資料讀取
"""
import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
from datetime import datetime
import logging
from chicken_config import GOOGLE_SHEETS_CONFIG, CHICKEN_PRODUCTS_CONFIG, CHICKEN_COLUMN_MAPPING

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChickenSheetsClient:
    """炸雞對帳系統 Google Sheets 客戶端類別"""
    
    # 讀寫範圍
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    
    def __init__(self, credentials_file, token_file, sheet_id):
        """
        初始化 Google Sheets 客戶端
        
        Args:
            credentials_file (str): 認證檔案路徑
            token_file (str): Token 檔案路徑
            sheet_id (str): Google Sheet ID
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.sheet_id = sheet_id
        self.service = None
        self.chicken_prices = {}
        self._authenticate()
        self._load_chicken_prices()
    
    def _authenticate(self):
        """進行 Google API 認證"""
        creds = None
        
        # 載入已存在的 token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # 如果沒有有效的認證，則進行 OAuth 流程
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(f"認證檔案不存在: {self.credentials_file}")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # 儲存認證資訊
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        # 建立服務物件
        self.service = build('sheets', 'v4', credentials=creds)
        logger.info("Google Sheets API 認證成功")
    
    def _load_chicken_prices(self):
        """從設定工作表載入炸雞品項價格"""
        try:
            # 讀取設定工作表
            settings_data = self.read_data(
                sheet_name=GOOGLE_SHEETS_CONFIG['SETTINGS_SHEET_NAME'],
                range_name=GOOGLE_SHEETS_CONFIG['SETTINGS_RANGE']
            )
            
            if settings_data:
                # 假設設定工作表格式為：品項名稱 | 價格
                for row in settings_data[1:]:  # 跳過標題列
                    if len(row) >= 2:
                        product_name = row[0].strip()
                        try:
                            price = float(row[1])
                            self.chicken_prices[product_name] = price
                        except (ValueError, IndexError):
                            continue
                
                logger.info(f"成功載入 {len(self.chicken_prices)} 個炸雞品項價格")
            else:
                # 如果沒有設定工作表，使用預設價格
                self.chicken_prices = CHICKEN_PRODUCTS_CONFIG.copy()
                logger.warning("無法讀取設定工作表，使用預設價格")
                
        except Exception as error:
            logger.error(f"載入炸雞品項價格時發生錯誤: {error}")
            # 使用預設價格
            self.chicken_prices = CHICKEN_PRODUCTS_CONFIG.copy()
    
    def read_data(self, sheet_name, range_name):
        """
        讀取 Google Sheet 資料
        
        Args:
            sheet_name (str): 工作表名稱
            range_name (str): 資料範圍
            
        Returns:
            list: 資料列表
        """
        try:
            range_full = f"{sheet_name}!{range_name}"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id,
                range=range_full
            ).execute()
            
            values = result.get('values', [])
            logger.info(f"成功讀取 {len(values)} 筆資料")
            return values
            
        except HttpError as error:
            logger.error(f"讀取資料時發生錯誤: {error}")
            raise
    
    def get_chicken_sales_data(self):
        """
        取得炸雞銷售資料
        
        Returns:
            pd.DataFrame: 炸雞銷售資料
        """
        try:
            # 讀取主要資料
            main_data = self.read_data(
                sheet_name=GOOGLE_SHEETS_CONFIG['MAIN_SHEET_NAME'],
                range_name=GOOGLE_SHEETS_CONFIG['DATA_RANGE']
            )
            
            if not main_data:
                logger.warning("沒有讀取到任何資料")
                return pd.DataFrame()
            
            # 轉換為 DataFrame
            df = pd.DataFrame(main_data[1:], columns=main_data[0])
            
            # 處理炸雞品項資料
            chicken_sales = []
            
            for _, row in df.iterrows():
                # 取得日期
                date_str = row.get('日期', '')
                if not date_str:
                    continue
                
                try:
                    date = pd.to_datetime(date_str)
                except:
                    continue
                
                # 處理每個炸雞品項
                for col_name, product_name in CHICKEN_COLUMN_MAPPING.items():
                    if col_name in row and row[col_name]:
                        try:
                            quantity = float(row[col_name])
                            if quantity > 0:  # 只處理有銷售的品項
                                price = self.chicken_prices.get(product_name, 0)
                                chicken_sales.append({
                                    '日期': date,
                                    '品項': product_name,
                                    '數量': quantity,
                                    '單價': price,
                                    '小計': quantity * price
                                })
                        except (ValueError, TypeError):
                            continue
            
            chicken_df = pd.DataFrame(chicken_sales)
            
            if chicken_df.empty:
                logger.warning("沒有找到炸雞銷售資料")
                return pd.DataFrame()
            
            logger.info(f"成功取得 {len(chicken_df)} 筆炸雞銷售資料")
            return chicken_df
            
        except Exception as error:
            logger.error(f"取得炸雞銷售資料時發生錯誤: {error}")
            raise
    
    def get_chicken_prices(self):
        """
        取得炸雞品項價格設定
        
        Returns:
            dict: 炸雞品項價格字典
        """
        return self.chicken_prices.copy()
    
    def update_chicken_prices(self, new_prices):
        """
        更新炸雞品項價格設定
        
        Args:
            new_prices (dict): 新的價格設定
        """
        self.chicken_prices.update(new_prices)
        logger.info("炸雞品項價格已更新")



