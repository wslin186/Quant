import time
from src.backtest.data_player import DataPlayer
from src.strategy.ma_cross_strategy import MaCrossStrategy
from src.event_engine.event_engine import EventEngine
from src.event_engine.event_type import EventType
from src.event_engine.event import Event
from src.record.signal_recorder import SignalRecorder
from src.account.account_simulator import AccountSimulator


def main():
    print("🚀 启动 DataPlayer 回测测试")

    # 初始化事件引擎
    engine = EventEngine("backtest")
    engine.start()

    account = AccountSimulator()
    recorder = SignalRecorder()
    engine.register(EventType.STRATEGY_SIGNAL, account.on_event)
    engine.register(EventType.STRATEGY_SIGNAL, recorder.on_event)

    # 初始化策略
    params = {"short_window": 3, "long_window": 5}
    strategy = MaCrossStrategy("ma_test", engine, params)
    engine.register(EventType.MARKET_SNAPSHOT, strategy.on_event)

    # 初始化记录器和账户模拟器
    recorder = SignalRecorder()
    account = AccountSimulator(initial_cash=100000)

    engine.register(EventType.STRATEGY_SIGNAL, recorder.on_event)
    engine.register(EventType.STRATEGY_SIGNAL, account.on_event)

    # 初始化数据播放器（可改为 csv 或 local）
    player = DataPlayer(
        event_engine=engine,
        data_source="mock",  # 可选: "mock" / "csv" / "local"
        config={"path": "tests/data/snapshot.csv"},  # 如果是csv
        delay=0.1
    )

    # 播放数据
    player.start()

    # 等待事件全部处理
    time.sleep(2)
    engine.stop()

    account.print_history()

    account.print_trades()

    recorder.print_signals()


if __name__ == "__main__":
    main()
