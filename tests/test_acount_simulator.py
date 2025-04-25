import time
from src.account.account_simulator import AccountSimulator
from src.event_engine.event_engine import EventEngine
from src.event_engine.event import Event
from src.event_engine.event_type import EventType

# 初始化账户模拟器
account = AccountSimulator(initial_cash=100000)

# 信号事件回调函数
def handle_strategy_signal(event: Event):
    signal = event.data
    print(f"📥 收到策略信号: {signal}")
    account.on_order_filled(signal)

def main():
    print("🚀 启动 AccountSimulator 测试")

    engine = EventEngine("account_test")
    engine.register(EventType.STRATEGY_SIGNAL, handle_strategy_signal)
    engine.start()

    # 模拟策略信号：买入 + 卖出
    signals = [
        {"action": "buy", "symbol": "600519", "price": 100},
        {"action": "sell", "symbol": "600519", "price": 110}
    ]

    for sig in signals:
        event = Event(type_=EventType.STRATEGY_SIGNAL, data=sig, source="test_strategy")
        engine.put(event)
        time.sleep(0.5)

    engine.stop()

    # 输出结果
    account.print_trades()
    account.print_history()

if __name__ == "__main__":
    main()
