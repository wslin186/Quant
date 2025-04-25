# src/event_engine/event.py

import time

class Event:
    def __init__(self, type_, data=None, timestamp=None, source=None):
        self.type = type_
        self.data = data
        self.timestamp = timestamp or time.time()
        self.source = source

    def __repr__(self):
        return (
            f"<Event | 类型: {self.type}, 来源: {self.source}, "
            f"时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.timestamp))}, "
            f"数据: {self.data}>"
        )
