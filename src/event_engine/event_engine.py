# src/event_engine/event_engine.py

import threading
import queue
import time
from typing import Callable, DefaultDict
from collections import defaultdict

from .event_type import EventType
from .event import Event


class EventEngine:
    """全局统一事件引擎，支持注册回调函数并分发事件"""

    def __init__(self, name: str = "default"):
        self.name = name
        self._queue: queue.Queue = queue.Queue()
        self._active: bool = False
        self._thread: threading.Thread = threading.Thread(target=self._run)
        self._handlers: DefaultDict[str, list[Callable[[Event], None]]] = defaultdict(list)
        self._lock = threading.Lock()

    def start(self):
        """启动事件处理线程"""
        self._active = True
        self._thread.start()

    def stop(self):
        """停止事件处理线程"""
        self._active = False
        self._thread.join()

    def _run(self):
        """事件处理主循环"""
        while self._active:
            try:
                event = self._queue.get(timeout=1)
                self._process(event)
            except queue.Empty:
                continue

    def _process(self, event: Event):
        """分发事件给所有注册的回调函数"""
        handlers = self._handlers.get(event.type, [])
        handlers += self._handlers.get("*", [])  # 通配符支持
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"[EventEngine] 处理事件异常: {e}")

    def put(self, event: Event):
        """向事件队列中注入事件"""
        self._queue.put(event)

    def register(self, event_type: str, handler: Callable[[Event], None]):
        """注册事件回调函数"""
        with self._lock:
            if handler not in self._handlers[event_type]:
                self._handlers[event_type].append(handler)

    def unregister(self, event_type: str, handler: Callable[[Event], None]):
        """注销事件回调函数"""
        with self._lock:
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)

    def _log(self, msg: str):
        print(f"[EventEngine:{self.name}] {msg}")


