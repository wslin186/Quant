# -*- coding: utf-8 -*-
"""utility相关结构体"""

import os
import sys
import platform
import inspect
import traceback

from typing import Any
from ctypes import (
    c_char, c_uint8, c_int8, c_uint16, c_int16, c_uint32, c_int32,
    c_uint64, c_int64, c_char_p, c_void_p, POINTER, CDLL, CFUNCTYPE,
    Structure, Union, byref, memmove, sizeof
)

# 导入ctypes函数指针类型 (兼容不同python版本)
try:
    from ctypes import _FuncPointer
except ImportError:
    from ctypes import _CFuncPtr as _FuncPointer

# 函数类型指针
CFuncPointer = _FuncPointer

# void类型空指针
VOID_NULLPTR: c_void_p = c_void_p()

# char型空指针
CHAR_NULLPTR: c_char_p = c_char_p()
# -------------------------


# ===================================================================
# 基础库常用函数定义
# ===================================================================

def memcpy(src: Any) -> Any:
    """
    内存拷贝一个参数

    Returns:  Any: [拷贝后的对象]
    """
    dst = type(src)()
    memmove(byref(dst), byref(src), sizeof(src))
    return dst
# -------------------------


# ===================================================================
# 基础库类装饰器函数定义
# ===================================================================

try:
    from dataclasses import dataclass
except ImportError:

    def dataclass(cls):
        """
        自定义的类装饰器
        """
        cls.__dataclass_fields__ = list(cls.__annotations__.keys())

        def init(self, *args, **kwargs):
            keys = cls.__dataclass_fields__

            for key in keys:
                if hasattr(cls, key):
                    setattr(self, key, getattr(cls, key))
            key_index = 0
            for value in args:
                setattr(self, keys[key_index], value)
                key_index += 1
            keys = set(keys[key_index:])

            for key, value in kwargs.items():
                assert key in keys
                setattr(self, key, value)

        def repr(self):
            data = ', '.join(
                [f"{k}={getattr(self, k)}" for k in self.__dataclass_fields__])
            return f"{cls.__name__}({data})"

        cls.__init__ = init
        cls.__repr__ = repr
        return cls

# 自定义的类装饰器
spk_dataclass = dataclass


def spk_decorator_exception(log_error, error_no: Any):
    """
    异常捕获装饰器
    Args:
        log_error (Logger): [发生异常时, 记录错误日志的句柄]
        error_no (Any): [发生异常时, 期望函数返回的取值]
    """
    def spk_decorator_exception_wrapper(func):
        def spk_decorator_exception_inner(*args, **kwargs):
            ret = 0

            # @note 消除警告
            # noinspection PyBroadException
            try:
                ret = func(*args, **kwargs)
            except Exception as err:
                ret = error_no

                log_error("调用函数 <{}> 发生异常, {}, errno[{}]\n{}".format(
                    func.__name__, err, ret, traceback.format_exc()))
            return ret

        return spk_decorator_exception_inner

    return spk_decorator_exception_wrapper
# -------------------------


# ===================================================================
# 基础库常用类定义
# ===================================================================

class SingletonType(type):
    """
    单例类的元类
    """

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class CCharP:
    """
    作为C函数参数的 <char *> 声明类型
      - 用于将Python中的字符串参数转换为C中的 <char *> 参数类型
    """

    def __init__(self, context) -> None:
        self.context = context

    @property
    def _as_parameter_(self):
        return self.context

    @classmethod
    def from_param(cls, obj):
        if isinstance(obj, str):
            obj = obj.encode()
        return c_char_p.from_param(obj)
# -------------------------


# ===================================================================
# 基础库常量定义
# ===================================================================

