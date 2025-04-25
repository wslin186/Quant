import os
import pandas as pd
from typing import Union, Optional


class DataLoader:
    """
    历史行情数据加载器：支持从 CSV 或本地目录加载数据
    """

    def __init__(self, data_path: str):
        """
        :param data_path: 本地数据目录或 CSV 文件路径
        """
        self.data_path = data_path

    def load_csv(self) -> pd.DataFrame:
        """
        直接从指定 CSV 文件读取行情数据
        :return: DataFrame
        """
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"找不到文件: {self.data_path}")

        df = pd.read_csv(self.data_path)
        return self._standardize_columns(df)

    def load_by_symbol(self, symbol: str) -> pd.DataFrame:
        """
        从本地数据目录中按股票代码加载历史行情数据
        文件命名约定: <symbol>.csv，例如 600519.csv
        :param symbol: 股票代码
        :return: DataFrame
        """
        file_path = os.path.join(self.data_path, f"{symbol}.csv")
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"找不到股票 {symbol} 的历史数据文件: {file_path}")

        df = pd.read_csv(file_path)
        return self._standardize_columns(df)

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        统一字段名为内部格式（如 TradePx, TradeDate, UpdateTime）
        """
        rename_map = {
            "price": "TradePx",
            "volume": "TotalVolumeTraded",
            "date": "TradeDate",
            "time": "UpdateTime",
            "symbol": "SecurityID"
        }
        df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
        return df
