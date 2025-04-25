# -*- coding: utf-8 -*-
"""
行情系统通讯报文定义
"""

from ctypes import (
    c_char, c_uint8, c_int8, c_uint16, c_uint32, c_int32, Structure, Union
)

from .mds_base_model import (
    MDS_MAX_SECURITY_CNT_PER_SUBSCRIBE,
    MDS_MAX_USERNAME_LEN,
    MDS_MAX_PASSWORD_LEN,
    MDS_MAX_TEST_REQ_ID_LEN,
    MDS_MAX_SENDING_TIME_LEN,
    MdsMktDataSnapshotT,
    MdsL2TradeT, MdsL2OrderT, MdsTickChannelHeartbeatT,
    MdsTradingSessionStatusMsgT, MdsSecurityStatusMsgT,
    STimespec32T, UnionForUserInfo
)

from .mds_qry_packets import (
    MdsQryMktDataSnapshotReqT, MdsQrySecurityStatusReqT,
    MdsQryTrdSessionStatusReqT, MdsQryStockStaticInfoListReqT,
    MdsQryOptionStaticInfoListReqT, MdsQrySnapshotListReqT,
    MdsQryStockStaticInfoListRspT, MdsQryOptionStaticInfoListRspT,
    MdsQrySnapshotListRspT, MdsQryApplUpgradeInfoRspT
)


# ===================================================================
# 协议版本号定义
# ===================================================================

# 当前采用的协议版本号
MDS_APPL_VER_ID                                 = "0.17.6.12"

# 当前采用的协议版本号数值
# - 版本号数值的格式为 10 位整型数值, 形如: 1AABBCCDDX, 其中:
#   - AA 为主版本号
#   - BB 为副版本号
#   - CC 为发布号
#   - DD 为构建号
#   - X  0, 表示不带时间戳的正常版本; 1, 表示带时间戳的延迟测量版本
#
MDS_APPL_VER_VALUE                              = 1001706121

# 兼容的最低协议版本号
MDS_MIN_APPL_VER_ID                             = "0.15.5"

# 应用名称
MDS_APPL_NAME                                   = "MDS"
# -------------------------


# ===================================================================
# 消息代码及报文中的枚举类型定义
# ===================================================================

# 通信消息的消息类型定义

class eMdsMsgTypeT:
    #
    # 会话类消息
    #
    # 心跳消息 (1/0x01)
    MDS_MSGTYPE_HEARTBEAT                       = 1
    # 测试请求消息 (2/0x02)
    MDS_MSGTYPE_TEST_REQUEST                    = 2
    # 注销消息 (4/0x04)
    MDS_MSGTYPE_LOGOUT                          = 4
    # 证券行情订阅消息 (5/0x05)
    MDS_MSGTYPE_MARKET_DATA_REQUEST             = 5
    # 压缩的数据包 (6/0x06, 内部使用)
    MDS_MSGTYPE_COMPRESSED_PACKETS              = 6
    # 最大的会话消息类型
    _MDS_MSGTYPE_SESSION_MAX                    = 7

    #
    # Level1 行情消息
    #
    # Level1 市场行情快照 (10/0x0A)
    MDS_MSGTYPE_MARKET_DATA_SNAPSHOT_FULL_REFRESH \
                                                = 10
    # Level1/Level2 指数行情快照 (11/0x0B)
    MDS_MSGTYPE_INDEX_SNAPSHOT_FULL_REFRESH     = 11
    # Level1/Level2 期权行情快照 (12/0x0C)
    MDS_MSGTYPE_OPTION_SNAPSHOT_FULL_REFRESH    = 12

    # 市场状态消息 (13/0x0D, 仅适用于上交所)
    MDS_MSGTYPE_TRADING_SESSION_STATUS          = 13
    # 证券状态消息 (14/0x0E, 仅适用于深交所)
    MDS_MSGTYPE_SECURITY_STATUS                 = 14
    # 最大的Level-1行情消息类型
    _MDS_MSGTYPE_L1_MAX                         = 15

    #
    # Level2 行情消息
    #
    # Level2 市场行情快照 (20/0x14)
    MDS_MSGTYPE_L2_MARKET_DATA_SNAPSHOT         = 20
    # Level2 委托队列快照 (买一/卖一前五十笔) (21/0x15)
    MDS_MSGTYPE_L2_BEST_ORDERS_SNAPSHOT         = 21

    # Level2 逐笔成交行情 (22/0x16)
    MDS_MSGTYPE_L2_TRADE                        = 22
    # Level2 深交所逐笔委托行情 (23/0x17, 仅适用于深交所)
    MDS_MSGTYPE_L2_ORDER                        = 23
    # Level2 上交所逐笔委托行情 (28/0x1C, 仅适用于上交所)
    MDS_MSGTYPE_L2_SSE_ORDER                    = 28
    # Level2 逐笔频道心跳消息 (29/0x1D)
    MDS_MSGTYPE_L2_TICK_CHANNEL_HEARTBEAT       = 29

    # Level2 市场总览消息 (26/0x1A, 仅适用于上交所)
    MDS_MSGTYPE_L2_MARKET_OVERVIEW              = 26

    # Level2 快照行情的增量更新消息 (24/0x18, 仅适用于上交所, @deprecated 已废弃)
    MDS_MSGTYPE_L2_MARKET_DATA_INCREMENTAL      = 24
    # Level2 委托队列快照的增量更新消息 (25/0x19, 仅适用于上交所, @deprecated 已废弃)
    MDS_MSGTYPE_L2_BEST_ORDERS_INCREMENTAL      = 25
    # Level2 虚拟集合竞价消息 (27/0x1B, 仅适用于上交所, @deprecated 已废弃)
    MDS_MSGTYPE_L2_VIRTUAL_AUCTION_PRICE        = 27
    # 最大的Level-2行情消息类型
    _MDS_MSGTYPE_L2_MAX                         = 28

    #
    # 指令类消息
    #
    # 修改客户端登录密码 (60/0x3C)
    MDS_MSGTYPE_CMD_CHANGE_PASSWORD             = 60
    # 最大的指令消息类型
    _MDS_MSGTYPE_CMD_MAX                        = 61

    #
    # 查询类消息
    #
    # 查询证券行情 (80/0x50)
    MDS_MSGTYPE_QRY_MARKET_DATA_SNAPSHOT        = 80
    # 查询(深圳)证券状态 (81/0x51)
    MDS_MSGTYPE_QRY_SECURITY_STATUS             = 81
    # 查询(上证)市场状态 (82/0x52)
    MDS_MSGTYPE_QRY_TRADING_SESSION_STATUS      = 82

    # 批量查询行情快照列表 (86/0x56)
    MDS_MSGTYPE_QRY_SNAPSHOT_LIST               = 86
    # 查询期权静态信息 (87/0x57)
    MDS_MSGTYPE_QRY_OPTION_STATIC_INFO          = 87
    # 查询证券(股票/债券/基金)静态信息 (88/0x58)  (0x55的更新版本, @since 0.15.11)
    MDS_MSGTYPE_QRY_STOCK_STATIC_INFO           = 88
    # 批量查询证券(股票/债券/基金)静态信息列表 (89/0x59)
    MDS_MSGTYPE_QRY_STOCK_STATIC_INFO_LIST      = 89
    # 批量查询期权静态信息列表 (90/0x5A)
    MDS_MSGTYPE_QRY_OPTION_STATIC_INFO_LIST     = 90

    # 逐笔数据重传请求 (96/0x60)
    MDS_MSGTYPE_TICK_RESEND_REQUEST             = 96
    # 最大的查询消息类型
    _MDS_MSGTYPE_QRY_MAX                        = 97



