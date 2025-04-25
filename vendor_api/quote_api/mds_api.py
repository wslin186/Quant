# -*- coding: utf-8 -*-
"""
mds capi的python封装
"""

import time
import errno
from collections import OrderedDict
from typing import Any, Dict, List, Optional
from ctypes import _Pointer, POINTER, byref

from quote_api.model import (
    # spk_util.py
    VOID_NULLPTR, CHAR_NULLPTR,
    GENERAL_CLI_MAX_NAME_LEN,
    GENERAL_CLI_MAX_REMOTE_CNT,
    SPK_ENDPOINT_MAX_REMOTE_CNT,
    spk_decorator_exception,
    SMsgHeadT, MdsApiRemoteCfgT, MdsApiAddrInfoT, MdsAsyncApiChannelCfgT,
    MdsAsyncApiChannelT,

    # mds_base_model.py
    MdsSecurityStatusMsgT, MdsTradingSessionStatusMsgT, MdsMktDataSnapshotT,
    MdsStockStaticInfoT,

    # mds_qry_packets.py
    MdsQrySnapshotListFilterT, MdsQryStockStaticInfoListFilterT,
    MdsQryOptionStaticInfoListFilterT,

    # mds_mkt_pachets.py
    MdsApiSubscribeInfoT, MdsMktDataRequestReqT, MdsMktDataRequestEntryT,
    MdsTickResendRequestReqT, MdsChangePasswordReqT, MdsChangePasswordRspT
)

from quote_api.c_api_wrapper import (
    MdsAsyncApiContextParamsT, CMdsApiFuncLoader, MdsMsgDispatcher,
    log_error, log_info
)

from quote_api.mds_spi import MdsClientSpi


# ===================================================================
# 常量定义
# ===================================================================

## 同步API定义
# 默认的主配置区段名称
MDSAPI_CFG_DEFAULT_SECTION                      = "mds_client"
# 默认的日志配置区段名称
MDSAPI_CFG_DEFAULT_SECTION_LOGGER               = "log"
# 默认的TCP行情订阅服务配置项名称
MDSAPI_CFG_DEFAULT_KEY_TCP_ADDR                 = "tcpServer"
# 默认的行情查询服务配置项名称
MDSAPI_CFG_DEFAULT_KEY_QRY_ADDR                 = "qryServer"

# UDP行情订阅服务配置项名称 (快照-频道1, 上海L1/L2快照)
MDSAPI_CFG_DEFAULT_KEY_UDP_ADDR_SNAP1           = "udpServer.Snap1"
# UDP行情订阅服务配置项名称 (快照-频道2, 深圳L1/L2快照)
MDSAPI_CFG_DEFAULT_KEY_UDP_ADDR_SNAP2           = "udpServer.Snap2"

# UDP行情订阅服务配置项名称 (逐笔-频道1, 上海逐笔成交/逐笔委托)
MDSAPI_CFG_DEFAULT_KEY_UDP_ADDR_TICK1           = "udpServer.Tick1"
# UDP行情订阅服务配置项名称 (逐笔-频道2, 深圳逐笔成交/逐笔委托)
MDSAPI_CFG_DEFAULT_KEY_UDP_ADDR_TICK2           = "udpServer.Tick2"

# 默认的TCP连接的心跳间隔 (30秒, 如果超过2倍心跳时间没有接收到任何网络消息, 则可以认为连接异常)
MDSAPI_DEFAULT_HEARTBEAT_INTERVAL               = 30
# 默认的UDP连接的心跳间隔 (10秒, 如果超过3倍心跳时间没有接收到任何组播消息, 就可以认为组播异常)
MDSAPI_DEFAULT_UDP_HEARTBEAT_INTERVAL           = 10

# 逐笔数据重传的默认超时时间 (长时间请求不到任何数据时的超时时间, 单位:毫秒)
MDSAPI_DEFAULT_TICK_RESEND_TIMEOUT_MS           = 30 * 1000
# 逐笔数据重传的最大超时时间 (长时间请求不到任何数据时的超时时间, 单位:毫秒)
MDSAPI_MAX_TICK_RESEND_TIMEOUT_MS               = 900 * 1000

# 默认的证券代码列表等字符串分隔符
MDSAPI_DEFAULT_STRING_DELIM                     = ",;| \t\r\n"

## 异步API定义
# 可以同时连接的远程服务器的最大数量 (256)
MDSAPI_ASYNC_MAX_REMOTE_CNT                     = SPK_ENDPOINT_MAX_REMOTE_CNT

# 默认的异步API配置区段名称
MDSAPI_CFG_DEFAULT_SECTION_ASYNC_API            = "async_api"
# 默认的CPU亲和性配置区段名称
MDSAPI_CFG_DEFAULT_SECTION_CPUSET               = "cpuset"

# 默认的异步API线程的CPU亲和性配置项名称 (通信线程)
MDSAPI_CFG_DEFAULT_KEY_CPUSET_COMMUNICATION     = "mdsapi_communication"
# 默认的异步API线程的CPU亲和性配置项名称 (异步回调线程)
MDSAPI_CFG_DEFAULT_KEY_CPUSET_CALLBACK          = "mdsapi_callback"
# 默认的异步API线程的CPU亲和性配置项名称 (连接管理线程)
MDSAPI_CFG_DEFAULT_KEY_CPUSET_CONNECT           = "mdsapi_connect"
# 默认的异步API线程的CPU亲和性配置项名称 (I/O线程)
MDSAPI_CFG_DEFAULT_KEY_CPUSET_IO_THREAD         = "mdsapi_io_thread"
# -------------------------


# ===================================================================
# 常量定义 (枚举类型定义)
# ===================================================================

# 通道类型定义
class eMdsApiChannelTypeT:
    """
    通道类型定义
    """
    MDSAPI_CHANNEL_TYPE_TCP                     = 11 # TCP行情订阅通道
    MDSAPI_CHANNEL_TYPE_UDP                     = 12 # UDP行情组播通道
    MDSAPI_CHANNEL_TYPE_QUERY                   = 13 # 行情查询通道
# -------------------------


