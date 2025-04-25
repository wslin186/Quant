# src/dispatcher/strategy_dispatcher.py

from src.event_engine.event import Event
from src.event_engine.event_type import EventType


class StrategyDispatcher:
    def __init__(self, event_engine):
        self.event_engine = event_engine
        self.strategies = {}  # 已部署的策略集合
        self.event_engine.register(EventType.STRATEGY_DEPLOY, self.on_deploy)

    def on_deploy(self, event: Event):
        try:
            strategy_info = event.data
            strategy_name = strategy_info.get("name")
            parameters = strategy_info.get("parameters", {})
            print(f"🧠 接收到策略部署请求: {strategy_name} | 参数: {parameters}")

            # TODO: 后续这里会触发 MARKET_SUBSCRIBE_REQUEST 或 HISTORICAL_DATA_REQUEST 等事件

            # 先记录策略，等待后续调度
            self.strategies[strategy_name] = strategy_info

        except Exception as e:
            print(f"[StrategyDispatcher] ❌ 处理部署事件异常: {e}")
