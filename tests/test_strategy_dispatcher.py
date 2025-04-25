# tests/test_strategy_dispatcher.py

import time
from src.event_engine.event_engine import EventEngine
from src.event_engine.event import Event
from src.event_engine.event_type import EventType
from src.dispatcher.strategy_dispatcher import StrategyDispatcher


def main():
    print("🚀 启动 StrategyDispatcher 测试")

    engine = EventEngine("test")
    dispatcher = StrategyDispatcher(engine)
    engine.start()

    # 模拟发出一个策略部署事件
    deploy_event = Event(
        type_=EventType.STRATEGY_DEPLOY,
        data={
            "name": "ma_cross_demo",
            "class": "MaCrossStrategy",
            "symbol": "600519",
            "parameters": {"short_window": 3, "long_window": 7}
        },
        source="TEST"
    )

    engine.put(deploy_event)
    time.sleep(1)
    engine.stop()


if __name__ == "__main__":
    main()
