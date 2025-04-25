import time
from src.strategy.ma_cross_strategy import MaCrossStrategy
from src.event_engine.event_engine import EventEngine
from src.event_engine.event import Event
from src.event_engine.event_type import EventType


def handle_signal(event: Event):
    print(f"📢 策略发出信号: {event.data}")


def main():
    print("🚀 启动 MaCrossStrategy 策略测试")

    # 初始化事件引擎并注册信号监听
    engine = EventEngine("test")
    engine.register(EventType.STRATEGY_SIGNAL, handle_signal)
    engine.start()

    # 初始化策略
    parameters = {"short_window": 3, "long_window": 5}
    strategy = MaCrossStrategy(name="ma_test", event_engine=engine, parameters=parameters)
    engine.register(EventType.MARKET_SNAPSHOT, strategy.on_event)

    # 模拟连续的价格快照事件
    prices = [100, 100, 100, 110, 120, 130, 140, 130, 120, 110, 100, 90]
    for px in prices:
        event = Event(
            type_=EventType.MARKET_SNAPSHOT,
            data={"SecurityID": "600519", "TradePx": px, "交易日期": 20250424, "更新时间": 93100000},
            source="TEST"
        )
        engine.put(event)
        time.sleep(0.1)

    engine.stop()


if __name__ == "__main__":
    main()
