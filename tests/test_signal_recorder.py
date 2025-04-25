import time
from src.event_engine.event_engine import EventEngine
from src.event_engine.event_type import EventType
from src.event_engine.event import Event
from src.record.signal_recorder import SignalRecorder


def main():
    print("🚀 启动 SignalRecorder 测试")

    # 初始化事件引擎
    engine = EventEngine("test")
    recorder = SignalRecorder()
    engine.register(EventType.STRATEGY_SIGNAL, recorder.on_event)
    engine.start()

    # 模拟两个策略信号事件
    events = [
        Event(EventType.STRATEGY_SIGNAL, {
            "action": "buy",
            "price": 105,
            "symbol": "600519"
        }, source="demo_strategy"),

        Event(EventType.STRATEGY_SIGNAL, {
            "action": "sell",
            "price": 115,
            "symbol": "600519"
        }, source="demo_strategy")
    ]

    for e in events:
        engine.put(e)
        time.sleep(0.1)

    engine.stop()

    # 打印捕获结果
    print("📊 策略信号记录：")
    for row in recorder.records:
        print(row)


if __name__ == "__main__":
    main()
