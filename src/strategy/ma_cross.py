# ------------- src/strategy/ma_cross_strategy.py（示例）-------------
from collections import deque

from src.event_engine import Event, EventType        # ★ 统一从包中拿
from src.strategy.base_strategy import BaseStrategy
# --------------------------------------------------------



class MaCrossStrategy(BaseStrategy):
    def __init__(self, name, event_engine, parameters):
        super().__init__(name, event_engine, parameters)
        self.short_window = parameters.get("short_window", 5)
        self.long_window  = parameters.get("long_window", 20)

        self.short_prices = deque(maxlen=self.short_window)
        self.long_prices  = deque(maxlen=self.long_window)
        self.in_position  = False

    # 收行情事件
    def on_event(self, event: Event):
        price = event.data.get("last_price")
        if price is None:
            return

        self.short_prices.append(price)
        self.long_prices.append(price)

        # 样本不足
        if len(self.long_prices) < self.long_window:
            return

        short_avg = sum(self.short_prices) / self.short_window
        long_avg  = sum(self.long_prices)  / self.long_window

        print(f"🧠 策略运行日志 | 当前价: {price}, "
              f"短均: {short_avg:.2f}, 长均: {long_avg:.2f}, "
              f"状态: {'持仓中' if self.in_position else '空仓'}")

        signal = None
        if short_avg > long_avg and not self.in_position:
            signal = {"action": "buy", "price": price,
                      "symbol": event.data["symbol"]}
            self.in_position = True
        elif short_avg < long_avg and self.in_position:
            signal = {"action": "sell", "price": price,
                      "symbol": event.data["symbol"]}
            self.in_position = False

        if signal:
            print(f"📢 交易信号输出: {signal}")
            self.event_engine.put(Event(
                type_=EventType.STRATEGY_SIGNAL,
                data=signal,
                source=self.name
            ))