# 订阅模式 (SubMode) 定义
# -  0: (Set)          重新订阅, 设置为订阅列表中的股票 (之前的订阅参数将被清空)
# -  1: (Append)       追加订阅, 增加订阅列表中的股票
# -  2: (Delete)       删除订阅, 删除订阅列表中的股票
#
# 新增的批量订阅模式定义 (@since v0.15.9.1)
# - 10: (BatchBegin)   批量订阅-开始订阅, 开始一轮新的批量订阅 (之前的订阅参数将被清空,
#                      行情推送也将暂停直到批量订阅结束)
# - 11: (BatchAppend)  批量订阅-追加订阅, 增加订阅列表中的股票
# - 12: (BatchDelete)  批量订阅-删除订阅, 删除订阅列表中的股票
# - 13: (BatchEnd)     批量订阅-结束订阅, 结束本轮的批量订阅, 提交和启用本轮的订阅参数
#
# @note 当订阅模式为 Append/Delete/BatchDelete 时将忽略 isRequireInitialMktData 和
#       beginTime 这两个订阅参数

class eMdsSubscribeModeT:
    # 重新订阅, 设置为订阅列表中的股票 (之前的订阅参数将被清空)
    MDS_SUB_MODE_SET                            = 0
    # 追加订阅, 增加订阅列表中的股票
    MDS_SUB_MODE_APPEND                         = 1
    # 删除订阅, 删除订阅列表中的股票
    MDS_SUB_MODE_DELETE                         = 2

    _MAX_MDS_SUB_MODE_NONBATCH                  = 3

    #  批量订阅-开始订阅, 开始一轮新的批量订阅
    #  (之前的订阅参数将被清空, 行情推送也将暂停直到批量订阅结束)
    MDS_SUB_MODE_BATCH_BEGIN                    = 10
    # 批量订阅-追加订阅, 增加订阅列表中的股票
    MDS_SUB_MODE_BATCH_APPEND                   = 11
    # 批量订阅-删除订阅, 删除订阅列表中的股票
    MDS_SUB_MODE_BATCH_DELETE                   = 12
    # 批量订阅-结束订阅, 结束本轮的批量订阅, 提交和启用本轮的订阅参数
    MDS_SUB_MODE_BATCH_END                      = 13

    _MAX_MDS_SUB_MODE                           = 14


# 市场-产品类型订阅标志 (SubFlag) 定义
# -  0: (Default) 根据订阅列表订阅产品行情
# -  1: (All) 订阅该市场和证券类型下的所有产品行情 (为兼容之前的版本, 也可以赋值为 -1)
# -  2: (Disable) 禁用该市场下的所有产品行情

class eMdsMktSubscribeFlagT:
    # 根据订阅列表订阅产品行情
    MDS_MKT_SUB_FLAG_DEFAULT                    = 0
    # 订阅该市场和证券类型下的所有产品行情
    MDS_MKT_SUB_FLAG_ALL                        = 1
    # 禁用该市场下的所有产品行情
    MDS_MKT_SUB_FLAG_DISABLE                    = 2

    _MAX_MDS_MKT_SUB_FLAG                       = 3


