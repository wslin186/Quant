# -*- coding: utf-8 -*-
"""
capi消息分发相关
"""

from ctypes import (
    c_void_p, POINTER, _Pointer, cast
)

from typing import (
    Any, Callable, Dict, List, Tuple, Optional
)

from functools import (
    partial
)

from quote_api.model import (
    # spk_util.py
    CFuncPointer, memcpy, SMsgHeadT, VOID_NULLPTR,
    MdsAsyncApiChannelT, MdsAsyncApiChannelCfgT,

    # mds_base_model.py
    MdsL1SnapshotT, MdsStockStaticInfoT, MdsOptionStaticInfoT,

    # mds_qry_packets.py
    MdsQryCursorT,

    # mds_mkt_pachets.py
    eMdsMsgTypeT, MdsMktRspMsgBodyT,
)

from quote_api.mds_spi import (
    MdsClientSpi
)

from .mds_func_loader import (
    F_MDSAPI_ASYNC_ON_MSG_T,
    F_MDSAPI_ASYNC_ON_QRY_MSG_T,
    F_MDSAPI_ASYNC_ON_CONNECT_T,
    F_MDSAPI_ASYNC_ON_DISCONNECT_T,
    CMdsApiFuncLoader, log_error
)


# ===================================================================
# MDS消息ID对应回调函数的派发规则定义
# dict字典说明:
# - {消息ID, Tuple[]}
# - KEY  : 消息ID
# - VALUE: tuple元组
#   - tuple元组说明:
#     - 0号元素: MDS回报消息结构体
#     - 1号元素: MDS回报的回调函数 (@note 参数5:MdsQryCursorT 仅适用于查询相关定义)
# ===================================================================

