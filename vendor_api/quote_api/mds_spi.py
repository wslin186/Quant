# -*- coding: utf-8 -*-
"""
MdsClientSpi
"""

from typing import Any, Optional
from abc import abstractmethod

from quote_api.model import (
    # spk_util.py
    SMsgHeadT, MdsAsyncApiChannelT,

    # mds_base_model.py
    eMdsExchangeIdT, eMdsMdProductTypeT,
    MdsTradingSessionStatusMsgT, MdsSecurityStatusMsgT, MdsL1SnapshotT,
    MdsL2StockSnapshotBodyT, MdsL2BestOrdersSnapshotBodyT, MdsL2MarketOverviewT,
    MdsMktDataSnapshotT, MdsL2TradeT, MdsL2OrderT, MdsTickChannelHeartbeatT,
    MdsStockStaticInfoT, MdsOptionStaticInfoT,

    # mds_qry_packets.py
    MdsQryCursorT, MdsQryStockStaticInfoListFilterT,

    # mds_mkt_pachets.py
    eMdsMsgTypeT, eMdsSubscribeModeT, eMdsSubscribeDataTypeT,
    MdsMktDataRequestRspT, MdsTestRequestRspT, MdsChangePasswordRspT,
    MdsTickResendRequestRspT
)


class MdsClientSpi:
    """
    行情接口响应基类
    """

    def __init__(self):
        # @note 解决与mds_api.py互相引用的问题, 故在此导入
        from quote_api.mds_api import MdsClientApi

        self.mds_api: Optional[MdsClientApi] = None

    @abstractmethod
    def on_connect(self,
            channel: MdsAsyncApiChannelT,
            user_info: Any) -> int:
        """
        异步API线程连接或重新连接完成后的回调函数

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            user_info (Any): [用户回调参数]
        """
        # 返回值说明:
        # - 返回大于0的值, 表示需要继续执行默认的 OnConnect 回调处理
        #   - 对于行情订阅通道, 将使用配置文件中的订阅参数订阅回报
        # - 若返回0, 表示已经处理成功
        #   - 包括行情订阅通道的数据订阅操作也需要显式的调用并执行成功, 将不再执行默认的回调处理
        # - 返回小于0的值, 处理失败, 异步API将中止运行

        return 1

    @abstractmethod
    def on_connect_failed(self,
            channel: MdsAsyncApiChannelT,
            user_info: Any) -> int:
        """
        异步API线程连接失败后的回调函数
        - OnConnectFailed 和 OnDisconnect 回调函数的区别在于:
          - 在连接成功以前:
            - 当尝试建立或重建连接时, 如果连接失败则回调 OnConnectFailed;
            - 如果连接成功, 则回调 OnConnect;
          - 在连接成功以后:
            - 如果发生连接中断, 则回调 OnDisconnect.

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            user_info (Any): [用户回调参数]

        Returns:
            int: [
                    >=0 大于等于0, 异步线程将尝试重建连接并继续执行
                    <0  小于0, 异步线程将中止运行
                 ]
        """

        return 0

    @abstractmethod
    def on_disconnect(self,
            channel: MdsAsyncApiChannelT,
            user_info: Any) -> int:
        """
        异步API线程连接断开后的回调函数
        - 仅用于通知客户端连接已经断开, 无需做特殊处理, 异步线程会自动尝试重建连接

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            user_info (Any): [用户回调参数]

        Returns:
            int: [
                    >=0 大于等于0, 异步线程将尝试重建连接并继续执行
                    <0  小于0, 异步线程将中止运行
                 ]
        """

        return 0

    # ===================================================================
    # MDS行情订阅接口对应的回调函数
    # ===================================================================

    @abstractmethod
    def on_l2_tick_trade(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: MdsL2TradeT,
            user_info: Any) -> int:
        """
        处理Level2 逐笔成交数据消息的回调函数

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            msg_head (SMsgHeadT): [回报消息的消息头]
            msg_body (MdsL2TradeT): [Level2 逐笔成交数据的消息]
            user_info (Any): [用户回调参数]
        """

        return 0

    @abstractmethod
    def on_l2_tick_order(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: MdsL2OrderT,
            user_info: Any) -> int:
        """
        处理Level2 逐笔委托数据消息的回调函数

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            msg_head (SMsgHeadT): [回报消息的消息头]
            msg_body (MdsL2OrderT): [Level2 逐笔委托数据的消息]
            user_info (Any): [用户回调参数]
        """

        return 0

    @abstractmethod
    def on_l2_market_data_snapshot(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: MdsL2StockSnapshotBodyT,
            user_info: Any) -> int:
        """
        处理Level2 快照行情数据消息的回调函数

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            msg_head (SMsgHeadT): [回报消息的消息头]
            msg_body (MdsL2StockSnapshotBodyT): [Level2 快照行情数据的消息]
            user_info (Any): [用户回调参数]
        """

        return 0

    @abstractmethod
    def on_l2_best_orders_snapshot(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: MdsL2BestOrdersSnapshotBodyT,
            user_info: Any) -> int:
        """
        处理Level2 委托队列信息的回调函数

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            msg_head (SMsgHeadT): [回报消息的消息头]
            msg_body (MdsL2BestOrdersSnapshotBodyT): [Level2 委托队列信息]
            user_info (Any): [用户回调参数]
        """

        return 0

    @abstractmethod
    def on_l2_market_overview(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: MdsL2MarketOverviewT,
            user_info: Any) -> int:
        """
        处理Level2 市场总览消息的回调函数

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            msg_head (SMsgHeadT): [回报消息的消息头]
            msg_body (MdsL2MarketOverviewT): [Level2 市场总览消息]
            user_info (Any): [用户回调参数]
        """

        return 0

    @abstractmethod
    def on_market_data_snapshot_full_refresh(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: MdsMktDataSnapshotT,
            user_info: Any) -> int:
        """
        处理Level1 股票快照行情消息的回调函数

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            msg_head (SMsgHeadT): [回报消息的消息头]
            msg_body (MdsMktDataSnapshotT): [Level1 股票行情数据的消息]
            user_info (Any): [用户回调参数]
        """

        return 0

    @abstractmethod
    def on_market_index_snapshot_full_refresh(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: MdsMktDataSnapshotT,
            user_info: Any) -> int:
        """
        处理指数快照行情消息的回调函数

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            msg_head (SMsgHeadT): [回报消息的消息头]
            msg_body (MdsMktDataSnapshotT): [指数快照行情数据的消息]
            user_info (Any): [用户回调参数]
        """

        return 0

    @abstractmethod
    def on_market_option_snapshot_full_refresh(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: MdsMktDataSnapshotT,
            user_info: Any) -> int:
        """
        处理期权快照行情消息的回调函数

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            msg_head (SMsgHeadT): [回报消息的消息头]
            msg_body (MdsMktDataSnapshotT): [期权快照行情数据的消息]
            user_info (Any): [用户回调参数]
        """

        return 0

    @abstractmethod
    def on_security_status(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: MdsSecurityStatusMsgT,
            user_info: Any) -> int:
        """
        处理证券实时状态消息的回调函数 (仅适用于深交所, 上交所行情中没有该数据)

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            msg_head (SMsgHeadT): [回报消息的消息头]
            msg_body (MdsSecurityStatusMsgT): [证券实时状态的消息]
            user_info (Any): [用户回调参数]
        """

        return 0

    @abstractmethod
    def on_trading_session_status(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: MdsTradingSessionStatusMsgT,
            user_info: Any) -> int:
        """
        处理市场状态消息的回调函数 (仅适用于上交所, 深交所行情中没有该数据)

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            msg_head (SMsgHeadT): [回报消息的消息头]
            msg_body (MdsTradingSessionStatusMsgT): [市场状态的消息]
            user_info (Any): [用户回调参数]
        """

        return 0

    @abstractmethod
    def on_tick_channel_heart_beat(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: MdsTickChannelHeartbeatT,
            user_info: Any) -> int:
        """
        处理Level2 逐笔频道心跳消息的回调函数

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            msg_head (SMsgHeadT): [回报消息的消息头]
            msg_body (MdsTradingSessionStatusMsgT): [Level2 逐笔频道心跳的消息]
            user_info (Any): [用户回调参数]
        """

        return 0

    @abstractmethod
    def on_market_data_request_rsp(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: MdsMktDataRequestRspT,
            user_info: Any) -> int:
        """
        行情订阅请求应答报文的回调函数

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            msg_head (SMsgHeadT): [回报消息的消息头]
            msg_body (MdsMktDataRequestRspT): [行情订阅请求的应答报文]
            user_info (Any): [用户回调参数]
        """

        return 0

    @abstractmethod
    def on_test_request_rsp(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: MdsTestRequestRspT,
            user_info: Any) -> int:
        """
        测试请求应答报文的回调函数

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            msg_head (SMsgHeadT): [回报消息的消息头]
            msg_body (MdsTestRequestRspT): [测试请求的应答报文]
            user_info (Any): [用户回调参数]
        """

        return 0

    @abstractmethod
    def on_heart_beat(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: Any,
            user_info: Any) -> int:
        """
        心跳应答报文的回调函数

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            msg_head (SMsgHeadT): [回报消息的消息头]
            msg_body (Any): [心跳的应答报文]
            user_info (Any): [用户回调参数]
        """

        return 0

    @abstractmethod
    def on_compressed_packets(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: Any,
            user_info: Any) -> int:
        """
        接收到了压缩后的行情数据的回调函数

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            msg_head (SMsgHeadT): [回报消息的消息头]
            msg_body (Any): [接收到了压缩后的行情数据]
            user_info (Any): [用户回调参数]
        """

        return 0
    # -------------------------


    # ===================================================================
    # MDS查询接口对应的回调函数
    # ===================================================================

    @abstractmethod
    def on_qry_security_status(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: MdsSecurityStatusMsgT,
            user_info: Any) -> int:
        """
        查询深交所证券实时状态 (MdsSecurityStatusMsgT)

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            msg_head (SMsgHeadT): [回报消息的消息头]
            - 当前回调函数暂未启用
            msg_body (MdsSecurityStatusMsgT): [查询应答的数据条目]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """

        return 0

    @abstractmethod
    def on_qry_trd_session_status(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: MdsTradingSessionStatusMsgT,
            user_info: Any) -> int:
        """
        查询上交所市场状态 (MdsTradingSessionStatusMsgT)

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            msg_head (SMsgHeadT): [回报消息的消息头]
            - 当前回调函数暂未启用
            msg_body (MdsTradingSessionStatusMsgT): [查询应答的数据条目]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """

        return 0

    @abstractmethod
    def on_qry_mkt_data_snapshot(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: MdsMktDataSnapshotT,
            user_info: Any) -> int:
        """
        查询证券行情快照 (MdsMktDataSnapshotT)

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            msg_head (SMsgHeadT): [回报消息的消息头]
            - 当前回调函数暂未启用
            msg_body (MdsMktDataSnapshotT): [查询应答的数据条目]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """

        return 0

    @abstractmethod
    def on_qry_snapshot_list(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: MdsL1SnapshotT,
            qry_cursor: MdsQryCursorT,
            user_info: Any) -> int:
        """
        用于处理快照行情查询结果的回调函数 (MdsL1SnapshotT)

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            msg_head (SMsgHeadT): [回报消息的消息头]
            msg_body (MdsL1SnapshotT): [查询应答的数据条目]
            qry_cursor (MdsQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """

        return 0

    @abstractmethod
    def on_qry_stock_static_info_list(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: MdsStockStaticInfoT,
            qry_cursor: MdsQryCursorT,
            user_info: Any) -> int:
        """
        用于处理批量查询证券(股票/债券/基金)静态信息列表的回调函数 (MdsStockStaticInfoT)

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            msg_head (SMsgHeadT): [回报消息的消息头]
            msg_body (MdsStockStaticInfoT): [查询应答的数据条目]
            qry_cursor (MdsQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """

        return 0

    @abstractmethod
    def on_qry_option_static_info_list(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: MdsOptionStaticInfoT,
            qry_cursor: MdsQryCursorT,
            user_info: Any) -> int:
        """
        用于处理批量查询期权静态信息列表的回调函数 (MdsOptionStaticInfoT)

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            msg_head (SMsgHeadT): [回报消息的消息头]
            msg_body (MdsOptionStaticInfoT): [查询应答的数据条目]
            qry_cursor (MdsQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """

        return 0
    # -------------------------


    # ===================================================================
    # MDS逐笔数据重传结果应答的回调处理函数
    # ===================================================================

    @abstractmethod
    def on_tick_resend_rsp(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: MdsTickResendRequestRspT,
            qry_cursor: MdsQryCursorT,
            user_info: Any) -> int:
        """
        对逐笔数据重传请求的应答消息进行处理的回调函数 (MdsMktRspMsgBodyT)

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            msg_head (SMsgHeadT): [回报消息的消息头]
            msg_body (MdsMktRspMsgBodyT): [查询应答的数据条目]
            - 消息体的数据类型包括:
              - MDS_MSGTYPE_L2_TRADE            => @see MdsL2TradeT
              - MDS_MSGTYPE_L2_ORDER            => @see MdsL2OrderT
              - MDS_MSGTYPE_L2_SSE_ORDER        => @see MdsL2OrderT
              - MDS_MSGTYPE_TICK_RESEND_REQUEST => @see MdsTickResendRequestRspT
            qry_cursor (MdsQryCursorT): [指示查询进度的游标]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功; <0: 处理失败 (负的错误号)]
        """

        return 0
    # -------------------------


    # ===================================================================
    # MDS密码修改结果应答的回调处理函数
    # ===================================================================

    @abstractmethod
    def on_change_password_rsp(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: MdsChangePasswordRspT) -> int:
        """
        对密码修改应答消息进行处理的回调函数 (MdsChangePasswordRspT)

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            msg_head (SMsgHeadT): [回报消息的消息头]
            msg_body (MdsChangePasswordRspT): [密码修改应答信息]
        """

        return 0
    # -------------------------