# IP字符串的最大长度
SPK_MAX_IP_LEN                              = 16
# URI最大长度
SPK_MAX_URI_LEN                             = 128
# 客户端名称最大长度
GENERAL_CLI_MAX_NAME_LEN                    = 32
# 可连接的最大远程服务器数量
GENERAL_CLI_MAX_REMOTE_CNT                  = 8
# 发送方/接收方代码字符串的最大长度
GENERAL_CLI_MAX_COMP_ID_LEN                 = 32
# BASE64编码后的密码最大长度
GENERAL_CLI_MAX_PWD_BASE64_LEN              = 128
# 会话信息中用于存储自定义数据的扩展空间大小
GENERAL_CLI_MAX_SESSION_EXTDATA_SIZE        = 128
# 连接通道组的最大连接数量
GENERAL_CLI_MAX_CHANNEL_GROUP_SIZE          = 256
# 可以同时连接的远程服务器的最大数量
SPK_ENDPOINT_MAX_REMOTE_CNT                 = GENERAL_CLI_MAX_CHANNEL_GROUP_SIZE

# 日志级别名称的长度
SLOG_MAX_LEVEL_NAME                         = 32

# 最大路径长度
SPK_MAX_PATH_LEN                            = 256
# -------------------------


# ===================================================================
# 基础库结构定义
# ===================================================================

class eSMsgFlagT:
    """
    消息标志, 用于在消息标志中标识消息的请求/应答类型与协议类型复用相同的字段, 通过高4位/低4位进行区分
    """
    SMSG_MSGFLAG_NONE           = 0x00          # 消息标志-无
    SMSG_MSGFLAG_REQ            = 0x00          # 消息标志-请求消息
    SMSG_MSGFLAG_RSP            = 0x50          # 消息标志-应答消息 TODO refactor => 0x10
    SMSG_MSGFLAG_NESTED         = 0x20          # 消息标志-嵌套的组合消息 (消息体由一到多条包含消息头的完整消息组成)
    SMSG_MSGFLAG_COMPRESSED     = 0x80          # 消息标志-消息体已压缩

    SMSG_MSGFLAG_MASK_RSPFLAG   = 0xF0          # 消息标志掩码-请求/应答标志的掩码
    SMSG_MSGFLAG_MASK_PROTOCOL  = 0x0F          # 消息标志掩码-协议类型的掩码


class eSLogLevelValueT:
    """
    日志级别结构体定义
    """
    SLOG_LEVEL_VALUE_TRACE      = 0             # 日志级别-跟踪信息 (TRACE)
    SLOG_LEVEL_VALUE_DEBUG      = 1             # 日志级别-调试信息 (DEBUG)
    SLOG_LEVEL_VALUE_INFO       = 2             # 日志级别-提示信息 (INFO)
    SLOG_LEVEL_VALUE_WARN       = 3             # 日志级别-警告信息 (WARN)
    SLOG_LEVEL_VALUE_ERROR      = 4             # 日志级别-错误信息 (ERROR)

    SLOG_LEVEL_VALUE_BZ_INFO    = 5             # 日志级别-业务提示 (BZINF, BZ_INFO)
    SLOG_LEVEL_VALUE_BZ_WARN    = 6             # 日志级别-业务警告 (BZWRN, BZ_WARN)
    SLOG_LEVEL_VALUE_BZ_ERROR   = 7             # 日志级别-业务错误 (BZERR, BZ_ERROR)
    SLOG_LEVEL_VALUE_FATAL      = 8             # 日志级别-致命错误 (FATAL)
    SLOG_LEVEL_VALUE_NONE       = 9             # 日志级别-屏蔽所有日志 (NONE)


class STimespec32T(Structure):
    """32位时间戳结构体"""
    _fields_ = (
        ("tv_sec", c_int32),
        ("tv_nsec", c_int32),
    )

    def __repr__(self):
        return str({"sec": self.tv_sec, "nsec": self.tv_nsec})


class SMsgHeadT(Structure):
    """
    通用消息头
    @see eSMsgFlagT
    """
    _fields_ = (
        ("msgFlag", c_uint8),                   # 消息标志 @see eSMsgFlagT
        ("msgId", c_uint8),                     # 消息代码
        ("status", c_uint8),                    # 状态码
        ("detailStatus", c_uint8),              # 明细状态代码 (@note 当消息为嵌套的组合消息时, 复用该字段记录消息体中的消息条数)
        ("msgSize", c_int32),                   # 消息大小
    )