_MDS_MSG_ID_TO_CALLBACK: Dict[
    int,
    Tuple[Any, Callable[[MdsAsyncApiChannelT, MdsClientSpi, SMsgHeadT, Any, MdsQryCursorT, Any], Any]]
] = {

        # ===================================================================
        # 行情数据回报相关消息定义
        # ===================================================================

        # Level2 逐笔成交行情 (22/0x16) @see MdsL2TradeT
        eMdsMsgTypeT.MDS_MSGTYPE_L2_TRADE: [
            MdsMktRspMsgBodyT,
            lambda channel, spi, msg_head, msg_body, _, user_info:
            spi.on_l2_tick_trade(
                channel,
                msg_head,
                msg_body.trade,
                user_info)
        ],

        # Level2 深交所逐笔委托行情 (23/0x17, 仅适用于深交所) @see MdsL2OrderT
        eMdsMsgTypeT.MDS_MSGTYPE_L2_ORDER: [
            MdsMktRspMsgBodyT,
            lambda channel, spi, msg_head, msg_body, _, user_info:
            spi.on_l2_tick_order(
                channel,
                msg_head,
                msg_body.order,
                user_info)
        ],

        # Level2 上交所逐笔委托行情 (28/0x1C, 仅适用于上交所) @see MdsL2OrderT
        eMdsMsgTypeT.MDS_MSGTYPE_L2_SSE_ORDER: [
            MdsMktRspMsgBodyT,
            lambda channel, spi, msg_head, msg_body, _, user_info:
            spi.on_l2_tick_order(
                channel,
                msg_head,
                msg_body.order,
                user_info)
        ],

        # Level2 市场行情快照 (20/0x14) @see MdsL2StockSnapshotBodyT
        eMdsMsgTypeT.MDS_MSGTYPE_L2_MARKET_DATA_SNAPSHOT: [
            MdsMktRspMsgBodyT,
            lambda channel, spi, msg_head, msg_body, _, user_info:
            spi.on_l2_market_data_snapshot(
                channel,
                msg_head,
                msg_body.mktDataSnapshot,
                user_info)
        ],

        # Level2 委托队列快照 (买一/卖一前五十笔) (21/0x15) @see MdsL2BestOrdersSnapshotBodyT
        eMdsMsgTypeT.MDS_MSGTYPE_L2_BEST_ORDERS_SNAPSHOT: [
            MdsMktRspMsgBodyT,
            lambda channel, spi, msg_head, msg_body, _, user_info:
            spi.on_l2_best_orders_snapshot(
                channel,
                msg_head,
                msg_body.mktDataSnapshot,
                user_info)
        ],

        # Level2 市场总览消息 (26/0x1A, 仅适用于上交所) @see MdsL2MarketOverviewT
        eMdsMsgTypeT.MDS_MSGTYPE_L2_MARKET_OVERVIEW: [
            MdsMktRspMsgBodyT,
            lambda channel, spi, msg_head, msg_body, _, user_info:
            spi.on_l2_market_overview(
                channel,
                msg_head,
                msg_body.mktDataSnapshot,
                user_info)
        ],

        # Level1 市场行情消息 (10/0x0A) @see MdsStockSnapshotBodyT
        eMdsMsgTypeT.MDS_MSGTYPE_MARKET_DATA_SNAPSHOT_FULL_REFRESH: [
            MdsMktRspMsgBodyT,
            lambda channel, spi, msg_head, msg_body, _, user_info:
            spi.on_market_data_snapshot_full_refresh(
                channel,
                msg_head,
                msg_body.mktDataSnapshot,
                user_info)
        ],

        # Level1/Level2 期权行情快照 (12/0x0C) @see MdsStockSnapshotBodyT
        eMdsMsgTypeT.MDS_MSGTYPE_OPTION_SNAPSHOT_FULL_REFRESH: [
            MdsMktRspMsgBodyT,
            lambda channel, spi, msg_head, msg_body, _, user_info:
            spi.on_market_option_snapshot_full_refresh(
                channel,
                msg_head,
                msg_body.mktDataSnapshot,
                user_info)
        ],

        # Level1/Level2 指数行情快照 (11/0x0B) @see MdsStockSnapshotBodyT
        eMdsMsgTypeT.MDS_MSGTYPE_INDEX_SNAPSHOT_FULL_REFRESH: [
            MdsMktRspMsgBodyT,
            lambda channel, spi, msg_head, msg_body, _, user_info:
            spi.on_market_index_snapshot_full_refresh(
                channel,
                msg_head,
                msg_body.mktDataSnapshot,
                user_info)
        ],

        # 证券状态消息 (14/0x0E, 仅适用于深交所) @see MdsSecurityStatusMsgT
        eMdsMsgTypeT.MDS_MSGTYPE_SECURITY_STATUS: [
            MdsMktRspMsgBodyT,
            lambda channel, spi, msg_head, msg_body, _, user_info:
            spi.on_security_status(
                channel,
                msg_head,
                msg_body.securityStatus,
                user_info)
        ],

        # 市场状态消息 (13/0x0D, 仅适用于上交所) @see MdsTradingSessionStatusMsgT
        eMdsMsgTypeT.MDS_MSGTYPE_TRADING_SESSION_STATUS: [
            MdsMktRspMsgBodyT,
            lambda channel, spi, msg_head, msg_body, _, user_info:
            spi.on_trading_session_status(
                channel,
                msg_head,
                msg_body.trdSessionStatus,
                user_info)
        ],

        # Level2 逐笔频道心跳消息 (29/0x1D) @see MdsTickChannelHeartbeatT
        eMdsMsgTypeT.MDS_MSGTYPE_L2_TICK_CHANNEL_HEARTBEAT: [
            MdsMktRspMsgBodyT,
            lambda channel, spi, msg_head, msg_body, _, user_info:
            spi.on_tick_channel_heart_beat(
                channel,
                msg_head,
                msg_body.tickChannelHeartbeat,
                user_info)
        ],

        # 证券行情订阅消息 (5/0x05) @see MdsMktDataRequestRspT
        eMdsMsgTypeT.MDS_MSGTYPE_MARKET_DATA_REQUEST: [
            MdsMktRspMsgBodyT,
            lambda channel, spi, msg_head, msg_body, _, user_info:
            spi.on_market_data_request_rsp(
                channel,
                msg_head,
                msg_body.mktDataRequestRsp,
                user_info)
        ],

        # 测试请求消息 (2/0x02) @see MdsTestRequestRspT
        eMdsMsgTypeT.MDS_MSGTYPE_TEST_REQUEST: [
            MdsMktRspMsgBodyT,
            lambda channel, spi, msg_head, msg_body, _, user_info:
            spi.on_test_request_rsp(
                channel,
                msg_head,
                msg_body.testRequestRsp,
                user_info)
        ],

        # 心跳消息 (1/0x01)
        eMdsMsgTypeT.MDS_MSGTYPE_HEARTBEAT: [
            MdsMktRspMsgBodyT,
            lambda channel, spi, msg_head, msg_body, _, user_info:
            spi.on_heart_beat(
                channel,
                msg_head,
                None,
                user_info)
        ],

        # 压缩的数据包 (6/0x06, 内部使用)
        eMdsMsgTypeT.MDS_MSGTYPE_COMPRESSED_PACKETS: [
            MdsMktRspMsgBodyT,
            lambda channel, spi, msg_head, msg_body, _, user_info:
            spi.on_compressed_packets(
                channel,
                msg_head,
                None,
                user_info)
        ],
        # -------------------------


        # ===================================================================
        # 查询回报相关消息定义 (批量查询相关)
        # ===================================================================

        # 批量查询行情快照 (86/0x56) @see MdsL1SnapshotT
        eMdsMsgTypeT.MDS_MSGTYPE_QRY_SNAPSHOT_LIST: [
            MdsL1SnapshotT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
            spi.on_qry_snapshot_list(
                channel,
                msg_head,
                msg_body,
                qry_cursor,
                user_info)
        ],

        # 批量查询证券(股票/债券/基金)静态信息列表 (89/0x59) @see MdsStockStaticInfoT
        eMdsMsgTypeT.MDS_MSGTYPE_QRY_STOCK_STATIC_INFO_LIST: [
            MdsStockStaticInfoT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
            spi.on_qry_stock_static_info_list(
                channel,
                msg_head,
                msg_body,
                qry_cursor,
                user_info)
        ],

        # 批量查询期权静态信息列表 (90/0x5A) @see MdsOptionStaticInfoT
        eMdsMsgTypeT.MDS_MSGTYPE_QRY_OPTION_STATIC_INFO_LIST: [
            MdsOptionStaticInfoT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
            spi.on_qry_option_static_info_list(
                channel,
                msg_head,
                msg_body,
                qry_cursor,
                user_info)
        ],

        # 逐笔数据重传请求 (96/0x60) @see MdsTickResendRequestRspT
        eMdsMsgTypeT.MDS_MSGTYPE_TICK_RESEND_REQUEST: [
            MdsMktRspMsgBodyT,
            lambda channel, spi, msg_head, msg_body, qry_cursor, user_info:
            spi.on_tick_resend_rsp(
                channel,
                msg_head,
                msg_body,
                qry_cursor,
                user_info)
        ],
        # -------------------------
}
# -------------------------


