from src.event_engine.event import Event
from src.event_engine.event_type import EventType


class MarketEventHandler:
    def __init__(self, event_engine):
        self.event_engine = event_engine

    def handle_l2_snapshot(self, msg):
        try:
            data = self._extract_common_snapshot(msg.l2Stock, msg.head)
            self._publish(EventType.MARKET_SNAPSHOT, data, "L2_SNAPSHOT")
        except Exception as e:
            self._log_error("L2快照", e)

    def handle_l2_tick_trade(self, msg):
        try:
            data = {
                "SecurityID": msg.SecurityID.decode(),
                "成交价格": msg.TradePrice,
                "成交数量": msg.TradeQty,
                "成交时间": msg.TradeTime,
                "交易日期": msg.TradeDate,
            }
            self._publish(EventType.MARKET_TICK, data, "L2_TICK_TRADE")
        except Exception as e:
            self._log_error("逐笔成交", e)

    def handle_l2_tick_order(self, msg):
        try:
            data = {
                "SecurityID": msg.SecurityID.decode(),
                "委托价格": msg.Price,
                "委托数量": msg.OrderQty,
                "委托方向": msg.Side,
                "委托类别": msg.OrderType,
                "委托时间": msg.OrderTime,
            }
            self._publish(EventType.MARKET_TICK, data, "L2_TICK_ORDER")
        except Exception as e:
            self._log_error("逐笔委托", e)

    def handle_l2_best_orders_snapshot(self, msg):
        try:
            orders = msg.l2BestOrders
            data = {
                "SecurityID": orders.SecurityID.decode(),
                "买一~买十档数量": list(orders.BidOrderQty),
                "卖一~卖十档数量": list(orders.OfferOrderQty),
                "买档位数": orders.NoBidOrders,
                "卖档位数": orders.NoOfferOrders,
            }
            self._publish(EventType.ORDER_BOOK, data, "L2_ORDER_BOOK")
        except Exception as e:
            self._log_error("委托队列", e)

    def handle_l2_market_overview(self, msg):
        try:
            overview = msg.l2MarketOverview
            data = {
                "交易所": msg.head.exchId,
                "原始日期": overview.OrigDate,
                "原始时间": overview.OrigTime,
            }
            self._publish(EventType.MARKET_SNAPSHOT, data, "L2_MARKET_OVERVIEW")
        except Exception as e:
            self._log_error("市场总览", e)

    def handle_l1_stock_snapshot(self, msg):
        try:
            data = self._extract_common_snapshot(msg.stock, msg.head)
            self._publish(EventType.MARKET_SNAPSHOT, data, "L1_STOCK_SNAPSHOT")
        except Exception as e:
            self._log_error("L1快照", e)

    def handle_index_snapshot(self, msg):
        try:
            index = msg.index
            head = msg.head
            data = {
                "SecurityID": index.SecurityID.decode(),
                "开盘价": index.OpenPx,
                "最高价": index.HighPx,
                "最低价": index.LowPx,
                "最新价": index.TradePx,
                "收盘价": index.ClosePx,
                "更新时间": head.updateTime,
            }
            self._publish(EventType.MARKET_SNAPSHOT, data, "INDEX_SNAPSHOT")
        except Exception as e:
            self._log_error("指数快照", e)

    def handle_option_snapshot(self, msg):
        try:
            option = msg.option
            head = msg.head
            data = {
                "SecurityID": option.SecurityID.decode(),
                "最新价": option.TradePx,
                "买档价格": [option.BidLevels[i].Price for i in range(5)],
                "卖档价格": [option.OfferLevels[i].Price for i in range(5)],
                "更新时间": head.updateTime,
            }
            self._publish(EventType.MARKET_SNAPSHOT, data, "OPTION_SNAPSHOT")
        except Exception as e:
            self._log_error("期权快照", e)

    def _extract_common_snapshot(self, body, head):
        """抽取快照类共有字段"""
        return {
            "SecurityID": body.SecurityID.decode(),
            "最新价": body.TradePx,
            "成交量": body.TotalVolumeTraded,
            "交易日期": head.tradeDate,
            "更新时间": head.updateTime,
        }

    def _publish(self, event_type, data, source):
        event = Event(
            type_=event_type,
            data=data,
            source=source
        )
        self.event_engine.put(event)

    def _log_error(self, name, e):
        print(f"[MarketEventHandler] ❌ 处理{name}时异常: {e}")
