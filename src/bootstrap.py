"""
系统入口——负责
1) 创建并启动 EventEngine
2) 加载策略、账户、日志处理器并注册回调
3) 实例化 QuantClient，启动行情链路
"""

from pathlib import Path
from src.event_engine import EventEngine, EventType
from src.event_engine.logging_handler import log_event_handler
from src.backtest.signal_recorder import SignalRecorder
from src.account.account_simulator import AccountSimulator
from src.strategy_loader import load_strategies_from_yaml
from src.subscribe_loader import load_subscribe_config
from src.client import QuantClient


def main():
    root = Path(__file__).resolve().parent.parent
    cfg_dir = root / "config"

    # 1. 事件引擎
    ee = EventEngine("main")
    ee.start()
    ee.register(EventType.LOG_EVENT, log_event_handler)

    # 2. 账户 & 信号记录器
    account = AccountSimulator()
    recorder = SignalRecorder()
    ee.register(EventType.STRATEGY_SIGNAL, account.on_event)
    ee.register(EventType.STRATEGY_SIGNAL, recorder.on_event)

    # 3. 加载策略（同一个 ee 注入）
    strategies = load_strategies_from_yaml(cfg_dir / "strategy.yaml", ee)
    for s in strategies:
        ee.register(EventType.MARKET_SNAPSHOT, s.on_event)

    # 4. 行情客户端
    qc = QuantClient(
        config_file=cfg_dir / "config_file.ini",
        strategies=strategies,
        subscribe_config=load_subscribe_config(cfg_dir / "subscribe.yaml"),
        event_engine=ee      # ⭐ 传入事件引擎
    )
    qc.start()

    print("✅ 系统就绪，等待行情...")
    ee._thread.join()        # 简易阻塞，按 Ctrl+C 退出


if __name__ == "__main__":
    main()
