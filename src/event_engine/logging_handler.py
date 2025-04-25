# src/event_engine/logging_handler.py

from .event import Event
from .event_type import EventType
import time

def log_event_handler(event: Event):
    """通用日志事件处理器"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(event.timestamp))
    print(
        f"[日志事件] 时间: {timestamp} | 类型: {event.type} | 来源: {event.source or '未知'}\n"
        f"➡ 内容: {event.data}"
    )
