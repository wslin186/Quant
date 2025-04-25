"""
读取 strategy.yaml 并实例化策略
"""

import importlib
import yaml


def load_strategies_from_yaml(yaml_path, event_engine):
    with open(yaml_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    strategies = []
    for entry in cfg.get("strategies", []):
        module_name, class_name = entry["class"].rsplit(".", 1)
        module = importlib.import_module(module_name)
        StrategyCls = getattr(module, class_name)

        name = entry["name"]
        params = entry.get("parameters", {})
        print(f"🔄 正在加载策略 {name} ...")
        instance = StrategyCls(
            name=name,
            event_engine=event_engine,
            parameters=params
        )
        strategies.append(instance)

    return strategies
