import os
import time
import pandas as pd
from src.event_engine.event import Event
from src.event_engine.event_type import EventType


class DataPlayer:
    def __init__(self, event_engine, data_source="mock", config=None, delay=0.1):
        """
        :param event_engine: 事件引擎实例
        :param data_source: 数据来源类型，可为 "mock"、"csv"、"local"
        :param config: 数据配置（文件路径、字段映射等）
        :param delay: 每条数据之间的时间间隔，控制回放节奏
        """
        self.event_engine = event_engine
        self.data_source = data_source
        self.config = config or {}
        self.delay = delay

    def start(self):
        if self.data_source == "mock":
            self._play_mock()
        elif self.data_source == "csv":
            self._play_csv()
        elif self.data_source == "local":
            self._play_local()
        else:
            raise ValueError(f"❌ 不支持的数据源类型: {self.data_source}")

    def _play_mock(self):
        print("🧪 使用 mock 数据回放")
        data = [
            {"SecurityID": "600519", "TradePx": 100, "TotalVolumeTraded": 1000, "TradeDate": 20250424,
             "UpdateTime": 93000000},
            {"SecurityID": "600519", "TradePx": 102, "TotalVolumeTraded": 1500, "TradeDate": 20250424,
             "UpdateTime": 93010000},
            {"SecurityID": "600519", "TradePx": 104, "TotalVolumeTraded": 2000, "TradeDate": 20250424,
             "UpdateTime": 93020000},
            {"SecurityID": "600519", "TradePx": 106, "TotalVolumeTraded": 2500, "TradeDate": 20250424,
             "UpdateTime": 93030000},
            {"SecurityID": "600519", "TradePx": 108, "TotalVolumeTraded": 3000, "TradeDate": 20250424,
             "UpdateTime": 93040000},
            {"SecurityID": "600519", "TradePx": 110, "TotalVolumeTraded": 3500, "TradeDate": 20250424,
             "UpdateTime": 93050000},
            {"SecurityID": "600519", "TradePx": 105, "TotalVolumeTraded": 3600, "TradeDate": 20250424,
             "UpdateTime": 93060000},
            {"SecurityID": "600519", "TradePx": 100, "TotalVolumeTraded": 3700, "TradeDate": 20250424,
             "UpdateTime": 93070000},
        ]

        for row in data:
            self._push_snapshot_event(row)
            time.sleep(self.delay)

    def _play_csv(self):
        path = self.config.get("path")
        if not path or not os.path.exists(path):
            print(f"❌ CSV 文件未找到: {path}")
            return

        print(f"📄 从 CSV 文件回放: {path}")
        df = pd.read_csv(path)
        for _, row in df.iterrows():
            record = row.to_dict()
            self._push_snapshot_event(record)
            time.sleep(self.delay)

    def _play_local(self):
        print("📦 本地历史数据播放未实现，请接入 DataLoader 后支持")
        # 可以调用已有的 data_loader.py 加载数据
        # 举例：
        # from src.data_loader import load_snapshot_data
        # df = load_snapshot_data(...)
        pass

    def _push_snapshot_event(self, data: dict):
        event = Event(
            type_=EventType.MARKET_SNAPSHOT,
            data=data,
            source="DataPlayer"
        )
        self.event_engine.put(event)

    def load_ohlc(self):
        """未来扩展：加载 OHLC 数据接口"""
        print("📉 OHLC 数据加载接口占位，尚未实现")
        return None
