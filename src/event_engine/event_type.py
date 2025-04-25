# src/event_engine/event_type.py
from enum import Enum

class EventType(str, Enum):
    # 行情类
    MARKET_SNAPSHOT = "市场快照"
    MARKET_TICK = "逐笔行情"
    ORDER_BOOK = "委托簿"
    MARKET_SUBSCRIBE_REQUEST = "请求订阅行情"
    HISTORICAL_DATA_REQUEST = "请求历史数据"

    # 策略控制类
    STRATEGY_DEPLOY = "策略部署"
    STRATEGY_START = "策略启动"
    STRATEGY_STOP = "策略停止"
    STRATEGY_SIGNAL = "策略信号"

    # 交易类
    ORDER_SUBMIT = "订单提交"
    ORDER_CANCEL = "订单撤单"
    ORDER_FILLED = "订单成交"

    # 系统类
    BACKTEST_START = "回测开始"
    BACKTEST_END = "回测结束"
    HEARTBEAT = "心跳"
    LOG_EVENT = "日志事件"
    EXCEPTION = "异常事件"
    RISK_ALERT = "风控告警"