# 数据模式 (TickType) 定义 (仅对快照行情生效, 用于标识订阅最新的行情快照还是所有时点的行情快照)
# 取值说明:
# -  0: (LatestSimplified) 只订阅最新的行情快照数据, 并忽略和跳过已经过时的数据
#       - 该模式推送的数据量最小, 服务器端会做去重处理, 不会再推送重复的和已经过时的快照数据
#       - 优点: 该模式在时延和带宽方面都更加优秀, 该模式优先关注快照行情的时效性, 并避免推送
#         没有实质变化的重复快照
#       - 缺点: 当没有行情变化时 (例如没有交易或盘中休市等), 就不会推送任何快照行情了, 这一
#         点可能会带来困扰, 不好确定是发生丢包了还是没有行情导致的
#       - 注意: 过时和重复的快照都会被过滤掉
# -  1: (LatestTimely) 只订阅最新的行情快照数据, 并立即发送最新数据
#       - 只要有行情更新事件, 便立即推送该产品的最新行情, 但行情数据本身可能是重复的, 即只有
#         行情时间有变化, 行情数据本身没有变化
#       - 优点: 可以获取到时间点更完整的快照行情, 不会因为行情数据没有变化而跳过 (如果是因为
#         接收慢等原因导致快照已经过时了, 该快照还是会被忽略掉)
#       - 缺点: 会收到仅更新时间有变化, 但行情数据本身并没有更新的重复数据, 带宽和数据量上会
#         有一定的浪费
#       - 注意: 重复的快照不会被过滤掉, 但过时的快照还是会被过滤掉
# -  2: (AllIncrements) 订阅所有时点的行情快照数据
#       - 该模式会推送所有时点的行情数据
#       - 如果需要获取全量的行情明细, 可以使用该模式
#
# 补充说明:
# - 当以 tickType=0 的模式订阅行情时, 服务器端会对重复的快照行情做去重处理, 不会再推送重复
#   的和已经过时的快照数据。
# - 如果需要获取到"所有时点"的快照, 可以使用 tickType=1 或 tickType=2 模式订阅行情。
# - 快照行情 "过时" 表示: 不是当前最新的快照即为"过时", 即存在时间点比该快照更新的快照 (同一只股票)。
# - @note  上交所行情存在更新时间相同但数据不同的Level-2快照。

class eMdsSubscribedTickTypeT:
    # 只订阅最新的行情快照数据, 并忽略和跳过已经过时的数据
    # (推送的数据量最小, 服务器端会做去重处理, 不会再推送重复的和已经过时的快照数据)
    MDS_TICK_TYPE_LATEST_SIMPLIFIED             = 0

    # 只订阅最新的行情快照数据, 并立即发送最新数据
    # (可以获取到时间点更完整的快照行情, 只要行情时间有变化, 即使数据重复也会对下游推送)
    MDS_TICK_TYPE_LATEST_TIMELY                 = 1

    # 订阅所有时点的行情快照数据
    MDS_TICK_TYPE_ALL_INCREMENTS                = 2

    _MAX_MDS_TICK_TYPE                          = 3



# 逐笔数据的过期时间定义 (仅对逐笔数据生效)
# @deprecated 已废弃, 将忽略逐笔数据过期时间参数, 不再生效
# class eMdsSubscribedTickExpireTypeT


# 逐笔数据的数据重建标识定义 (标识是否订阅重建到的或重复的逐笔数据, 仅对逐笔数据生效)
class eMdsSubscribedTickRebuildFlagT:
    # 不订阅重建到的逐笔数据或重复的逐笔数据 (仅实时行情)
    MDS_TICK_REBUILD_FLAG_EXCLUDE_REBUILDED     = 0
    # 订阅重建到的逐笔数据和重复的逐笔数据 (实时行情+重建数据+重复的逐笔数据)
    MDS_TICK_REBUILD_FLAG_INCLUDE_REBUILDED     = 1
    # 只订阅重建到的逐笔数据 (仅重建数据 @note 需要通过压缩行情端口进行订阅, 非压缩行情和组播行情不支持该选项)
    MDS_TICK_REBUILD_FLAG_ONLY_REBUILDED        = 2

    _MAX_MDS_TICK_REBUILD_FLAG                  = 3


# 可订阅的数据种类 (DataType) 定义
# - 0:      默认数据种类 (所有)
# - 0x0001: L1快照/指数/期权
# - 0x0002: L2快照
# - 0x0004: L2委托队列
# - 0x0008: L2逐笔成交
# - 0x0010: L2深交所逐笔委托 (仅适用于深交所)
# - 0x0020: L2上交所逐笔委托 (仅适用于上交所)
# - 0x0040: L2市场总览 (仅适用于上交所)
# - 0x0080: L2逐笔频道心跳消息
# - 0x0100: 市场状态 (仅适用于上交所)
# - 0x0200: 证券实时状态 (仅适用于深交所)
# - 0x0400: 指数行情 (与0x0001的区别在于, 0x0400可以单独订阅指数行情)
# - 0x0800: 期权行情 (与0x0001的区别在于, 0x0800可以单独订阅期权行情)
# - 0xFFFF: 所有数据种类

class eMdsSubscribeDataTypeT:
    # 默认数据种类 (所有种类)
    MDS_SUB_DATA_TYPE_DEFAULT                   = 0

    # L1快照/指数/期权 (L1快照行情 + 指数行情 + 期权行情)
    MDS_SUB_DATA_TYPE_L1_SNAPSHOT               = 0x0001

    # L2快照
    MDS_SUB_DATA_TYPE_L2_SNAPSHOT               = 0x0002

    # L2委托队列
    MDS_SUB_DATA_TYPE_L2_BEST_ORDERS            = 0x0004

    # 逐笔成交
    MDS_SUB_DATA_TYPE_L2_TRADE                  = 0x0008

    # 深交所逐笔委托 (*仅适用于深交所, 0x10/16)
    MDS_SUB_DATA_TYPE_L2_ORDER                  = 0x0010

    # 上交所逐笔委托 (*仅适用于上交所, 0x20/32)
    MDS_SUB_DATA_TYPE_L2_SSE_ORDER              = 0x0020

    # L2市场总览 (*仅适用于上交所, 0x40/64)
    MDS_SUB_DATA_TYPE_L2_MARKET_OVERVIEW        = 0x0040

    # 逐笔频道心跳消息 (0x80/128)
    MDS_SUB_DATA_TYPE_L2_TICK_CHANNEL_HEARTBEAT = 0x0080

    # 市场状态 (*仅适用于上交所, 0x100/256)
    MDS_SUB_DATA_TYPE_TRADING_SESSION_STATUS    = 0x0100

    # 证券实时状态 (*仅适用于深交所, 0x200/512)
    MDS_SUB_DATA_TYPE_SECURITY_STATUS           = 0x0200

    # 指数行情 (与L1_SNAPSHOT的区别在于, INDEX_SNAPSHOT可以单独订阅指数行情)
    MDS_SUB_DATA_TYPE_INDEX_SNAPSHOT            = 0x0400

    # 期权行情 (与L1_SNAPSHOT的区别在于, OPTION_SNAPSHOT可以单独订阅期权行情)
    MDS_SUB_DATA_TYPE_OPTION_SNAPSHOT           = 0x0800

    # 空数据种类 (可用于不订阅任何数据的场景)
    MDS_SUB_DATA_TYPE_NONE                      = 0x8000

    # 所有数据种类
    MDS_SUB_DATA_TYPE_ALL                       = 0xFFFF

    _MAX_MDS_SUB_DATA_TYPE                      = 0x7FFFFFFF


