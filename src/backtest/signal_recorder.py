# src/backtest/signal_recorder.py
import csv
import os
from datetime import datetime
from src.event_engine.event_type import EventType


class SignalRecorder:
    """
    把策略信号实时写进 CSV，方便回测/复盘
    """
    def __init__(self, output_path="tests/data/trades.csv"):
        self.output_path = output_path
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 写表头（覆盖式）
        with open(self.output_path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["时间", "动作", "标的", "价格", "来源"])

    # 订阅 EventEngine 后直接作为回调用
    def on_event(self, event):
        if event.type != EventType.STRATEGY_SIGNAL:
            return

        s = event.data          # shorthand
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            s.get("action"),
            s.get("symbol"),
            s.get("price"),
            event.source
        ]

        # 追加写 CSV
        with open(self.output_path, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(row)

        print(f"📝 已记录交易信号: {row}")

    def print_signals(self):
        with open(self.output_path, newline="", encoding="utf-8") as f:
            for r in csv.reader(f):
                print(r)
