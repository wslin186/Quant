import time
from src.event_engine.event_engine import EventEngine
from src.market.market_event_handler import MarketEventHandler
from src.event_engine.event_type import EventType


class MockL2Stock:
    def __init__(self):
        self.SecurityID = b"600519"
        self.TradePx = 1580000
        self.TotalVolumeTraded = 24000
        self.BidLevels = [type("Bid", (), {"Price": i}) for i in range(10)]
        self.OfferLevels = [type("Offer", (), {"Price": i + 10}) for i in range(10)]
        self.BidOrderQty = list(range(10))
        self.OfferOrderQty = list(range(10))
        self.NoBidOrders = 10
        self.NoOfferOrders = 10


class MockMsgHead:
    def __init__(self):
        self.updateTime = 93100000
        self.tradeDate = 20250424
        self.exchId = 1


class MockMsg:
    def __init__(self, kind="l2Stock"):
        self.head = MockMsgHead()
        self.l2Stock = MockL2Stock()
        self.stock = self.l2Stock
        self.TradeTime = 93100000
        self.TradeDate = 20250424
        self.index = type("Index", (), {
            "SecurityID": b"000001",
            "OpenPx": 1000, "HighPx": 2000,
            "LowPx": 900, "TradePx": 1500, "ClosePx": 1400
        })()
        self.option = type("Option", (), {
            "SecurityID": b"100001",
            "TradePx": 320,
            "BidLevels": [type("Bid", (), {"Price": 1}) for _ in range(5)],
            "OfferLevels": [type("Offer", (), {"Price": 2}) for _ in range(5)]
        })()
        self.l2BestOrders = self.l2Stock
        self.l2MarketOverview = type("Overview", (), {
            "OrigDate": 20250424,
            "OrigTime": 93100000
        })()
        self.SecurityID = b"300001"
        self.TradePrice = 145000
        self.TradeQty = 100
        self.Price = 145000
        self.OrderQty = 200
        self.OrderType = "1"
        self.Side = "B"
        self.OrderTime = 93100000


def handle_event(event):
    print(f"✅ 捕获事件: 类型={event.type}, 来源={event.source}, 数据={event.data}")


def main():
    print("🚀 启动 MarketEventHandler 测试")
    engine = EventEngine("test")
    engine.register("*", handle_event)
    engine.start()

    handler = MarketEventHandler(engine)

    msg = MockMsg()
    handler.handle_l2_snapshot(msg)
    handler.handle_l2_tick_trade(msg)
    handler.handle_l2_tick_order(msg)
    handler.handle_l2_best_orders_snapshot(msg)
    handler.handle_l2_market_overview(msg)
    handler.handle_l1_stock_snapshot(msg)
    handler.handle_index_snapshot(msg)
    handler.handle_option_snapshot(msg)

    time.sleep(1)
    engine.stop()


if __name__ == "__main__":
    main()
