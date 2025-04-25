from vendor_api.quote_sample.my_spi import MdsClientMySpi
from typing import List, Optional

from src.data_handler import MarketDataSaver
from src.market.market_event_handler import MarketEventHandler


class MdsSpiHandler(MdsClientMySpi):
    def __init__(
        self,
        strategy_group: List,
        subscribe_codes: Optional[list[str]] = None,
        subscribe_config: Optional[dict] = None,
        event_engine=None,
    ):
        super().__init__()
        self.strategy_group = strategy_group or []
        self.subscribe_config = subscribe_config or {}
        self.subscribe_codes = [str(code) for code in (subscribe_codes or [])]
        self.data_saver = MarketDataSaver(compress=True)
        self.event_engine = event_engine
        self.market_event_handler = MarketEventHandler(event_engine)

    def on_connect(self, channel, user_info):
        print("✅ SPI 已连接，准备订阅行情...")
        if self.subscribe_config:
            self._subscribe_by_config(channel)
        else:
            self._subscribe_by_codes(channel)
        return 0

    def _subscribe_by_config(self, channel):
        try:
            for item in self.subscribe_config.get("subscriptions", []):
                codes = [str(code) for code in item.get("codes", [])]
                exch_id = item.get("exchange_id", 0)
                product_type = item.get("product_type", 1)
                sub_mode = item.get("sub_mode", 0)
                data_types = item.get("data_types", 1)

                if not codes:
                    continue

                ret = self.mds_api.subscribe_by_string(
                    channel=channel,
                    security_list=",".join(codes),
                    delimiter=",",
                    exchange_id=exch_id,
                    product_type=product_type,
                    sub_mode=sub_mode,
                    data_types=data_types
                )
                print(f"✅ 已订阅: {codes} | exch_id={exch_id}, product_type={product_type}, data_types={data_types}, ret={ret}")

        except Exception as e:
            print("❌ 订阅调用异常:", e)

    def _subscribe_by_codes(self, channel):
        try:
            codes = self.subscribe_codes
            sse_codes = [c for c in codes if c.startswith("6")]
            szse_codes = [c for c in codes if c.startswith("0") or c.startswith("3")]

            if sse_codes:
                ret1 = self.mds_api.subscribe_by_string(
                    channel=channel,
                    security_list=",".join(sse_codes),
                    delimiter=",",
                    exchange_id=1,
                    product_type=1,
                    sub_mode=0,
                    data_types=1
                )
                print("✅ 订阅请求成功！\n    SSE Stock:", ret1)
            if szse_codes:
                ret2 = self.mds_api.subscribe_by_string(
                    channel=channel,
                    security_list=",".join(szse_codes),
                    delimiter=",",
                    exchange_id=2,
                    product_type=1,
                    sub_mode=1,
                    data_types=1
                )
                print("✅ 订阅请求成功！\n    SZSE Stock:", ret2)

            print(f"✅ 已订阅股票: {codes}")

        except Exception as e:
            print("❌ 订阅调用异常:", e)

    def on_l2_market_data_snapshot(self, channel, msg_head, msg_body, user_info):
        try:
            self.market_event_handler.handle_l2_snapshot(msg_body)
        except Exception as e:
            print("❌ L2 快照事件处理异常:", e)
        return 0

    def on_l2_tick_trade(self, channel, msg_head, msg_body, user_info):
        try:
            self.market_event_handler.handle_l2_tick_trade(msg_body)
        except Exception as e:
            print("❌ 逐笔成交事件处理异常:", e)
        return 0

    def on_l2_tick_order(self, channel, msg_head, msg_body, user_info):
        try:
            self.market_event_handler.handle_l2_tick_order(msg_body)
        except Exception as e:
            print("❌ 逐笔委托事件处理异常:", e)
        return 0

    def on_l2_best_orders_snapshot(self, channel, msg_head, msg_body, user_info):
        try:
            self.market_event_handler.handle_l2_best_orders_snapshot(msg_body)
        except Exception as e:
            print("❌ L2 委托簿事件处理异常:", e)
        return 0

    def on_l2_market_overview(self, channel, msg_head, msg_body, user_info):
        try:
            self.market_event_handler.handle_l2_market_overview(msg_body)
        except Exception as e:
            print("❌ 市场总览事件处理异常:", e)
        return 0

    def on_market_data_snapshot_full_refresh(self, channel, msg_head, msg_body, user_info):
        try:
            self.market_event_handler.handle_l1_stock_snapshot(msg_body)
        except Exception as e:
            print("❌ L1 快照事件处理异常:", e)
        return 0

    def on_market_index_snapshot_full_refresh(self, channel, msg_head, msg_body, user_info):
        try:
            self.market_event_handler.handle_index_snapshot(msg_body)
        except Exception as e:
            print("❌ 指数快照事件处理异常:", e)
        return 0

    def on_market_option_snapshot_full_refresh(self, channel, msg_head, msg_body, user_info):
        try:
            self.market_event_handler.handle_option_snapshot(msg_body)
        except Exception as e:
            print("❌ 期权快照事件处理异常:", e)
        return 0
