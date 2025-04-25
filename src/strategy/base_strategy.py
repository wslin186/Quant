# src/strategy/base_strategy.py

from abc import ABC, abstractmethod
from typing import Dict, Any
from src.event_engine.event import Event
from src.event_engine.event_type import EventType


class BaseStrategy(ABC):
    """策略基类，所有策略需继承该接口"""

    def __init__(self, name: str, event_engine, parameters: Dict[str, Any]):
        self.name = name
        self.event_engine = event_engine
        self.parameters = parameters or {}
        self.active = False

    def start(self):
        """策略启动钩子"""
        self.active = True
        self._log(f"策略已启动，参数: {self.parameters}")

    def stop(self):
        """策略停止钩子"""
        self.active = False
        self._log("策略已停止")

    def _send_signal(self, signal_data: Dict[str, Any]):
        """生成策略信号事件"""
        event = Event(
            type_=EventType.STRATEGY_SIGNAL,
            data={
                "strategy": self.name,
                "signal": signal_data
            },
            source=self.name
        )
        self.event_engine.put(event)

    def _log(self, message: str):
        """统一日志接口"""
        event = Event(
            type_=EventType.LOG_EVENT,
            data={
                "module": self.name,
                "message": message
            },
            source=self.name
        )
        self.event_engine.put(event)

    @abstractmethod
    def on_event(self, event: Event):
        """事件处理函数（行情等）"""
        pass
