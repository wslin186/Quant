# tests/test_data_player.py  ← 直接覆盖整文件
import time

from src.backtest.data_player import DataPlayer
from src.strategy.ma_cross import MaCrossStrategy
from src.event_engine.event_engine import EventEngine
from src.event_engine.event_type import EventType
from src.record.signal_recorder import SignalRecorder
from src.account.account_simulator import AccountSimulator


def main() -> None:
    print("🚀 启动 DataPlayer 回测测试")

    # 1. 事件引擎
    eng = EventEngine("backtest")
    eng.start()

    # 2. 账户 & 信号记录器（各只实例化一次）
    account  = AccountSimulator(initial_cash=100_000)
    recorder = SignalRecorder()

    eng.register(EventType.STRATEGY_SIGNAL, account.on_event)
    eng.register(EventType.STRATEGY_SIGNAL, recorder.on_event)

    # 3. 策略
    params   = {"short_window": 3, "long_window": 5}
    strategy = MaCrossStrategy("ma_test", eng, params)
    eng.register(EventType.MARKET_SNAPSHOT, strategy.on_event)

    # 4. 数据播放器（mock 数据，0.1 秒一行）
    player = DataPlayer(
        event_engine=eng,
        data_source="mock",           # 也可改为 "csv"
        config={"path": "tests/data/snapshot.csv"},
        delay=0.1
    )
    player.start()

    # 5. 等待所有事件处理完
    time.sleep(2)
    eng.stop()

    # 6. 打印结果
    account.print_history()
    account.print_trades()
    recorder.print_signals()


if __name__ == "__main__":
    main()
