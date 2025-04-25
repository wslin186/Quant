# src/utils/logger.py
import logging
import sys
from pathlib import Path

_LOGGERS: dict[str, logging.Logger] = {}


def get_logger(name: str = "Quant",
               level: str | int = "INFO",
               log_file: str | None = None) -> logging.Logger:
    """
    按 name 获取单例 logger，终端彩色 + 可选写文件。
    level 既可传字符串 DEBUG/INFO…，也可传数字 10/20…
    """
    if name in _LOGGERS:
        return _LOGGERS[name]

    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(level if isinstance(level, int) else level.upper())

    # 控制台
    c_fmt = "\033[96m%(asctime)s\033[0m [%(levelname)s] \033[92m%(name)s\033[0m - %(message)s"
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(logging.Formatter(c_fmt, datefmt="%H:%M:%S"))
    logger.addHandler(ch)

    # 文件（可选）
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        f_fmt = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(logging.Formatter(f_fmt, datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(fh)

    _LOGGERS[name] = logger
    return logger