# 可订阅的内部数据频道定义 (供内部使用, 尚未对外开放)

class eMdsTickChannelNoT:
    # 默认频道 (所有频道)
    MDS_CHANNEL_NO_DEFAULT                      = 0

    # 频道1
    MDS_CHANNEL_NO_ONE                          = 0x01
    # 频道2
    MDS_CHANNEL_NO_TWO                          = 0x02
    # 频道3
    MDS_CHANNEL_NO_THREE                        = 0x04
    # 频道4
    MDS_CHANNEL_NO_FOUR                         = 0x08

    # 所有频道
    MDS_CHANNEL_NO_ALL                          = 0x0F
    # 空数据频道 (可用于不订阅任何频道的情况)
    MDS_CHANNEL_NO_NONE                         = 0x80


# 逐笔数据重传的重传状态定义

class eMdsTickResendStatusT:
    # 未定义
    MDS_TICK_RESEND_STATUS_UNDEFINE             = 0
    # 完成
    MDS_TICK_RESEND_STATUS_COMPLETED            = 1
    # 部分完成 (有部分请求的数据没有返回)
    MDS_TICK_RESEND_STATUS_PARTIALLY            = 2
    # 拒绝 (无权限或请求数据不合法)
    MDS_TICK_RESEND_STATUS_NO_PERMISSION        = 3
    # 数据不可用
    MDS_TICK_RESEND_STATUS_NO_DATA              = 4

    _MAX_MDS_TICK_RESEND_STATUS                 = 5
# -------------------------


# ===================================================================
#  会话消息报文定义
# ===================================================================

class MdsMktDataRequestEntryT(Structure):
    """
    行情订阅请求的订阅产品条目
    """
    _fields_ = [
        ("exchId", c_uint8),                    # 交易所代码 @see eMdsExchangeIdT
        ("mdProductType", c_uint8),             # 证券类型 @see eMdsMdProductTypeT
        ("__filler", c_uint8 * 2),              # 按64位对齐的填充域
        ("instrId", c_int32)                    # 证券代码 (转换为整数类型的证券代码)
    ]