class SEndpointContextT(Structure):
    """
    通信端点的运行时上下文环境
    该结构体下的字段均为API内部使用和管理, 客户端不应直接修改该结构体下的数据
    """
    _fields_ = (
        # 内部参考数据指针
        ("pInternalRefs", c_void_p),
        # 按64位对齐的填充域
        ("__filler", c_void_p),
        # 通知线程终止运行的标志变量
        ('terminateFlag', c_uint8),
        # 按64位对齐的填充域
        ("__filler2", c_uint8 * 7),
    )


class SEndpointChannelCfgT(Structure):
    """
    通信端点的通道配置信息 (详细定义请参考SEndpointChannelCfgT._fields_)
    """


class _UnionForCustomData(Union):
    """
    用户私有数据联合体
    """
    _fields_ = (
        ('buf', c_char * GENERAL_CLI_MAX_SESSION_EXTDATA_SIZE),
        ('i8', c_int8 * GENERAL_CLI_MAX_SESSION_EXTDATA_SIZE),
        ('u8', c_uint8 * GENERAL_CLI_MAX_SESSION_EXTDATA_SIZE),
        ('i16', c_int16 * int(GENERAL_CLI_MAX_SESSION_EXTDATA_SIZE / 2)),
        ('u16', c_uint16 * int(GENERAL_CLI_MAX_SESSION_EXTDATA_SIZE / 2)),
        ('i32', c_int32 * int(GENERAL_CLI_MAX_SESSION_EXTDATA_SIZE / 4)),
        ('u32', c_uint32 * int(GENERAL_CLI_MAX_SESSION_EXTDATA_SIZE / 4)),
        ('i64', c_int64 * int(GENERAL_CLI_MAX_SESSION_EXTDATA_SIZE / 8)),
        ('u64', c_uint64 * int(GENERAL_CLI_MAX_SESSION_EXTDATA_SIZE / 8)),
        ('ptr', c_void_p * int(GENERAL_CLI_MAX_SESSION_EXTDATA_SIZE / 8)),
    )

    def __repr__(self):
        return f"{self.__class__.__name__} at 0x{id(self):0x}"


class SEndpointChannelT(Structure):
    """
    MDS异步API的连接通道运行时信息
    """
    _hiden_attributes = {
        'pContext', 'pExtChannelCfg', '__filler'
    }

    _fields_ = (
        # 会话信息指针
        ('pSessionInfo', c_void_p),
        # 通信端点的运行时上下文环境指针
        ('pContext', POINTER(SEndpointContextT)),
        # 通道配置信息指针
        ('pChannelCfg', POINTER(SEndpointChannelCfgT)),
        # 扩展的通道配置数据 (由基础库负责分配空间, 由应用层或API负责解释和维护)
        ('pExtChannelCfg', c_void_p),
        # 标识通道是否已连接就绪
        ('isConnected', c_uint8),
        # 通信协议类型 (由异步端点启动时自动检测和赋值) @see eSSocketProtocolTypeT
        ('protocolType', c_uint8),
        # 是否是无连接的UDP类型通信协议
        ('isUdpChannel', c_uint8),
        # 按64位对齐的填充域
        ('__filler', c_uint8 * 5),
        # 最近/上一次会话实际接收到的入向消息序号 (由应用层或API负责维护)
        ('lastInMsgSeq', c_int64),
        # 最近/上一次会话实际已发送的出向消息序号 (由应用层或API负责维护)
        ('lastOutMsgSeq', c_int64),
    )


