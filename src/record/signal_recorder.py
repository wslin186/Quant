# src/backtest/signal_recorder.py

import csv
import os
from datetime import datetime
from src.event_engine.event_type import EventType


class SignalRecorder:
    def __init__(self, output_path="tests/logs/trades.csv"):
        self.output_path = output_path
        self.records = []

        # 如果路径不存在则创建
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # 写入表头
        with open(self.output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["时间", "动作", "标的", "价格", "来源"])

    def on_event(self, event):
        signal = event.data
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            signal.get("action"),
            signal.get("symbol"),
            signal.get("price"),
            event.source
        ]
        self.records.append(row)

        # 实时写入 CSV
        with open(self.output_path, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(row)

        print(f"📝 已记录交易信号: {row}")

    def print_signals(self):
        for row in self.records:
            print(
                f"  - 时间: {row[0]} | 操作: {'买入' if row[1] == 'buy' else '卖出'} | 标的: {row[2]} | 价格: {row[3]} | 来源: {row[4]}"
            )