class MdsMktDataRequestReqT(Structure):
    """
    行情订阅请求报文

    - 对于可同时订阅产品数量有如下限制:
    - 每个订阅请求中最多能同时指定 4000 只产品, 可以通过追加订阅的方式订阅更多数量的产品
    - 对于沪/深两市的现货产品没有总订阅数量的限制, 可以订阅任意数量的产品
    - 对于沪/深两市的期权产品, 限制对每个市场最多允许同时订阅 2000 只期权产品

    @see MdsMktDataRequestEntryT
    """
    _fields_ = [
        # 订阅模式
        # -  0: (Set)          重新订阅, 设置为订阅列表中的股票 (之前的订阅参数将被清空)
        # -  1: (Append)       追加订阅, 增加订阅列表中的股票
        # -  2: (Delete)       删除订阅, 删除订阅列表中的股票
        #
        # 新增的批量订阅模式定义 (@since v0.15.9.1)
        # - 10: (BatchBegin)   批量订阅-开始订阅, 开始一轮新的批量订阅 (之前的订阅参数将被清空,
        #                      行情推送也将暂停直到批量订阅结束)
        # - 11: (BatchAppend)  批量订阅-追加订阅, 增加订阅列表中的股票
        # - 12: (BatchDelete)  批量订阅-删除订阅, 删除订阅列表中的股票
        # - 13: (BatchEnd)     批量订阅-结束订阅, 结束本轮的批量订阅, 提交和启用本轮的订阅参数
        #
        # @see eMdsSubscribeModeT
        ("subMode", c_uint8),

        # 数据模式, 订阅最新的行情快照还是所有时点的数据
        # -  0: (LatestSimplified) 只订阅最新的行情快照数据, 并忽略和跳过已经过时的数据
        #       (推送的数据量最小, 服务器端会做去重处理, 不会再推送重复的和已经过时的快照数据)
        # -  1: (LatestTimely) 只订阅最新的行情快照数据, 并立即发送最新数据
        #       (可以获取到时间点更完整的快照行情, 只要行情时间有变化, 即使数据重复也会对下游推送)
        # -  2: (AllIncrements) 订阅所有时点的行情快照数据
        #
        # @see eMdsSubscribedTickTypeT
        ("tickType", c_uint8),

        # 上证股票(股票/债券/基金)产品的订阅标志
        # -  0: (Default) 根据订阅列表订阅产品行情
        # -  1: (All) 订阅该市场和证券类型下的所有产品行情 (为兼容之前的版本, 也可以赋值为 -1)
        # -  2: (Disable) 禁用该市场下的所有股票/债券/基金行情
        #
        # @see eMdsMktSubscribeFlagT
        ("sseStockFlag", c_int8),

        # 上证指数产品的订阅标志
        # -  0: (Default) 根据订阅列表订阅产品行情
        # -  1: (All) 订阅该市场和证券类型下的所有产品行情
        # -  2: (Disable) 禁用该市场下的所有指数行情
        #
        # @see eMdsMktSubscribeFlagT
        ("sseIndexFlag", c_int8),

        # 上证期权产品的订阅标志
        # -  0: (Default) 根据订阅列表订阅产品行情
        # -  1: (All) 订阅该市场和证券类型下的所有产品行情
        # -  2: (Disable) 禁用该市场下的所有期权行情
        #
        # @see eMdsMktSubscribeFlagT
        ("sseOptionFlag", c_int8),

        # 深圳股票(股票/债券/基金)产品的订阅标志深圳股票(股票/债券/基金)产品的订阅标志
        # -  0: (Default) 根据订阅列表订阅产品行情
        # -  1: (All) 订阅该市场和证券类型下的所有产品行情
        # -  2: (Disable) 禁用该市场下的所有股票/债券/基金行情
        #
        # @see eMdsMktSubscribeFlagT
        ("szseStockFlag", c_int8),

        # 深圳指数产品的订阅标志
        # -  0: (Default) 根据订阅列表订阅产品行情
        # -  1: (All) 订阅该市场和证券类型下的所有产品行情
        # -  2: (Disable) 禁用该市场下的所有指数行情
        #
        # @see eMdsMktSubscribeFlagT
        ("szseIndexFlag", c_int8),

        # 深圳期权产品的订阅标志
        # -  0: (Default) 根据订阅列表订阅产品行情
        # -  1: (All) 订阅该市场和证券类型下的所有产品行情
        # -  2: (Disable) 禁用该市场下的所有期权行情
        #
        # @see eMdsMktSubscribeFlagT
        ("szseOptionFlag", c_int8),

        # 在推送实时行情数据之前, 是否需要推送已订阅产品的初始的行情快照
        # -  0: 不需要推送初始的行情快照
        # -  1: 需要推送初始的行情快照, 即确保客户端可以至少收到一幅已订阅产品的快照行情 (如果有的话)
        #
        # @note 从 0.15.9.1开始, 允许在会话过程中任意时间指定isRequireInitialMktData
        #       标志来订阅初始快照。不过频繁订阅初始行情快照, 会对当前客户端的行情获取速度产
        #       生不利影响。应谨慎使用, 避免频繁订阅
        #
        # @note 当订阅模式为 Append / Delete / BatchDelete 时将忽略
        #       isRequireInitialMktData、beginTime 这两个订阅参数
        ("isRequireInitialMktData", c_uint8),

        # 待订阅的内部频道号 (供内部使用, 尚未对外开放)
        ("_channelNos", c_uint8),

        # 逐笔数据的过期时间类型
        # -  0: 不过期
        # -  1: 立即过期 (1秒, 若落后于快照1秒则视为过期)
        # -  2: 及时过期 (3秒)
        # -  3: 超时过期 (30秒)
        #
        # @deprecated  已废弃, 将忽略该参数, 不再生效
        ("tickExpireType", c_uint8),

        # 逐笔数据的数据重建标识 (标识是否订阅重建到的逐笔数据)
        # -  0: 不订阅重建到的逐笔数据或重复的逐笔数据
        # -  1: 订阅重建到的逐笔数据和重复的逐笔数据 (实时行情+重建数据+重复的逐笔数据)
        # -  2: 只订阅重建到的逐笔数据 (仅重建数据 @note 需要通过压缩行情端口进行订阅, 非压缩行情和组播行情不支持该选项)
        #
        # @see         eMdsSubscribedTickRebuildFlagT
        # @deprecated  已过时, 建议固定设置为0, 并通过逐笔数据重传接口来重传缺失的逐笔数据
        ("tickRebuildFlag", c_uint8),

        # 订阅的数据种类
        # - 0:      默认数据种类 (所有)
        # - 0x0001: L1快照/指数/期权
        # - 0x0002: L2快照
        # - 0x0004: L2委托队列
        # - 0x0008: L2逐笔成交
        # - 0x0010: L2深交所逐笔委托 (仅适用于深交所)
        # - 0x0020: L2上交所逐笔委托 (仅适用于上交所)
        # - 0x0040: L2市场总览 (仅适用于上交所)
        # - 0x0080: L2逐笔频道心跳消息
        # - 0x0100: 市场状态 (仅适用于上交所)
        # - 0x0200: 证券实时状态 (仅适用于深交所)
        # - 0x0400: 指数行情 (与0x0001的区别在于, 0x0400可以单独订阅指数行情)
        # - 0x0800: 期权行情 (与0x0001的区别在于, 0x0800可以单独订阅期权行情)
        # - 0xFFFF: 所有数据
        #
        # @see eMdsSubscribeDataTypeT
        ("dataTypes", c_int32),

        # 请求订阅的行情数据的起始时间 (格式为: HHMMSS 或 HHMMSSsss)
        # - -1: 从头开始获取
        # -  0: 从最新位置开始获取实时行情
        # - >0: 从指定的起始时间开始获取 (HHMMSS / HHMMSSsss)
        # - 对于应答数据, 若为 0 则表示当前没有比起始时间更加新的行情数据
        #
        # @note    从 0.15.9.1 开始, 允许在会话过程中任意时间指定 beginTime 订阅参数。不过
        #          频繁指定起始时间, 会对当前客户端的行情获取速度产生不利影响。应谨慎使用, 避免
        #          频繁订阅
        # @note    当订阅模式为 Append/Delete/BatchDelete 时将忽略
        #          isRequireInitialMktData、beginTime 这两个订阅参数
        ("beginTime", c_int32),

        # 本次订阅的产品数量 (订阅列表中的产品数量)
        # - 该字段表示后续报文为subSecurityCnt个订阅产品条目结构体, 通过这样的方式可以实现同
        #   时订阅多只产品的行情快照
        # - 每个订阅请求中最多能同时指定 4000 只产品, 可以通过追加订阅的方式订阅更多数量的产品
        # - 订阅产品总数量的限制如下:
        #   - 对于沪/深两市的现货产品没有订阅数量限制, 可以订阅任意数量的产品
        #   - 对于沪/深两市的期权产品, 限制对每个市场最多允许同时订阅 2000 只期权产品
        #
        # @see MdsMktDataRequestEntryT
        # @see MDS_MAX_SECURITY_CNT_PER_SUBSCRIBE
        ("subSecurityCnt", c_int32)

        # 后续报文为 subSecurityCnt 个订阅产品条目结构体
        #
        # @see MdsMktDataRequestEntryT
        # @see MDS_MAX_SECURITY_CNT_PER_SUBSCRIBE
    ]