class SGeneralClientAddrInfoT(Structure):
    """
    Socket URI地址信息
    """
    _fields_ = (
        # 地址信息
        ("uri", c_char * SPK_MAX_URI_LEN),
        # 接收方代码
        ("targetCompId", c_char * GENERAL_CLI_MAX_COMP_ID_LEN),
        # 用户名
        ("username", c_char * GENERAL_CLI_MAX_NAME_LEN),
        # 密码
        ("password", c_char * GENERAL_CLI_MAX_PWD_BASE64_LEN),
        # 主机编号
        ("hostNum", c_uint8),
        # 按64位对齐的填充域
        ("__filler", c_uint8 * 7),
    )


class SSocketOptionConfigT(Structure):
    """
    套接口选项配置
    """
    _fields_ = (
        ("soRcvbuf", c_int32),                  # socket SO_RCVBUF size (KB)
        ("soSndbuf", c_int32),                  # socket SO_SNDBUF size (KB)
        ("tcpNodelay", c_int8),                 # socket TCP_NODELAY option, 0 or 1
        ("quickAck", c_int8),                   # socket TCP_QUICKACK option, 0 or 1
        ("mcastTtlNum", c_int8),                # mutilcast TTL number
        ("mcastLoopbackDisabled", c_int8),      # disable mutilcast loopback, 0 or 1
        ("soBacklog", c_uint16),                # BACKLOG size for listen
        ("connTimeoutMs", c_uint16),            # 连接操作(connect)的超时时间 (毫秒)
        ("keepIdle", c_int16),                  # socket TCP_KEEPIDLE option, 超时时间(秒)
        ("keepIntvl", c_int16),                 # socket TCP_KEEPINTVL option, 间隔时间(秒)
        ("keepalive", c_int8),                  # socket SO_KEEPALIVE option (0 or 1)
        ("keepCnt", c_int8),                    # socket TCP_KEEPCNT option, 尝试次数
        # disable SO_REUSEADDR option for bind (enabled by default)
        ("disableReuseAddr", c_int8),
        # enable SO_REUSEPORT option for listen (disabled by default)
        ("enableReusePort", c_int8),
        ("__filler", c_int8 * 4),               # 按64位对齐的填充域
        ("localSendingPort", c_int32),          # 本地绑定的端口地址 (适用于发送端)
        # 本地绑定的网络设备接口的IP地址 (适用于发送端)
        ("4", c_char * (SPK_MAX_IP_LEN + 4)),
        # 用于组播接收和发送的特定网络设备接口的IP地址
        ("4", c_char * (SPK_MAX_IP_LEN + 4)),
    )


class SGeneralClientRemoteCfgT(Structure):
    """
    远程主机配置信息
    """
    _fields_ = (
        ("addrCnt", c_int32),                   # 服务器地址的数量
        ("heartBtInt", c_int32),                # 心跳间隔,单位为秒
        ("clusterType", c_uint8),               # 服务器集群的集群类型 (0:默认, 1:复制集, 2:对等节点)
        ("clEnvId", c_int8),                    # 客户端环境号
        ("targetSetNum", c_uint8),              # 远程主机的集群号
        ("businessType", c_uint8),              # 期望对接的业务类型
        ("__filler", c_uint8 * 4),              # 按64位对齐的填充域
        ("senderCompId", c_char * GENERAL_CLI_MAX_COMP_ID_LEN),
                                                # 发送方代码
        ("targetCompId", c_char * GENERAL_CLI_MAX_COMP_ID_LEN),
                                                # 接收方代码
        ("username", c_char * GENERAL_CLI_MAX_NAME_LEN),
                                                # 用户名
        ("password", c_char * GENERAL_CLI_MAX_PWD_BASE64_LEN),
                                                # 密码
        ("addrList", SGeneralClientAddrInfoT * GENERAL_CLI_MAX_REMOTE_CNT),
                                                # 服务器地址列表
        ("socketOpt", SSocketOptionConfigT),    # 套接口选项配置
    )


