import csv
import os
from datetime import datetime
from utils.logger import get_logger
from src.event_engine.event_type import EventType

logger = get_logger("Signal")


class SignalRecorder:
    CSV_HEADER = ["时间", "动作", "标的", "价格", "来源"]

    def __init__(self,
                 output_path: str = "tests/logs/trades.csv",
                 verbose: bool = True):
        self.output_path = output_path
        self.verbose = verbose
        self.records: list[list] = []

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(self.output_path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(self.CSV_HEADER)

    def on_event(self, event):
        if event.type != EventType.STRATEGY_SIGNAL:
            return
        sig = event.data
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            sig.get("action"),
            sig.get("symbol"),
            sig.get("price"),
            event.source
        ]
        self.records.append(row)
        with open(self.output_path, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(row)

        if self.verbose:
            logger.info("📝 信号记录 %s", row)

    def print_signals(self):
        logger.info("🗒️  [信号记录]")
        for t, act, sym, price, src in self.records:
            logger.info("  - %s | %s | %s | %s | %s",
                        t, "买入" if act == 'buy' else "卖出", sym, price, src)
