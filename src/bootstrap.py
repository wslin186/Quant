# src/bootstrap.py
from pathlib import Path
from src.event_engine import EventEngine, EventType
from src.event_engine.logging_handler import log_event_handler
from src.account.account_simulator import AccountSimulator
from src.backtest.signal_recorder import SignalRecorder
from src.strategy_loader import load_strategies_from_yaml
from src.subscribe_loader import load_subscribe_config
from src.client import QuantClient

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "config"

def main():
    # 1. 启动事件引擎
    ee = EventEngine("main")
    ee.start()
    ee.register(EventType.LOG_EVENT, log_event_handler)   # 可选：统一日志

    # 2. 账户 & 信号记录器
    account = AccountSimulator()
    recorder = SignalRecorder()
    ee.register(EventType.STRATEGY_SIGNAL, account.on_event)
    ee.register(EventType.STRATEGY_SIGNAL, recorder.on_event)

    # 3. 加载策略 —— 立刻把同一个 ee 注入
    strategies = load_strategies_from_yaml(CFG / "strategy.yaml", ee)
    for s in strategies:
        ee.register(EventType.MARKET_SNAPSHOT, s.on_event)

    # 4. 启动行情客户端（下一步会改造 QuantClient）
    qc = QuantClient(
        config_file=CFG / "config_file.ini",
        strategies=strategies,
        subscribe_config=load_subscribe_config(CFG / "subscribe.yaml"),
        event_engine=ee          # ⭐ 新参数
    )
    qc.start()

    print("✅ 系统就绪，等待行情……")
    ee._thread.join()            # 简易阻塞

if __name__ == "__main__":
    main()
