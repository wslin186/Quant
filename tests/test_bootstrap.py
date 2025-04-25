from src.event_engine import EventEngine, EventType, Event
from src.strategy.ma_cross import MaCrossStrategy

ee = EventEngine()
ee.start()
s = MaCrossStrategy("test", ee, {"short_window": 3, "long_window": 5})
ee.register(EventType.MARKET_SNAPSHOT, s.on_event)

prices = [100,101,102,103,104,102,100,98,96]
for p in prices:
    snapshot = {
        "SecurityID": "600519",
        "TradePx": p
    }
    ee.put(Event(type_=EventType.MARKET_SNAPSHOT, data=snapshot, source="unit"))