class MdsMktDataRequestReqBufT(Structure):
    """
    完整的行情订阅请求报文缓存
    """
    _fields_ = [
        # 行情订阅请求
        ("mktDataRequestReq", MdsMktDataRequestReqT),
        # 订阅产品列表
        ("entries", MdsMktDataRequestEntryT * MDS_MAX_SECURITY_CNT_PER_SUBSCRIBE)
    ]


# MDS行情订阅信息配置
MdsApiSubscribeInfoT = MdsMktDataRequestReqBufT


class MdsMktDataRequestRspT(Structure):
    """
    行情订阅请求的应答报文
    """
    _fields_ = [
        # 订阅模式
        # -  0: (Set)          重新订阅, 设置为订阅列表中的股票 (之前的订阅参数将被清空)
        # -  1: (Append)       追加订阅, 增加订阅列表中的股票
        # -  2: (Delete)       删除订阅, 删除订阅列表中的股票
        #
        # 新增的批量订阅模式定义 (@since v0.15.9.1)
        # - 10: (BatchBegin)   批量订阅-开始订阅, 开始一轮新的批量订阅 (之前的订阅参数将被清空,
        #                      行情推送也将暂停直到批量订阅结束)
        # - 11: (BatchAppend)  批量订阅-追加订阅, 增加订阅列表中的股票
        # - 12: (BatchDelete)  批量订阅-删除订阅, 删除订阅列表中的股票
        # - 13: (BatchEnd)     批量订阅-结束订阅, 结束本轮的批量订阅, 提交和启用本轮的订阅参数
        #
        # @see     eMdsSubscribeModeT
        ("subMode", c_uint8),

        # 数据模式, 订阅最新的行情快照还是所有时点的数据
        # -  0: (LatestSimplified) 只订阅最新的行情快照数据, 并忽略和跳过已经过时的数据
        #       (推送的数据量最小, 服务器端会做去重处理, 不会再推送重复的和已经过时的快照数据)
        # -  1: (LatestTimely) 只订阅最新的行情快照数据, 并立即发送最新数据
        #       (可以获取到时间点更完整的快照行情, 只要行情时间有变化, 即使数据重复也会对下游推送)
        # -  2: (AllIncrements) 订阅所有时点的行情快照数据
        #
        # @see eMdsSubscribedTickTypeT
        ("tickType", c_uint8),

        # 在推送实时行情数据之前, 是否需要推送已订阅产品的初始的行情快照
        # -  0: 不需要推送初始的行情快照
        # -  1: 需要推送初始的行情快照, 即确保客户端可以至少收到一幅已订阅产品的快照行情 (如果有的话)
        #
        # @note 从 0.15.9.1开始, 允许在会话过程中任意时间指定isRequireInitialMktData
        #       标志来订阅初始快照。不过频繁订阅初始行情快照, 会对当前客户端的行情获取速度产
        #       生不利影响。应谨慎使用, 避免频繁订阅
        #
        # @note 当订阅模式为 Append / Delete / BatchDelete 时将忽略
        #       isRequireInitialMktData、beginTime 这两个订阅参数
        ("isRequireInitialMktData", c_uint8),

        # 订阅的内部频道号 (供内部使用, 尚未对外开放)
        ("_channelNos", c_uint8),

        # 逐笔数据的过期时间类型
        # -  0: 不过期
        # -  1: 立即过期 (1秒, 若落后于快照1秒则视为过期)
        # -  2: 及时过期 (3秒)
        # -  3: 超时过期 (30秒)
        #
        # @deprecated  已废弃, 将忽略该参数, 不再生效
        ("tickExpireType", c_uint8),

        # 逐笔数据的数据重建标识 (标识是否订阅重建到的逐笔数据)
        # -  0: 不订阅重建到的逐笔数据或重复的逐笔数据
        # -  1: 订阅重建到的逐笔数据和重复的逐笔数据 (实时行情+重建数据+重复的逐笔数据)
        # -  2: 只订阅重建到的逐笔数据 (仅重建数据 @note 需要通过压缩行情端口进行订阅, 非压缩行情和组播行情不支持该选项)
        #
        # @see         eMdsSubscribedTickRebuildFlagT
        # @deprecated  已过时, 建议固定设置为0, 并通过逐笔数据重传接口来重传缺失的逐笔数据
        ("tickRebuildFlag", c_uint8),

        # 按64位对齐的填充域
        ("__filler", c_uint8 * 2),

        # 订阅的数据种类
        # - 0:      默认数据种类 (所有)
        # - 0x0001: L1快照/指数/期权
        # - 0x0002: L2快照
        # - 0x0004: L2委托队列
        # - 0x0008: L2逐笔成交
        # - 0x0010: L2深交所逐笔委托 (仅适用于深交所)
        # - 0x0020: L2上交所逐笔委托 (仅适用于上交所)
        # - 0x0040: L2市场总览 (仅适用于上交所)
        # - 0x0080: L2逐笔频道心跳消息
        # - 0x0100: 市场状态 (仅适用于上交所)
        # - 0x0200: 证券实时状态 (仅适用于深交所)
        # - 0x0400: 指数行情 (与0x0001的区别在于, 0x0400可以单独订阅指数行情)
        # - 0x0800: 期权行情 (与0x0001的区别在于, 0x0800可以单独订阅期权行情)
        # - 0xFFFF: 所有数据
        #
        # @see eMdsSubscribeDataTypeT
        ("dataTypes", c_int32),

        # 请求订阅的行情数据的起始时间 (格式为: HHMMSS 或 HHMMSSsss)
        # - -1: 从头开始获取
        # -  0: 从最新位置开始获取实时行情
        # - >0: 从指定的起始时间开始获取 (HHMMSS / HHMMSSsss)
        # - 对于应答数据, 若为 0 则表示当前没有比起始时间更加新的行情数据
        #
        # @note    从 0.15.9.1 开始, 允许在会话过程中任意时间指定 beginTime 订阅参数。不过
        #          频繁指定起始时间, 会对当前客户端的行情获取速度产生不利影响。所以应谨慎使用,
        #          避免频繁订阅
        # @note    当订阅模式为 Append/Delete/BatchDelete 时将忽略
        #          isRequireInitialMktData、beginTime 这两个订阅参数
        ("beginTime", c_int32),

        # 上证股票(股票/债券/基金)产品的订阅结果 (实际已订阅的产品数量)
        # - -1: 订阅了所有产品;
        # -  0: 未订阅或已禁用;
        # - > 0: 已订阅的产品数量(当前已生效的合计值)
        ("sseStockSubscribed", c_int32),

        # 上证指数产品的订阅结果 (实际已订阅的产品数量)
        # - -1: 订阅了所有产品;
        # -  0: 未订阅或已禁用;
        # - > 0: 已订阅的产品数量(当前已生效的合计值)
        ("sseIndexSubscribed", c_int32),

        # 上证期权产品的订阅结果 (实际已订阅的产品数量)
        # - -1: 订阅了所有产品;
        # -  0: 未订阅或已禁用;
        # - > 0: 已订阅的产品数量(当前已生效的合计值)
        ("sseOptionSubscribed", c_int32),

        # 深圳股票(股票/债券/基金)产品的订阅结果 (实际已订阅的产品数量)
        # - -1: 订阅了所有产品;
        # -  0: 未订阅或已禁用;
        # - > 0: 已订阅的产品数量(当前已生效的合计值)
        ("szseStockSubscribed", c_int32),

        # 深圳指数产品的订阅结果 (实际已订阅的产品数量)
        # - -1: 订阅了所有产品;
        # -  0: 未订阅或已禁用;
        # - > 0: 已订阅的产品数量(当前已生效的合计值)
        ("szseIndexSubscribed", c_int32),

        # 深圳期权产品的订阅结果 (实际已订阅的产品数量)
        # - -1: 订阅了所有产品;
        # -  0: 未订阅或已禁用;
        # - > 0: 已订阅的产品数量(当前已生效的合计值)
        ("szseOptionSubscribed", c_int32)
    ]