class MdsMsgDispatcher:
    """
    python对c_mds_api回调函数的转换类
    """

    def __init__(self, spi: MdsClientSpi, copy_args: bool) -> None:
        """
        Args:
            spi (MdsClientSpi): [回调处理类实例]
            copy_args (bool, optional): [capi回调时是否复制参数]. Defaults to True.

        Raises:
            Exception: [参数spi类型错误]
        """
        if not isinstance(spi, MdsClientSpi):
            raise Exception(f'spi参数错误:{spi}:{type(spi)}')

        self._spi: MdsClientSpi = spi
        self._copy_args = copy_args

        # python有垃圾回收，传递给capi的非实时调用回调需要增加引用防止自动回收
        self._refs: List[CFuncPointer] = []

    def get_spi(self) -> MdsClientSpi:
        return self._spi

    def release(self) -> None:
        """
        释放额外增添引用的回调
        """
        self._refs = []

    def _on_connect(self, p_channel: _Pointer,
            p_params: c_void_p, partial_user_info: Any) -> int:
        """
        异步API线程连接或重新连接完成后的回调函数
        - 回调函数运行在异步API线程下

        Args:
            p_channel (_Pointer[MdsAsyncApiChannelT]): [TCP行情订阅通道]
            p_params (c_void_p, None): [CAPI 用户回调参数, 取值固定为空; 回调参数通过<partial_user_info>在Python层面进行传递]
            partial_user_info (Any, None): [用户实际回调参数, 由偏函数传入]

        Returns:
            int: [
                    =0 等于0, 成功
                    <0 小于0, 处理失败, 异步线程将中止运行
                    >0 大于0, 处理失败, 将重建连接并继续尝试执行
                 ]
        """
        try:
            ret: int = self._spi.on_connect(
                memcpy(p_channel.contents), partial_user_info)
            if ret < 0:
                # 返回小于0的值, 处理失败, 异步API将中止运行
                return ret
            elif ret == 0:
                # 若返回0, 表示已经处理成功
                return 0
            else:
                # 返回大于0的值, 执行默认的连接完成后处理 (执行默认的行情订阅处理)
                return CMdsApiFuncLoader().c_mds_async_api_default_on_connect(
                    p_channel, VOID_NULLPTR)

        except Exception as err:
            channel_cfg: MdsAsyncApiChannelCfgT = \
                p_channel.contents.pChannelCfg.contents  # type: ignore

            log_error("调用通道spi.on_connect回调函数时异常! channelType[{}], "
                      "error_msg[{}]".format(channel_cfg.channelType, err))
            return -1

    def on_connect(self, user_info: Any) -> CFuncPointer:
        """
        对spi.on_connect进行包装，返回行情订阅通道连接成功回调函数

        Args:
            user_info (Any, None): [用户回调参数]
        Returns:
            CFuncPointer: [传递给capi的通道连接成功回调函数]
        """

        func: CFuncPointer = F_MDSAPI_ASYNC_ON_CONNECT_T(
            partial(self._on_connect, partial_user_info=user_info))
        # 回调异步运行在回报线程中，因此需要增加引用，防止被自动垃圾回收
        self._refs.append(func)
        return func

    def _on_connect_failed(self, p_channel: _Pointer,
            p_params: c_void_p, partial_user_info: Any) -> int:
        """
        异步API线程连接断开后的回调函数
        - 仅用于通知客户端连接已经断开, 无需做特殊处理, 异步线程会自动尝试重建连接

        Args:
            p_channel (_Pointer[MdsAsyncApiChannelT]): [TCP连接通道]
            p_params (c_void_p, None): [CAPI 用户回调参数, 取值固定为空; 回调参数通过<partial_user_info>在Python层面进行传递]
            partial_user_info (Any, None): [用户实际回调参数, 由偏函数传入]

        Returns:
            int: [
                    >=0 大于等于0, 异步线程将尝试重建连接并继续执行
                    <0  小于0, 异步线程将中止运行
                 ]
        """
        try:
            return self._spi.on_connect_failed(
                memcpy(p_channel.contents), partial_user_info)

        except Exception as err:
            channel_cfg: MdsAsyncApiChannelCfgT = \
                p_channel.contents.pChannelCfg.contents

            log_error("调用通道spi.on_connect_failed回调函数时异常! channelType[{}], "
                      "error_msg[{}]".format(channel_cfg.channelType, err))
            return -1


    def on_connect_failed(self, user_info: Any) -> CFuncPointer:
        """
        对spi.on_connect_failed进行包装，返回行情订阅通道连接失败回调函数

        Args:
            user_info (Any, None): [用户回调参数]
        Returns:
            CFuncPointer: [传递给capi的通道连接失败回调函数]
        """

        func: CFuncPointer = F_MDSAPI_ASYNC_ON_DISCONNECT_T(
            partial(self._on_connect_failed, partial_user_info=user_info))
        # 回调异步运行在回报线程中，因此需要增加引用，防止被自动垃圾回收
        self._refs.append(func)
        return func

    def _on_disconnect(self, p_channel: _Pointer,
            p_params: c_void_p, partial_user_info: Any) -> int:
        """
        异步API线程连接断开后的回调函数
        - 仅用于通知客户端连接已经断开, 无需做特殊处理, 异步线程会自动尝试重建连接

        Args:
            p_channel (_Pointer[MdsAsyncApiChannelT]): [TCP连接通道]
            p_params (c_void_p, None): [CAPI 用户回调参数, 取值固定为空; 回调参数通过<partial_user_info>在Python层面进行传递]
            partial_user_info (Any, None): [用户实际回调参数, 由偏函数传入]

        Returns:
            int: [
                    >=0 大于等于0, 异步线程将尝试重建连接并继续执行
                    <0  小于0, 异步线程将中止运行
                 ]
        """
        try:
            return self._spi.on_disconnect(
                memcpy(p_channel.contents), partial_user_info)

        except Exception as err:
            channel_cfg: MdsAsyncApiChannelCfgT = \
                p_channel.contents.pChannelCfg.contents

            log_error("调用通道spi.on_disconnect回调函数时异常! channelType[{}], "
                      "error_msg[{}]".format(channel_cfg.channelType, err))
            return -1

    def on_disconnect(self, user_info: Any) -> CFuncPointer:
        """
        对spi.on_disconnect进行包装，返回行情订阅通道连接断开回调函数

        Args:
            user_info (Any, None): [用户回调参数]
        Returns:
            CFuncPointer: [传递给capi的通道连接断开回调函数]
        """

        func: CFuncPointer = F_MDSAPI_ASYNC_ON_DISCONNECT_T(
            partial(self._on_disconnect, partial_user_info=user_info))
        # 回调异步运行在回报线程中，因此需要增加引用，防止被自动垃圾回收
        self._refs.append(func)
        return func

    def _handle_mkt_data_msg(self, p_session: c_void_p, p_msg_head: _Pointer,
            p_msg_item: _Pointer, p_params: c_void_p, partial_user_info: Any) -> int:
        """
        对接收到的消息进行派发的回调函数 (适用于回报通道)
        - 运行在异步API线程下

        Args:
            p_session (c_void_p): [异步API会话信息]
            p_msg_head (_Pointer[SMsgHeadT]): [回报消息的消息头]
            p_msg_item (_Pointer[MdsRspMsgBodyT]): [回报消息的数据条目]
            p_params (c_void_p, None): [CAPI 用户回调参数, 取值固定为空; 回调参数通过<partial_user_info>在Python层面进行传递]
            partial_user_info (Any, None): [用户实际回调参数, 由偏函数传入]

        Returns:
            [0]: [成功]
        """

        msg_id: int = int(p_msg_head.contents.msgId)
        p_channel = CMdsApiFuncLoader().\
            c_mds_async_api_get_channel_by_session(p_session)

        tuple_callback = _MDS_MSG_ID_TO_CALLBACK.get(msg_id)
        if not tuple_callback:
            log_error(f"Invalid message type! msgId[0x{msg_id:0x}]")
            return 0

        # 元组说明:
        # - 0号元素: MDS查询回报消息结构体
        # - 1号元素: MDS查询回报的回调函数
        e_mds_msg_type = tuple_callback[0]
        callback: Optional[Callable] = tuple_callback[1]

        ret: int = -1
        try:
            if self._copy_args:
                ret = callback(p_channel.contents, self._spi,
                    memcpy(p_msg_head.contents),
                    memcpy(p_msg_item.contents),
                    MdsQryCursorT(),    # 无实际意义
                    partial_user_info)
            else:
                ret = callback(p_channel.contents, self._spi,
                    p_msg_head.contents,
                    p_msg_item.contents,
                    MdsQryCursorT(),    # 无实际意义
                    partial_user_info)
        except Exception as err:
            log_error(f"调用消息msgId: {msg_id} 的回调函数时发生异常:{err}")

        return ret

    def handle_mkt_data_msg(self, user_info: Any) -> CFuncPointer:
        """
        对self._handle_mkt_data_msg，返回行情数据回调函数
        消息派发方式参考 _MDS_MSG_ID_TO_CALLBACK

        Returns:
            CFuncPointer: [传递给capi的通道回报回调函数]
        """

        func: CFuncPointer = F_MDSAPI_ASYNC_ON_MSG_T(
            partial(self._handle_mkt_data_msg, partial_user_info=user_info))
        # 回调异步运行在回报线程中，因此需要增加引用，防止被自动垃圾回收
        self._refs.append(func)
        return func

    def _handle_qry_msg(self, p_session: c_void_p, p_msg_head: _Pointer,
            p_msg_item: c_void_p, p_qry_cursor: c_void_p, p_params: c_void_p,
            partial_user_info: Any, partial_is_tick_resend: bool) -> int:
        """
        对查询的回报消息进行派发的回调函数 (适用于查询通道)
        - 运行在异步API线程下

        Args:
            p_session (c_void_p): [异步API会话信息]
            p_msg_head (_Pointer[SMsgHeadT]): [查询回报消息的消息头]
            p_msg_item (_Pointer[MdsRspMsgBodyT]): [查询回报消息的数据条目]
            p_qry_cursor (_Pointer[MdsRspMsgBodyT]): [查询定位的游标结构]
            p_params (c_void_p, None): [CAPI 用户回调参数, 取值固定为空; 回调参数通过<partial_user_info>在Python层面进行传递]
            partial_user_info (Any, None): [用户实际回调参数, 由偏函数传入]
            partial_is_tick_resend (bool): [是否是逐笔数据重传接口调用]

        Returns:
            [0]: [成功]
        """

        p_channel = CMdsApiFuncLoader().\
            c_mds_async_api_get_channel_by_session(p_session)

        if partial_is_tick_resend is True:
            # @note 逐笔数据重传应答有多种数据类型, 统一按逐笔数据重传请求 (96/0x60)进行回调处理
            # - 回调函数: spi.on_tick_resend_rsp
            # - 消息体的数据类型包括:
            #   - MDS_MSGTYPE_L2_TRADE            => @see MdsL2TradeT
            #   - MDS_MSGTYPE_L2_ORDER            => @see MdsL2OrderT
            #   - MDS_MSGTYPE_L2_SSE_ORDER        => @see MdsL2OrderT
            #   - MDS_MSGTYPE_TICK_RESEND_REQUEST => @see MdsTickResendRequestRspT

            msg_id: int = eMdsMsgTypeT.MDS_MSGTYPE_TICK_RESEND_REQUEST
        else:
            msg_id: int = int(p_msg_head.contents.msgId)

        tuple_callback = _MDS_MSG_ID_TO_CALLBACK.get(msg_id)
        if not tuple_callback:
            log_error(f"Invalid message type! msgId[0x{msg_id:0x}]")
            return 0

        # 元组说明:
        # - 0号元素: MDS查询回报消息结构体
        # - 1号元素: MDS查询回报的回调函数
        e_mds_msg_type = tuple_callback[0]
        qry_callback: Optional[Callable] = tuple_callback[1]

        ret: int = -1
        try:
            if self._copy_args:
                ret = qry_callback(p_channel.contents, self._spi,
                    memcpy(p_msg_head.contents),
                    memcpy(cast(p_msg_item, POINTER(e_mds_msg_type)).contents),
                    memcpy(cast(p_qry_cursor, POINTER(MdsQryCursorT)).contents),
                    partial_user_info)
            else:
                ret = qry_callback(p_channel.contents, self._spi,
                    p_msg_head.contents,
                    cast(p_msg_item, POINTER(e_mds_msg_type)).contents,
                    cast(p_qry_cursor, POINTER(MdsQryCursorT)).contents,
                    partial_user_info)
        except Exception as err:
            log_error(f"调用消息msgId: {msg_id} 的回调函数时发生异常:{err}")

        return ret

    def handle_qry_msg(self, user_info: Any,
            is_tick_resend: bool = False) -> CFuncPointer:
        """
        对self._handle_qry_msg，返回查询通道数据回调函数
        消息派发方式参考 _MDS_MSG_ID_TO_CALLBACK

        Args:
            user_info (c_void_p): [用户回调参数]
            is_tick_resend (bool): [是否是逐笔数据重传接口调用]
        Returns:
            CFuncPointer: [传递给capi的回报通道回报回调函数]
        """

        func: CFuncPointer = F_MDSAPI_ASYNC_ON_QRY_MSG_T(
            partial(self._handle_qry_msg,
                    partial_user_info=user_info,
                    partial_is_tick_resend=is_tick_resend))
        # 回调异步运行在回报线程中，因此需要增加引用，防止被自动垃圾回收
        self._refs.append(func)
        return func