"""
通信端点的通道配置信息详细定义
"""
SEndpointChannelCfgT._fields_ = (
    # 通道顺序号 (根据添加的次序自动设置)
    ('channelIndex', c_int32),
    # 通道类型
    ('channelType', c_int32),
    # 通道标签
    ('channelTag', c_char * GENERAL_CLI_MAX_NAME_LEN),
    # 远程主机配置信息
    ('remoteCfg', SGeneralClientRemoteCfgT),
    # 对接收到的应答或回报消息进行处理的回调函数
    # - 若回调函数返回小于0的数, 将尝试断开并重建连接
    # int32 (*fnOnMsg) (
    #       SGeneralClientChannelT *pSessionInfo, SMsgHeadT *pMsgHead,
    #       void *pMsgItem, void *pCallbackParams);
    ('fnOnMsg', CFUNCTYPE(c_int32, c_void_p, POINTER(SMsgHeadT), c_void_p, c_void_p)),
    # 传递给fnOnMsg回调函数的参数
    ('pOnMsgParams', c_void_p),
    # 连接或重新连接完成后的回调函数
    # - 需要通过该回调函数完成回报订阅操作
    # - 若函数指针为空, 则会使用通道配置中默认的回报订阅参数进行订阅
    # - 若函数指针不为空, 但未订阅回报, 90秒以后服务器端会强制断开连接
    # - 若回调函数返回小于0的数, 则通信端点将中止运行
    # int32 (*fnOnConnect) (struct _SEndpointChannel *pAsyncChannel, void *pCallbackParams);
    ('fnOnConnect', CFUNCTYPE(c_int32, POINTER(SEndpointChannelT), c_void_p)),
    # 传递给fnOnConnect回调函数的参数
    ('pOnConnectParams', c_void_p),
    # 连接断开后的回调函数
    # - 无需做特殊处理, 通信线程会自动尝试重建连接
    # - 若函数指针为空, 通信线程会自动尝试重建连接并继续执行
    # - 若回调函数返回小于0的数, 则通信端点将中止运行
    # int32 (*fnOnDisconnect) (
    #       struct _SEndpointChannel *pAsyncChannel, void *pCallbackParams);
    ('fnOnDisconnect', CFUNCTYPE(c_int32, POINTER(SEndpointChannelT), c_void_p)),
    # 传递给fnOnDisconnect回调函数的参数
    ('pOnDisconnectParams', c_void_p),
    # 可以由应用层自定义使用的, 用于存储自定义数据的扩展空间
    ('customData', _UnionForCustomData),
)


class UnionForUserInfo(Union):
    """用户自定义数据联合体"""
    _fields_ = [
        ('u64', c_uint64),
        ('i64', c_int64),
        ('u32', c_uint32 * 2),
        ('i32', c_int32 * 2),
        ('c8', c_char * 8),
    ]

    def __repr__(self):
        return f"{{{self.u32[0]}, {self.u32[1]}}}"


class SLogLevelT(Structure):
    """日志级别结构体定义"""
    _fields_ = [('level', c_int8), ('__filler', c_int8 * 7),
                ('name', c_char * SLOG_MAX_LEVEL_NAME)]


ERROR_LEVEL: SLogLevelT = SLogLevelT(
    level=eSLogLevelValueT.SLOG_LEVEL_VALUE_ERROR, name=b"ERROR")
INFO_LEVEL: SLogLevelT = SLogLevelT(
    level=eSLogLevelValueT.SLOG_LEVEL_VALUE_INFO, name=b"INFO")
DEBUG_LEVEL: SLogLevelT = SLogLevelT(
    level=eSLogLevelValueT.SLOG_LEVEL_VALUE_DEBUG, name=b"DEBUG")
TRACE_LEVEL: SLogLevelT = SLogLevelT(
    level=eSLogLevelValueT.SLOG_LEVEL_VALUE_DEBUG, name=b"TRACE")