class MdsTestRequestReqT(Structure):
    """
    测试请求报文
    """
    _fields_ = [
        # 测试请求标识符
        ("testReqId", c_char * MDS_MAX_TEST_REQ_ID_LEN),
        # 发送时间 (timeval结构或形如'YYYYMMDD-HH:mm:SS.sss'的字符串)
        ("sendTime", c_char * MDS_MAX_SENDING_TIME_LEN),
        # 按64位对齐的填充域
        ("__filler", c_char * 2)
    ]


class MdsTestRequestRspT(Structure):
    """
    测试请求的应答报文
    """
    _fields_ = [
        # 测试请求标识符
        ("testReqId", c_char * MDS_MAX_TEST_REQ_ID_LEN),
        # 测试请求的原始发送时间 (timeval结构或形如'YYYYMMDD-HH:mm:SS.sss'的字符串)
        ("origSendTime", c_char * MDS_MAX_SENDING_TIME_LEN),
        # 按64位对齐的填充域
        ("__filler1", c_char * 2),

        # 测试请求应答的发送时间 (timeval结构或形如'YYYYMMDD-HH:mm:SS.sss'的字符串)
        ("respTime", c_char * MDS_MAX_SENDING_TIME_LEN),
        # 按64位对齐的填充域
        ("__filler2", c_char * 2),

        # 消息实际接收时间 (开始解码等处理之前的时间)
        ("recvTime", STimespec32T),
        # 消息采集处理完成时间
        ("collectedTime", STimespec32T),
        # 消息推送时间 (写入推送缓存以后, 实际网络发送之前)
        ("pushingTime", STimespec32T)
    ]


class MdsTickResendRequestReqT(Structure):
    """
    逐笔数据重传请求消息
    """
    _fields_ = [
        ("exchId", c_uint8),                    # 交易所代码(沪/深) @see eMdsExchangeIdT
        ("isSseOldTickOrder", c_uint8),         # 对应的逐笔数据类型是否是上交所老版竞价逐笔委托 (非债券逐笔委托、非逐笔合并数据)
                                                # - 上交所逐笔合并数据上线前该字段需要区分逐笔数据类型, 逐笔委托固定设置为 1, 逐笔成交固定设置为 0
                                                # - 上交所逐笔合并数据上线后该字段将被废弃, 固定设置为 0 即可
        ("channelNo", c_uint16),                # 频道代码 (取值范围[1..9999])

        ("beginApplSeqNum", c_uint32),          # 待重传的逐笔数据起始序号
        ("endApplSeqNum", c_uint32),            # 待重传的逐笔数据结束序号
        ("__filler", c_uint32 * 3),             # 按64位对齐的填充域

        # 用户私有信息 (由客户端自定义填充, 并在回报数据中原样返回)
        ("userInfo", UnionForUserInfo),
        ("__reserve", c_char * 16),             # 预留的备用字段
    ]


