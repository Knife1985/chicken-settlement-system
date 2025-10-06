"""
炸雞對帳計算器
專門處理炸雞品項的銷售對帳計算
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class ChickenSettlementCalculator:
    """炸雞對帳計算器類別"""
    
    def __init__(self, chicken_products_config: Dict[str, Dict[str, float]]):
        """
        初始化計算器
        
        Args:
            chicken_products_config (Dict[str, Dict[str, float]]): 炸雞品項設定，包含成本和售價
        """
        self.chicken_products_config = chicken_products_config
    
    def process_chicken_sales_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        處理炸雞銷售資料，清理和標準化資料
        
        Args:
            df (pd.DataFrame): 原始銷售資料
            
        Returns:
            pd.DataFrame: 處理後的資料
        """
        try:
            # 複製資料避免修改原始資料
            processed_df = df.copy()
            
            # 確保日期欄位為 datetime 格式
            if '日期' in processed_df.columns:
                processed_df['日期'] = pd.to_datetime(processed_df['日期'], errors='coerce')
            
            # 確保數量欄位為數值格式
            if '數量' in processed_df.columns:
                processed_df['數量'] = pd.to_numeric(processed_df['數量'], errors='coerce')
            
            # 處理單價欄位
            if '單價' in processed_df.columns:
                processed_df['單價'] = pd.to_numeric(processed_df['單價'], errors='coerce')
            else:
                # 如果沒有單價欄位，根據品項設定預設售價
                processed_df['單價'] = processed_df['品項'].map(lambda x: self.chicken_products_config.get(x, {}).get('price', 0))
            
            # 處理數量欄位，將「一份」轉換為數字
            if '數量' in processed_df.columns:
                # 將文字「一份」轉換為數字 1
                processed_df['數量'] = processed_df['數量'].astype(str).str.replace('一份', '1', regex=False)
                processed_df['數量'] = pd.to_numeric(processed_df['數量'], errors='coerce')
            
            # 計算小計
            processed_df['小計'] = processed_df['數量'] * processed_df['單價']
            
            # 移除無效資料
            processed_df = processed_df.dropna(subset=['日期', '品項', '數量'])
            
            # 只保留炸雞相關品項
            chicken_items = list(self.chicken_products_config.keys())
            processed_df = processed_df[processed_df['品項'].isin(chicken_items)]
            
            # 添加成本欄位
            processed_df['成本'] = processed_df['品項'].map(lambda x: self.chicken_products_config.get(x, {}).get('cost', 0))
            processed_df['成本小計'] = processed_df['數量'] * processed_df['成本']
            
            logger.info(f"處理完成，有效炸雞銷售資料 {len(processed_df)} 筆")
            return processed_df
            
        except Exception as error:
            logger.error(f"處理炸雞銷售資料時發生錯誤: {error}")
            raise
    
    def calculate_settlement_period(self, start_date: datetime, period_days: int = 14) -> Tuple[datetime, datetime]:
        """
        計算結算期間
        
        Args:
            start_date (datetime): 開始日期
            period_days (int): 結算週期天數
            
        Returns:
            Tuple[datetime, datetime]: (開始日期, 結束日期)
        """
        end_date = start_date + timedelta(days=period_days - 1)
        return start_date, end_date
    
    def filter_data_by_period(self, df: pd.DataFrame, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        根據日期範圍篩選資料
        
        Args:
            df (pd.DataFrame): 銷售資料
            start_date (datetime): 開始日期
            end_date (datetime): 結束日期
            
        Returns:
            pd.DataFrame: 篩選後的資料
        """
        try:
            # 篩選日期範圍內的資料
            mask = (df['日期'] >= start_date) & (df['日期'] <= end_date)
            filtered_df = df[mask].copy()
            
            logger.info(f"篩選期間 {start_date.date()} 到 {end_date.date()}，共 {len(filtered_df)} 筆炸雞銷售資料")
            return filtered_df
            
        except Exception as error:
            logger.error(f"篩選資料時發生錯誤: {error}")
            raise
    
    def calculate_chicken_product_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        計算各炸雞品項的銷售摘要
        
        Args:
            df (pd.DataFrame): 銷售資料
            
        Returns:
            pd.DataFrame: 炸雞品項銷售摘要
        """
        try:
            # 按品項分組計算
            summary = df.groupby('品項').agg({
                '數量': 'sum',
                '小計': 'sum',
                '單價': 'mean'
            }).round(2)
            
            # 重新命名欄位
            summary.columns = ['總數量', '總金額', '平均單價']
            
            # 重置索引
            summary = summary.reset_index()
            
            # 按總金額排序
            summary = summary.sort_values('總金額', ascending=False)
            
            logger.info(f"計算完成，共 {len(summary)} 個炸雞品項")
            return summary
            
        except Exception as error:
            logger.error(f"計算炸雞品項摘要時發生錯誤: {error}")
            raise
    
    def calculate_daily_chicken_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        計算每日炸雞銷售摘要
        
        Args:
            df (pd.DataFrame): 銷售資料
            
        Returns:
            pd.DataFrame: 每日炸雞銷售摘要
        """
        try:
            # 按日期分組計算
            daily_summary = df.groupby('日期').agg({
                '數量': 'sum',
                '小計': 'sum'
            }).round(2)
            
            # 重新命名欄位
            daily_summary.columns = ['總數量', '總金額']
            
            # 重置索引
            daily_summary = daily_summary.reset_index()
            
            # 按日期排序
            daily_summary = daily_summary.sort_values('日期')
            
            logger.info(f"計算完成，共 {len(daily_summary)} 天的炸雞銷售資料")
            return daily_summary
            
        except Exception as error:
            logger.error(f"計算每日炸雞摘要時發生錯誤: {error}")
            raise
    
    def calculate_chicken_settlement(self, df: pd.DataFrame) -> Dict:
        """
        計算炸雞對帳金額
        
        Args:
            df (pd.DataFrame): 銷售資料
            
        Returns:
            Dict: 炸雞對帳資訊
        """
        try:
            total_quantity = df['數量'].sum()
            total_amount = df['小計'].sum()
            total_cost = df['成本小計'].sum()
            total_orders = len(df)
            unique_products = df['品項'].nunique()
            
            # 計算需要付給炸雞老闆的金額（總成本）
            chicken_boss_amount = total_cost
            
            # 計算利潤
            profit = total_amount - total_cost
            
            # 計算成本比例
            cost_ratio = total_cost / total_amount if total_amount > 0 else 0
            
            settlement_info = {
                '總銷售數量': total_quantity,
                '總銷售金額': round(total_amount, 2),
                '總成本': round(total_cost, 2),
                '總訂單數': total_orders,
                '品項種類': unique_products,
                '平均單價': round(total_amount / total_quantity, 2) if total_quantity > 0 else 0,
                '平均成本': round(total_cost / total_quantity, 2) if total_quantity > 0 else 0,
                '炸雞老闆應付金額': round(chicken_boss_amount, 2),
                '成本比例': round(cost_ratio, 4),
                '利潤': round(profit, 2)
            }
            
            logger.info(f"炸雞對帳計算完成: 總銷售金額 {settlement_info['總銷售金額']} 元，總成本 {settlement_info['總成本']} 元，應付炸雞老闆 {settlement_info['炸雞老闆應付金額']} 元")
            return settlement_info
            
        except Exception as error:
            logger.error(f"計算炸雞對帳時發生錯誤: {error}")
            raise
    
    def generate_text_settlement_summary(self, df: pd.DataFrame, start_date: datetime, end_date: datetime) -> str:
        """
        生成純文字對帳摘要，方便與雞排老闆對帳
        
        Args:
            df (pd.DataFrame): 銷售資料
            start_date (datetime): 開始日期
            end_date (datetime): 結束日期
            
        Returns:
            str: 純文字對帳摘要
        """
        try:
            # 處理資料
            processed_df = self.process_chicken_sales_data(df)
            
            # 篩選期間資料
            period_df = self.filter_data_by_period(processed_df, start_date, end_date)
            
            if period_df.empty:
                return f"期間：{start_date.date()} 至 {end_date.date()}\n無炸雞銷售資料"
            
            # 計算各種摘要
            product_summary = self.calculate_chicken_product_summary(period_df)
            daily_summary = self.calculate_daily_chicken_summary(period_df)
            settlement_info = self.calculate_chicken_settlement(period_df)
            
            # 生成文字摘要
            text_summary = []
            text_summary.append("=" * 50)
            text_summary.append("🍗 炸雞對帳摘要")
            text_summary.append("=" * 50)
            text_summary.append(f"對帳期間：{start_date.date()} 至 {end_date.date()}")
            text_summary.append("")
            
            # 每日明細（按品項分開）
            text_summary.append("📅 每日明細：")
            text_summary.append("-" * 30)
            
            # 按日期分組，顯示每個日期的品項明細
            daily_items = period_df.groupby('日期').apply(lambda x: x.groupby('品項').agg({
                '數量': 'sum',
                '小計': 'sum'
            }).reset_index()).reset_index(level=0)
            
            current_date = None
            for _, row in daily_items.iterrows():
                date_str = row['日期'].strftime('%Y-%m-%d') if hasattr(row['日期'], 'strftime') else str(row['日期'])
                
                # 如果是新的日期，顯示日期標題
                if current_date != date_str:
                    if current_date is not None:
                        text_summary.append("")  # 日期之間空一行
                    text_summary.append(f"📅 {date_str}：")
                    current_date = date_str
                
                # 顯示該日期的品項明細（使用進價）
                item_name = row['品項']
                quantity = row['數量']
                # 計算進價總額
                cost_per_unit = self.chicken_products_config.get(item_name, {}).get('cost', 0)
                cost_total = quantity * cost_per_unit
                text_summary.append(f"  {item_name}：{quantity} 份 × {cost_per_unit} 元（進價） = {cost_total} 元")
            
            # 顯示每日總計（進價）
            text_summary.append("")
            text_summary.append("📊 每日總計（進價）：")
            for _, row in daily_summary.iterrows():
                date_str = row['日期'].strftime('%Y-%m-%d') if hasattr(row['日期'], 'strftime') else str(row['日期'])
                # 計算該日期的進價總額
                daily_cost = 0
                daily_items = period_df[period_df['日期'] == row['日期']]
                for _, item_row in daily_items.iterrows():
                    item_name = item_row['品項']
                    quantity = item_row['數量']
                    cost_per_unit = self.chicken_products_config.get(item_name, {}).get('cost', 0)
                    daily_cost += quantity * cost_per_unit
                text_summary.append(f"{date_str}：總計 {row['總數量']} 份，進價 {daily_cost} 元")
            
            text_summary.append("")
            
            # 品項對帳明細
            text_summary.append("🍗 品項對帳明細：")
            text_summary.append("-" * 30)
            for _, row in product_summary.iterrows():
                item_name = row['品項']
                quantity = row['總數量']
                cost = self.chicken_products_config.get(item_name, {}).get('cost', 0)
                cost_total = quantity * cost
                text_summary.append(f"{item_name}：{quantity} 份 × {cost} 元（進價） = {cost_total} 元")
            
            text_summary.append("")
            
            # 計算式
            text_summary.append("🧮 計算式：")
            text_summary.append("-" * 30)
            text_summary.append(f"總數量：{settlement_info['總銷售數量']} 份")
            text_summary.append(f"應付金額：{settlement_info['總成本']} 元")
            text_summary.append("")
            text_summary.append("金額計算明細：")
            for _, row in product_summary.iterrows():
                item_name = row['品項']
                quantity = row['總數量']
                cost = self.chicken_products_config.get(item_name, {}).get('cost', 0)
                cost_total = quantity * cost
                text_summary.append(f"  {item_name}：{quantity} 份 × {cost} 元 = {cost_total} 元")
            
            text_summary.append("")
            text_summary.append("=" * 50)
            text_summary.append(f"💰 應付金額：{settlement_info['炸雞老闆應付金額']} 元")
            text_summary.append("=" * 50)
            
            return "\n".join(text_summary)
            
        except Exception as error:
            logger.error(f"生成文字對帳摘要時發生錯誤: {error}")
            raise

    def generate_chicken_settlement_report(self, df: pd.DataFrame, start_date: datetime, end_date: datetime) -> Dict:
        """
        生成完整的炸雞對帳報告
        
        Args:
            df (pd.DataFrame): 銷售資料
            start_date (datetime): 開始日期
            end_date (datetime): 結束日期
            
        Returns:
            Dict: 完整炸雞對帳報告
        """
        try:
            # 處理資料
            processed_df = self.process_chicken_sales_data(df)
            
            # 篩選期間資料
            period_df = self.filter_data_by_period(processed_df, start_date, end_date)
            
            if period_df.empty:
                logger.warning("指定期間內沒有炸雞銷售資料")
                return {
                    '期間': f"{start_date.date()} 至 {end_date.date()}",
                    '總銷售金額': 0,
                    '總銷售數量': 0,
                    '炸雞老闆應付金額': 0,
                    '品項摘要': pd.DataFrame(),
                    '每日摘要': pd.DataFrame(),
                    '詳細資料': pd.DataFrame(),
                    '文字摘要': f"期間：{start_date.date()} 至 {end_date.date()}\n無炸雞銷售資料"
                }
            
            # 計算各種摘要
            product_summary = self.calculate_chicken_product_summary(period_df)
            daily_summary = self.calculate_daily_chicken_summary(period_df)
            settlement_info = self.calculate_chicken_settlement(period_df)
            
            # 生成文字摘要
            text_summary = self.generate_text_settlement_summary(df, start_date, end_date)
            
            # 組合報告
            report = {
                '期間': f"{start_date.date()} 至 {end_date.date()}",
                '總銷售金額': settlement_info['總銷售金額'],
                '總銷售數量': settlement_info['總銷售數量'],
                '總訂單數': settlement_info['總訂單數'],
                '品項種類': settlement_info['品項種類'],
                '平均單價': settlement_info['平均單價'],
                '炸雞老闆應付金額': settlement_info['炸雞老闆應付金額'],
                '成本比例': settlement_info['成本比例'],
                '利潤': settlement_info['利潤'],
                '品項摘要': product_summary,
                '每日摘要': daily_summary,
                '詳細資料': period_df,
                '文字摘要': text_summary
            }
            
            logger.info(f"炸雞對帳報告生成完成: 期間 {report['期間']}, 總銷售金額 {report['總銷售金額']} 元，應付炸雞老闆 {report['炸雞老闆應付金額']} 元")
            return report
            
        except Exception as error:
            logger.error(f"生成炸雞對帳報告時發生錯誤: {error}")
            raise
