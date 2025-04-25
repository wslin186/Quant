# src/config_loader.py
import yaml
from pathlib import Path

def load_settings(path="config/settings.yaml"):
    config_path = Path(__file__).resolve().parent.parent / path
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_subscribe_config(config_path: str):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
