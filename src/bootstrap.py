from pathlib import Path
import time
import yaml

from utils.logger import get_logger
from src.event_engine.event_engine import EventEngine
from src.event_engine.event_type import EventType
from src.client import QuantClient
from src.strategy_loader import load_strategies_from_yaml
from src.account.account_simulator import AccountSimulator
from src.record.signal_recorder import SignalRecorder


def main() -> None:
    # ── 读取全局配置 ───────────────────────────
    cfg_dir = Path(__file__).resolve().parent.parent / "config"
    settings = yaml.safe_load(open(cfg_dir / "settings.yaml", encoding="utf-8"))

    log_level = settings.get("log_level", "INFO")
    log_file  = settings.get("log_file", "logs/quant.log")
    run_mode  = settings.get("run_mode", "realtime")

    logger = get_logger("Quant", log_level, log_file)
    logger.info("🚀 Quant 启动 | run_mode=%s | log_level=%s", run_mode, log_level)

    # ── 事件引擎 ─────────────────────────────
    ee = EventEngine("main")
    ee.start()

    # ── 账户 & 记录器 ───────────────────────
    account  = AccountSimulator()
    recorder = SignalRecorder(verbose=(log_level in ("DEBUG", "INFO")))

    ee.register(EventType.STRATEGY_SIGNAL, account.on_event)
    ee.register(EventType.MARKET_SNAPSHOT, account.on_event)
    ee.register(EventType.STRATEGY_SIGNAL, recorder.on_event)

    # ── 加载策略 ───────────────────────────
    strategies = load_strategies_from_yaml(cfg_dir / "strategy.yaml", ee)
    for st in strategies:
        ee.register(EventType.MARKET_SNAPSHOT, st.on_event)

    # ── 启动数据源 ─────────────────────────
    if run_mode == "realtime":
        qc = QuantClient(
            config_file=cfg_dir / "config_file.ini",
            strategies=strategies,
            subscribe_codes=[],
            subscribe_config=yaml.safe_load(open(cfg_dir / "subscribe.yaml", encoding="utf-8"))
        )
        qc.start()
        logger.info("✅ 实时行情启动完成")

    else:  # backtest / replay
        from src.backtest.data_player import DataPlayer
        player = DataPlayer(event_engine=ee, data_source="mock", delay=0.1)
        player.start()
        logger.info("✅ 数据回放开始")
        time.sleep(2)

    # ── 停止并输出结果 ─────────────────────
    ee.stop()
    account.print_history()
    account.print_trades()
    recorder.print_signals()


if __name__ == "__main__":
    main()
