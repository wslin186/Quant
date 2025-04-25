import datetime
from src.event_engine.event_type import EventType
from utils.logger import get_logger

logger = get_logger("Account")


class AccountSimulator:
    def __init__(self, initial_cash: int = 1_000_000):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.position: dict[str, int] = {}
        self.trades:   list[list] = []
        self.history:  list[dict] = []
        self._last_prices: dict[str, float] = {}

    # ========== 事件入口 ==========
    def on_event(self, event):
        if event.type == EventType.STRATEGY_SIGNAL:
            self._on_order_filled(event.data)
        elif event.type == EventType.MARKET_SNAPSHOT:
            self._on_price(event.data)

    # ---------- 信号处理 ----------
    def _on_order_filled(self, sig: dict):
        sym, act, price = sig["symbol"], sig["action"], sig["price"]
        vol = sig.get("volume", 100)
        ts  = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if act == "buy":
            cost = price * vol
            if self.cash < cost:
                logger.warning("资金不足：cash=%s cost=%s", self.cash, cost)
                return
            self.cash -= cost
            self.position[sym] = self.position.get(sym, 0) + vol
        else:
            if self.position.get(sym, 0) < vol:
                logger.warning("持仓不足：%s 想卖 %s 现有 %s", sym, vol, self.position.get(sym, 0))
                return
            self.cash += price * vol
            self.position[sym] -= vol

        self.trades.append([ts, act, sym, price, vol])
        self._last_prices[sym] = price
        self._snapshot(ts)

    # ---------- 行情估值 ----------
    def _on_price(self, md: dict):
        sym, price = md.get("SecurityID"), md.get("TradePx")
        if sym and price is not None:
            self._last_prices[sym] = price
            if self.position.get(sym, 0):
                self._snapshot(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # ---------- 快照 ----------
    def _snapshot(self, ts: str):
        total = self.cash + sum(q * self._last_prices.get(s, 0)
                                for s, q in self.position.items())
        self.history.append({
            "time": ts,
            "cash": self.cash,
            "position": dict(self.position),
            "total_value": total
        })

    # ---------- 输出 ----------
    def print_trades(self):
        logger.info("📋 [成交记录]")
        for ts, act, sym, p, q in self.trades:
            logger.info("  - %s | %s | %s | %s | %s", ts,
                        "买入" if act == "buy" else "卖出", sym, p, q)

    def print_history(self):
        logger.info("📈 [账户资产变化]")
        for r in self.history:
            pos = ", ".join(f"{k}:{v}" for k, v in r['position'].items()) or "无"
            logger.info("  - %s | 现金:%s | 持仓:%s | 总资产:%s",
                        r['time'], r['cash'], pos, r['total_value'])