class CApiFuncLoader:
    """
    capi动态库函数加载
    """

    def __init__(self) -> None:
        # 获取对应平台的API动态库文件路径
        c_api_dll_name: str = ""
        system, _, _, _, machine, _ = platform.uname()

        if system == "Windows":
            if machine == "AMD64":
                c_api_dll_name = "win64/oes_api.dll"
            else:
                c_api_dll_name = "win32/oes_api.dll"

        elif system == "Darwin":
            if machine == "arm64":
                c_api_dll_name = "macos_arm/dll/liboes_api.so"
            else:
                c_api_dll_name = "macos_x86/dll/liboes_api.so"

        elif system == "Linux":
            if machine == "x86_64":
                c_api_dll_name = "linux64/dll/liboes_api.so"

        if c_api_dll_name == "":
            raise Exception("Not supported platform")

        # 加载API动态库文件
        try:
            # /home/user/python_api/quote_api/model/../../libs/
            prefix: str = os.path.dirname(os.path.abspath(__file__)) \
                + os.path.sep + ".." + os.path.sep + ".." + os.path.sep \
                + "libs" + os.path.sep

            self.c_api_dll = CDLL(prefix + c_api_dll_name)

        except Exception as err1:
            # /home/user/python_api/sutil/../libs/
            prefix: str = os.path.dirname(os.path.abspath(__file__)) \
                + os.path.sep + ".." + os.path.sep + "libs" + os.path.sep

            try:
                self.c_api_dll = CDLL(prefix + c_api_dll_name)
            except Exception as err2: # noqa
                print(f">>> 错误提示: 没有找到 oes_api 库文件 '{c_api_dll_name}' \n"
                      f">>> 错误检查: 当前系统 oes_api 库文件 是否已拷贝至 => python_api-x.x.x.x-release/libs 目录下! \n"
                      f">>> 错误详情: {err1}")
                sys.exit(-1)


    # ===================================================================
    # 公共接口函数声明
    # ===================================================================

        # 日志登记处理实现声明
        self.c_log = self.c_api_dll._SLog_LogImpl
        self.c_log.restype = None
        self.c_log.argtypes = [
            CCharP, c_int32, c_int32, CCharP, c_int32,
            POINTER(SLogLevelT), CCharP
        ]
    # -------------------------


    # ===================================================================
    #  加载并封装capi中的日志函数方法
    # ===================================================================

    def _do_log(
            self,
            log_level: SLogLevelT,
            error_msg: str,
            stack_index: int) -> None:
        """
        打印日志

        Args:
            log_level (SLogLevelT): [日志级别]
            error_msg (str): [日志信息]
            stack_index (int): [堆栈调用深度]
        """
        stack_index += 1
        caller_frame = inspect.stack()[stack_index]
        filename = caller_frame.filename.split('/')[-1]

        self.c_log(filename, len(filename) + 1, caller_frame.lineno,
                   caller_frame.function, 0, log_level, error_msg)

    def error(self, error_msg: str, stack_index: int = 1) -> None:
        """
        输出error日志

        Args:
            error_msg (str): [日志信息]
            stack_index (int, optional): [堆栈调用深度]. Defaults to 1.
        """
        self._do_log(ERROR_LEVEL, error_msg, stack_index)

    def info(self, error_msg: str, stack_index: int = 1) -> None:
        """
        输出debug日志

        Args:
            error_msg (str): [日志信息]
            stack_index (int, optional): [堆栈调用深度]. Defaults to 1.
        """
        self._do_log(INFO_LEVEL, error_msg, stack_index)

    def debug(self, error_msg: str, stack_index: int = 1) -> None:
        """
        输出debug日志

        Args:
            error_msg (str): [日志信息]
            stack_index (int, optional): [堆栈调用深度]. Defaults to 1.
        """
        self._do_log(DEBUG_LEVEL, error_msg, stack_index)

    def trace(self, error_msg: str, stack_index: int = 1) -> None:
        """
        输出trace日志

        Args:
            error_msg (str): [日志信息]
            stack_index (int, optional): [堆栈调用深度]. Defaults to 1.
        """
        self._do_log(TRACE_LEVEL, error_msg, stack_index)
    # -------------------------
