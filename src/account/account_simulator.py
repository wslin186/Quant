import datetime
from src.event_engine.event_type import EventType


class AccountSimulator:
    def __init__(self, initial_cash=1_000_000):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.position = {}  # symbol -> quantity
        self.trades = []    # 成交记录：每一笔交易
        self.history = []   # 每次更新的账户状态

    def on_event(self, event):
        if event.type == EventType.STRATEGY_SIGNAL:
            self.on_order_filled(event.data)

    def on_order_filled(self, signal: dict):
        symbol = signal["symbol"]
        action = signal["action"]
        price = signal["price"]
        volume = signal.get("volume", 100)  # 默认为100股
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if action == "buy":
            cost = price * volume
            if self.cash >= cost:
                self.cash -= cost
                self.position[symbol] = self.position.get(symbol, 0) + volume
                self.trades.append([time, "buy", symbol, price, volume])
            else:
                print("❌ 资金不足，买入失败")

        elif action == "sell":
            if self.position.get(symbol, 0) >= volume:
                self.cash += price * volume
                self.position[symbol] -= volume
                self.trades.append([time, "sell", symbol, price, volume])
            else:
                print("❌ 持仓不足，卖出失败")

        # 记录账户快照
        self._snapshot(time)

    def _snapshot(self, time):
        snapshot = {
            "time": time,
            "cash": self.cash,
            "position": dict(self.position),
            "total_value": self.cash + sum(
                qty * 0  # 此处价格=0，后续接入实时行情估值
                for qty in self.position.values()
            )
        }
        self.history.append(snapshot)

    def print_trades(self):
        print("📋 [成交记录]")
        for row in self.trades:
            ts, action, symbol, price, qty = row
            print(
                f"  - 时间: {ts} | 操作: {'买入' if action == 'buy' else '卖出'} | 标的: {symbol} | 价格: {price} | 数量: {qty}")

    def print_history(self):
        print("📈 [账户资产变化]")
        for record in self.history:
            time_str = record['time']
            cash = record['cash']
            position = record['position']
            value = record['total_value']
            pos_str = ", ".join([f"{k}: {v}" for k, v in position.items()])
            print(f"  - 时间: {time_str} | 现金: {cash} | 持仓: {pos_str or '无'} | 总资产: {value}")

