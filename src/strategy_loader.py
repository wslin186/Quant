import yaml
import importlib

def load_strategies_from_yaml(yaml_path):
    with open(yaml_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    strategies = []
    for entry in config.get("strategies", []):
        class_path = entry.get("class")
        strategy_config = entry.get("config", {})

        if not class_path:
            continue

        # 动态导入类
        module_path, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        StrategyClass = getattr(module, class_name)

        print(f"📦 正在加载策略 {entry['name']}...")
        instance = StrategyClass(config=strategy_config)
        print(f"✅ 策略实例化完成，参数： {strategy_config}")

        strategies.append(instance)

    return strategies
