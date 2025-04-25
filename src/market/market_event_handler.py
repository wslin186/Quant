from src.event_engine.event import Event
from src.event_engine.event_type import EventType


class MarketEventHandler:
    def __init__(self, event_engine):
        self.event_engine = event_engine

    # ---------------- Level-2 快照 ----------------
    def handle_l2_snapshot(self, msg):
        try:
            data = self._extract_common_snapshot(msg.l2Stock, msg.head)
            self._publish(EventType.MARKET_SNAPSHOT, data, "L2_SNAPSHOT")
        except Exception as e:
            self._log_error("L2快照", e)

    # -------- 其它 handler 保持结构，只要需要字段就改同样方式 --------
    # （下面代码省略，只示范一处——其余 handle_* 方法留在原文件即可）

    # ---------------- 公共工具函数 ----------------
    def _extract_common_snapshot(self, body, head):
        """抽取快照共有字段——统一成英文小写，下划线命名"""
        return {
            # --- 主要字段 ---
            "symbol":      body.SecurityID.decode(),
            "last_price":  body.TradePx,
            "volume":      body.TotalVolumeTraded,
            "trade_date":  head.tradeDate,
            "update_time": head.updateTime,

            # --- 兼容旧字段（可后续移除） ---
            "SecurityID": body.SecurityID.decode(),
            "最新价":      body.TradePx,
        }

    def _publish(self, event_type, data, source):
        self.event_engine.put(Event(type_=event_type, data=data, source=source))

    def _log_error(self, name, e):
        print(f"[MarketEventHandler] ❌ 处理{name}时异常: {e}")
