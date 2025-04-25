# src/strategy/ma_cross.py
from collections import deque
from utils.logger import get_logger

from src.event_engine.event import Event
from src.event_engine.event_type import EventType
from src.strategy.base_strategy import BaseStrategy

logger = get_logger("MaCross")        # ← 统一日志接口


class MaCrossStrategy(BaseStrategy):
    """简单均线交叉示例"""

    def __init__(self, name, event_engine, parameters):
        super().__init__(name, event_engine, parameters)
        self.short_window = parameters.get("short_window", 5)
        self.long_window  = parameters.get("long_window", 20)
        self.short_prices = deque(maxlen=self.short_window)
        self.long_prices  = deque(maxlen=self.long_window)
        self.in_position  = False

    # 订阅 MARKET_SNAPSHOT / TICK_TRADE
    def on_event(self, event: Event):
        price  = event.data.get("TradePx")
        symbol = event.data.get("SecurityID")
        if price is None:
            return

        self.short_prices.append(price)
        self.long_prices.append(price)

        # 长均未充满样本
        if len(self.long_prices) < self.long_window:
            return

        short_avg = sum(self.short_prices) / self.short_window
        long_avg  = sum(self.long_prices) / self.long_window

        logger.debug("价:%s 短:%s 长:%s 状态:%s",
                     price, f"{short_avg:.2f}", f"{long_avg:.2f}",
                     "持仓" if self.in_position else "空仓")

        signal = None
        if short_avg > long_avg and not self.in_position:
            signal = {"action": "buy", "price": price, "symbol": symbol}
            self.in_position = True
        elif short_avg < long_avg and self.in_position:
            signal = {"action": "sell", "price": price, "symbol": symbol}
            self.in_position = False

        if signal:
            logger.info("📢 交易信号 %s", signal)
            self.event_engine.put(Event(
                type_=EventType.STRATEGY_SIGNAL,
                data=signal,
                source=self.name
            ))