class MdsTickResendRequestRspT(Structure):
    """
    逐笔数据重传请求的应答消息

    - 逐笔数据重传请求的应答数据依次由如下消息组成:
      - 1 条逐笔数据重传请求的应答消息, msgType 为: MDS_MSGTYPE_TICK_RESEND_REQUEST
      - [0~1000] 条重传的逐笔数据, msgType 为: MDS_MSGTYPE_L2_TRADE / MDS_MSGTYPE_L2_ORDER / MDS_MSGTYPE_L2_SSE_ORDER
    """
    _fields_ = [
        ("exchId", c_uint8),                    # 交易所代码(沪/深) @see eMdsExchangeIdT
        ("isSseOldTickOrder", c_uint8),         # 对应的逐笔数据类型是否是上交所老版竞价逐笔委托 (非债券逐笔委托、非逐笔合并数据)
        ("channelNo", c_uint16),                # 频道代码 (取值范围[1..9999])

        ("beginApplSeqNum", c_uint32),          # 待重传的逐笔数据起始序号
        ("endApplSeqNum", c_uint32),            # 待重传的逐笔数据结束序号
        ("resendMsgCount", c_int32),            # 重传消息数量
        ("resendStatus", c_int32),              # 重传状态 (1:完成, 2:部分完成, 3:拒绝, 4:数据不可用) @see eMdsTickResendStatusT
        ("__filler", c_uint32),                 # 按64位对齐的填充域

        # 用户私有信息 (由客户端自定义填充, 并在回报数据中原样返回)
        ("userInfo", UnionForUserInfo),
        ("__reserve", c_char * 16),             # 预留的备用字段
    ]


class MdsChangePasswordReqT(Structure):
    """
    修改登录密码请求报文
    """
    _fields_ = [
        # 加密方法
        ("encryptMethod", c_int32),
        # 按64位对齐的填充域
        ("__filler", c_int32),

        # 登录用户名
        ("username", c_char * MDS_MAX_USERNAME_LEN),
        # 用户私有信息 (由客户端自定义填充, 并在回报数据中原样返回)
        ("userInfo", UnionForUserInfo),

        # 之前的登录密码
        ("oldPassword", c_char * MDS_MAX_PASSWORD_LEN),
        # 新的登录密码
        ("newPassword", c_char * MDS_MAX_PASSWORD_LEN)
    ]


class MdsChangePasswordRspT(Structure):
    """
    修改登录密码应答报文
    """
    _fields_ = [
        # 加密方法
        ("encryptMethod", c_int32),
        # 按64位对齐的填充域
        ("__filler", c_int32),

        # 登录用户名
        ("username", c_char * MDS_MAX_USERNAME_LEN),
        # 用户私有信息 (由客户端自定义填充, 并在回报数据中原样返回)
        ("userInfo", UnionForUserInfo),

        # 按64位对齐的填充域
        ("__filler2", c_int32),
        # 发生日期 (格式为 YYYYMMDD, 形如 20160830)
        ("transDate", c_int32),
        # 发生时间 (格式为 HHMMSSsss, 形如 141205000)
        ("transTime", c_int32),
        # 拒绝原因
        ("rejReason", c_int32),
    ]


class MdsMktReqMsgBodyT(Union):
    """
    汇总的请求消息的消息体定义
    """
    _fields_ = [
        # 完整的行情订阅请求报文缓存
        ("wholeMktDataReqBuf", MdsMktDataRequestReqBufT),
        # 行情订阅请求
        ("mktDataRequestReq", MdsMktDataRequestReqT),
        # 测试请求
        ("testRequestReq", MdsTestRequestReqT),

        # 证券行情查询请求
        ("qryMktDataSnapshotReq", MdsQryMktDataSnapshotReqT),
        # (深圳)证券实时状态查询请求
        ("qrySecurityStatusReq", MdsQrySecurityStatusReqT),
        # (上证)市场状态查询请求
        ("qryTrdSessionStatusReq", MdsQryTrdSessionStatusReqT),

        # 证券静态信息查询请求 (@deprecated 已废弃)
        # 期权静态信息批量查询请求 (@deprecated 已废弃)

        # 证券静态信息列表批量查询请求
        ("qryStockStaticInfoListReq", MdsQryStockStaticInfoListReqT),
        # 期权静态信息批量查询请求
        ("qryOptionStaticInfoListReq", MdsQryOptionStaticInfoListReqT),
        # 行情快照列表批量查询请求
        ("qrySnapshotListReq", MdsQrySnapshotListReqT),

        # 逐笔数据重传请求
        ("tickResendRequestReq", MdsTickResendRequestReqT),

        # 修改登录密码的应答数据
        ("changePasswordReq", MdsChangePasswordReqT)
    ]


class MdsMktRspMsgBodyT(Union):
    """
    汇总的应答消息的消息体定义
    """
    _fields_ = [
        # 行情订阅请求的应答消息
        ("mktDataRequestRsp", MdsMktDataRequestRspT),
        # 测试请求的应答消息
        ("testRequestRsp", MdsTestRequestRspT),

        # 证券行情全幅消息
        ("mktDataSnapshot", MdsMktDataSnapshotT),
        # Level2 逐笔成交行情
        ("trade", MdsL2TradeT),
        # Level2 逐笔委托行情
        ("order", MdsL2OrderT),
        # Level2 逐笔频道心跳消息
        ("tickChannelHeartbeat", MdsTickChannelHeartbeatT),

        # 市场状态消息
        ("trdSessionStatus", MdsTradingSessionStatusMsgT),
        # 证券实时状态消息
        ("securityStatus", MdsSecurityStatusMsgT),

        # 证券静态信息列表批量查询的应答数据
        ("qryStockStaticInfoListRsp", MdsQryStockStaticInfoListRspT),
        # 期权静态信息查询的应答数据
        ("qryOptionStaticInfoListRsp", MdsQryOptionStaticInfoListRspT),
        # 行情快照列表批量查询的应答数据
        ("qrySnapshotListRsp", MdsQrySnapshotListRspT),
        # 周边应用升级信息查询的应答数据
        ("qryApplUpgradeInfoRsp", MdsQryApplUpgradeInfoRspT),

        # 逐笔数据重传请求的应答消息
        ("tickResendRsp", MdsTickResendRequestRspT),

        # 证券静态信息查询的应答数据 (@deprecated 已废弃)
        # 期权静态信息查询的应答数据 (@deprecated 已废弃)

        # 修改登录密码的应答数据
        ("changePasswordRsp", MdsChangePasswordRspT)
    ]
# -------------------------
