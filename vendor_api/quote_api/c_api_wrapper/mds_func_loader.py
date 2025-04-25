# -*- coding: utf-8 -*-
"""
capi函数加载相关
"""

from ctypes import (
    c_uint8, c_int16, c_uint16, c_int, c_int32, c_uint32, c_int64,
    c_void_p, c_char_p, POINTER, CFUNCTYPE, Structure
)

from quote_api.model import (
    # spk_util.py
    SingletonType, CCharP, SMsgHeadT, MdsApiRemoteCfgT, MdsApiAddrInfoT,
    MdsAsyncApiChannelT, MdsAsyncApiContextT, MdsAsyncApiChannelCfgT,
    CApiFuncLoader,

    # mds_base_model.py
    MdsTradingSessionStatusMsgT, MdsSecurityStatusMsgT, MdsMktDataSnapshotT,
    MdsStockStaticInfoT,

    # mds_qry_packets.py
    MdsQryCursorT,MdsQryStockStaticInfoListFilterT,

    # mds_mkt_pachets.py
    MdsMktRspMsgBodyT, MdsApiSubscribeInfoT,
    MdsMktDataRequestReqT, MdsMktDataRequestEntryT,
    MdsTickResendRequestReqT, MdsTickResendRequestRspT,
    MdsChangePasswordReqT, MdsChangePasswordRspT,
)


# ===================================================================
# 结构体定义
# ===================================================================

class MdsAsyncApiContextParamsT(Structure):
    """
    MDS异步API的上下文环境的创建参数 (仅做为 CreateContext 接口的参数使用)
    """
    _fields_ = (
        # 异步队列的大小
        ("asyncQueueSize", c_int32),

        # 是否优先使用大页内存来创建异步队列
        ("isHugepageAble", c_uint8),
        # 是否启动独立的回调线程来执行回调处理 (否则将直接在通信线程下执行回调处理)
        ("isAsyncCallbackAble", c_uint8),
        # 是否启动独立的连接管理线程来执行连接处理和OnConnect回调处理 (当通道数量大于1时建议开启, 否则将直接在通信线程下执行)
        ("isAsyncConnectAble", c_uint8),
        # 是否使用忙等待模式 (TRUE:延迟更低但CPU会被100%占用; FALSE:延迟和CPU使用率相对均衡)
        ("isBusyPollAble", c_uint8),
        # 是否在启动前预创建并校验所有的连接
        ("isPreconnectAble", c_uint8),
        # 是否启用内置的查询通道 (TRUE:启动异步API时自动创建内置的查询通道; FALSE:不创建内置的查询通道)
        ("isBuiltinQueryable", c_uint8),

        # Onload 加速标志
        # - 0: 未启用 onload 加速
        # - 1: 已启用 onload 加速
        # - 2: 自动管理 onload 栈
        ("onloadFlag", c_uint8),
        # 是否需要支持对接压缩后的行情数据
        ("isCompressible", c_uint8),
        # 是否启用对UDP行情数据的本地行情订阅和过滤功能
        ("isUdpFilterable", c_uint8),
        # 为保证64位对齐而设
        ("__filler1", c_uint8 * 3),

        # 自动执行时间同步的间隔时间 (单位为秒, 必须启用内置的查询通道才能生效. 小于等于0:不自动执行时间同步)
        ("autoTimeSyncInterval", c_int16),
        # 为保证64位对齐而设
        ("__filler2", c_uint8 * 2),
        # 统计时钟漂移情况的起始时间 (格式: HHMMSS 或 HHMMSSsss. 小于等于0:默认从09:10开始统计时钟漂移情况)
        ("clockDriftBeginTime", c_int32)
    )
# -------------------------


# ===================================================================
# 回调函数的函数原型定义
# ===================================================================

# 对接收到的应答或回报消息进行处理的回调函数的函数原型定义
F_MDSAPI_ASYNC_ON_MSG_T = CFUNCTYPE(
    c_int32,
    c_void_p,
    POINTER(SMsgHeadT),
    POINTER(MdsMktRspMsgBodyT),
    c_void_p
)

# 对查询结果进行处理的回调函数的函数原型定义
F_MDSAPI_ASYNC_ON_QRY_MSG_T = CFUNCTYPE(
    c_int32,
    c_void_p,
    POINTER(SMsgHeadT),
    c_void_p,
    POINTER(MdsQryCursorT),
    c_void_p
)

# 异步API线程连接或重新连接完成后的回调函数的函数原型定义
F_MDSAPI_ASYNC_ON_CONNECT_T = CFUNCTYPE(
    c_int32,
    POINTER(MdsAsyncApiChannelT),
    c_void_p
)

# 异步API线程连接断开后的回调函数的函数原型定义
F_MDSAPI_ASYNC_ON_DISCONNECT_T = CFUNCTYPE(
    c_int32,
    POINTER(MdsAsyncApiChannelT),
    c_void_p
)

# 异步API遍历所有的连接通道信息的回调函数的函数原型定义
F_MDSAPI_ASYNC_FOREACH_CHANNEL_T = CFUNCTYPE(
    c_int32,
    POINTER(MdsAsyncApiChannelT),
    c_void_p
)
# -------------------------


