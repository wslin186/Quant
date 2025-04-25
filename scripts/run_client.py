from pathlib import Path
import time

from src.client import QuantClient
from src.strategy_loader import load_strategies_from_yaml
from src.config_loader import load_settings
from src.subscribe_loader import load_subscribe_config  # ✅ 专门加载订阅配置

def main():
    root = Path(__file__).resolve().parent.parent
    config_file = root / "config" / "config_file.ini"
    strategy_file = root / "config" / "strategy.yaml"
    subscribe_file = root / "config" / "subscribe.yaml"

    # 加载策略实例
    strategies = load_strategies_from_yaml(strategy_file)

    # 加载订阅配置
    subscribe_conf = load_subscribe_config(subscribe_file)
    codes = []
    for item in subscribe_conf.get("subscriptions", []):
        codes.extend(item.get("codes", []))
    print(f"📈 将订阅股票: {codes}")

    # 初始化行情客户端
    qc = QuantClient(
        config_file=config_file,
        strategies=strategies,
        subscribe_codes=codes,
        subscribe_config=subscribe_conf
    )
    qc.start()

    print("✅ 主线程挂起，等待行情回调中...")
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
