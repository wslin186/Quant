# tests/test_log_event_handler.py

from src.event_engine.event_engine import EventEngine
from src.event_engine.event import Event
from src.event_engine.event_type import EventType
from src.event_engine.logging_handler import log_event_handler
import time

def main():
    print("🚀 启动日志事件监听测试")

    engine = EventEngine("log-test")
    engine.register(EventType.LOG_EVENT, log_event_handler)
    engine.start()

    print("🧪 投递一个日志事件")
    log_event = Event(
        type_=EventType.LOG_EVENT,
        data="测试日志：事件机制运行正常。",
        source="测试模块"
    )
    engine.put(log_event)

    time.sleep(1)  # 等待日志输出
    engine.stop()

if __name__ == "__main__":
    main()
