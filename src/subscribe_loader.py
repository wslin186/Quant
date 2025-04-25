# src/subscribe_loader.py

import yaml
from pathlib import Path

def load_subscribe_config(path: str = "config/subscribe.yaml") -> dict:
    path = Path(path).resolve()
    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config  # 🔁 直接返回整个结构即可
