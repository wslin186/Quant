# tests/test_event_engine.py

import time
from src.event_engine.event_engine import EventEngine
from src.event_engine.event import Event
from src.event_engine.event_type import EventType


def handle_custom_event(event: Event):
    print(f"📬 收到事件: {event.type} | 数据: {event.data}")


def main():
    print("🚀 启动事件引擎测试")
    engine = EventEngine()
    engine.register(EventType.CUSTOM, handle_custom_event)
    engine.start()

    # 推送测试事件
    event = Event(type=EventType.CUSTOM, data={"msg": "Hello EventEngine!"})
    engine.put(event)

    # 等待处理完成
    time.sleep(1)

    engine.stop()
    print("🛑 停止事件引擎")


if __name__ == "__main__":
    main()