class MdsClientApi:
    """
    行情接口类
    """

    def __init__(self, config_file: str = '') -> None:
        """
        初始化 MdsClientApi

        Args:
            config_file (str): [配置文件路径]
            - 取值为空 或 None, 需在MdsClientApi实例化后, 显示创建异步api运行时环境

        Raises:
            Exception: [description]
        """
        # TODO 版本检查

        self._mds_api_context: Optional[_Pointer] = None

        self._config_file: str = config_file
        if self._config_file and self._config_file.strip() != '':
            if self.create_context(config_file) is False:
                raise Exception("创建MDS异步API的运行时环境失败! "
                    "config_file[{}]".format(config_file))

        self._mds_msg_dispatchers: List[MdsMsgDispatcher] = []

        # 用于自动分配默认的 channel_tag
        self.current_channel_no: int = id(self)
        self.mds_spi: Optional[MdsClientSpi] = None

        self._channels: Dict[str, tuple] = OrderedDict()
        self._default_channel: Optional[_Pointer] = None

        # 是否启动异步环境
        self._mds_api_started: bool = False
        self._mds_api_released: bool = False

    # ===================================================================
    # MDS异步API接口函数封装 (上下文管理接口)
    # ===================================================================

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def create_context(self, config_file: str) -> bool:
        """
        创建异步API的运行时环境 (通过配置文件和默认的配置区段加载相关配置参数)

        Args:
            config_file (str): [配置文件路径]
            - 取值为空 或 None, 需在MdsClientApi实例化后, 显示创建异步api的运行时环境

        Returns:
            [bool]: [True: 创建成功; False: 创建失败]
        """
        if self._mds_api_context:
            raise Exception("重复创建异步API运行时环境, 执行失败! "
                "config_file[{}], mds_api_context[{}]".format(
                config_file, self._mds_api_context))

        self._mds_api_context = \
            CMdsApiFuncLoader().c_mds_async_api_create_context(config_file)

        return True if self._mds_api_context else False

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def create_context2(self, config_file: str, log_section: str,
            async_api_section: str, cpuset_section: str) -> bool:
        """
        创建异步API的运行时环境 (通过配置文件和指定的配置区段加载相关配置参数)

        Args:
            config_file (str): [配置文件路径]
            - 取值为空 或 None, 需在MdsClientApi实例化后, 显示创建异步api的运行时环境
            log_section (str): [日志记录器的配置区段名称 (e.g. "log")]
            - 为空则忽略, 不初始化日志记录器
            async_api_section (str): [异步API扩展配置参数的配置区段名称 (e.g. "mds_client.async_api")]
            - 为空则忽略, 不加载异步API相关的扩展配置参数
            cpuset_section (str): [CPU亲和性配置的配置区段名称 (e.g. "cpuset")]
            - 为空则忽略, 不加载CPU亲和性配置

        Returns:
            [bool]: [True: 创建成功; False: 创建失败]
        """
        if self._mds_api_context:
            raise Exception("重复创建异步API运行时环境, 执行失败! "
                "config_file[{}], mds_api_context[{}]".format(
                config_file, self._mds_api_context))

        self._mds_api_context = \
            CMdsApiFuncLoader().c_mds_async_api_create_context2(
                config_file, log_section, async_api_section, cpuset_section)

        return True if self._mds_api_context else False

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def create_context_simple(self, log_conf_file: str,
            log_section: str, async_queue_size: int) -> bool:
        """
        创建异步API的运行时环境 (仅通过函数参数指定必要的配置参数)

        Args:
            log_conf_file (str): [日志配置文件路径]
            - 为空则忽略, 不初始化日志记录器
            log_section (str): [日志记录器的配置区段名称 (e.g. "log")]
            - 为空则使用默认值
            async_queue_size (int): [用于缓存行情数据的消息队列大小 (最大可缓存的消息数量)]
            - 为空则忽略, 不加载异步API相关的扩展配置参数

        Returns:
            [bool]: [True: 创建成功; False: 创建失败]
        """
        if self._mds_api_context:
            raise Exception("重复创建异步API运行时环境, 执行失败! "
                "config_file[{}], mds_api_context[{}]".format(
                log_conf_file, self._mds_api_context))

        self._mds_api_context = \
            CMdsApiFuncLoader().c_mds_async_api_create_context_simple(
                log_conf_file, log_section, async_queue_size)

        return True if self._mds_api_context else False

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def create_context_simple2(self,
            log_conf_file: str, log_section: str,
            context_params: MdsAsyncApiContextParamsT) -> bool:
        """
        创建异步API的运行时环境 (仅通过函数参数指定必要的配置参数)

        Args:
            log_conf_file (str): [日志配置文件路径]
            - 为空则忽略, 不初始化日志记录器
            log_section (str): [日志记录器的配置区段名称 (e.g. "log")]
            - 为空则使用默认值
            context_params (MdsAsyncApiContextParamsT): [上下文环境的创建参数]
            - 为空则使用默认值

        Returns:
            [bool]: [True: 创建成功; False: 创建失败]
        """
        if self._mds_api_context:
            raise Exception("重复创建异步API运行时环境, 执行失败! "
                "config_file[{}], mds_api_context[{}]".format(
                log_conf_file, self._mds_api_context))

        self._mds_api_context = \
            CMdsApiFuncLoader().c_mds_async_api_create_context_simple2(
                log_conf_file,
                log_section,
                byref(context_params) if context_params else None)

        return True if self._mds_api_context else False

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def register_spi(self,
            mds_client_spi: MdsClientSpi,
            add_default_channel = False) -> bool:
        """
        注册默认的回调类，并根据需要自动创建默认的回调和委托通道

        Args:
            mds_client_spi (MdsClientSpi): [回调类实例，用于处理默认通道的行情数据回报和查询结果]
            add_default_channel (bool, optional): [是否创建默认的行情订阅通道].
            - Defaults to False.

        Returns:
            [bool]: [True: 成功; False: 失败]
        """

        if self._mds_api_started:
            raise Exception('请在调用start前尝试!')

        if not isinstance(mds_client_spi, MdsClientSpi):
            raise Exception(f"错误的mds_client_spi参数: {mds_client_spi} "
                            f"{type(mds_client_spi)}")

        if self.mds_spi:
            raise Exception("已经调用过register_handler")

        self.mds_spi = mds_client_spi
        mds_client_spi.mds_api = self

        if add_default_channel:
            if not self._config_file or self._config_file.strip() == '':
                raise Exception("执行register_spi函数并指定参数add_default_channel"
                        "为True时, 需同时指定MdsClientApi._config_file配置文件名称")

            self.add_channel_from_file(mds_client_spi = mds_client_spi)

        return True

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def start(self) -> bool:
        """
        启动异步运行环境，调用前请确保已经无需再添加新的委托和回报通道, 启动后添加通道将不会生效

        Returns:
            [bool]: [True: 成功; False: 失败]
        """
        if self._mds_api_started:
            raise Exception("已经调用过start")

        if getattr(self, "_mds_api_released", False):
            raise Exception("已经调用过release")

        if not self._channels:
            raise Exception("未找到有效通道，启动失败")

        if not CMdsApiFuncLoader().c_mds_async_api_start(self._mds_api_context):
            raise Exception("启动异步线程失败!")

        self._mds_api_started = True
        return True

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def release(self) -> bool:
        """
        清空资源，释放实例

        Returns:
            [bool]: [True: 成功; False: 失败]
        """
        if self._mds_api_started is False:
            raise Exception("尚未启动异步API, 无需释放资源")

        if getattr(self, "_mds_api_released", False):
            raise Exception("已经调用过release")

        self._mds_api_released = True
        self._mds_api_started = False

        CMdsApiFuncLoader().c_mds_async_api_stop(self._mds_api_context)
        time.sleep(0.05)

        while not self.is_all_terminated():
            log_info(">>> 正在等待回调线程等异步API线程安全退出...")
            time.sleep(1)

        CMdsApiFuncLoader().c_mds_async_api_release_context(
            self._mds_api_context)

        del self._mds_api_context
        del self._config_file
        del self._channels
        del self._default_channel
        del self.mds_spi

        for dpt in self._mds_msg_dispatchers:
            dpt.release()
        del self._mds_msg_dispatchers

        return True

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def is_api_running(self) -> bool:
        """
        返回异步API的通信线程是否正在运行过程中

        Returns:
            [bool]: [True: 运行中; False: 未运行或已终止运行]
        """
        return CMdsApiFuncLoader().c_mds_async_api_is_running(
            self._mds_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=True)
    def is_all_terminated(self) -> bool:
        """
        返回异步API相关的所有线程是否都已经安全退出 (或尚未运行)

        Returns:
            [bool]: [True: 安全退出; False: 未安全退出]
        """
        return CMdsApiFuncLoader().c_mds_async_api_is_all_terminated(
            self._mds_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=0)
    def get_total_picked(self) -> int:
        """
        返回异步API累计已提取和处理过的消息数量

        Returns:
            [int]: [异步API累计已提取和处理过的消息数量]
        """
        return CMdsApiFuncLoader().c_mds_async_api_get_total_picked(
            self._mds_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=0)
    def get_total_io_picked(self) -> int:
        """
        返回异步I/O线程累计已提取和处理过的消息数量

        Returns:
            [int]: [异步I/O线程累计已提取和处理过的消息数量]
        """
        return CMdsApiFuncLoader().c_mds_async_api_get_total_io_picked(
            self._mds_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=0)
    def get_async_queue_total_count(self) -> int:
        """
        返回异步API累计已入队的消息数量

        Returns:
            [int]: [异步API累计已入队的消息数量]
        """
        return CMdsApiFuncLoader().c_mds_async_api_get_async_queue_total_count(
            self._mds_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=0)
    def get_async_queue_remaining_count(self) -> int:
        """
        返回队列中尚未被处理的剩余数据数量

        Returns:
            [int]: [队列中尚未被处理的剩余数据数量]
        """
        return CMdsApiFuncLoader().c_mds_async_api_get_async_queue_remaining_count(
            self._mds_api_context)
    # -------------------------


    # ===================================================================
    # MDS异步API接口函数封装 (通道管理接口)
    # ===================================================================

    @spk_decorator_exception(log_error=log_error, error_no=0)
    def get_channel_count(self) -> int:
        """
        返回通道数量 (通道配置信息数量)

        Returns:
            [int]: [通道数量 (通道配置信息数量)]
        """
        return CMdsApiFuncLoader().c_mds_async_api_get_channel_count(
            self._mds_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=0)
    def get_connected_channel_count(self) -> int:
        """
        返回当前已连接的通道数量

        Returns:
            [int]: [当前已连接的通道数量]
        """
        return CMdsApiFuncLoader().c_mds_async_api_get_connected_channel_count(
            self._mds_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=None)
    def add_channel(self,
            channel_tag: str = "",
            remote_cfg: MdsApiRemoteCfgT = None,
            user_info: Any = "",
            mds_client_spi: MdsClientSpi = None,
            copy_args: bool = True) -> MdsAsyncApiChannelT:
        """
        添加通道配置信息

        @note 提示:
        - 不能将TCP通道和UDP通道添加到同一个异步API实例中
        - 异步API内置了对查询接口的支持, 不能直接将查询通道添加到异步API实例中

        Args:
            channel_tag (str): [通道配置信息的自定义标签, 长度应小于32 (可以为空)]
            remote_cfg (MdsApiRemoteCfgT): [待添加的通道配置信息 (不可为空)]
            user_info (Any): [用户回调参数]

            mds_client_spi (MdsClientSpi): [行情订阅通道消息的处理函数类]
            - Defaults to None. 此时默认使用self.mds_spi

            copy_args (bool): [是否复制服务端返回的行情数据]
            - Defaults to True
            - 可手动设置成False, 会提升吞吐和降低时延，但是行情数据需要立即保存起来, 否则后期使用会因异步队列数据覆盖而无法访问的风险

        Returns:
            [MdsAsyncApiChannelT]: [通道信息，请勿对其进行任何修改赋值操作]
        """
        return self.__add_channel_base_impl(False,
            channel_tag, user_info, mds_client_spi, copy_args,
            remote_cfg, "", "", "")

    @spk_decorator_exception(log_error=log_error, error_no=None)
    def add_channel_from_file(self,
            channel_tag: str = "",
            config_file: str = "",
            config_section: str = MDSAPI_CFG_DEFAULT_SECTION,
            addr_key: str = MDSAPI_CFG_DEFAULT_KEY_TCP_ADDR,
            user_info: Any = "",
            mds_client_spi: MdsClientSpi = None,
            copy_args: bool = True) -> MdsAsyncApiChannelT:
        """
        从配置文件中加载并添加通道配置信息

        @note 提示:
        - 不能将TCP通道和UDP通道添加到同一个异步API实例中
        - 异步API内置了对查询接口的支持, 不能直接将查询通道添加到异步API实例中

        Args:
            channel_tag (str): [通道配置信息的自定义标签, 长度应小于32 (可以为空)]
            config_file (str): [配置文件路径 (不可为空)]
            config_section (str): [配置区段名称 (不可为空, e.g. "mds_client")]
            addr_key (str): [服务器地址的配置项关键字 (不可为空)]
            user_info (Any): [用户回调参数]

            mds_client_spi (MdsClientSpi): [行情订阅通道消息的处理函数类].
            - Defaults to None. 此时默认使用self.mds_spi

            copy_args (bool): [是否复制服务端返回的行情数据].
            - Defaults to True
            - 可手动设置成False, 会提升吞吐和降低时延，但是行情数据需要立即保存起来, 否则后期使用会因异步队列数据覆盖而无法访问的风险

        Returns:
            [MdsAsyncApiChannelT]: [通道信息，请勿对其进行任何修改赋值操作]
        """
        return self.__add_channel_base_impl(True,
            channel_tag, user_info, mds_client_spi, copy_args,
            None, config_file, config_section, addr_key)

    @spk_decorator_exception(log_error=log_error, error_no=None)
    def get_channel(self, channel_index: int) -> MdsAsyncApiChannelT:
        """
        返回顺序号对应的连接通道信息

        Args:
            channel_index (str): [通道顺序号]
            - 大于0: 返回与指定顺序号相对应的, 并且与指定通道类型相匹配的通道信息 (顺序号与通道配置的添加顺序一致)
            - 小于0: 返回第一个与指定通道类型相匹配的通道信息
            - INT_MAX: 返回最后一个与指定通道类型相匹配的通道信息

        Returns:
            [MdsAsyncApiChannelT]: [通道信息，请勿对其进行任何修改赋值操作]
        """
        p_channel: _Pointer = \
            CMdsApiFuncLoader().c_mds_async_api_get_channel(
                self._mds_api_context, channel_index)
        return p_channel.contents if p_channel else None

    @spk_decorator_exception(log_error=log_error, error_no=None)
    def get_channel_by_tag(self, channel_tag: str) -> MdsAsyncApiChannelT:
        """
        返回标签对应的连接通道信息

        Args:
            channel_tag (str): [通道配置信息的自定义标签]

        Returns:
            [MdsAsyncApiChannelT]: [通道信息，请勿对其进行任何修改赋值操作]
        """
        p_channel: _Pointer = \
            CMdsApiFuncLoader().c_mds_async_api_get_channel_by_tag(
                self._mds_api_context, channel_tag)
        return p_channel.contents if p_channel else None

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def is_channel_connected(self, channel: MdsAsyncApiChannelT) -> bool:
        """
        返回通道是否已连接就绪

        Args:
            channel (MdsAsyncApiChannelT): [异步API的连接通道信息]

        Returns:
            [bool]: [True: 已就绪; False: 未就绪]
        """
        return CMdsApiFuncLoader().c_mds_async_api_is_channel_connected(channel)

    @spk_decorator_exception(log_error=log_error, error_no=None)
    def get_channel_cfg(self,
            channel: MdsAsyncApiChannelT) -> MdsAsyncApiChannelCfgT:
        """
        返回通道对应的配置信息

        Args:
            channel (MdsAsyncApiChannelT): [异步API的连接通道信息]

        Returns:
            [MdsAsyncApiChannelCfgT]: [通道配置信息]
        """
        channel_cfg: MdsAsyncApiChannelCfgT = \
            CMdsApiFuncLoader().c_mds_async_api_get_channel_cfg(channel)
        return channel_cfg.contents if channel_cfg else None

    @spk_decorator_exception(log_error=log_error, error_no=None)
    def get_channel_subscribe_cfg(self,
            channel: MdsAsyncApiChannelT) -> MdsApiSubscribeInfoT:
        """
        返回通道对应的行情订阅配置信息

        Args:
            channel (MdsAsyncApiChannelT): [异步API的连接通道信息]

        Returns:
            [MdsApiSubscribeInfoT]: [行情订阅配置信息]
        """
        subscribe_info: MdsApiSubscribeInfoT = \
            CMdsApiFuncLoader().c_mds_async_api_get_channel_subscribe_cfg(
                channel)
        return subscribe_info.contents if subscribe_info else None
    # -------------------------


    # ===================================================================
    # MDS异步API接口函数封装 (会话管理接口)
    # ===================================================================

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def subscribe_market_data(self,
            channel: MdsAsyncApiChannelT = None,
            subscribe_info: MdsApiSubscribeInfoT = None) -> bool:
        """
        以异步的方式发送证券行情实时订阅请求, 以重新订阅、追加订阅或删除订阅行情数据

        Args:
            channel (MdsAsyncApiChannelT): [异步API的连接通道信息]
            subscribe_info (MdsApiSubscribeInfoT): [行情订阅请求信息]

        Returns:
            [bool]: [True: 订阅成功; False: 订阅失败]
        """
        return CMdsApiFuncLoader().c_mds_async_api_subscribe_market_data(
            channel,
            byref(subscribe_info.mktDataRequestReq) if subscribe_info else None,
            subscribe_info.entries if subscribe_info else None)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def subscribe_by_string(self,
            channel: MdsAsyncApiChannelT = None,
            security_list: str = "",
            delimiter: str = MDSAPI_DEFAULT_STRING_DELIM,
            exchange_id: int = 0,
            product_type: int = 0,
            sub_mode: int = 0,
            data_types: int = 0) -> bool:
        """
        根据字符串形式的证券代码列表订阅行情信息

        Args:
            channel (MdsAsyncApiChannelT): [异步API的连接通道信息]
            security_list (str): [证券代码列表字符串]
            - 证券代码支持以 .SH 或 .SZ 为后缀来指定其所属的交易所
            - 空字符串 "", 表示不订阅任何产品的行情
            - 空指针 NULL, 表示订阅所有产品的行情

            delimiter (str): [证券代码列表的分隔符 (e.g. ",;| \t")]
            - 如果为空, 则使用默认的分隔符: ',' 或 ';' 或 '|' 或 ' ' 或 '\t'

            exchange_id (int): [证券代码所属的交易所代码 (如果证券代码没有 .SH 或 .SZ 后缀的话)]
            product_type (int): [行情产品类型 (股票(基金、债券)/指数/期权)]
            sub_mode (int): [订阅模式 (重新订阅/追加订阅/删除订阅)]

            data_types (int): [订阅的数据种类 @see eMdsSubscribeDataTypeT
                              (e.g. MDS_SUB_DATA_TYPE_L1_SNAPSHOT
                              | MDS_SUB_DATA_TYPE_L2_SNAPSHOT
                              | MDS_SUB_DATA_TYPE_L2_TRADE)]
                              - 当订阅模式为追加订阅时, 如果该参数小于0, 将忽略该参数, 维持上一次订阅时的设置
                              - 当订阅模式为删除订阅时, 该参数没有意义, 将会被忽略

        Returns:
            [bool]: [True: 订阅成功; False: 订阅失败]
        """
        return CMdsApiFuncLoader().c_mds_async_api_subscribe_by_string(
            channel, security_list, delimiter, exchange_id,
            product_type, sub_mode, data_types)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def subscribe_by_string_and_prefixes(self,
            channel: MdsAsyncApiChannelT = None,
            security_list: str = "",
            delimiter: str = MDSAPI_DEFAULT_STRING_DELIM,
            sse_code_prefixes: str = "",
            szse_code_prefixes: str = "",
            product_type: int = 0,
            sub_mode: int = 0,
            data_types: int = 0) -> bool:
        """
        直接根据字符串形式的证券代码列表订阅行情, 并通过证券代码前缀来区分和识别所属市场

        Args:
            channel (MdsAsyncApiChannelT): [异步API的连接通道信息]
            security_list (str): [证券代码列表字符串]
            - 证券代码支持以 .SH 或 .SZ 为后缀来指定其所属的交易所
            - 空字符串 "", 表示不订阅任何产品的行情
            - 空指针 NULL, 表示订阅所有产品的行情

            delimiter (str): [证券代码列表的分隔符 (e.g. ",;| \t")]
            - 如果为空, 则使用默认的分隔符: ',' 或 ';' 或 '|' 或 ' ' 或 '\t'

            sse_code_prefixes (str): [以逗号或空格分隔的上海证券代码前缀列表, e.g.
                              - "6, 300, 301" 将匹配证券代码列表中所有以 '6' 或 '300' 或 '301' 起始的证券代码
                              - 若为NULL或空字符串, 则不会匹配任何证券代码
                              - 上海证券代码前缀参考:
                                  - "009, 01, 02, "               //国债
                                  - "10, 11, 12, 13, 18, 19, "    //债券 (企业债、可转债等)
                                  - "20, "                        //债券 (回购)
                                  - "5, "                         //基金
                                  - "6, "                         //A股
                                  - "000"                         //指数]

            szse_code_prefixes (str): [以逗号或空格分隔的深圳证券代码前缀列表
                              - 若为NULL或空字符串, 则不会匹配任何证券代码
                              - 证券代码前缀可以和上海相同, 此时匹配的证券代码会同时对上海和深圳两个市场进行订阅
                              - 深圳证券代码前缀参考:
                                  - "00, "                        //股票
                                  - "10, 11, 12, 13, "            //债券
                                  - "15, 16, 17, 18, "            //基金
                                  - "30, "                        //创业板
                                  - "39"                          //指数

            product_type (int): [行情产品类型 (股票(基金、债券)/指数/期权)]
            sub_mode (int): [订阅模式 (重新订阅/追加订阅/删除订阅)]

            data_types (int): [订阅的数据种类 @see eMdsSubscribeDataTypeT
                              (e.g. MDS_SUB_DATA_TYPE_L1_SNAPSHOT
                              | MDS_SUB_DATA_TYPE_L2_SNAPSHOT
                              | MDS_SUB_DATA_TYPE_L2_TRADE)]
                              - 当订阅模式为追加订阅时, 如果该参数小于0, 将忽略该参数, 维持上一次订阅时的设置
                              - 当订阅模式为删除订阅时, 该参数没有意义, 将会被忽略

        Returns:
            [bool]: [True: 订阅成功; False: 订阅失败]
        """
        return CMdsApiFuncLoader().c_mds_async_api_subscribe_by_string_and_prefixes(
            channel,
            security_list if security_list else CHAR_NULLPTR,
            delimiter,
            sse_code_prefixes if szse_code_prefixes else CHAR_NULLPTR,
            szse_code_prefixes if szse_code_prefixes else CHAR_NULLPTR,
            product_type, sub_mode, data_types)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def subscribe_by_query(self,
            channel: MdsAsyncApiChannelT = None,
            sub_mode: int = 0,
            data_types: int = 0,
            qry_filter: MdsQryStockStaticInfoListFilterT = None) -> int:
        """
        查询证券静态信息, 并根据查询结果订阅行情信息

        Args:
            channel (MdsAsyncApiChannelT): [异步API的连接通道信息]

            sub_mode (int): [订阅模式 (重新订阅/追加订阅/删除订阅)]

            data_types (int): [订阅的数据种类 @see eMdsSubscribeDataTypeT
                              (e.g. MDS_SUB_DATA_TYPE_L1_SNAPSHOT
                              | MDS_SUB_DATA_TYPE_L2_SNAPSHOT
                              | MDS_SUB_DATA_TYPE_L2_TRADE)]
                              - 当订阅模式为追加订阅时, 如果该参数小于0, 将忽略该参数, 维持上一次订阅时的设置
                              - 当订阅模式为删除订阅时, 该参数没有意义, 将会被忽略

            qry_filter (MdsQryStockStaticInfoListFilterT): [查询过滤条件]
            - 传None 或 将过滤条件初始化为0, 代表无需过滤

        Returns:
            [int]: [>=0: 成功查询到的记录数; <0: 失败 (负的错误号)]
        """
        return CMdsApiFuncLoader().c_mds_async_api_subscribe_by_query(
            channel, sub_mode, data_types, None,
            byref(qry_filter) if qry_filter else None)

    @spk_decorator_exception(log_error=log_error, error_no=1)
    def default_on_connect(self, channel: MdsAsyncApiChannelT) -> int:
        """
        连接完成后处理的默认实现

        Args:
            channel (MdsAsyncApiChannelT): [异步API的连接通道信息]

        Returns:
            [int]: [=0: 成功
                  >0: 处理失败, 将重建连接并继续尝试执行
                  <0: 处理失败, 异步API将中止运行
                  ]
        """
        return CMdsApiFuncLoader().c_mds_async_api_default_on_connect(
            channel, VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=1)
    def subscribe_nothing_on_connect(self, channel: MdsAsyncApiChannelT) -> int:
        """
        连接完成后处理的默认实现 (不订阅任何行情数据)

        Args:
            channel (MdsAsyncApiChannelT): [异步API的连接通道信息]

        Returns:
            [int]: [=0: 成功
                  >0: 处理失败, 将重建连接并继续尝试执行
                  <0: 处理失败, 异步API将中止运行
                  ]
        """
        return CMdsApiFuncLoader().c_mds_async_api_subscribe_nothing_on_connect(
            channel, VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def send_heart_beat(self, channel: MdsAsyncApiChannelT) -> bool:
        """
        发送心跳消息

        Args:
            channel (MdsAsyncApiChannelT): [异步API的连接通道信息]

        Returns:
            [bool]: [TRUE 成功; FALSE 失败]
        """
        return CMdsApiFuncLoader().c_mds_async_api_send_heart_beat(channel)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def send_test_req(self, channel: MdsAsyncApiChannelT,
            test_req_id: str, test_req_id_size: int) -> bool:
        """
        发送测试消息

        Args:
            channel (MdsAsyncApiChannelT): [异步API的连接通道信息]
            test_req_id (str): [测试请求标识符 (C32, 可以为空)]
            test_req_id_size (int): [测试请求标识符的长度]

        Returns:
            [bool]: [TRUE 成功; FALSE 失败]
        """
        return CMdsApiFuncLoader().c_mds_async_api_send_test_req(
            channel, test_req_id, test_req_id_size)
    # -------------------------


    # ===================================================================
    # MDS异步API接口函数封装 (辅助的配置管理接口)
    # ===================================================================

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_preconnect_able(self, is_preconnect_able: bool) -> bool:
        """
        设置是否在启动前预创建并校验所有的连接

        Args:
            is_preconnect_able (bool): [是否在启动前预创建并校验所有的连接]
            - TRUE: 启动前预创建并校验所有的连接, 如果连接失败则中止启动
            - FALSE: 启动前不预先创建和校验连接 (默认行为)

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        return CMdsApiFuncLoader().c_mds_async_api_set_preconnect_able(
            self._mds_api_context, is_preconnect_able)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def is_preconnect_able(self) -> bool:
        """
        返回是否在启动前预创建并校验所有的连接

        Returns:
            [bool]: [True: 是; False: 否]
        """
        return CMdsApiFuncLoader().c_mds_async_api_is_preconnect_able(
            self._mds_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_compressible(self, is_compressible: bool) -> bool:
        """
        设置是否需要支持对接压缩后的行情数据

        Args:
            is_compressible (bool): [是否需要支持对接压缩后的行情数据]
            - 如果可能会对接压缩行情端口, 可以将该参数设置为TRUE, 这样就可以同时兼容压缩和非压缩的行情数据
            - 如果确定不会对接压缩行情端口的话, 则可以将该参数设置为FALSE, 这样可以避免额外的(微小的)性能消耗

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        return CMdsApiFuncLoader().c_mds_async_api_set_compressible(
            self._mds_api_context, is_compressible)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def is_compressible(self) -> bool:
        """
        返回是否支持对接压缩后的行情数据

        Returns:
            [bool]: [True: 是; False: 否]
        """
        return CMdsApiFuncLoader().c_mds_async_api_is_compressible(
            self._mds_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_udp_filter_able(self, is_udp_filter_able: bool) -> bool:
        """
        设置是否启用对UDP行情数据的本地行情订阅和过滤功能

        Args:
            is_udp_filter_able (bool): [是否启用对UDP行情数据的本地订阅和过滤功能]
            - 如果将该参数设置为TRUE, 则允许通过 MdsAsyncApi_SubscribeByString 等接口
              设置 UDP 行情的订阅条件, 并在API端完成对行情数据的过滤
            - 如果不需要通过API进行行情数据过滤的话, 可以将该参数设置为FALSE, 这样可以避免额外的(微小的)性能消耗

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        return CMdsApiFuncLoader().c_mds_async_api_set_udp_filter_able(
            self._mds_api_context, is_udp_filter_able)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def is_udp_filter_able(self) -> bool:
        """
        返回是否启用对UDP行情数据的本地行情订阅和过滤功能

        Returns:
            [bool]: [True: 是; False: 否]
        """
        return CMdsApiFuncLoader().c_mds_async_api_is_udp_filter_able(
            self._mds_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_async_callback_able(self, is_async_callback_able: bool) -> bool:
        """
        设置是否启动独立的回调线程来执行回调处理

        Args:
            is_async_callback_able (bool): [是否启动独立的回调线程来执行回调处理]
            - TRUE: 创建单独的回调线程
            - FALSE: 不启动单独的回调线程, 直接在通信线程下执行回调处理 (默认行为)

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        return CMdsApiFuncLoader().c_mds_async_api_set_async_callback_able(
            self._mds_api_context, is_async_callback_able)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def is_async_callback_able(self) -> bool:
        """
        返回是否启动独立的回调线程来执行回调处理

        Returns:
            [bool]: [True: 是; False: 否]
        """
        return CMdsApiFuncLoader().c_mds_async_api_is_async_callback_able(
            self._mds_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def get_async_queue_length(self) -> int:
        """
        返回异步通信队列的长度 (可缓存的最大消息数量)

        Returns:
            [int]: [异步通信队列的长度 (可缓存的最大消息数量)]
        """
        return CMdsApiFuncLoader().c_mds_async_api_get_async_queue_length(
            self._mds_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def get_async_queue_data_area_size(self) -> int:
        """
        返回异步通信队列的数据空间大小

        Returns:
            [int]: [异步通信队列的数据空间大小]
        """
        return CMdsApiFuncLoader().\
            c_mds_async_api_get_async_queue_data_area_size(
                self._mds_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_builtin_query_able(self, is_builtin_query_able: bool) -> bool:
        """
        设置是否启用内置的查询通道

        Args:
            is_builtin_query_able (bool): [是否启用内置的查询通道]
            - 如果将该参数设置为TRUE, 则启动异步API时将自动创建一个与行情查询服务的连接
            - 如果不需要通过异步API查询行情数据的话, 可以将该参数设置为FALSE, 这样可以避免额外占用一个查询通道的连接数量
            - 不指定的话, 默认为FALSE

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        return CMdsApiFuncLoader().c_mds_async_api_set_builtin_query_able(
            self._mds_api_context, is_builtin_query_able)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def is_builtin_query_able(self) -> bool:
        """
        返回是否启用内置的查询通道

        Returns:
            [bool]: [True: 是; False: 否]
        """
        return CMdsApiFuncLoader().c_mds_async_api_is_builtin_query_able(
            self._mds_api_context)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def is_builtin_query_channel_connected(self) -> bool:
        """
        返回内置的查询通道是否已连接就绪

        Returns:
            [bool]: [True: 是; False: 否]
        """
        return CMdsApiFuncLoader().\
            c_mds_async_api_is_builtin_query_channel_connected(
                self._mds_api_context)
    # -------------------------


    # ===================================================================
    # MDS异步API接口函数封装 (查询接口)
    # ===================================================================

    @spk_decorator_exception(log_error=log_error, error_no='')
    def get_api_version(self) -> str:
        """
        获取API的发行版本号

        Returns:
            [str]: [API的发行版本号 (如: "0.15.3")]
        """
        return CMdsApiFuncLoader().c_mds_async_api_get_api_version().decode()

    @spk_decorator_exception(log_error=log_error, error_no=None)
    def query_mkt_data_snapshot(self,
            channel: MdsAsyncApiChannelT = None,
            exchange_id: int = 0,
            product_type: int = 0,
            instr_id: int = 0,
            user_info: Any = None) -> int:
        """
        查询证券行情快照

        Args:
            channel (MdsAsyncApiChannelT): [查询通道]
            exchange_id (int): [交易所代码]
            product_type (int): [行情产品类型]
            instr_id (int): [证券代码 (转换为整数类型的证券代码)]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [=0: 成功; <0: 查询失败 (负的错误号); ENOENT: 未检索到待查询的数据]
        """
        mkt_data_snapshot = MdsMktDataSnapshotT()

        ret: int = CMdsApiFuncLoader().c_mds_async_api_query_mkt_data_snapshot(
            self._mds_api_context or None,
            exchange_id,
            product_type,
            instr_id,
            byref(mkt_data_snapshot))

        if ret == 0:
            self.__get_mds_msg_dispatcher_by_channel(channel). \
                get_spi().on_qry_mkt_data_snapshot(channel,
                    SMsgHeadT(), mkt_data_snapshot, user_info)

        return ret

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_snapshot_list(self,
            channel: MdsAsyncApiChannelT = None,
            security_list: str = '',
            delimiter: str = MDSAPI_DEFAULT_STRING_DELIM,
            qry_filter: MdsQrySnapshotListFilterT = None,
            user_info: Any = None) -> int:
        """
        批量查询行情快照

        Args:
            channel (MdsAsyncApiChannelT): [查询通道]
            security_list (str): [证券代码列表字符串]
                - 证券代码支持以 .SH 或 .SZ 为后缀来指定其所属的交易所
                - 空字符串 "" 或 None, 表示查询所有产品的行情 (不包括指数和期权)
            delimiter (str): [证券代码列表的分隔符 (e.g. ",;| \t")]
                - 空字符串 "" 或 None, 则使用默认的分隔符: ',' 或 ';' 或 '|' 或 ' ' 或 '\t'
            qry_filter (MdsQrySnapshotListFilterT): [查询过滤条件]
                - None 或 将过滤条件初始化为0, 代表无需过滤
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功查询到的记录数; <0: 失败 (负的错误号)]
        """
        return CMdsApiFuncLoader().c_mds_async_api_query_snapshot_list(
            self._mds_api_context or None,
            security_list or CHAR_NULLPTR,
            delimiter or CHAR_NULLPTR,
            byref(qry_filter) if qry_filter else None,
            self.__get_mds_msg_dispatcher_by_channel(
                channel).handle_qry_msg(user_info),
            VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_security_status(self,
            channel: MdsAsyncApiChannelT = None,
            exchange_id: int = 0,
            product_type: int = 0,
            instr_id: int = 0,
            user_info: Any = None) -> int:
        """
        查询(深圳)证券实时状态

        Args:
            channel (MdsAsyncApiChannelT): [查询通道]
            exchange_id (int): [交易所代码]
            product_type (int): [行情产品类型]
            instr_id (int): [证券代码 (转换为整数类型的证券代码)]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [=0: 查询成功; <0: 查询失败 (负的错误号)]
        """
        security_status = MdsSecurityStatusMsgT()

        ret: int = CMdsApiFuncLoader().c_mds_async_api_query_security_status(
            self._mds_api_context or None,
            exchange_id,
            product_type,
            instr_id,
            byref(security_status))

        if ret == 0:
            self.__get_mds_msg_dispatcher_by_channel(channel).\
                get_spi().on_qry_security_status(channel,
                    SMsgHeadT(), security_status, user_info)

        return ret

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_trd_session_status(self,
            channel: MdsAsyncApiChannelT = None,
            exchange_id: int = 0,
            product_type: int = 0,
            user_info: Any = None) -> int:
        """
        查询(上证)市场状态

        Args:
            channel (MdsAsyncApiChannelT): [查询通道]
            exchange_id (int): [交易所代码]
            product_type (int): [行情产品类型]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [=0: 查询成功; <0: 查询失败 (负的错误号)]
        """
        trd_session_status = MdsTradingSessionStatusMsgT()

        ret: int = CMdsApiFuncLoader().c_mds_async_api_query_trd_session_status(
            self._mds_api_context or None,
            exchange_id,
            product_type,
            byref(trd_session_status))

        if ret == 0:
            self.__get_mds_msg_dispatcher_by_channel(channel).\
                get_spi().on_qry_trd_session_status(channel,
                    SMsgHeadT(), trd_session_status, user_info)

        return ret

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_stock_static_info_list(self,
            channel: MdsAsyncApiChannelT = None,
            security_list: str = '',
            delimiter: str = MDSAPI_DEFAULT_STRING_DELIM,
            qry_filter: MdsQryStockStaticInfoListFilterT = None,
            user_info: Any = None) -> int:
        """
        批量查询证券(股票/债券/基金)静态信息列表

        Args:
            channel (MdsAsyncApiChannelT): [查询通道]
            security_list (str): [证券代码列表字符串]
                - 证券代码支持以 .SH 或 .SZ 为后缀来指定其所属的交易所
                - 空字符串 "" 或 None, 表示查询所有产品的行情 (不包括指数和期权)
            delimiter (str): [证券代码列表的分隔符 (e.g. ",;| \t")].
                - 空字符串 "" 或 None, 则使用默认的分隔符: ',' 或 ';' 或 '|' 或 ' ' 或 '\t'
            qry_filter (MdsQryStockStaticInfoListFilterT): [查询过滤条件]
                - None 或 将过滤条件初始化为0, 代表无需过滤
            user_info (Any): [用户回调参数]


        Returns:
            [int]: [>=0: 成功查询到的记录数; <0: 失败 (负的错误号)]
        """
        return CMdsApiFuncLoader().c_mds_async_api_query_stock_static_info_list(
            self._mds_api_context or None,
            security_list or CHAR_NULLPTR,
            delimiter or CHAR_NULLPTR,
            byref(qry_filter) if qry_filter else None,
            self.__get_mds_msg_dispatcher_by_channel(
                channel).handle_qry_msg(user_info),
            VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def query_option_static_info_list(self,
            channel: MdsAsyncApiChannelT = None,
            security_list: str = '',
            delimiter: str = MDSAPI_DEFAULT_STRING_DELIM,
            qry_filter: MdsQryOptionStaticInfoListFilterT = None,
            user_info: Any = None) -> int:
        """
        批量查询期权合约静态信息列表

        Args:
            channel (MdsAsyncApiChannelT): [查询通道]
            security_list (str): [证券代码列表字符串]
                - 证券代码支持以 .SH 或 .SZ 为后缀来指定其所属的交易所
                - 空字符串 "" 或 None, 表示查询所有产品的行情 (不包括指数和期权)
            delimiter (str): [证券代码列表的分隔符 (e.g. ",;| \t")].
                - 空字符串 "" 或 None, 则使用默认的分隔符: ',' 或 ';' 或 '|' 或 ' ' 或 '\t'
            qry_filter (MdsQryOptionStaticInfoListFilterT): [查询过滤条件]
                - None 或 将过滤条件初始化为0, 代表无需过滤
            user_info (Any): [用户回调参数]


        Returns:
            [int]: [>=0: 成功查询到的记录数; <0: 失败 (负的错误号)]
        """
        return CMdsApiFuncLoader().c_mds_async_api_query_option_static_info_list(
            self._mds_api_context or None,
            security_list or CHAR_NULLPTR,
            delimiter or CHAR_NULLPTR,
            byref(qry_filter) if qry_filter else None,
            self.__get_mds_msg_dispatcher_by_channel(
                channel).handle_qry_msg(user_info),
            VOID_NULLPTR)
    # -------------------------


    # ===================================================================
    # MDS异步API接口函数封装 (逐笔数据重传请求接口函数声明)
    # ===================================================================

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def send_tick_resend_request(self,
            channel: MdsAsyncApiChannelT = None,
            exchange_id: int = 0,
            channel_no: int = 0,
            begin_appl_seq_num: int = 0,
            end_appl_seq_num: int = 0,
            user_info: Any = None) -> int:
        """
        发送逐笔数据重传请求
        逐笔数据重传请求通过查询通道发送到MDS服务器, 并采用请求/应答的方式返回处理结果并同步执行回调函数

        @note        因为上交所逐笔合并数据即将上线, 为了简化接口, 未提供是否上交所老版竞价逐笔委托
                     频道 (isSseOldTickOrder) 参数。在逐笔合并数据上线前如需重传上交所老版竞价
                     逐笔委托数据, 需要使用 MdsAsyncApi_SendTickResendRequest2 接口

        @note        建议每次请求重传的数据不要大于 1000 (MDS_MAX_TICK_RESEND_ITEM_COUNT) 条,
                     如果请求重传的数据范围超过 1000 条, 服务器端只会返回前 1000 条数据
        @note        提示: 重传请求的应答数据类型和回调函数的执行次序如下:
                     - [0~1000] 条重传的逐笔数据, msgType 为: MDS_MSGTYPE_L2_TRADE / MDS_MSGTYPE_L2_ORDER / MDS_MSGTYPE_L2_SSE_ORDER
                     - 1 条逐笔数据重传请求的应答消息, msgType 为: MDS_MSGTYPE_TICK_RESEND_REQUEST

        Args:
            channel (MdsAsyncApiChannelT): [查询通道]
            exchange_id (int): [交易所代码(沪/深) @see eMdsExchangeIdT]
            channel_no (int): [频道代码 (取值范围[1..9999])]
            begin_appl_seq_num (int): [待重传的逐笔数据起始序号]
            end_appl_seq_num (int): [待重传的逐笔数据结束序号]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功重建到的逐笔成交/逐笔委托记录数; <0: 失败 (负的错误号)]
        """
        return CMdsApiFuncLoader().c_mds_async_api_send_tick_resend_request(
            self._mds_api_context or None,
            exchange_id,
            channel_no,
            begin_appl_seq_num,
            end_appl_seq_num,
            self.__get_mds_msg_dispatcher_by_channel(
                channel).handle_qry_msg(user_info, is_tick_resend = True),
            VOID_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def send_tick_resend_request2(self,
            channel: MdsAsyncApiChannelT = None,
            tick_resend_req: MdsTickResendRequestReqT = None,
            user_info: Any = None) -> int:
        """
        发送逐笔数据重传请求
        逐笔数据重传请求通过查询通道发送到MDS服务器, 并采用请求/应答的方式返回处理结果并同步执行回调函数

        @note        建议每次请求重传的数据不要大于 1000 (MDS_MAX_TICK_RESEND_ITEM_COUNT) 条,
                   如果请求重传的数据范围超过 1000 条, 服务器端只会返回前 1000 条数据
        @note        提示: 重传请求的应答数据类型和回调函数的执行次序如下:
                   - [0~1000] 条重传的逐笔数据, msgType 为: MDS_MSGTYPE_L2_TRADE / MDS_MSGTYPE_L2_ORDER / MDS_MSGTYPE_L2_SSE_ORDER
                   - 1 条逐笔数据重传请求的应答消息, msgType 为: MDS_MSGTYPE_TICK_RESEND_REQUEST

        Args:
            channel (MdsAsyncApiChannelT): [查询通道]
            tick_resend_req (MdsTickResendRequestReqT): [待发送的逐笔数据重传请求]
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功重建到的逐笔成交/逐笔委托记录数; <0: 失败 (负的错误号)]
        """
        return CMdsApiFuncLoader().c_mds_async_api_send_tick_resend_request2(
            self._mds_api_context or None,
            byref(tick_resend_req) if tick_resend_req else None,
            self.__get_mds_msg_dispatcher_by_channel(
                channel).handle_qry_msg(user_info, is_tick_resend = True),
            VOID_NULLPTR, None)

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def send_tick_resend_request_hugely(self,
            channel: MdsAsyncApiChannelT = None,
            tick_resend_req: MdsTickResendRequestReqT = None,
            time_out_ms: int = 0,
            user_info: Any = None) -> int:
        """
        发送超大的逐笔数据重传请求
        支持不限制大小的重传请求 (将自动拆分为多条小的逐笔数据重传请求发送到MDS服务器, 并采用请求/应答的方式返回处理结果并同步执行回调函数)

        @note      注意: 请谨慎使用该接口, 避免发起过大或不必要的重传请求, 以免挤占带宽资源
        @note      提示: 重传请求的应答数据类型和回调函数的执行次序如下:
                   - n 条重传的逐笔数据, msgType 为: MDS_MSGTYPE_L2_TRADE / MDS_MSGTYPE_L2_ORDER / MDS_MSGTYPE_L2_SSE_ORDER
                   - 1 条逐笔数据重传请求的应答消息, msgType 为: MDS_MSGTYPE_TICK_RESEND_REQUEST
        @note      当长时间请求不到任何数据时而超时返回时, 函数返回值仍然为大于等于0的值.
                   具体的重传状态可以通过重传请求的应答消息(回调处理)判断, 或直接通过函数返回值
                   (成功重建到的逐笔数量)进行判断

        Args:
            channel (MdsAsyncApiChannelT): [查询通道]
            tick_resend_req (MdsTickResendRequestReqT): [待发送的逐笔数据重传请求]
            time_out_ms (int): [长时间请求不到任何数据时的超时时间 (单位:毫秒)]
            - 大于0, 最大超时时间 (毫秒)
            - 等于0, 立即返回
            - 小于0, 使用默认值 (30秒)
            user_info (Any): [用户回调参数]

        Returns:
            [int]: [>=0: 成功重建到的逐笔成交/逐笔委托记录数; <0: 失败 (负的错误号)]
        """
        return CMdsApiFuncLoader().c_mds_async_api_send_tick_resend_request_hugely(
            self._mds_api_context or None,
            byref(tick_resend_req) if tick_resend_req else None,
            self.__get_mds_msg_dispatcher_by_channel(
                channel).handle_qry_msg(user_info, is_tick_resend = True),
            VOID_NULLPTR, None, time_out_ms)
    # -------------------------


    # ===================================================================
    # MDS异步API接口函数封装 (密码修改接口函数声明)
    # ===================================================================

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def send_change_password_req(self,
            channel: MdsAsyncApiChannelT = None,
            req: MdsChangePasswordReqT = None) -> int:
        """
        发送密码修改请求(修改客户端登录密码)
        密码修改请求通过查询通道发送到MDS服务器, 并采用请求 / 应答的方式直接返回处理结果

        Args:
            channel (MdsAsyncApiChannelT): [查询通道]
            req (MdsChangePasswordReqT): [待发送的密码修改请求]

        Returns:
            [int]: [=0: 成功; >0: API调用失败 (负的错误号); <0: 服务端业务处理失败 (MDS错误号)]
        """
        change_password_rsp = MdsChangePasswordRspT()

        ret: int = CMdsApiFuncLoader().c_mds_async_api_send_change_password_req(
            self._mds_api_context or None,
            byref(req) if req else None,
            byref(change_password_rsp))

        if ret == 0:
            self.__get_mds_msg_dispatcher_by_channel(channel). \
                get_spi().on_change_password_rsp(channel,
                    SMsgHeadT(), change_password_rsp)

        return ret
    # -------------------------


    # ===================================================================
    # MDS异步API接口函数封装 (辅助函数)
    # ===================================================================

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def init_logger(self, config_file: str, logger_section: str) -> bool:
        """
        初始化日志记录器

        Args:
            config_file (str): [配置文件路径]
            logger_section (str): [配置区段名称]

        Returns:
            [bool]: [TRUE 成功; FALSE 失败]
        """
        return CMdsApiFuncLoader().c_mds_api_init_logger(
            config_file or CHAR_NULLPTR,
            logger_section or CHAR_NULLPTR)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def init_logger_direct(self, log_mode: str, min_log_level: str,
            log_file_path: str, max_file_length: int,
            max_backup_count: int) -> bool:
        """
        直接通过指定的参数初始化日志记录器

        Args:
            log_mode (str): [日志模式]
            - 取值说明:
              - FILE              : 文件日志 - 等同于 FILE_ROLLING (轮换, 不区分具体日期)
              - FILE_ROLLING      : 文件日志 - 轮换, 不区分具体日期
              - FILE_DAILY        : 文件日志 - 每天一个日志文件
              - FILE_DAILY_ROLLING: 文件日志 - 每天N个日志文件 (N >= 1)
              - CONSOLE           : 控制台日志 - 等同于 CONSOLE_STDOUT (输出到标准输出)
              - CONSOLE_STDOUT    : 控制台日志 - 输出到标准输出 (stdout)
              - CONSOLE_STDERR    : 控制台日志 - 输出到标准错误 (stderr)
            min_log_level (str): [日志登记的起始级别]
            - 日志级别列表 (级别从低到高):
              - 跟踪信息 (TRACE)
              - 调试信息 (DEBUG)
              - 提示信息 (INFO)
              - 警告信息 (WARN)
              - 错误信息 (ERROR)
              - 业务提示 (BZINF, BZ_INFO)
              - 业务警告 (BZWRN, BZ_WARN)
              - 业务错误 (BZERR, BZ_ERROR)
              - 致命错误 (FATAL)
              - 屏蔽所有日志 (NONE)
            log_file_path (str): [日志文件路径]
            max_file_length (int): [日志文件最大长度]
            - 取值小于0, 表示无最大长度限制
            - 取值等于0, 将使用默认值 (400M)
            max_backup_count (int): [日志文件最大备份数]
            - 轮换(ROLLING)模式下的最大保留的历史日志文件数量
            - 取值小于0, 表示不保留备份文件
            - 取值等于0, 将使用默认值 (3)

        Returns:
            [bool]: [TRUE 成功; FALSE 失败]
        """
        return CMdsApiFuncLoader().c_mds_api_init_logger_direct(
            log_mode or CHAR_NULLPTR,
            min_log_level or CHAR_NULLPTR,
            log_file_path or CHAR_NULLPTR,
            max_file_length, max_backup_count)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def parse_config_from_file(self, config_file_name: str,
            section: str, addr_key: str, remote_cfg: MdsApiRemoteCfgT) -> bool:
        """
        解析客户端配置文件

        Args:
            config_file_name (str): [配置文件路径]
            section (str): [配置区段名称]
            addr_key (str): [地址列表的配置项关键字]
            remote_cfg (MdsApiRemoteCfgT): [输出远程主机配置信息]

        Returns:
            [bool]: [TRUE 成功; FALSE 失败]
        """
        subscribe_info: MdsApiSubscribeInfoT = MdsApiSubscribeInfoT()

        return CMdsApiFuncLoader().c_mds_api_parse_config_from_file(
            config_file_name, section, addr_key,
            byref(remote_cfg) if remote_cfg else None,
            byref(subscribe_info))

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def parse_addr_list_string(self, uri_list: str,
            p_out_addr_list: POINTER(MdsApiAddrInfoT) = None) -> int:
        """
        解析服务器地址列表字符串
        - 待解析的地址列表可是以空格、逗号或分号分割的地址列表字符串
          - e.g. "tcp://127.0.0.1:5100, tcp://192.168.0.11:5100"
        - 同时也可以在每个地址之前, 为其指定对应的主机编号
          - e.g. "2 tcp://192.168.0.12:5100, 1 tcp://192.168.0.11:5100, 3 tcp://192.168.0.13:5100"

        Args:
            uri_list (str): [主机地址列表 (以空格、逗号或分号分割的地址列表字符串)]
            p_out_addr_list (POINTER(MdsApiAddrInfoT)): [用于输出解析后的地址信息的地址信息数组]

        Returns:
            [int]: [大于等于0, 解析得到的地址数量; 小于0, 解析失败]
        """
        return CMdsApiFuncLoader().c_mds_api_parse_addr_list_string(
            uri_list,
            p_out_addr_list if p_out_addr_list else None,
            GENERAL_CLI_MAX_REMOTE_CNT)

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_thread_subscribe_tick_type(self, tick_type: int) ->bool:
        """
        设置SubscribeByString接口默认使用的数据模式 (tick_type)

        Args:
            tick_type (int): [数据模式 @see eMdsSubscribedTickTypeT]
            - 当订阅模式为追加订阅时, 如果该参数小于0, 将忽略该参数, 维持上一次订阅时的设置
            - 如果该参数值为 INT_MIN, 则清空之前的设置 (重置为默认值)

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        CMdsApiFuncLoader().c_mds_api_set_thread_subscribe_tick_type(tick_type)
        return True

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_thread_subscribe_require_init_md(self,
            is_require_initial_mkt_data: bool) -> bool:
        """
        设置SubscribeByString接口默认使用的初始快照订阅标志 (is_require_initial_mkt_data)

        Args:
            is_require_initial_mkt_data (bool): [是否需要推送已订阅产品的初始的行情快照]
            - @see MdsMktDataRequestReqT.isRequireInitialMktData

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        CMdsApiFuncLoader().c_mds_api_set_thread_subscribe_require_init_md(
            is_require_initial_mkt_data)
        return True

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_thread_subscribe_begin_time(self,
            begin_time: int) -> bool:
        """
        设置SubscribeByString接口默认使用的初始快照订阅标志 (is_require_initial_mkt_data)

        Args:
            begin_time (int): [行情数据的起始时间]
            - -1: 从头开始获取
            -  0: 从最新位置开始获取实时行情
            - >0: 从指定的起始时间开始获取 (HHMMSS / HHMMSSsss)
            - 当订阅模式为 Append/Delete/BatchDelete 时将忽略该参数
            - @see MdsMktDataRequestReqT.beginTime

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        CMdsApiFuncLoader().c_mds_api_set_thread_subscribe_begin_time(
            begin_time)
        return True

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_customized_ip(self, ip_str: str) -> bool:
        """
        设置客户端自定义的本地IP地址

        Args:
            ip_str (str): [点分十进制的IP地址字符串]

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        return CMdsApiFuncLoader().c_mds_api_set_customized_ip(ip_str)

    @spk_decorator_exception(log_error=log_error, error_no='')
    def get_customized_ip(self) -> str:
        """
        获取客户端自定义的本地IP

        Returns:
            [str]: [客户端自定义的本地IP]
        """
        return CMdsApiFuncLoader().c_mds_api_get_customized_ip().decode()

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_customized_mac(self, mac_str: str) -> bool:
        """
        设置客户端自定义的本地MAC地址

        Args:
            mac_str (str): [MAC地址字符串 (MAC地址格式 45:38:56:89:78:5A)]

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        return CMdsApiFuncLoader().c_mds_api_set_customized_mac(mac_str)

    @spk_decorator_exception(log_error=log_error, error_no='')
    def get_customized_mac(self) -> str:
        """
        获取客户端自定义的本地MAC

        Returns:
            [str]: [客户端自定义的本地MAC]
        """
        return CMdsApiFuncLoader().c_mds_api_get_customized_mac().decode()

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_customized_driver_id(self, driver_id: str) -> bool:
        """
        设置客户端自定义的本地设备序列号字符串

        Args:
            driver_id (str): [设备序列号字符串]

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        return CMdsApiFuncLoader().c_mds_api_set_customized_driver_id(driver_id)

    @spk_decorator_exception(log_error=log_error, error_no='')
    def get_customized_driver_id(self) -> str:
        """
        获取客户端自定义的本地设备序列号

        Returns:
            [str]: [客户端自定义的本地设备序列号]
        """
        return CMdsApiFuncLoader().c_mds_api_get_customized_driver_id().decode()

    @spk_decorator_exception(log_error=log_error, error_no=-errno.EINVAL)
    def get_last_error(self) -> int:
        """
        返回当前线程最近一次API调用失败的错误号

        Returns:
            [int]: [错误号]
        """
        return CMdsApiFuncLoader().c_mds_api_get_last_error()

    @spk_decorator_exception(log_error=log_error, error_no=False)
    def set_last_error(self, err_code: int) -> bool:
        """
        设置当前线程的API错误号

        Args:
            err_code (int): [错误号]

        Returns:
            [bool]: [True: 设置成功; False: 设置失败]
        """
        CMdsApiFuncLoader().c_mds_api_set_last_error(err_code)
        return True

    @spk_decorator_exception(log_error=log_error, error_no='')
    def get_error_msg(self, err_code: int) -> str:
        """
        返回错误号对应的错误信息

        Args:
            err_code (int): [错误号]

        Returns:
            [str]: [错误码对应的错误信息]
        """
        return CMdsApiFuncLoader().c_mds_api_get_error_msg(err_code).decode()

    @spk_decorator_exception(log_error=log_error, error_no='')
    def has_stock_stock(self, stock_static_info: MdsStockStaticInfoT,
            status: int) -> bool:
        """
        返回现货产品是否具有指定状态
        - 根据证券状态'securityStatus'字段判断 @see MdsStockStaticInfoT

        Args:
            stock_static_info (MdsStockStaticInfoT): [现货产品信息]
            status (int): [指定的状态 @see eOesSecurityStatusT]

        Returns:
            [bool]: [True: 具有指定的状态; False: 没有指定的状态]
        """
        return CMdsApiFuncLoader().c_mds_api_has_stock_status(
            byref(stock_static_info) if stock_static_info else None,
            status)
    # -------------------------


    # ===================================================================
    # Python API自定义接口函数
    # ===================================================================

    def get_default_channel(self) -> Optional[MdsAsyncApiChannelT]:
        """
        返回默认的TCP行情订阅通道

        Returns:
            [MdsAsyncApiChannelT]: [默认的TCP行情订阅通道]
        """
        if self._default_channel:
            return self._default_channel.contents

        if self._channels:
            for tuple_value in self._channels.values():
                return tuple_value[0]
        else:
            return None
    # -------------------------


    # ===================================================================
    # Python API自定义私有函数 (内部使用, 不对外开放)
    # ===================================================================

    def __add_channel_base_impl(self,
            is_add_from_file: bool = True,
            channel_tag: str = "",
            user_info: Any = "",
            mds_client_spi: Optional[MdsClientSpi] = None,
            copy_args: bool = True,

            remote_cfg: MdsApiRemoteCfgT = None,

            config_file: str = "",
            config_section: str = MDSAPI_CFG_DEFAULT_SECTION,
            addr_key: str = MDSAPI_CFG_DEFAULT_KEY_TCP_ADDR) -> MdsAsyncApiChannelT:
        """
        添加通道的基础实现

        Args:
            is_add_from_file (bool): [是否为 "从配置文件中加载并添加通道配置信息"]
            channel_tag (str): [通道配置信息的自定义标签 (可以为空)]
            user_info (Any): [用户回调参数].
            mds_client_spi (MdsClientSpi): [行情订阅通道消息的处理函数类]
            - Defaults to None. 此时默认使用self.mds_spi
            copy_args (bool): [是否复制服务端返回的行情数据]
            - Defaults to True
            - 可手动设置成False, 会提升吞吐和降低时延，但是行情数据需要立即保存起来, 否则后期使用会因异步队列数据覆盖而无法访问的风险

            remote_cfg (MdsApiRemoteCfgT): [待添加的通道配置信息 (不可为空)]
            - 仅适用于is_add_from_file=False有效

            config_file (MdsApiRemoteCfgT): [待添加的通道配置信息 (不可为空)]
            - 仅适用于is_add_from_file=True有效
            config_section (MdsApiRemoteCfgT): [待添加的通道配置信息 (不可为空)]
            - 仅适用于is_add_from_file=True有效
            addr_key (MdsApiRemoteCfgT): [待添加的通道配置信息 (不可为空)]
            - 仅适用于is_add_from_file=True有效

        Returns:
            [MdsAsyncApiChannelT]: [通道信息，请勿对其进行任何修改赋值操作]
        """
        if self._mds_api_started:
            raise Exception("需在调用start前添加行情订阅通道信息! "
                "mds_api_started[{}]".format(self._mds_api_started))

        if not channel_tag or channel_tag.strip() == '' :
            channel_tag = self.__get_auto_allocated_channel_tag()

        if len(channel_tag) >= GENERAL_CLI_MAX_NAME_LEN:
            # @note 需注意分配的通道标签长度不能超过32位, 否则截取后32位 (正常不会进入该分支)
            channel_tag = \
                channel_tag[len(channel_tag) - GENERAL_CLI_MAX_NAME_LEN + 1:]

        if channel_tag in self._channels.keys():
            raise Exception("通道标签已存在, 重复添加了行情订阅通道? "
                "channel_tag[{}], channels[{}]".format(
                channel_tag, self._channels.keys()))

        if mds_client_spi is None:
            if self.mds_spi is None:
                raise Exception("尚未给异步API注册有效的回调类实例!")
            else:
                mds_client_spi = self.mds_spi

        if not isinstance(mds_client_spi, MdsClientSpi):
            raise Exception("非法的回调类类型! spi_type[{}]".format(
                type(mds_client_spi)))

        msg_dispatcher: MdsMsgDispatcher = \
            MdsMsgDispatcher(mds_client_spi, copy_args)
        self._mds_msg_dispatchers.append(msg_dispatcher)

        if is_add_from_file:
            assert remote_cfg is None

            if not config_file:
                config_file = self._config_file

            p_channel: _Pointer = \
                CMdsApiFuncLoader().c_mds_async_api_add_channel_from_file(
                    self._mds_api_context, channel_tag, config_file,
                    config_section, addr_key,
                    msg_dispatcher.handle_mkt_data_msg(user_info),
                    VOID_NULLPTR,
                    msg_dispatcher.on_connect(user_info), VOID_NULLPTR,
                    msg_dispatcher.on_disconnect(user_info), VOID_NULLPTR)

        else:
            assert config_file == "" and config_section == "" and addr_key == ""

            if not remote_cfg:
                raise Exception("待添加的通道配置信息, 不可为空! "
                    "remote_cfg[{}]".format(remote_cfg))

            p_channel: _Pointer = \
                CMdsApiFuncLoader().c_mds_async_api_add_channel(
                    self._mds_api_context, channel_tag,
                    byref(remote_cfg) if remote_cfg else None, None,
                    msg_dispatcher.handle_mkt_data_msg(user_info), VOID_NULLPTR,
                    msg_dispatcher.on_connect(user_info), VOID_NULLPTR,
                    msg_dispatcher.on_disconnect(user_info), VOID_NULLPTR)

        if not p_channel:
            log_error("行情订阅通道添加失败! channel_tag[{}]".format(channel_tag))
            raise Exception("行情订阅通道添加失败!")
        else:
            # 设置连接失败时的回调函数
            CMdsApiFuncLoader().c_mds_async_api_set_on_connect_failed(
                p_channel,
                msg_dispatcher.on_connect_failed(user_info),
                VOID_NULLPTR)

        if not self._default_channel:
            # 如果尚无默认的行情订阅通道, 则使用首次添加的channel作为默认的行情订阅通道
            self._default_channel = p_channel

        # 将通道与消息分发器一对一绑定
        self._channels[channel_tag] = (p_channel.contents, msg_dispatcher)

        return p_channel.contents

    def __get_mds_msg_dispatcher_by_channel(self,
            channel: MdsAsyncApiChannelT = None) -> MdsMsgDispatcher:
        """
        获取通道对应的MDS消息分发器 (内部使用, 暂不对外开放)

        Args:
            channel (MdsAsyncApiChannelT): [查询通道]

        Returns:
            [MdsMsgDispatcher]: [消息分发器]
        """
        if channel is None:
            channel = self.get_default_channel()

        channel_tag = channel.pChannelCfg.contents.channelTag.decode()
        channel_dispatcher: tuple = self._channels.get(channel_tag, None)
        if channel_dispatcher is None:
            raise Exception("Invalid params! channel_tag[{}], "
                    "channels[{}]".format(channel_tag, self._channels))

        # 0号元素: MdsAsyncApiChannelT
        # 1号元素: MdsMsgDispatcher
        assert len(channel_dispatcher) == 2
        mds_msg_dispatcher: MdsMsgDispatcher = channel_dispatcher[1]
        if mds_msg_dispatcher is None:
            raise Exception("Invalid params! channel[{}]".format(
                channel))
        else:
            assert mds_msg_dispatcher.get_spi() is not None

        return mds_msg_dispatcher

    def __get_auto_allocated_channel_tag(self) -> str:
        """
        获取自动分配的通道标签 (内部使用, 暂不对外开放)
        - 外部添加通道时, 未指定标签, API内部会自动分配

        Returns:
            [str]: [自动分配的通道标签]
        """
        self.current_channel_no += 1

        channel_tag = f"__default_channel@0x{self.current_channel_no:0x}"

        if len(channel_tag) >= GENERAL_CLI_MAX_NAME_LEN:
            # @note 需注意分配的通道标签长度不能超过32位, 否则截取后32位 (正常不会进入该分支)
            channel_tag = \
                channel_tag[len(channel_tag) - GENERAL_CLI_MAX_NAME_LEN + 1:]

        return channel_tag
    # -------------------------