class CMdsApiFuncLoader(CApiFuncLoader, metaclass=SingletonType):
    """
    行情capi动态库函数加载
    """

    def __init__(self) -> None:
        super().__init__()

        # ===================================================================
        # MDS异步API接口函数封装 (上下文管理接口)
        # ===================================================================

        # 创建异步API的运行时环境 (通过配置文件和默认的配置区段加载相关配置参数)
        self.c_mds_async_api_create_context = self.c_api_dll.MdsAsyncApi_CreateContext
        self.c_mds_async_api_create_context.restype = POINTER(MdsAsyncApiContextT)
        self.c_mds_async_api_create_context.argtypes = [CCharP]

        # 创建异步API的运行时环境 (通过配置文件和指定的配置区段加载相关配置参数)
        self.c_mds_async_api_create_context2 = self.c_api_dll.MdsAsyncApi_CreateContext2
        self.c_mds_async_api_create_context2.restype = POINTER(MdsAsyncApiContextT)
        self.c_mds_async_api_create_context2.argtypes = [CCharP, CCharP, CCharP, CCharP]

        # 创建异步API的运行时环境 (仅通过函数参数指定必要的配置参数)
        self.c_mds_async_api_create_context_simple = self.c_api_dll.MdsAsyncApi_CreateContextSimple
        self.c_mds_async_api_create_context_simple.restype = POINTER(MdsAsyncApiContextT)
        self.c_mds_async_api_create_context_simple.argtypes = [CCharP, CCharP, c_int]

        # 创建异步API的运行时环境 (仅通过函数参数指定必要的配置参数)
        self.c_mds_async_api_create_context_simple2 = self.c_api_dll.MdsAsyncApi_CreateContextSimple2
        self.c_mds_async_api_create_context_simple2.restype = POINTER(MdsAsyncApiContextT)
        self.c_mds_async_api_create_context_simple2.argtypes = [
            CCharP, CCharP, POINTER(MdsAsyncApiContextParamsT)
        ]

        # 释放异步API的运行时环境
        self.c_mds_async_api_release_context = self.c_api_dll.MdsAsyncApi_ReleaseContext
        self.c_mds_async_api_release_context.restype = None
        self.c_mds_async_api_release_context.argtypes = [POINTER(MdsAsyncApiContextT)]

        # 启动异步API线程
        self.c_mds_async_api_start = self.c_api_dll.MdsAsyncApi_Start
        self.c_mds_async_api_start.restype = c_int
        self.c_mds_async_api_start.argtypes = [POINTER(MdsAsyncApiContextT)]

        # 终止异步API线程
        self.c_mds_async_api_stop = self.c_api_dll.MdsAsyncApi_Stop
        self.c_mds_async_api_stop.restype = None
        self.c_mds_async_api_stop.argtypes = [POINTER(MdsAsyncApiContextT)]

        # 返回异步API的通信线程是否正在运行过程中
        self.c_mds_async_api_is_running = self.c_api_dll.MdsAsyncApi_IsRunning
        self.c_mds_async_api_is_running.restype = c_int
        self.c_mds_async_api_is_running.argtypes = [POINTER(MdsAsyncApiContextT)]

        # 返回异步API相关的所有线程是否都已经安全退出 (或尚未运行)
        self.c_mds_async_api_is_all_terminated = self.c_api_dll.MdsAsyncApi_IsAllTerminated
        self.c_mds_async_api_is_all_terminated.restype = c_int
        self.c_mds_async_api_is_all_terminated.argtypes = [POINTER(MdsAsyncApiContextT)]

        # 返回异步API累计已提取和处理过的行情消息数量
        self.c_mds_async_api_get_total_picked = self.c_api_dll.MdsAsyncApi_GetTotalPicked
        self.c_mds_async_api_get_total_picked.restype = c_int64
        self.c_mds_async_api_get_total_picked.argtypes = [POINTER(MdsAsyncApiContextT)]

        # 返回异步I/O线程累计已提取和处理过的消息数量
        self.c_mds_async_api_get_total_io_picked = self.c_api_dll.MdsAsyncApi_GetTotalIoPicked
        self.c_mds_async_api_get_total_io_picked.restype = c_int64
        self.c_mds_async_api_get_total_io_picked.argtypes = [POINTER(MdsAsyncApiContextT)]

        # 返回异步API累计已入队的消息数量
        self.c_mds_async_api_get_async_queue_total_count = self.c_api_dll.MdsAsyncApi_GetAsyncQueueTotalCount
        self.c_mds_async_api_get_async_queue_total_count.restype = c_int64
        self.c_mds_async_api_get_async_queue_total_count.argtypes = [POINTER(MdsAsyncApiContextT)]

        # 返回队列中尚未被处理的剩余数据数量
        self.c_mds_async_api_get_async_queue_remaining_count = self.c_api_dll.MdsAsyncApi_GetAsyncQueueRemainingCount
        self.c_mds_async_api_get_async_queue_remaining_count.restype = c_int64
        self.c_mds_async_api_get_async_queue_remaining_count.argtypes = [POINTER(MdsAsyncApiContextT)]
        # -------------------------


        # ===================================================================
        # MDS异步API接口函数封装 (通道管理接口)
        # ===================================================================

        # 返回通道数量 (通道配置信息数量)
        self.c_mds_async_api_get_channel_count = self.c_api_dll.MdsAsyncApi_GetChannelCount
        self.c_mds_async_api_get_channel_count.restype = c_int32
        self.c_mds_async_api_get_channel_count.argtypes = [POINTER(MdsAsyncApiContextT)]

        # 返回当前已连接的通道数量
        self.c_mds_async_api_get_connected_channel_count = self.c_api_dll.MdsAsyncApi_GetConnectedChannelCount
        self.c_mds_async_api_get_connected_channel_count.restype = c_int32
        self.c_mds_async_api_get_connected_channel_count.argtypes = [POINTER(MdsAsyncApiContextT)]

        # 添加通道配置信息
        self.c_mds_async_api_add_channel = self.c_api_dll.MdsAsyncApi_AddChannel
        self.c_mds_async_api_add_channel.restype = POINTER(MdsAsyncApiChannelT)
        self.c_mds_async_api_add_channel.argtypes = [
            POINTER(MdsAsyncApiContextT), CCharP,
            POINTER(MdsApiRemoteCfgT),
            POINTER(MdsApiSubscribeInfoT),
            F_MDSAPI_ASYNC_ON_MSG_T, c_void_p,
            F_MDSAPI_ASYNC_ON_CONNECT_T, c_void_p,
            F_MDSAPI_ASYNC_ON_DISCONNECT_T, c_void_p
        ]

        # 从配置文件中加载并添加通道配置信息
        self.c_mds_async_api_add_channel_from_file = self.c_api_dll.MdsAsyncApi_AddChannelFromFile
        self.c_mds_async_api_add_channel_from_file.restype = POINTER(MdsAsyncApiChannelT)
        self.c_mds_async_api_add_channel_from_file.argtypes = [
            POINTER(MdsAsyncApiContextT), CCharP, CCharP, CCharP, CCharP,
            F_MDSAPI_ASYNC_ON_MSG_T, c_void_p,
            F_MDSAPI_ASYNC_ON_CONNECT_T, c_void_p,
            F_MDSAPI_ASYNC_ON_DISCONNECT_T, c_void_p
        ]

        # 返回顺序号对应的连接通道信息
        self.c_mds_async_api_get_channel = self.c_api_dll.MdsAsyncApi_GetChannel
        self.c_mds_async_api_get_channel.restype = POINTER(MdsAsyncApiChannelT)
        self.c_mds_async_api_get_channel.argtypes = [c_void_p, c_int32]

        # 返回标签对应的连接通道信息
        self.c_mds_async_api_get_channel_by_tag = self.c_api_dll.MdsAsyncApi_GetChannelByTag
        self.c_mds_async_api_get_channel_by_tag.restype = POINTER(MdsAsyncApiChannelT)
        self.c_mds_async_api_get_channel_by_tag.argtypes = [c_void_p, CCharP]

        # 返回会话信息对应的异步API连接通道信息 (Python API内部使用, 暂不对外开放)
        self.c_mds_async_api_get_channel_by_session = self.c_api_dll.MdsAsyncApi_GetChannelBySession
        self.c_mds_async_api_get_channel_by_session.restype = POINTER(MdsAsyncApiChannelT)
        self.c_mds_async_api_get_channel_by_session.argtypes = [c_void_p]

        # 遍历所有的连接通道信息并执行回调函数
        self.c_mds_async_api_foreach_channel = self.c_api_dll.MdsAsyncApi_ForeachChannel
        self.c_mds_async_api_foreach_channel.restype = POINTER(c_int32)
        self.c_mds_async_api_foreach_channel.argtypes = [
            POINTER(MdsAsyncApiContextT),
            F_MDSAPI_ASYNC_FOREACH_CHANNEL_T, c_void_p
        ]
        # 遍历所有的连接通道信息并执行回调函数 (暂不对接, 与MdsAsyncApi_ForeachChannel区别在于自定义参数个数)
        # MdsAsyncApi_ForeachChannel2
        # 遍历所有的连接通道信息并执行回调函数 (暂不对接, 与MdsAsyncApi_ForeachChannel区别在于自定义参数个数)
        # MdsAsyncApi_ForeachChannel3

        # 返回通道是否已连接就绪
        self.c_mds_async_api_is_channel_connected = self.c_api_dll.MdsAsyncApi_IsChannelConnected
        self.c_mds_async_api_is_channel_connected.restype = c_int
        self.c_mds_async_api_is_channel_connected.argtypes = [POINTER(MdsAsyncApiChannelT)]

        # 返回通道对应的配置信息
        self.c_mds_async_api_get_channel_cfg = self.c_api_dll.MdsAsyncApi_GetChannelCfg
        self.c_mds_async_api_get_channel_cfg.restype = POINTER(MdsAsyncApiChannelCfgT)
        self.c_mds_async_api_get_channel_cfg.argtypes = [POINTER(MdsAsyncApiChannelT)]

        # 返回通道对应的行情订阅配置信息
        self.c_mds_async_api_get_channel_subscribe_cfg = self.c_api_dll.MdsAsyncApi_GetChannelSubscribeCfg
        self.c_mds_async_api_get_channel_subscribe_cfg.restype = POINTER(MdsApiSubscribeInfoT)
        self.c_mds_async_api_get_channel_subscribe_cfg.argtypes = [POINTER(MdsAsyncApiChannelT)]

        # 设置连接或重新连接完成后的回调函数 (Python API内部使用, 暂不对外开放)
        self.c_mds_async_api_set_on_connect = self.c_api_dll.MdsAsyncApi_SetOnConnect
        self.c_mds_async_api_set_on_connect.restype = c_int
        self.c_mds_async_api_set_on_connect.argtypes = [
            POINTER(MdsAsyncApiChannelT),
            F_MDSAPI_ASYNC_ON_CONNECT_T,
            c_void_p
        ]

        # 返回连接或重新连接完成后的回调函数 (Python API内部使用, 暂不对外开放)
        self.c_mds_async_api_get_on_connect = self.c_api_dll.MdsAsyncApi_GetOnConnect
        self.c_mds_async_api_get_on_connect.restype = F_MDSAPI_ASYNC_ON_CONNECT_T
        self.c_mds_async_api_get_on_connect.argtypes = [POINTER(MdsAsyncApiChannelT)]

        # 设置连接断开后的回调函数 (Python API内部使用, 暂不对外开放)
        self.c_mds_async_api_set_on_disconnect = self.c_api_dll.MdsAsyncApi_SetOnDisconnect
        self.c_mds_async_api_set_on_disconnect.restype = c_int
        self.c_mds_async_api_set_on_disconnect.argtypes = [
            POINTER(MdsAsyncApiChannelT),
            F_MDSAPI_ASYNC_ON_DISCONNECT_T,
            c_void_p
        ]

        # 返回连接断开后的回调函数 (Python API内部使用, 暂不对外开放)
        self.c_mds_async_api_get_on_disconnect = self.c_api_dll.MdsAsyncApi_GetOnDisconnect
        self.c_mds_async_api_get_on_disconnect.restype = F_MDSAPI_ASYNC_ON_DISCONNECT_T
        self.c_mds_async_api_get_on_disconnect.argtypes = [POINTER(MdsAsyncApiChannelT)]

        # 设置连接失败时的回调函数 (Python API内部使用, 暂不对外开放)
        self.c_mds_async_api_set_on_connect_failed = self.c_api_dll.MdsAsyncApi_SetOnConnectFailed
        self.c_mds_async_api_set_on_connect_failed.restype = c_int
        self.c_mds_async_api_set_on_connect_failed.argtypes = [
            POINTER(MdsAsyncApiChannelT),
            F_MDSAPI_ASYNC_ON_DISCONNECT_T,
            c_void_p
        ]

        # 返回连接失败时的回调函数 (Python API内部使用, 暂不对外开放)
        self.c_mds_async_api_get_on_connect_failed = self.c_api_dll.MdsAsyncApi_GetOnConnectFailed
        self.c_mds_async_api_get_on_connect_failed.restype = F_MDSAPI_ASYNC_ON_DISCONNECT_T
        self.c_mds_async_api_get_on_connect_failed.argtypes = [POINTER(MdsAsyncApiChannelT)]
        # -------------------------


        # ===================================================================
        # MDS异步API接口函数封装 (会话管理接口)
        # ===================================================================

        # 以异步的方式发送证券行情实时订阅请求, 以重新订阅、追加订阅或删除订阅行情数据
        self.c_mds_async_api_subscribe_market_data = self.c_api_dll.MdsAsyncApi_SubscribeMarketData
        self.c_mds_async_api_subscribe_market_data.restype = c_int
        self.c_mds_async_api_subscribe_market_data.argtypes = [
            POINTER(MdsAsyncApiChannelT),
            POINTER(MdsMktDataRequestReqT),
            POINTER(MdsMktDataRequestEntryT)
        ]

        # 根据字符串形式的证券代码列表订阅行情信息
        self.c_mds_async_api_subscribe_by_string = self.c_api_dll.MdsAsyncApi_SubscribeByString
        self.c_mds_async_api_subscribe_by_string.restype = c_int
        self.c_mds_async_api_subscribe_by_string.argtypes = [
            POINTER(MdsAsyncApiChannelT), CCharP, CCharP,
            c_int, c_int, c_int, c_int32
        ]

        # 直接根据字符串形式的证券代码列表订阅行情, 并通过证券代码前缀来区分和识别所属市场
        self.c_mds_async_api_subscribe_by_string_and_prefixes = self.c_api_dll.MdsAsyncApi_SubscribeByStringAndPrefixes
        self.c_mds_async_api_subscribe_by_string_and_prefixes.restype = c_int
        self.c_mds_async_api_subscribe_by_string_and_prefixes.argtypes = [
            POINTER(MdsAsyncApiChannelT), CCharP, CCharP, CCharP, CCharP,
            c_int, c_int, c_int32
        ]

        # 查询证券静态信息, 并根据查询结果订阅行情信息
        self.c_mds_async_api_subscribe_by_query = self.c_api_dll.MdsAsyncApi_SubscribeByQuery
        self.c_mds_async_api_subscribe_by_query.restype = c_int32
        self.c_mds_async_api_subscribe_by_query.argtypes = [
            POINTER(MdsAsyncApiChannelT), c_int, c_int32,
            c_void_p, POINTER(MdsQryStockStaticInfoListFilterT)
        ]

        # 发送心跳消息
        self.c_mds_async_api_send_heart_beat = self.c_api_dll.MdsAsyncApi_SendHeartbeat
        self.c_mds_async_api_send_heart_beat.restype = c_int
        self.c_mds_async_api_send_heart_beat.argtypes = [POINTER(MdsAsyncApiChannelT)]

        # 发送测试请求消息
        self.c_mds_async_api_send_test_req = self.c_api_dll.MdsAsyncApi_SendTestReq
        self.c_mds_async_api_send_test_req.restype = c_int
        self.c_mds_async_api_send_test_req.argtypes = [
            POINTER(MdsAsyncApiChannelT), CCharP, c_int32
        ]

        # 连接完成后处理的默认实现 (执行默认的行情订阅处理)
        self.c_mds_async_api_default_on_connect = self.c_api_dll.MdsAsyncApi_DefaultOnConnect
        self.c_mds_async_api_default_on_connect.restype = c_int32
        self.c_mds_async_api_default_on_connect.argtypes = [
            POINTER(MdsAsyncApiChannelT), c_void_p
        ]

        # 连接完成后处理的默认实现 (不订阅任何行情数据)
        self.c_mds_async_api_subscribe_nothing_on_connect = self.c_api_dll.MdsAsyncApi_SubscribeNothingOnConnect
        self.c_mds_async_api_subscribe_nothing_on_connect.restype = c_int32
        self.c_mds_async_api_subscribe_nothing_on_connect.argtypes = [
            POINTER(MdsAsyncApiChannelT), c_void_p
        ]
        # -------------------------


        # ===================================================================
        # MDS异步API接口函数封装 (辅助的配置管理接口)
        # ===================================================================

        # 从配置文件中加载异步API运行参数
        # MdsAsyncApi_LoadContextParams

        # 从配置文件中加载CPU亲和性配置
        # MdsAsyncApi_LoadCpusetCfg

        # 从配置文件中加载CPU亲和性配置 (额外增加对连接管理线程的支持)
        # MdsAsyncApi_LoadCpusetCfg2

        # 设置通信线程的CPU亲和性配置
        # MdsAsyncApi_SetCommunicationCpusetCfg

        # 返回通信线程的CPU亲和性配置信息
        # MdsAsyncApi_GetCommunicationCpusetCfg

        # 设置异步回调线程的CPU亲和性配置
        # MdsAsyncApi_SetCallbackThreadCpusetCfg

        # 返回异步回调线程的CPU亲和性配置信息
        # MdsAsyncApi_GetCallbackThreadCpusetCfg

        # 设置连接管理线程的CPU亲和性配置
        # MdsAsyncApi_SetConnectThreadCpusetCfg

        # 返回连接管理线程的CPU亲和性配置信息
        # MdsAsyncApi_GetConnectThreadCpusetCfg

        # 设置异步I/O线程的CPU亲和性配置
        # MdsAsyncApi_SetIoThreadCpusetCfg

        # 返回异步I/O线程的CPU亲和性配置信息
        # MdsAsyncApi_GetIoThreadCpusetCfg

        # 设置是否在启动前预创建并校验所有的连接
        self.c_mds_async_api_set_preconnect_able = self.c_api_dll.MdsAsyncApi_SetPreconnectAble
        self.c_mds_async_api_set_preconnect_able.restype = c_int
        self.c_mds_async_api_set_preconnect_able.argtypes = [
            POINTER(MdsAsyncApiContextT), c_int
        ]

        # 返回是否在启动前预创建并校验所有的连接
        self.c_mds_async_api_is_preconnect_able = self.c_api_dll.MdsAsyncApi_IsPreconnectAble
        self.c_mds_async_api_is_preconnect_able.restype = c_int
        self.c_mds_async_api_is_preconnect_able.argtypes = [POINTER(MdsAsyncApiContextT)]

        # 设置是否需要支持对接压缩后的行情数据
        self.c_mds_async_api_set_compressible = self.c_api_dll.MdsAsyncApi_SetCompressible
        self.c_mds_async_api_set_compressible.restype = c_int
        self.c_mds_async_api_set_compressible.argtypes = [
            POINTER(MdsAsyncApiContextT), c_int
        ]

        # 返回是否支持对接压缩后的行情数据
        self.c_mds_async_api_is_compressible = self.c_api_dll.MdsAsyncApi_IsCompressible
        self.c_mds_async_api_is_compressible.restype = c_int
        self.c_mds_async_api_is_compressible.argtypes = [POINTER(MdsAsyncApiContextT)]

        # 设置是否启用对UDP行情数据的本地行情订阅和过滤功能
        self.c_mds_async_api_set_udp_filter_able = self.c_api_dll.MdsAsyncApi_SetUdpFilterable
        self.c_mds_async_api_set_udp_filter_able.restype = c_int
        self.c_mds_async_api_set_udp_filter_able.argtypes = [
            POINTER(MdsAsyncApiContextT), c_int
        ]

        # 返回是否启用对UDP行情数据的本地行情订阅和过滤功能
        self.c_mds_async_api_is_udp_filter_able = self.c_api_dll.MdsAsyncApi_IsUdpFilterable
        self.c_mds_async_api_is_udp_filter_able.restype = c_int
        self.c_mds_async_api_is_udp_filter_able.argtypes = [POINTER(MdsAsyncApiContextT)]

        # 设置是否接管启动线程
        # MdsAsyncApi_SetTakeoverStartThreadFlag

        # 返回是否接管启动线程
        # MdsAsyncApi_GetTakeoverStartThreadFlag

        # 设置是否启动独立的回调线程来执行回调处理
        self.c_mds_async_api_set_async_callback_able = self.c_api_dll.MdsAsyncApi_SetAsyncCallbackAble
        self.c_mds_async_api_set_async_callback_able.restype = c_int
        self.c_mds_async_api_set_async_callback_able.argtypes = [
            POINTER(MdsAsyncApiContextT), c_int
        ]

        # 返回是否启动独立的回调线程来执行回调处理
        self.c_mds_async_api_is_async_callback_able = self.c_api_dll.MdsAsyncApi_IsAsyncCallbackAble
        self.c_mds_async_api_is_async_callback_able.restype = c_int
        self.c_mds_async_api_is_async_callback_able.argtypes = [POINTER(MdsAsyncApiContextT)]

        # 设置是否启动独立的连接管理线程来执行连接处理和OnConnect回调处理
        # MdsAsyncApi_SetAsyncConnectAble

        # 返回是否启动独立的连接管理线程来执行连接处理和OnConnect回调处理
        # MdsAsyncApi_IsAsyncConnectAble

        # 设置 Onload 加速标志
        # MdsAsyncApi_SetOnloadFlag

        # 返回 Onload 加速标志
        # MdsAsyncApi_GetOnloadFlag

        # 设置异步回调线程的忙等待模式
        # MdsAsyncApi_SetAsyncCallbackBusyPollAble

        # 返回异步回调线程的忙等待模式
        # MdsAsyncApi_IsAsyncCallbackBusyPollAble

        # 返回异步通信队列的长度 (可缓存的最大消息数量)
        self.c_mds_async_api_get_async_queue_length = self.c_api_dll.MdsAsyncApi_GetAsyncQueueLength
        self.c_mds_async_api_get_async_queue_length.restype = c_int64
        self.c_mds_async_api_get_async_queue_length.argtypes = [POINTER(MdsAsyncApiContextT)]

        # 返回异步通信队列的数据空间大小
        self.c_mds_async_api_get_async_queue_data_area_size = self.c_api_dll.MdsAsyncApi_GetAsyncQueueDataAreaSize
        self.c_mds_async_api_get_async_queue_data_area_size.restype = c_int64
        self.c_mds_async_api_get_async_queue_data_area_size.argtypes = [POINTER(MdsAsyncApiContextT)]

        # 设置是否启用内置的查询通道
        self.c_mds_async_api_set_builtin_query_able = self.c_api_dll.MdsAsyncApi_SetBuiltinQueryable
        self.c_mds_async_api_set_builtin_query_able.restype = c_int
        self.c_mds_async_api_set_builtin_query_able.argtypes = [
            POINTER(MdsAsyncApiContextT), c_int
        ]

        # 返回是否启用内置的查询通道
        self.c_mds_async_api_is_builtin_query_able = self.c_api_dll.MdsAsyncApi_IsBuiltinQueryable
        self.c_mds_async_api_is_builtin_query_able.restype = c_int
        self.c_mds_async_api_is_builtin_query_able.argtypes = [POINTER(MdsAsyncApiContextT)]

        # 返回内置的查询通道是否已连接就绪
        self.c_mds_async_api_is_builtin_query_channel_connected = self.c_api_dll.MdsAsyncApi_IsBuiltinQueryChannelConnected
        self.c_mds_async_api_is_builtin_query_channel_connected.restype = c_int
        self.c_mds_async_api_is_builtin_query_channel_connected.argtypes = [POINTER(MdsAsyncApiContextT)]

        # 设置内置的查询通道的配置信息
        # MdsAsyncApi_SetBuiltinQueryChannelCfg

        # 从配置文件中加载内置的查询通道的配置信息
        # MdsAsyncApi_LoadBuiltinQueryChannelCfg

        # 返回内置的查询通道的配置信息
        # MdsAsyncApi_GetBuiltinQueryChannelCfg

        # 返回内置的查询通道的会话信息
        # MdsAsyncApi_GetBuiltinQueryChannelRef

        # 设置异步I/O线程配置
        # MdsAsyncApi_SetIoThreadCfg

        # 从配置文件中加载异步I/O线程配置
        # MdsAsyncApi_LoadIoThreadCfg

        # 返回异步I/O线程配置
        # MdsAsyncApi_GetIoThreadCfg

        # 设置异步I/O线程的使能标志
        # MdsAsyncApi_SetIoThreadEnabled

        # 返回异步I/O线程的使能标志
        # MdsAsyncApi_IsIoThreadEnabled

        # 设置通信线程的线程初始化回调函数
        # MdsAsyncApi_SetOnCommunicationThreadStart

        # 设置回调线程的线程初始化回调函数 (如果已启用了独立的回调线程的话)
        # MdsAsyncApi_SetOnCallbackThreadStart

        # 设置异步I/O线程的线程初始化回调函数 (如果已启用了异步I/O线程的话)
        # MdsAsyncApi_SetOnIoThreadStart
        # -------------------------


        # ===================================================================
        # MDS异步API接口函数封装 (查询接口)
        # ===================================================================

        # 获取API的发行版本号
        self.c_mds_async_api_get_api_version = self.c_api_dll.MdsAsyncApi_GetApiVersion
        self.c_mds_async_api_get_api_version.restype = c_char_p

        # 查询证券行情快照
        self.c_mds_async_api_query_mkt_data_snapshot = self.c_api_dll.MdsAsyncApi_QueryMktDataSnapshot
        self.c_mds_async_api_query_mkt_data_snapshot.restype = c_int32
        self.c_mds_async_api_query_mkt_data_snapshot.argtypes = [
            POINTER(MdsAsyncApiContextT), c_int32, c_int32, c_int32,
            POINTER(MdsMktDataSnapshotT)
        ]

        # 批量查询行情快照
        self.c_mds_async_api_query_snapshot_list = self.c_api_dll.MdsAsyncApi_QuerySnapshotList
        self.c_mds_async_api_query_snapshot_list.restype = c_int32
        self.c_mds_async_api_query_snapshot_list.argtypes = [
            POINTER(MdsAsyncApiContextT), CCharP, CCharP,
            c_void_p, F_MDSAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 批量查询行情快照 (使用字符串指针数组形式的证券代码列表) (暂不对外开放)
        # self.c_mds_async_api_query_snapshot_list2 = self.c_api_dll.MdsAsyncApi_QuerySnapshotList2
        # self.c_mds_async_api_query_snapshot_list2.restype = c_int32
        # self.c_mds_async_api_query_snapshot_list2.argtypes = [
        #     POINTER(MdsAsyncApiContextT), POINTER(c_char_p), c_int32,
        #     c_void_p, F_MDSAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        # ]

        # 查询(深圳)证券实时状态 (基于异步API内置的查询通道执行)
        self.c_mds_async_api_query_security_status = self.c_api_dll.MdsAsyncApi_QuerySecurityStatus
        self.c_mds_async_api_query_security_status.restype = c_int32
        self.c_mds_async_api_query_security_status.argtypes = [
            POINTER(MdsAsyncApiContextT), c_int, c_int, c_int32,
            POINTER(MdsSecurityStatusMsgT)
        ]

        # 查询(上证)市场状态 (基于异步API内置的查询通道执行)
        self.c_mds_async_api_query_trd_session_status = self.c_api_dll.MdsAsyncApi_QueryTrdSessionStatus
        self.c_mds_async_api_query_trd_session_status.restype = c_int32
        self.c_mds_async_api_query_trd_session_status.argtypes = [
            POINTER(MdsAsyncApiContextT), c_int, c_int,
            POINTER(MdsTradingSessionStatusMsgT)
        ]

        # 批量查询证券(股票/债券/基金)静态信息列表 (基于异步API内置的查询通道执行)
        self.c_mds_async_api_query_stock_static_info_list = self.c_api_dll.MdsAsyncApi_QueryStockStaticInfoList
        self.c_mds_async_api_query_stock_static_info_list.restype = c_int32
        self.c_mds_async_api_query_stock_static_info_list.argtypes = [
            POINTER(MdsAsyncApiContextT), CCharP, CCharP,
            c_void_p, F_MDSAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 批量查询证券(股票/债券/基金)静态信息列表 (字符串指针数组形式的证券代码列表) (暂不对外开放)
        # self.c_mds_async_api_query_stock_static_info_list2 = self.c_api_dll.MdsAsyncApi_QueryStockStaticInfoList2
        # self.c_mds_async_api_query_stock_static_info_list2.restype = c_int32
        # self.c_mds_async_api_query_stock_static_info_list2.argtypes = [
        #     POINTER(MdsAsyncApiContextT), POINTER(c_char_p), c_int32,
        #     c_void_p, F_MDSAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        # ]

        # 批量查询期权合约静态信息列表 (基于异步API内置的查询通道执行)
        self.c_mds_async_api_query_option_static_info_list = self.c_api_dll.MdsAsyncApi_QueryOptionStaticInfoList
        self.c_mds_async_api_query_option_static_info_list.restype = c_int32
        self.c_mds_async_api_query_option_static_info_list.argtypes = [
            POINTER(MdsAsyncApiContextT), CCharP, CCharP,
            c_void_p, F_MDSAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 批量查询期权合约静态信息列表 (字符串指针数组形式的证券代码列表) (暂不对外开放)
        # self.c_mds_async_api_query_option_static_info_list2 = self.c_api_dll.MdsAsyncApi_QueryOptionStaticInfoList2
        # self.c_mds_async_api_query_option_static_info_list2.restype = c_int32
        # self.c_mds_async_api_query_option_static_info_list2.argtypes = [
        #     POINTER(MdsAsyncApiContextT), POINTER(c_char_p), c_int32,
        #     c_void_p, F_MDSAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        # ]
        # -------------------------


        # ===================================================================
        # MDS异步API接口函数封装 (逐笔数据重传请求接口函数声明)
        # ===================================================================

        # 发送逐笔数据重传请求
        # 逐笔数据重传请求通过查询通道发送到MDS服务器, 并采用请求/应答的方式返回处理结果并同步执行回调函数
        self.c_mds_async_api_send_tick_resend_request = self.c_api_dll.MdsAsyncApi_SendTickResendRequest
        self.c_mds_async_api_send_tick_resend_request.restype = c_int32
        self.c_mds_async_api_send_tick_resend_request.argtypes = [
            POINTER(MdsAsyncApiContextT),
            c_uint8, c_uint16, c_uint32, c_uint32,
            F_MDSAPI_ASYNC_ON_QRY_MSG_T, c_void_p
        ]

        # 发送逐笔数据重传请求
        # 逐笔数据重传请求通过查询通道发送到MDS服务器, 并采用请求/应答的方式返回处理结果并同步执行回调函数
        self.c_mds_async_api_send_tick_resend_request2 = self.c_api_dll.MdsAsyncApi_SendTickResendRequest2
        self.c_mds_async_api_send_tick_resend_request2.restype = c_int32
        self.c_mds_async_api_send_tick_resend_request2.argtypes = [
            POINTER(MdsAsyncApiContextT),
            POINTER(MdsTickResendRequestReqT),
            F_MDSAPI_ASYNC_ON_QRY_MSG_T,
            c_void_p,
            POINTER(MdsTickResendRequestRspT)
        ]

        # 发送逐笔数据重传请求
        # 支持不限制大小的重传请求 (将自动拆分为多条小的逐笔数据重传请求发送到MDS服务器, 并采用请求/应答的方式返回处理结果并同步执行回调函数)
        self.c_mds_async_api_send_tick_resend_request_hugely = self.c_api_dll.MdsAsyncApi_SendTickResendRequestHugely
        self.c_mds_async_api_send_tick_resend_request_hugely.restype = c_int32
        self.c_mds_async_api_send_tick_resend_request_hugely.argtypes = [
            POINTER(MdsAsyncApiContextT),
            POINTER(MdsTickResendRequestReqT),
            F_MDSAPI_ASYNC_ON_QRY_MSG_T,
            c_void_p,
            POINTER(MdsTickResendRequestRspT),
            c_int32
        ]
        # -------------------------


        # ===================================================================
        # MDS异步API接口函数封装 (密码修改接口函数声明)
        # ===================================================================

        # 发送密码修改请求(修改客户端登录密码)
        # 密码修改请求通过查询通道发送到MDS服务器, 并采用请求 / 应答的方式直接返回处理结果
        self.c_mds_async_api_send_change_password_req = self.c_api_dll.MdsAsyncApi_SendChangePasswordReq
        self.c_mds_async_api_send_change_password_req.restype = c_int32
        self.c_mds_async_api_send_change_password_req.argtypes = [
            POINTER(MdsAsyncApiContextT),
            POINTER(MdsChangePasswordReqT),
            POINTER(MdsChangePasswordRspT)
        ]
        # -------------------------


        # ===================================================================
        # MDS同步API接口函数封装
        # ===================================================================

        # 初始化日志记录器
        self.c_mds_api_init_logger = self.c_api_dll.MdsApi_InitLogger
        self.c_mds_api_init_logger.restype = c_int
        self.c_mds_api_init_logger.argtypes = [CCharP, CCharP]

        # 直接通过指定的参数初始化日志记录器
        self.c_mds_api_init_logger_direct = self.c_api_dll.MdsApi_InitLoggerDirect
        self.c_mds_api_init_logger_direct.restype = c_int
        self.c_mds_api_init_logger_direct.argtypes = [
            CCharP, CCharP, CCharP, c_int32, c_int32
        ]

        # 解析客户端配置文件
        self.c_mds_api_parse_config_from_file = self.c_api_dll.MdsApi_ParseConfigFromFile
        self.c_mds_api_parse_config_from_file.restype = c_int
        self.c_mds_api_parse_config_from_file.argtypes = [
            CCharP, CCharP, CCharP,
            POINTER(MdsApiRemoteCfgT),
            POINTER(MdsApiSubscribeInfoT)
        ]

        # 解析服务器地址列表字符串
        self.c_mds_api_parse_addr_list_string = self.c_api_dll.MdsApi_ParseAddrListString
        self.c_mds_api_parse_addr_list_string.restype = c_int32
        self.c_mds_api_parse_addr_list_string.argtypes = [
            CCharP, POINTER(MdsApiAddrInfoT), c_int32
        ]

        # 设置SubscribeByString接口默认使用的数据模式 (tickType)
        self.c_mds_api_set_thread_subscribe_tick_type = self.c_api_dll.MdsApi_SetThreadSubscribeTickType
        self.c_mds_api_set_thread_subscribe_tick_type.restype = None
        self.c_mds_api_set_thread_subscribe_tick_type.argtypes = [c_int32]

        # 设置SubscribeByString接口默认使用的初始快照订阅标志 (isRequireInitialMktData)
        self.c_mds_api_set_thread_subscribe_require_init_md = self.c_api_dll.MdsApi_SetThreadSubscribeRequireInitMd
        self.c_mds_api_set_thread_subscribe_require_init_md.restype = None
        self.c_mds_api_set_thread_subscribe_require_init_md.argtypes = [c_int]

        # 设置SubscribeByString接口默认使用的行情数据的起始时间 (beginTime)
        self.c_mds_api_set_thread_subscribe_begin_time = self.c_api_dll.MdsApi_SetThreadSubscribeBeginTime
        self.c_mds_api_set_thread_subscribe_begin_time.restype = None
        self.c_mds_api_set_thread_subscribe_begin_time.argtypes = [c_int32]

        # 设置客户端自定义的本地IP地址
        self.c_mds_api_set_customized_ip = self.c_api_dll.MdsApi_SetCustomizedIp
        self.c_mds_api_set_customized_ip.restype = c_int
        self.c_mds_api_set_customized_ip.argtypes = [CCharP]

        # 获取客户端自定义的本地IP
        self.c_mds_api_get_customized_ip = self.c_api_dll.MdsApi_GetCustomizedIp
        self.c_mds_api_get_customized_ip.restype = c_char_p

        # 设置客户端自定义的本地MAC地址
        self.c_mds_api_set_customized_mac = self.c_api_dll.MdsApi_SetCustomizedMac
        self.c_mds_api_set_customized_mac.restype = c_int
        self.c_mds_api_set_customized_mac.argtypes = [CCharP]

        # 获取客户端自定义的本地MAC
        self.c_mds_api_get_customized_mac = self.c_api_dll.MdsApi_GetCustomizedMac
        self.c_mds_api_get_customized_mac.restype = c_char_p

        # 设置客户端自定义的本地设备序列号
        self.c_mds_api_set_customized_driver_id = self.c_api_dll.MdsApi_SetCustomizedDriverId
        self.c_mds_api_set_customized_driver_id.restype = c_int
        self.c_mds_api_set_customized_driver_id.argtypes = [CCharP]

        # 获取客户端自定义的本地设备序列号
        self.c_mds_api_get_customized_driver_id = self.c_api_dll.MdsApi_GetCustomizedDriverId
        self.c_mds_api_get_customized_driver_id.restype = c_char_p

        # 返回当前线程最近一次API调用失败的错误号
        self.c_mds_api_get_last_error = self.c_api_dll.MdsApi_GetLastError
        self.c_mds_api_get_last_error.restype = c_int

        # 设置当前线程的API错误号
        self.c_mds_api_set_last_error = self.c_api_dll.MdsApi_SetLastError
        self.c_mds_api_set_last_error.restype = None
        self.c_mds_api_set_last_error.argtypes = [c_int32]

        # 返回错误号对应的错误信息
        self.c_mds_api_get_error_msg = self.c_api_dll.MdsApi_GetErrorMsg
        self.c_mds_api_get_error_msg.restype = c_char_p
        self.c_mds_api_get_error_msg.argtypes = [c_int32]

        # 返回现货产品是否具有指定状态
        # 根据证券状态'securityStatus'字段判断 @see MdsStockStaticInfoT
        self.c_mds_api_has_stock_status = self.c_api_dll.MdsApi_HasStockStatus
        self.c_mds_api_has_stock_status.restype = c_int
        self.c_mds_api_has_stock_status.argtypes = [
            POINTER(MdsStockStaticInfoT),
            c_int32
        ]
        # -------------------------


# ===================================================================
# 行情日志接口函数定义
# ===================================================================

c_mds_api_loader = CMdsApiFuncLoader()

log_error = c_mds_api_loader.error
log_info  = c_mds_api_loader.info
log_debug = c_mds_api_loader.debug
log_trace = c_mds_api_loader.trace
# -------------------------