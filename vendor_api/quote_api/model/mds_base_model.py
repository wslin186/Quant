# -*- coding: utf-8 -*-
"""
MDS系统的基础领域模型(数据结构)定义
"""

from ctypes import (
    c_char, c_uint8, c_int8, c_uint16, c_int16, c_uint32, c_int32,
    c_uint64, c_int64, Structure, Union
)

try:
    from .spk_util import (
        SPK_MAX_PATH_LEN, STimespec32T, UnionForUserInfo
    )
except ImportError:
    from sutil.spk_util import (
        SPK_MAX_PATH_LEN, STimespec32T, UnionForUserInfo
    )


# ===================================================================
# 常量定义 (宏定义)
# ===================================================================

# 每次的行情订阅请求中可以同时指定的最大订阅产品数量 (可以通过追加订阅的方式订阅更多的产品)
MDS_MAX_SECURITY_CNT_PER_SUBSCRIBE              = 4000
# 对于沪/深两市的期权产品, 限制对每个市场最多允许同时订阅 2000 只产品
MDS_MAX_OPTION_CNT_TOTAL_SUBSCRIBED             = 2000

# 用户名最大长度
MDS_MAX_USERNAME_LEN                            = 32
# 密码最大长度
MDS_MAX_PASSWORD_LEN                            = 40
# 客户端标签最大长度
MDS_CLIENT_TAG_MAX_LEN                          = 32
# 协议版本号的最大长度
MDS_VER_ID_MAX_LEN                              = 32
# 测试请求标识符的最大长度
MDS_MAX_TEST_REQ_ID_LEN                         = 32
# 发送方/接收方代码的最大长度
MDS_MAX_COMP_ID_LEN                             = 32

# 点分十进制的IPv4, 字符串的最大长度
MDS_MAX_IP_LEN                                  = 16
# MAC地址字符串的最大长度
MDS_MAX_MAC_LEN                                 = 20
# MAC地址字符串的最大长度(按64位对齐的长度)
MDS_MAX_MAC_ALGIN_LEN                           = 24
# 设备序列号字符串的最大长度
MDS_MAX_DRIVER_ID_LEN                           = 21
# 设备序列号字符串的最大长度(按64位对齐的长度)
MDS_MAX_DRIVER_ID_ALGIN_LEN                     = 24

# 证券代码长度(C6/C8)
MDS_MAX_INSTR_CODE_LEN                          = 9
# 实际的股票产品代码长度
MDS_REAL_STOCK_CODE_LEN                         = 6
# 实际的期权产品代码长度
MDS_REAL_OPTION_CODE_LEN                        = 8
# 允许带.SH/.SZ后缀的产品代码的最大长度
MDS_MAX_POSTFIXED_INSTR_CODE_LEN                = 12

# 证券名称最大长度
MDS_MAX_SECURITY_NAME_LEN                       = 40
# 证券长名称长度
MDS_MAX_SECURITY_LONG_NAME_LEN                  = 80
# 证券英文名称长度
MDS_MAX_SECURITY_ENGLISH_NAME_LEN               = 48
# 证券ISIN代码长度
MDS_MAX_SECURITY_ISIN_CODE_LEN                  = 16

# 期权合约交易代码长度
MDS_MAX_CONTRACT_EXCH_ID_LEN                    = 24
# 期权合约交易代码实际长度
MDS_REAL_CONTRACT_EXCH_ID_LEN                   = 19
# 期权合约简称长度
MDS_MAX_CONTRACT_SYMBOL_LEN                     = 56

# 发送时间字段(YYYYMMDD-HH:mm:SS.sss (*C21))的最大长度
MDS_MAX_SENDING_TIME_LEN                        = 22
# 发送时间字段(YYYYMMDD-HH:mm:SS.sss (*C21))的实际有效数据长度
MDS_REAL_SENDING_TIME_LEN                       = 21

# 交易日期字段(YYYYMMDD (*C8))的最大长度
MDS_MAX_TRADE_DATE_LEN                          = 9
# 交易日期字段(YYYYMMDD (*C8))的实际有效数据长度
MDS_REAL_TRADE_DATE_LEN                         = 8

# 最新更新时间字段(HHMMSSss (*C8))的最大长度
MDS_MAX_UPDATE_TIME_LEN                         = 9
# 最新更新时间字段(HHMMSSss (*C8))的实际有效数据长度
MDS_REAL_UPDATE_TIME_LEN                        = 8

# 全市场行情状态字段(*C8)的最大长度
MDS_MAX_TRADING_SESSION_ID_LEN                  = 9
# 全市场行情状态字段(*C8)的实际有效数据长度
MDS_REAL_TRADING_SESSION_ID_LEN                 = 8

# 产品实时阶段及标志(C8/C4)的最大长度
MDS_MAX_TRADING_PHASE_CODE_LEN                  = 9
# 产品实时阶段及标志(C8/C4)的实际有效数据长度
MDS_REAL_TRADING_PHASE_CODE_LEN                 = 8

# 证券状态字段(深交所证券实时状态消息 C8)的最大长度
MDS_MAX_FINANCIAL_STATUS_LEN                    = 9
# 证券状态字段(深交所证券实时状态消息 C8)的实际有效数据长度
MDS_REAL_FINANCIAL_STATUS_LEN                   = 8

# 证券业务开关的最大数量(深交所证券实时状态消息)
MDS_MAX_SECURITY_SWITCH_CNT                     = 40

# 统一的价格单位
MDS_UNIFIED_PRICE_UNIT                          = 10000
# 统一的金额单位
MDS_UNIFIED_MONEY_UNIT                          = 10000

# 总成交金额的金额单位 (上交所的总成交金额精度原本为2位, 但在此统一整合为4位精度)
MDS_TOTAL_VALUE_TRADED_UNIT                     = MDS_UNIFIED_MONEY_UNIT
# 指数的价格单位
MDS_INDEX_PRICE_UNIT                            = MDS_UNIFIED_PRICE_UNIT
# 股票的价格单位 (上交所的股票价格精度原本为3位, 但在此统一整合为4位精度)
MDS_STOCK_PRICE_UNIT                            = MDS_UNIFIED_PRICE_UNIT
# 期权的价格单位
MDS_OPTION_PRICE_UNIT                           = MDS_UNIFIED_PRICE_UNIT

# 逐笔委托中委托价格的最大值 (如果逐笔委托中的委托价格超出该值, 则将赋值为该值)
MDS_MAX_ORDER_PRICE                             = 1999999999

# 股票代码的最大范围
MDS_MAX_STOCK_ID_SCOPE                          = 1000000
# 期权代码的最大范围
MDS_MAX_OPTION_ID_SCOPE                         = 100000000

# 逐笔数据频道代码的最大范围 (频道代码取值范围[1..9999])
MDS_MAX_TICK_CHANNEL_NO_SCOPE                   = 10000
# 逐笔数据重传请求每次可重传的最大数据数量
MDS_MAX_TICK_RESEND_ITEM_COUNT                  = 1000

# 周边应用废弃版本数目的最大个数
MDS_APPL_DISCARD_VERSION_MAX_COUNT              = 5
# 周边应用升级协议名称的最大长度
MDS_APPL_UPGRADE_PROTOCOL_MAX_LEN               = 32
# -------------------------


# ===================================================================
# Level2 相关的常量定义
# ===================================================================

# Level2披露的买一／卖一委托明细最大数量
MDS_MAX_L2_DISCLOSE_ORDERS_CNT                  = 50

# Level2增量更新的价位列表最大数量 @deprecated 已废弃, 上交所行情快照发送机制调整后, 不再推送增量更新消息
MDS_MAX_L2_PRICE_LEVEL_INCREMENTS               = 8

# Level2增量更新的委托明细最大数量 @deprecated 已废弃, 上交所行情快照发送机制调整后, 不再推送增量更新消息
MDS_MAX_L2_DISCLOSE_ORDERS_INCREMENTS           = 8
# -------------------------


# ===================================================================
# 常量定义 (宏定义)
# ===================================================================

# 交易所代码
class eMdsExchangeIdT:
    MDS_EXCH_UNDEFINE                   = 0     # 未定义的交易所代码
    MDS_EXCH_SSE                        = 1     # 交易所-上交所
    MDS_EXCH_SZSE                       = 2     # 交易所-深交所
    _MAX_MDS_EXCH                       = 3

    _MAX_MDS_EXCH_ALIGNED4              = 4     # 交易所代码最大值 (按4字节对齐的大小)
    _MAX_MDS_EXCH_ALIGNED8              = 8     # 交易所代码最大值 (按8字节对齐的大小)


# 消息来源
class eMdsMsgSourceT:
    MDS_MSGSRC_UNDEFINED                = 0     # 消息来源-未定义
    MDS_MSGSRC_EZEI_TCP                 = 1     # 消息来源-EzEI(TCP)
    MDS_MSGSRC_EZEI_UDP                 = 2     # 消息来源-EzEI(UDP)
    MDS_MSGSRC_SSE_MDGW_BINARY          = 10    # 消息来源-SSE-MDGW-BINARY
    MDS_MSGSRC_SSE_MDGW_STEP            = 11    # 消息来源-SSE-MDGW-STEP

    MDS_MSGSRC_VDE_LEVEL1               = 20    # 消息来源-SSE-VDE-LEVEL1-FAST
    MDS_MSGSRC_VDE_LEVEL1_BINARY        = 21    # 消息来源-SSE-VDE-LEVEL1-BINARY
    MDS_MSGSRC_VDE_LEVEL2               = 22    # 消息来源-SSE-VDE-LEVEL2
    MDS_MSGSRC_VDE_MERGED_TICK          = 23    # 消息来源-SSE-VDE-逐笔合并数据
    MDS_MSGSRC_VDE_MERGED_TICK_REBUILD  = 28    # 消息来源-SSE-VDE-逐笔合并数据-逐笔重建
    MDS_MSGSRC_VDE_LEVEL2_REBUILD       = 29    # 消息来源-SSE-VDE-LEVEL2-逐笔重建

    MDS_MSGSRC_SZSE_MDGW_BINARY         = 31    # 消息来源-SZSE-MDGW-BINARY
    MDS_MSGSRC_SZSE_MDGW_STEP           = 32    # 消息来源-SZSE-MDGW-STEP
    MDS_MSGSRC_SZSE_MDGW_MULTICAST      = 33    # 消息来源-SZSE-MDGW-组播
    MDS_MSGSRC_SZSE_MDGW_REBUILD        = 39    # 消息来源-SZSE-MDGW-逐笔重建

    MDS_MSGSRC_FILE_MKTDT               = 90    # 消息来源-文件(mktdt, 实盘下不会出现)
    MDS_MSGSRC_MDS_TCP                  = 91    # 消息来源-MDS(TCP, 仅内部测试使用, 实盘下不会出现)
    MDS_MSGSRC_MDS_UDP                  = 92    # 消息来源-MDS(UDP, 仅内部测试使用, 实盘下不会出现)
    MDS_MSGSRC_MDS_REBUILD              = 93    # 消息来源-MDS(TCP, 仅内部测试使用, 实盘下不会出现)
    _MAX_MDS_MSGSRC                     = 94

    # 消息来源-SZSE-MDGW-Binary @deprecated 已过时, 请使用 MDS_MSGSRC_SZSE_MDGW_BINARY
    # MDS_MSGSRC_MDGW_BINARY              = MDS_MSGSRC_SZSE_MDGW_BINARY
    # 消息来源-SZSE-MDGW-STEP @deprecated 已过时, 请使用 MDS_MSGSRC_SZSE_MDGW_STEP
    # MDS_MSGSRC_MDGW_STEP                = MDS_MSGSRC_SZSE_MDGW_STEP


# 行情产品类型 (和交易端的产品类型不同, 行情数据中的产品类型只是用于区分是现货行情还是衍生品行情)
class eMdsMdProductTypeT:
    MDS_MD_PRODUCT_TYPE_UNDEFINE        = 0     # 未定义的行情产品类型
    MDS_MD_PRODUCT_TYPE_STOCK           = 1     # 股票 (包含基金和债券)
    MDS_MD_PRODUCT_TYPE_INDEX           = 2     # 指数
    MDS_MD_PRODUCT_TYPE_OPTION          = 3     # 期权
    _MAX_MDS_MD_PRODUCT_TYPE            = 4

    _MAX_MDS_MD_PRODUCT_TYPE_ALIGNED4   = 4     # 行情产品类型最大值 (按4字节对齐的大小)
    _MAX_MDS_MD_PRODUCT_TYPE_ALIGNED8   = 8     # 行情产品类型最大值 (按8字节对齐的大小)

    # @deprecated 以下定义已过时, 为保持兼容而暂时保留
    # MDS_SECURITY_TYPE_STOCK             = MDS_MD_PRODUCT_TYPE_STOCK
    # MDS_SECURITY_TYPE_INDEX             = MDS_MD_PRODUCT_TYPE_INDEX
    # MDS_SECURITY_TYPE_OPTION            = MDS_MD_PRODUCT_TYPE_OPTION
    # _MAX_MDS_SECURITY_TYPE              = _MAX_MDS_MD_PRODUCT_TYPE


# 行情数据类别
class eMdsSubStreamTypeT:
    MDS_SUB_STREAM_TYPE_UNDEFINE        = 0     # 未定义的行情数据类别
    MDS_SUB_STREAM_TYPE_MARKET_STATUS   = 1     # 市场状态 (市场总览消息等状态消息)

    MDS_SUB_STREAM_TYPE_STOCK           = 10    # 股票
    MDS_SUB_STREAM_TYPE_BOND            = 20    # 债券
    MDS_SUB_STREAM_TYPE_BOND_NEGOTIATED = 21    # 债券 - 债券现券交易协商成交逐笔行情 (仅适用于深交所逐笔行情)
    MDS_SUB_STREAM_TYPE_BOND_CLICK      = 22    # 债券 - 债券现券交易点击成交逐笔行情 (仅适用于深交所逐笔行情)
    MDS_SUB_STREAM_TYPE_BOND_INQUIRY    = 23    # 债券 - 债券现券交易询价成交逐笔行情 (仅适用于深交所逐笔行情)
    MDS_SUB_STREAM_TYPE_BOND_IOI        = 24    # 债券 - 债券现券交易意向申报逐笔行情 (仅适用于深交所逐笔行情  IOI: Indication of Interest)
    MDS_SUB_STREAM_TYPE_BOND_BIDDING    = 25    # 债券 - 债券现券交易竞买成交逐笔行情 (仅适用于深交所逐笔行情)
    MDS_SUB_STREAM_TYPE_BOND_BLOCK_TRADE \
                                        = 26    # 债券 - 债券现券交易匹配成交大额逐笔行情 (仅适用于深交所逐笔行情)

    MDS_SUB_STREAM_TYPE_FUND            = 40    # 基金 (@note 上交所Level2行情尚无法区分基金数据, 将归类为股票)
    MDS_SUB_STREAM_TYPE_OPTION          = 50    # 期权

    MDS_SUB_STREAM_TYPE_INDEX           = 90    # 指数
    MDS_SUB_STREAM_TYPE_TRADE_STATS     = 91    # 指数 - 成交量统计指标 (结构与指数行情相同, 仅适用于深交所)
    MDS_SUB_STREAM_TYPE_CN_INDEX        = 92    # 指数 - 国证指数 (结构与指数快照相同, 仅适用于深交所)

    _MAX_MDS_SUB_STREAM_TYPE            = 93


# 快照行情数据对应的消息类型 (@deprecated 已废弃, 请改为直接使用消息类型定义(eMdsMsgTypeT))
# @deprecated  已废弃
#              - 判断消息类型, 请直接使用快照行情相关的消息类型定义 @see eMdsMsgTypeT
#              - 判断行情类别, 请改为使用行情数据类别(subStreamType)字段 @see eMdsSubStreamTypeT
# eMdsMdStreamTypeT


# 行情数据级别 (Level1 / Level2)
class eMdsMdLevelT:
    MDS_MD_LEVEL_0                      = 0     # 未设置
    MDS_MD_LEVEL_1                      = 1     # Level-1 行情
    MDS_MD_LEVEL_2                      = 2     # Level-2 行情
    _MAX_MDS_MD_LEVEL                   = 3


# Level2增量更新消息的价位运算 (1=Add, 2=Update, 3=Delete)
# @deprecated 已废弃, 上交所行情快照发送机制调整后, 不再推送增量更新消息
# eMdsL2PriceLevelOperatorT


# Level2逐笔成交的成交类别
# - 仅适用于深交所 ('4'=撤销, 'F'=成交)
# - 对于上交所, 将固定取值为 'F'(成交)
class eMdsL2TradeExecTypeT:
    MDS_L2_TRADE_EXECTYPE_CANCELED      = '4'   # L2执行类型 - 已撤销
    MDS_L2_TRADE_EXECTYPE_TRADE         = 'F'   # L2执行类型 - 已成交


# Level2逐笔成交的内外盘标志
# - 仅适用于上交所 ('B'=外盘,主动买, 'S'=内盘,主动卖, 'N'=未知)
# - 对于深交所, 将固定取值为 'N'(未知)
class eMdsL2TradeBSFlagT:
    MDS_L2_TRADE_BSFLAG_BUY             = 'B'   # L2内外盘标志 - 外盘,主动买
    MDS_L2_TRADE_BSFLAG_SELL            = 'S'   # L2内外盘标志 - 内盘,主动卖
    MDS_L2_TRADE_BSFLAG_UNKNOWN         = 'N'   # L2内外盘标志 - 未知


# Level2逐笔委托的买卖方向 ('1'=买 '2'=卖 'G'=借入 'F'=出借)
class eMdsL2OrderSideT:
    MDS_L2_ORDER_SIDE_BUY               = '1'   # L2买卖方向 - 买
    MDS_L2_ORDER_SIDE_SELL              = '2'   # L2买卖方向 - 卖
    MDS_L2_ORDER_SIDE_BORROW            = 'G'   # L2买卖方向 - 借入 (仅适用于深交所)
    MDS_L2_ORDER_SIDE_LEND              = 'F'   # L2买卖方向 - 出借 (仅适用于深交所)


# 上交所产品状态订单的逐笔委托买卖方向字段取值
# @note 对于上交所产品状态订单(OrderType='S'), Side 字段取值含义如下:
# - 'A': ADD   – 产品未上市
# - 'S': START – 启动
# - 'O': OCALL – 开市集合竞价
# - 'T': TRADE – 连续自动撮合
# - 'P': SUSP  – 停牌
# - 'L': CCALL – 收盘集合竞价
# - 'C': CLOSE – 闭市
# - 'E': ENDTR – 交易结束
class eMdsL2SseStatusOrderSideT:
    MDS_L2_SSE_STATUS_ORDER_SIDE_ADD    = 'A'   # 产品未上市
    MDS_L2_SSE_STATUS_ORDER_SIDE_START  = 'S'   # 启动
    MDS_L2_SSE_STATUS_ORDER_SIDE_OCALL  = 'O'   # 开市集合竞价
    MDS_L2_SSE_STATUS_ORDER_SIDE_TRADE  = 'T'   # 连续自动撮合
    MDS_L2_SSE_STATUS_ORDER_SIDE_SUSP   = 'P'   # 停牌
    MDS_L2_SSE_STATUS_ORDER_SIDE_CCALL  = 'L'   # 收盘集合竞价
    MDS_L2_SSE_STATUS_ORDER_SIDE_CLOSE  = 'C'   # 闭市
    MDS_L2_SSE_STATUS_ORDER_SIDE_ENDTR  = 'E'   # 交易结束


# 深交所逐笔委托的订单类型
class eMdsL2OrderTypeT:
    MDS_L2_ORDER_TYPE_MKT               = '1'   # 深交所订单类型 - 市价
    MDS_L2_ORDER_TYPE_LMT               = '2'   # 深交所订单类型 - 限价
    MDS_L2_ORDER_TYPE_SAMEPARTY_BEST    = 'U'   # 深交所订单类型 - 本方最优


# 上交所逐笔委托的订单类型
class eMdsL2SseOrderTypeT:
    MDS_L2_SSE_ORDER_TYPE_ADD           = 'A'   # 上交所订单类型 - 新增委托订单 (即: 新订单)
    MDS_L2_SSE_ORDER_TYPE_DELETE        = 'D'   # 上交所订单类型 - 删除委托订单 (即: 撤单)
    MDS_L2_SSE_ORDER_TYPE_STATUS        = 'S'   # 上交所订单类型 - 产品状态订单


# 组播行情的组播频道类型定义
class eMdsUdpChannelTypeT:
    MDS_UDP_CHANNEL_TYPE_UNDEFINE       = 0     # 未定义
    MDS_UDP_CHANNEL_TYPE_SNAP1          = 1     # 快照频道1 (上海L1/L2快照)
    MDS_UDP_CHANNEL_TYPE_SNAP2          = 2     # 快照频道2 (深圳L1/L2快照)
    MDS_UDP_CHANNEL_TYPE_TICK1          = 3     # 逐笔频道1 (上海逐笔成交/逐笔委托)
    MDS_UDP_CHANNEL_TYPE_TICK2          = 4     # 逐笔频道2 (深圳逐笔成交/逐笔委托)
    _MAX_MDS_UDP_CHANNEL_TYPE           = 5


# 客户端类型定义 (内部使用)
class eMdsClientTypeT:
    MDS_CLIENT_TYPE_UNDEFINED           = 0     # 客户端类型-未定义
    MDS_CLIENT_TYPE_INVESTOR            = 1     # 普通投资人
    MDS_CLIENT_TYPE_VIRTUAL             = 2     # 虚拟账户 (仅开通行情, 不可交易)


# 客户端状态定义 (内部使用)
class eMdsClientStatusT:
    MDS_CLIENT_STATUS_UNACTIVATED       = 0     # 未激活 (不加载)
    MDS_CLIENT_STATUS_ACTIVATED         = 1     # 已激活 (正常加载)
    MDS_CLIENT_STATUS_PAUSE             = 2     # 已暂停 (正常加载, 不可交易)
    MDS_CLIENT_STATUS_SUSPENDED         = 3     # 已挂起 (不加载)
    MDS_CLIENT_STATUS_CANCELLED         = 4     # 已注销 (不加载)
# -------------------------


# ===================================================================
# Level1 行情消息定义
# ===================================================================

class MdsTradingSessionStatusMsgT(Structure):
    """
    市场状态消息(MsgType=h)定义 (仅适用于上交所, 深交所行情中没有该数据)
    """
    _fields_ = (
        ("exchId", c_uint8),                    # 交易所代码(沪/深) @see eMdsExchangeIdT
        ("mdProductType", c_uint8),             # 行情产品类型 (股票(包含基金和债券)/期权) @see eMdsMdProductTypeT
        ("_isRepeated", c_int8),                # 是否是重复的行情 (供内部使用, 小于0 表示数据倒流)
        ("origMdSource", c_uint8),              # 原始行情数据来源 @see eMdsMsgSourceT

        ("tradeDate", c_int32),                 # 交易日期 (YYYYMMDD, 通过拆解数据生成时间OrigTime得到)
        ("updateTime", c_int32),                # 行情时间 (HHMMSSsss, 交易所时间, 通过拆解数据生成时间OrigTime得到)
        ("exchSendingTime", c_int32),           # 交易所发送时间 (HHMMSSsss, 目前获取不到深交所的发送时间, 固定为 0)
        ("mdsRecvTime", c_int32),               # MDS接收到时间 (HHMMSSsss)

        ("TotNoRelatedSym", c_int32),           # 最大产品数目 (包括指数)

        # 全市场行情状态 (*C8)
        # 该字段为 8 位字符串,左起每位表示特定的含义,无定义则填空格。
        #
        # 上交所股票、基金、指数及债券分销:
        # 第 0 位: ‘S’表示全市场启动期间(开市前), ‘T’表示全市场处于交易期间(含中间休市), ‘E’表示全市场处于闭市期间。
        # 第 1 位: ‘1’表示开盘集合竞价结束标志, 未结束取‘0’
        # 第 2 位: ‘1’表示全市场行情闭市标志, 未闭市取‘0’
        # 第 3 位: ‘1’表示上海(股票、基金、债券分销)市场行情结束标志, 未结束取‘0’
        #
        # 上交所债券:
        # 第 0 位: ‘S’表示全市场启动期间(开市前), ‘T’表示全市场处于交易期间(含中间休市), ‘E’表示全市场处于闭市期间。
        # 第 1 位: ‘1’表示开盘集合竞价结束标志, 未结束取‘0’
        # 第 2 位: ‘1’表示债券市场行情闭市标志, 未闭市取‘0’
        # 第 3 位: ‘1’表示债券现券(可转债及新标准券)行情结束标志, 未结束取‘0’
        # 第 4 位: ‘1’表示债券质押回购、债券现券(除可转债及新标准券)行情结束标志, 未结束取‘0’
        #
        # 上交所期权:
        # 第 0 位: ‘S’表示全市场启动期间(开市前), ‘T’表示全市场处于交易期间(含中间休市), ‘E’表示全市场处于闭市期间。
        # 第 1 位: ‘1’表示开盘集合竞价结束标志, 未结束取‘0’
        # 第 2 位: ‘1’表示期权市场行情闭市标志, 未闭市取‘0’
        ("TradingSessionID", c_char * MDS_MAX_TRADING_SESSION_ID_LEN),

        ("__filler3", c_uint8 * 3),             # 按64位对齐的填充域
        ("dataVersion", c_uint16),              # 行情数据的更新版本号 (当__isRepeated!=0时, 该值仅作为参考值)
        ("__filler", c_uint16),                 # 按64位对齐的填充域
        ("origTickSeq", c_uint64),              # 对应的原始行情的序列号(供内部使用)

        # 消息原始接收时间 (从网络接收到数据的最初时间)
        ("origNetTime", STimespec32T),
        # 消息实际接收时间 (开始解码等处理之前的时间)
        ("recvTime", STimespec32T),
        # 消息采集处理完成时间
        ("collectedTime", STimespec32T),
        # 消息加工处理完成时间
        ("processedTime", STimespec32T),
        # 消息推送时间 (写入推送缓存以后, 实际网络发送之前)
        ("pushingTime", STimespec32T)
    )


class _MdsSecurityStatusSwitchT(Structure):
    """
    证券业务开关列表
    """
    _fields_ = (
        ("switchFlag", c_uint8),                # 业务开关的使能标志 (0:未启用, 1:启用)
        ("switchStatus", c_uint8)               # 开关状态 (0:关闭, 1:开启)
    )


class MdsSecurityStatusMsgT(Structure):
    """
    证券实时状态定义 (仅适用于深交所, 上交所行情中没有该数据)
    """
    _fields_ = (
        ("exchId", c_uint8),                    # 交易所代码(沪/深) @see eMdsExchangeIdT
        ("mdProductType", c_uint8),             # 行情产品类型 (股票(包含基金和债券)/期权) @see eMdsMdProductTypeT
        ("_isRepeated", c_int8),                # 是否是重复的行情 (供内部使用, 小于0 表示数据倒流)
        ("origMdSource", c_uint8),              # 原始行情数据来源 @see eMdsMsgSourceT

        ("tradeDate", c_int32),                 # 交易日期 (YYYYMMDD, 通过拆解数据生成时间OrigTime得到)
        ("updateTime", c_int32),                # 行情时间 (HHMMSSsss, 交易所时间, 通过拆解数据生成时间OrigTime得到)
        ("exchSendingTime", c_int32),           # 交易所发送时间 (HHMMSSsss, 目前获取不到深交所的发送时间, 固定为 0)
        ("mdsRecvTime", c_int32),               # MDS接收到时间 (HHMMSSsss)

        ("instrId", c_int32),                   # 证券代码 (转换为整数类型的证券代码)

        # 证券代码 C6 / C8 (如: '000001' 等)
        ("SecurityID", c_char * MDS_MAX_INSTR_CODE_LEN),

        # 证券状态(C8)
        # A=上市公司早间披露提示
        # B=上市公司午间披露提示
        ("FinancialStatus", c_char * MDS_MAX_FINANCIAL_STATUS_LEN),

        ("__filler2", c_uint8 * 2),             # 按64位对齐的填充域
        ("dataVersion", c_uint16),            # 行情数据的更新版本号 (当__isRepeated!=0时, 该值仅作为参考值)
        ("__filler", c_uint16),                 # 按64位对齐的填充域
        ("origTickSeq", c_uint64),            # 对应的原始行情的序列号(供内部使用)

        ("NoSwitch", c_int32),                  # 开关个数
        ("__filler4", c_int32),                 # 按64位对齐的填充域

        # 证券业务开关列表
        # 业务开关列表为定长数组, 数组的下标位置对应于各个业务开关, 业务开关说明如下:
        #  -  1: 融资买入, 适用于融资标的证券
        #  -  2: 融券卖出, 适用于融券标的证券
        #  -  3: 申购, 适用于 ETF/LOF 等开放式基金, 对于黄金 ETF 是指现金申购
        #  -  4: 赎回, 适用于 ETF/LOF 等开放式基金, 对于黄金 ETF 是指现金赎回开关
        #  -  5: 认购, 适用于网上发行认购代码
        #  -  6: 转股, 适用于处于转股回售期的可转债
        #  -  7: 回售, 适用于处于转股回售期的可转债
        #  -  8: 行权, 适用于处于行权期的权证或期权
        #  - 10: 买开仓, 适用于期权等衍生品
        #  - 11: 卖开仓, 适用于期权等衍生品
        #  - 12: 黄金ETF实物申购, 适用于黄金 ETF
        #  - 13: 黄金ETF实物赎回, 适用于黄金 ETF
        #  - 14: 预受要约, 适用于处于要约收购期的股票
        #  - 15: 解除要约, 适用于处于要约收购期的股票
        #  - 18: 转股撤单, 适用于处于转股回售期的可转债
        #  - 19: 回售撤单, 适用于处于转股回售期的可转债
        #  - 20: 质押, 适用于质押式回购可质押入库证券
        #  - 21: 解押, 适用于质押式回购可质押入库证券
        #  - 22: 表决权, 适用于优先股
        #  - 23: 股票质押式回购, 适用于可开展股票质押式回购业务的证券
        #  - 24: 实时分拆, 适用于分级基金
        #  - 25: 实时合并, 适用于分级基金
        #  - 26: 备兑开仓, 适用于期权等衍生品
        #  - 27: 做市商报价, 适用于期权等支持做市商报价的证券
        #  - 28: 港股通整手买
        #  - 29: 港股通整手卖
        #  - 30: 港股通零股买
        #  - 31: 港股通零股卖
        #  - 32: 期权普通转备兑仓
        #  - 33: 期权备兑转普通仓
        ("switches", _MdsSecurityStatusSwitchT * MDS_MAX_SECURITY_SWITCH_CNT),

        # 消息原始接收时间 (从网络接收到数据的最初时间)
        ("origNetTime", STimespec32T),
        # 消息实际接收时间 (开始解码等处理之前的时间)
        ("recvTime", STimespec32T),
        # 消息采集处理完成时间
        ("collectedTime", STimespec32T),
        # 消息加工处理完成时间
        ("processedTime", STimespec32T),
        # 消息推送时间 (写入推送缓存以后, 实际网络发送之前)
        ("pushingTime", STimespec32T)
    )
# -------------------------


# ===================================================================
#  Level1 快照行情定义
# ===================================================================

class MdsPriceLevelEntryT(Structure):
    """
    价位信息定义
    """
    _fields_ = (
        ("Price", c_int32),                     # 委托价格
        ("NumberOfOrders", c_int32),            # 价位总委托笔数 (Level1不揭示该值, 固定为0)
        ("OrderQty", c_int64)                   # 委托数量 (上交所债券的数量单位为手)
    )


class MdsMktDataSnapshotHeadT(Structure):
    """
    Level1/Level2 快照行情(证券行情全幅消息)的消息头定义
    """
    _fields_ = (
        ("exchId", c_uint8),                    # 交易所代码(沪/深) @see eMdsExchangeIdT
        ("mdProductType", c_uint8),             # 行情产品类型 (股票/指数/期权) @see eMdsMdProductTypeT
        ("_isRepeated", c_int8),                # 是否是重复的行情 (内部使用, 小于0表示数据倒流)
        ("origMdSource", c_uint8),              # 原始行情数据来源 @see eMdsMsgSourceT

        ("tradeDate", c_int32),                 # 交易日期 (YYYYMMDD, 8位整型数值)
        ("updateTime", c_int32),                # 行情时间 (HHMMSSsss, 交易所时间)

        ("instrId", c_int32),                   # 证券代码 (转换为整数类型的证券代码)
        ("bodyLength", c_int16),                # 实际数据长度
        ("bodyType", c_uint8),                  # 快照数据对应的消息类型 @see eMdsMsgTypeT

        ("subStreamType", c_uint8),             # 行情数据类别 @see eMdsSubStreamTypeT
        ("channelNo", c_uint16),                # 频道代码 (仅适用于深交所, 对于上交所快照该字段无意义, 取值范围[0..9999])
        ("dataVersion", c_uint16),              # 行情数据的更新版本号
        ("_origTickSeq", c_uint32),             # 对应的原始行情的序列号 (供内部使用)
        ("_directSourceId", c_uint32),          # 内部数据来源标识 (仅内部使用)

        # 消息原始接收时间 (从网络接收到数据的最初时间)
        ("origNetTime", STimespec32T),
        # 消息实际接收时间 (开始解码等处理之前的时间)
        ("recvTime", STimespec32T),
        # 消息采集处理完成时间
        ("collectedTime", STimespec32T),
        # 消息加工处理完成时间
        ("processedTime", STimespec32T),
        # 消息推送时间 (写入推送缓存以后, 实际网络发送之前)
        ("pushingTime", STimespec32T)
    )


class MdsIndexSnapshotBodyT(Structure):
    """
    Level1/Level2 指数快照行情定义
    """
    _fields_ = (
        # 证券代码 C6 / C8 (如: '600000' 等)
        ("SecurityID", c_char * MDS_MAX_INSTR_CODE_LEN),
        # 产品实时阶段及标志 C8 / C4
        # @see MdsStockSnapshotBodyT.TradingPhaseCode
        ("TradingPhaseCode", c_char * MDS_MAX_TRADING_PHASE_CODE_LEN),
        ("__filler", c_char * 6),               # 按64位对齐的填充域

        ("NumTrades", c_uint64),                # 成交笔数
        ("TotalVolumeTraded", c_uint64),        # 成交总量 (上交所债券的数量单位为手)
        ("TotalValueTraded", c_int64),          # 成交总金额 (金额单位精确到元后四位, 即: 1元=10000)

        ("PrevClosePx", c_int64),               # 昨日收盘价 (价格单位精确到元后四位, 即: 1元=10000)
        ("OpenPx", c_int64),                    # 今开盘价 (价格单位精确到元后四位, 即: 1元=10000)
        ("HighPx", c_int64),                    # 最高价
        ("LowPx", c_int64),                     # 最低价
        ("TradePx", c_int64),                   # 成交价 (最新价)
        ("ClosePx", c_int64),                   # 今收盘价/期权收盘价 (适用于上交所行情和深交所债券现券交易产品)

        ("StockNum", c_int32),                  # 统计量指标样本个数 (@note 仅适用于深交所成交量统计指标)
        ("__filler1", c_int32)                  # 按64位对齐的填充域
    )


class MdsStockSnapshotBodyT(Structure):
    """
    Level1 股票快照行情定义
    股票(A、B股)、债券、基金、期权

    关于集合竞价期间的虚拟集合竞价行情 (上交所L1、深交所L1):
    - 集合竞价期间的虚拟成交价通过买卖盘档位揭示, 其中买一和卖一都揭示虚拟成交价格和成交数量,
      买二或卖二揭示虚拟成交价位上的买剩余量或卖剩余量
    """
    _fields_ = (
        # 证券代码 C6 / C8 (如: '600000' 等)
        ("SecurityID", c_char * MDS_MAX_INSTR_CODE_LEN),
        
        # 产品实时阶段及标志 C8 / C4
        #
        # 上交所股票 (C8):
        #  -# 第 0 位:
        #      - ‘S’表示启动 (开市前) 时段, ‘C’表示开盘集合竞价时段, ‘T’表示连续交易时段,
        #      - ‘E’表示闭市时段, ‘P’表示产品停牌,
        #      - ‘M’表示可恢复交易的熔断时段 (盘中集合竞价), ‘N’表示不可恢复交易的熔断时段 (暂停交易至闭市),
        #      - ‘U’表示收盘集合竞价时段。
        #  -# 第 1 位:
        #      - ‘0’表示此产品不可正常交易,
        #      - ‘1’表示此产品可正常交易,
        #      - 无意义填空格。
        #      - 在产品进入开盘集合竞价、连续交易、收盘集合竞价、熔断(盘中集合竞价)状态时值为‘1’,
        #        在产品进入停牌、熔断(暂停交易至闭市)状态时值为‘0’, 且闭市后保持该产品闭市前的是否可正常交易状态。
        #  -# 第 2 位:
        #      - ‘0’表示未上市, ‘1’表示已上市。
        #  -# 第 3 位:
        #      - ‘0’表示此产品在当前时段不接受订单申报,
        #      - ‘1’表示此产品在当前时段可接受订单申报。
        #      - 仅在交易时段有效, 在非交易时段无效。无意义填空格。
        #
        # 上交所期权 (C4):
        #  -# 第 0 位:
        #      - ‘S’表示启动(开市前)时段, ‘C’表示集合竞价时段, ‘T’表示连续交易时段,
        #      - ‘B’表示休市时段, ‘E’表示闭市时段, ‘V’表示波动性中断, ‘P’表示临时停牌, ‘U’收盘集合竞价。
        #      - ‘M’表示可恢复交易的熔断 (盘中集合竞价), ‘N’表示不可恢复交易的熔断 (暂停交易至闭市)
        #  -# 第 1 位:
        #      - ‘0’表示未连续停牌, ‘1’表示连续停牌。(预留, 暂填空格)
        #  -# 第 2 位:
        #      - ‘0’表示不限制开仓, ‘1’表示限制备兑开仓, ‘2’表示卖出开仓, ‘3’表示限制卖出开仓、备兑开仓,
        #      - ‘4’表示限制买入开仓, ‘5’表示限制买入开仓、备兑开仓, ‘6’表示限制买入开仓、卖出开仓,
        #      - ‘7’表示限制买入开仓、卖出开仓、备兑开仓
        #  -# 第 3 位:
        #      - ‘0’表示此产品在当前时段不接受进行新订单申报,
        #      - ‘1’表示此产品在当前时段可接受进行新订单申报。
        #      - 仅在交易时段有效, 在非交易时段无效。
        #
        # 深交所 (C8):
        #  -# 第 0 位:
        #      - S=启动(开市前) O=开盘集合竞价 T=连续竞价
        #      - B=休市 C=收盘集合竞价 E=已闭市 H=临时停牌
        #      - A=盘后交易 V=波动性中断
        #  -# 第 1 位:
        #      - 0=正常状态
        #      - 1=全天停牌
        ("TradingPhaseCode", c_char * MDS_MAX_TRADING_PHASE_CODE_LEN),
        ("__filler", c_char * 6),               # 按64位对齐的填充域

        ("NumTrades", c_uint64),                # 成交笔数
        ("TotalVolumeTraded", c_uint64),        # 成交总量 (上交所债券的数量单位为手)
        ("TotalValueTraded", c_int64),          # 成交总金额 (金额单位精确到元后四位, 即: 1元=10000)

        ("PrevClosePx", c_int32),               # 昨日收盘价 (价格单位精确到元后四位, 即: 1元=10000)
        ("OpenPx", c_int32),                    # 今开盘价 (价格单位精确到元后四位, 即: 1元=10000)
        ("HighPx", c_int32),                    # 最高价
        ("LowPx", c_int32),                     # 最低价
        ("TradePx", c_int32),                   # 成交价 (最新价)
        ("ClosePx", c_int32),                   # 今收盘价/期权收盘价 (适用于上交所行情和深交所债券现券交易产品)

        ## 适用于基金、期权产品的字段
        # 基金份额参考净值/ETF申赎的单位参考净值 (适用于基金. 单位精确到元后四位, 即: 1元=10000)
        ("IOPV", c_int32),
        # 基金 T-1 日净值 (适用于基金, 上交所Level-2实时行情里面没有该字段. 单位精确到元后四位, 即: 1元=10000)
        ("NAV", c_int32),
        # 期权合约总持仓量 (适用于期权. 单位为张)
        ("TotalLongPosition", c_uint64),

        ## 适用于债券产品的字段, @note 以下三个字段外部可直接引用:
        #
        #  - ("BondWeightedAvgPx", c_int32)         # 深交所债券加权平均价
        #    - 引用方式: object.BondWeightedAvgPx
        #    - 详细参见: self.BondWeightedAvgPx() 类成员函数
        #  - ("BondAuctionTradePx", c_int32)        # 深交所债券匹配成交的最近成交价
        #    - 引用方式: object.BondAuctionTradePx
        #    - 详细参见: self.BondAuctionTradePx() 类成员函数
        #  - ("BondAuctionVolumeTraded", c_uint64)  # 深交所债券匹配成交的成交总量
        #    - 引用方式: object.BondAuctionVolumeTraded
        #    - 详细参见: self.BondAuctionVolumeTraded() 类成员函数

        # 五档买盘价位信息
        ("BidLevels", MdsPriceLevelEntryT * 5),

        # 五档卖盘价位信息
        ("OfferLevels", MdsPriceLevelEntryT * 5)
    )

    @property
    def BondWeightedAvgPx(self) -> c_int32:
        """
        深交所债券加权平均价 (价格单位精确到元后四位, 即: 1元 = 10000)
        - @note (仅适用于深交所质押式回购及债券现券交易产品, 表示质押式回购成交量加权平均利率及债券现券交易成交量加权平均价)
        - @note C结构中, BondWeightedAvgPx 是 IOPV 字段的Union共用体
        """
        return self.IOPV

    @property
    def BondAuctionTradePx(self) -> c_int32:
        """
        深交所债券匹配成交的最近成交价 (仅适用于深交所债券现券交易产品. 价格单位精确到元后四位, 即: 1元=10000)
        - @note 如果证券还没有产生匹配成交交易方式的成交, 则该字段为0
        - @note 对于深交所可转债, 该字段固定为0 (深交所可转债仍然在现货竞价平台交易, 不属于债券现券交易产品)
        - @note C结构中, BondAuctionTradePx 是 NAV 字段的Union共用体
        """
        return self.NAV

    @property
    def BondAuctionVolumeTraded(self) -> c_uint64:
        """
        深交所债券匹配成交的成交总量 (仅适用于深交所债券现券交易产品)
        - @note C结构中, BondAuctionVolumeTraded 是 TotalLongPosition 字段的Union共用体
        """
        return self.TotalLongPosition

class MdsL1SnapshotBodyT(Union):
    """
    Level1 证券行情全幅消息的完整消息体定义
    """
    _fields_ = [
        ('stock', MdsStockSnapshotBodyT),       # 股票、债券、基金行情数据
        ('option', MdsStockSnapshotBodyT),      # 期权行情数据
        ('index', MdsIndexSnapshotBodyT)        # 指数行情数据
    ]


class MdsL1SnapshotT(Structure):
    """
    完整的 Level1 证券行情全幅消息定义
    """
    _fields_ = (
        ("head", MdsMktDataSnapshotHeadT),      # 行情数据的消息头
        ("__union", MdsL1SnapshotBodyT)         # 行情数据的消息体
    )
    _anonymous_ = ['__union']


# ===================================================================
#  Level2 快照行情消息定义
# ===================================================================

class MdsL2StockSnapshotBodyT(Structure):
    """
    Level2 快照行情定义
    股票(A、B股)、债券、基金

    关于集合竞价期间的虚拟集合竞价行情 (上交所L2、深交所L2):
    - 集合竞价期间的虚拟成交价通过买卖盘档位揭示, 其中买一和卖一都揭示虚拟成交价格和成交数量,
      买二或卖二揭示虚拟成交价位上的买剩余量或卖剩余量
    """
    _fields_ = (
        # 证券代码 C6 / C8 (如: '600000' 等)
        ("SecurityID", c_char * MDS_MAX_INSTR_CODE_LEN),

        # 产品实时阶段及标志 C8 / C4
        #
        # 上交所股票 (C8):
        #  -# 第 0 位:
        #      - ‘S’表示启动 (开市前) 时段, ‘C’表示开盘集合竞价时段, ‘T’表示连续交易时段,
        #      - ‘E’表示闭市时段, ‘P’表示产品停牌,
        #      - ‘M’表示可恢复交易的熔断时段 (盘中集合竞价), ‘N’表示不可恢复交易的熔断时段 (暂停交易至闭市),
        #      - ‘U’表示收盘集合竞价时段。
        #  -# 第 1 位:
        #      - ‘0’表示此产品不可正常交易,
        #      - ‘1’表示此产品可正常交易,
        #      - 无意义填空格。
        #      - 在产品进入开盘集合竞价、连续交易、收盘集合竞价、熔断(盘中集合竞价)状态时值为‘1’,
        #        在产品进入停牌、熔断(暂停交易至闭市)状态时值为‘0’, 且闭市后保持该产品闭市前的是否可正常交易状态。
        #  -# 第 2 位:
        #      - ‘0’表示未上市, ‘1’表示已上市。
        #  -# 第 3 位:
        #      - ‘0’表示此产品在当前时段不接受订单申报,
        #      - ‘1’表示此产品在当前时段可接受订单申报。
        #      - 仅在交易时段有效, 在非交易时段无效。无意义填空格。
        #
        # 上交所期权 (C4):
        #  -# 第 0 位:
        #      - ‘S’表示启动(开市前)时段, ‘C’表示集合竞价时段, ‘T’表示连续交易时段,
        #      - ‘B’表示休市时段, ‘E’表示闭市时段, ‘V’表示波动性中断, ‘P’表示临时停牌, ‘U’收盘集合竞价。
        #      - ‘M’表示可恢复交易的熔断 (盘中集合竞价), ‘N’表示不可恢复交易的熔断 (暂停交易至闭市)
        #  -# 第 1 位:
        #      - ‘0’表示未连续停牌, ‘1’表示连续停牌。(预留, 暂填空格)
        #  -# 第 2 位:
        #      - ‘0’表示不限制开仓, ‘1’表示限制备兑开仓, ‘2’表示卖出开仓, ‘3’表示限制卖出开仓、备兑开仓,
        #      - ‘4’表示限制买入开仓, ‘5’表示限制买入开仓、备兑开仓, ‘6’表示限制买入开仓、卖出开仓,
        #      - ‘7’表示限制买入开仓、卖出开仓、备兑开仓
        #  -# 第 3 位:
        #      - ‘0’表示此产品在当前时段不接受进行新订单申报,
        #      - ‘1’表示此产品在当前时段可接受进行新订单申报。
        #      - 仅在交易时段有效, 在非交易时段无效。
        #
        # 深交所 (C8):
        #  -# 第 0 位:
        #      - S=启动(开市前) O=开盘集合竞价 T=连续竞价
        #      - B=休市 C=收盘集合竞价 E=已闭市 H=临时停牌
        #      - A=盘后交易 V=波动性中断
        #  -# 第 1 位:
        #      - 0=正常状态
        #      - 1=全天停牌
        ("TradingPhaseCode", c_char * MDS_MAX_TRADING_PHASE_CODE_LEN),
        ("__filler", c_char * 6),               # 按64位对齐的填充域

        ("NumTrades", c_uint64),                # 成交笔数
        ("TotalVolumeTraded", c_uint64),        # 成交总量 (上交所债券的数量单位为手)
        ("TotalValueTraded", c_int64),          # 成交总金额 (金额单位精确到元后四位, 即: 1元=10000)

        ("PrevClosePx", c_int32),               # 昨日收盘价 (价格单位精确到元后四位, 即: 1元=10000)
        ("OpenPx", c_int32),                    # 今开盘价 (价格单位精确到元后四位, 即: 1元=10000)
        ("HighPx", c_int32),                    # 最高价
        ("LowPx", c_int32),                     # 最低价
        ("TradePx", c_int32),                   # 成交价 (最新价)
        ("ClosePx", c_int32),                   # 今收盘价/期权收盘价 (适用于上交所行情和深交所债券现券交易产品)

        ## 适用于基金、期权产品的字段
        # 基金份额参考净值/ETF申赎的单位参考净值 (适用于基金. 单位精确到元后四位, 即: 1元=10000)
        ("IOPV", c_int32),
        # 基金 T-1 日净值 (适用于基金, 上交所Level-2实时行情里面没有该字段. 单位精确到元后四位, 即: 1元=10000)
        ("NAV", c_int32),
        # 期权合约总持仓量 (适用于期权. 单位为张)
        ("TotalLongPosition", c_uint64),

        ## 适用于债券产品的字段, @note 以下三个字段外部可直接引用:
        #
        #  - ("BondWeightedAvgPx", c_int32)         # 深交所债券加权平均价
        #    - 引用方式: object.BondWeightedAvgPx
        #    - 详细参见: self.BondWeightedAvgPx() 类成员函数
        #  - ("BondAuctionTradePx", c_int32)        # 深交所债券匹配成交的最近成交价
        #    - 引用方式: object.BondAuctionTradePx
        #    - 详细参见: self.BondAuctionTradePx() 类成员函数
        #  - ("BondAuctionVolumeTraded", c_uint64)  # 深交所债券匹配成交的成交总量
        #    - 引用方式: object.BondAuctionVolumeTraded
        #    - 详细参见: self.BondAuctionVolumeTraded() 类成员函数

        ("TotalBidQty", c_int64),               # 委托买入总量 (@note 上交所债券的数量单位为手)
        ("TotalOfferQty", c_int64),             # 委托卖出总量 (@note 上交所债券的数量单位为手)
        ("WeightedAvgBidPx", c_int32),          # 加权平均委买价格 (价格单位精确到元后四位, 即: 1元=10000)
        ("WeightedAvgOfferPx", c_int32),        # 加权平均委卖价格 (价格单位精确到元后四位, 即: 1元=10000)

        ## 仅适用于上交所的委托价位数相关字段
        ("BidPriceLevel", c_int32),             # 买方委托价位数 (实际的委托价位总数, @note 仅适用于上交所)
        ("OfferPriceLevel", c_int32),           # 卖方委托价位数 (实际的委托价位总数, @note 仅适用于上交所)

        ## 仅适用于深交所的债券现券交易相关字段 (为支持新债券业务改造而增加的字段) @note API已特殊处理, 以下字段外部可直接引用
        #
        # 深交所债券匹配成交的成交总金额 (@note 仅适用于深交所债券现券交易产品. 金额单位精确到元后四位, 即: 1元=10000)
        # ("BondAuctionValueTraded", c_int64)   # @note API已特殊处理, SPI中可直接引用此字段 body.BondAuctionValueTraded

        # 十档买盘价位信息
        ("BidLevels", MdsPriceLevelEntryT * 10),

        # 十档卖盘价位信息
        ("OfferLevels", MdsPriceLevelEntryT * 10)
    )

    @property
    def BondWeightedAvgPx(self) -> c_int32:
        """
        深交所债券加权平均价 (价格单位精确到元后四位, 即: 1元 = 10000)
        - @note (仅适用于深交所质押式回购及债券现券交易产品, 表示质押式回购成交量加权平均利率及债券现券交易成交量加权平均价)
        - @note C结构中, BondWeightedAvgPx 是 IOPV 字段的Union共用体
        """
        return self.IOPV

    @property
    def BondAuctionTradePx(self) -> c_int32:
        """
        深交所债券匹配成交的最近成交价 (仅适用于深交所债券现券交易产品. 价格单位精确到元后四位, 即: 1元=10000)
        - @note 如果证券还没有产生匹配成交交易方式的成交, 则该字段为0
        - @note 对于深交所可转债, 该字段固定为0 (深交所可转债仍然在现货竞价平台交易, 不属于债券现券交易产品)
        - @note C结构中, BondAuctionTradePx 是 NAV 字段的Union共用体
        """
        return self.NAV

    @property
    def BondAuctionVolumeTraded(self) -> c_uint64:
        """
        深交所债券匹配成交的成交总量 (仅适用于深交所债券现券交易产品)
        - @note C结构中, BondAuctionVolumeTraded 是 TotalLongPosition 字段的Union共用体
        """
        return self.TotalLongPosition


# Level2 快照行情的增量更新消息定义 (增量更新消息仅适用于上交所L2)
# 股票(A、B股)、债券、基金
# @deprecated  已废弃, 上交所行情快照发送机制调整后, 不再推送增量更新消息
# MdsL2StockSnapshotIncrementalT


class MdsL2BestOrdersSnapshotBodyT(Structure):
    """
    Level2 委托队列信息 (买一／卖一前五十笔委托明细)
    """
    _fields_ = (
        # 证券代码 C6 / C8 (如: '600000' 等)
        ("SecurityID", c_char * MDS_MAX_INSTR_CODE_LEN),
        ("__filler", c_uint8 * 5),              # 按64位对齐的填充域
        ("NoBidOrders", c_uint8),               # 买一价位的揭示委托笔数
        ("NoOfferOrders", c_uint8),             # 卖一价位的揭示委托笔数

        ("TotalVolumeTraded", c_uint64),        # 成交总量 (来自快照行情的冗余字段)
        ("BestBidPrice", c_int32),              # 最优申买价 (价格单位精确到元后四位, 即: 1元=10000)
        ("BestOfferPrice", c_int32),            # 最优申卖价 (价格单位精确到元后四位, 即: 1元=10000)

        # 买一价位的委托明细(前50笔
        ("BidOrderQty", c_int32 * MDS_MAX_L2_DISCLOSE_ORDERS_CNT),

        # 卖一价位的委托明细(前50笔)
        ("OfferOrderQty", c_int32 * MDS_MAX_L2_DISCLOSE_ORDERS_CNT)
    )


# Level2 委托队列的增量更新信息 (买一／卖一前五十笔委托明细, 增量更新消息仅适用于上交所L2)
# @deprecated 已废弃, 上交所行情快照发送机制调整后, 不再推送增量更新消息
# MdsL2BestOrdersSnapshotIncrementalT


class MdsL2MarketOverviewT(Structure):
    """
    Level2 市场总览消息定义
    """
    _fields_ = (
        ("OrigDate", c_int32),                  # 市场日期 (YYYYMMDD)
        ("OrigTime", c_int32),                  # 市场时间 (HHMMSSss0, 实际精度为百分之一秒(HHMMSSss))

        ("exchSendingTime", c_int32),           # 交易所发送时间 (HHMMSS000, 实际精度为秒(HHMMSS))
        ("mdsRecvTime", c_int32)                # MDS接收到时间 (HHMMSSsss)
    )


class MdsL2SnapshotBodyT(Union):
    """
    Level2 快照行情的完整消息体定义
    """
    _fields_ = [
        # Level2 快照行情(股票、债券、基金、期权)
        ('l2Stock', MdsL2StockSnapshotBodyT),

        # Level2 委托队列(买一／卖一前五十笔委托明细)
        ('l2BestOrders', MdsL2BestOrdersSnapshotBodyT),

        # 期权行情数据
        ('option', MdsStockSnapshotBodyT),

        # 指数行情数据
        ('index', MdsIndexSnapshotBodyT),

        # Level2 市场总览 (仅适用于上交所)
        ('l2MarketOverview', MdsL2MarketOverviewT)

        # Level2 快照行情的增量更新消息 @deprecated 已废弃
        # ('l2StockIncremental', MdsL2StockSnapshotIncrementalT),

        # Level2 委托队列(买一／卖一前五十笔委托明细)的增量更新消息 @deprecated 已废弃
        # ('l2BestOrdersIncremental', MdsL2BestOrdersSnapshotIncrementalT),
    ]


class _UnionForMdsMktDataSnapshotT(Union):
    """
    (对外发布的) 完整的 Level1/Level2 快照行情消息体定义
    """
    _fields_ = [
        # Level2 快照行情(股票、债券、基金、期权)
        ('l2Stock', MdsL2StockSnapshotBodyT),

        # Level2 委托队列(买一／卖一前五十笔委托明细)
        ('l2BestOrders', MdsL2BestOrdersSnapshotBodyT),

        # Level1 股票、债券、基金行情数据
        ('stock', MdsStockSnapshotBodyT),

        # 期权行情数据
        ('option', MdsStockSnapshotBodyT),

        # 指数行情数据
        ('index', MdsIndexSnapshotBodyT),

        # Level2 市场总览 (仅适用于上交所)
        ('l2MarketOverview', MdsL2MarketOverviewT)

        # Level2 快照行情的增量更新消息 @deprecated 已废弃
        # ('l2StockIncremental', MdsL2StockSnapshotIncrementalT),

        # Level2 委托队列(买一／卖一前五十笔委托明细)的增量更新消息 @deprecated 已废弃
        # ('l2BestOrdersIncremental', MdsL2BestOrdersSnapshotIncrementalT),
    ]


class MdsMktDataSnapshotT(Structure):
    """
    (对外发布的) 完整的 Level1/Level2 快照行情定义
    """
    _fields_ = (
        # 行情数据的消息头
        ("head", MdsMktDataSnapshotHeadT),

        # 行情数据的消息体
        ("__union", _UnionForMdsMktDataSnapshotT)
    )
    _anonymous_ = ['__union']
# -------------------------


# ===================================================================
# Level2 逐笔成交/逐笔委托行情消息定义
# ===================================================================

class MdsL2TradeT(Structure):
    """
    Level2 逐笔成交行情定义
    """
    _fields_ = (
        ("exchId", c_uint8),                    # 交易所代码(沪/深) @see eMdsExchangeIdT
        ("mdProductType", c_uint8),             # 行情产品类型 (股票/指数/期权) @see eMdsMdProductTypeT
        ("_isRepeated", c_int8),                # 是否是重复的行情 (内部使用, 小于0表示数据倒流)
        ("origMdSource", c_uint8),              # 原始行情数据来源 @see eMdsMsgSourceT

        ("tradeDate", c_int32),                 # 交易日期 (YYYYMMDD, 8位整型数值)
        ("TransactTime", c_int32),              # 成交时间 (HHMMSSsss)

        ("instrId", c_int32),                   # 证券代码 (转换为整数类型的证券代码)
        ("ChannelNo", c_uint16),                # 频道代码 [0..9999]
        ("__reserve", c_uint16),                # 按64位对齐的保留字段

        # 深交所消息记录号 / 上交所成交序号(从1开始, 按频道连续)
        # - 深交所为逐笔成交 + 逐笔委托统一编号
        # - 上交所债券行情和逐笔合并数据为逐笔成交 + 逐笔委托统一编号(TickIndex / BizIndex)
        # - 上交所老版竞价行情(非逐笔合并数据)为逐笔成交独立编号 (TradeIndex)
        ("ApplSeqNum", c_uint32),

        # 证券代码 C6 / C8 (如: '600000' 等)
        ("SecurityID", c_char * MDS_MAX_INSTR_CODE_LEN),

        # 成交类别(仅适用于深交所)
        # - 深交所: '4'=撤销, 'F'=成交
        # - 上交所: 将固定为 'F' (成交)
        # - @see eMdsL2TradeExecTypeT
        ("ExecType", c_char),

        # 内外盘标志 (仅适用于上交所)
        # - 上交所: 'B'=外盘(主动买), 'S'=内盘(主动卖), 'N'=未知
        # - 深交所: 将固定为 'N' (未知)
        # - @see eMdsL2TradeBSFlagT
        ("TradeBSFlag", c_char),
        # 行情数据类别 @see eMdsSubStreamTypeT
        ("subStreamType", c_uint8),

        # 业务序列号 (仅适用于上交所)
        # - 仅适用于上交所, 逐笔成交+逐笔委托统一编号, 从1开始, 按频道连续
        # - 对于深交所, 该字段将固定为 0
        # - 对于上交所债券行情和逐笔合并数据, 该字段的取值将与 ApplSeqNum 相同
        ("SseBizIndex", c_uint32),
        # 为保持协议兼容而定义的填充域
        ("__filler", c_uint64),

        # 成交价格 (价格单位精确到元后四位, 即: 1元=10000)
        ("TradePrice", c_int32),
        # 成交数量 (@note 仅上交所债券的数量单位为手, 其它均为股或张)
        ("TradeQty", c_int32),
        # 成交金额 (金额单位精确到元后四位, 即: 1元=10000)
        ("TradeMoney", c_int64),

        # 买方订单号 (从 1 开始计数, 0 表示无对应委托)
        # - 对于深交所, 该字段对应于买方逐笔委托的 ApplSeqNum 字段
        # - 对于上交所, 该字段对应于买方逐笔委托的 SseOrderNo 字段
        ("BidApplSeqNum", c_int64),
        # 卖方订单号 (从 1 开始计数, 0 表示无对应委托)
        # - 对于深交所, 该字段对应于卖方逐笔委托的 ApplSeqNum 字段
        # - 对于上交所, 该字段对应于卖方逐笔委托的 SseOrderNo 字段
        ("OfferApplSeqNum", c_int64),

        # 消息原始接收时间 (从网络接收到数据的最初时间)
        ("origNetTime", STimespec32T),
        # 消息实际接收时间 (开始解码等处理之前的时间)
        ("recvTime", STimespec32T),
        # 消息采集处理完成时间
        ("collectedTime", STimespec32T),
        # 消息加工处理完成时间
        ("processedTime", STimespec32T),
        # 消息推送时间 (写入推送缓存以后, 实际网络发送之前)
        ("pushingTime", STimespec32T)
    )


class MdsL2OrderT(Structure):
    """
    Level2 逐笔委托行情定义

    @note 上交所债券行情逐笔数据的说明信息:
    - 集合竞价及停牌期间不发送逐笔委托数据, 到集合竞价或停牌结束时统一发送期间的逐笔委托数据;
    - 债券逐笔委托数据为原始订单数据;
    - 涉及交易状态改变产生的集中撮合成交数据在产品状态订单之前发布。

    @note 上交所竞价逐笔合并数据中的逐笔委托消息的说明:
    - 集合竞价及停牌期间不发送逐笔类数据, 到集合竞价或停牌结束时统一发送期间的数据, 先发送委托
      订单数据, 再发送成交数据和产品状态订单数据;
    - 在连续竞价阶段, 同一笔委托产生的主动成交及剩余新增委托订单数据, 先发送成交数据, 再发送成
      交后的剩余新增委托订单数据, 之后再产生的剩余委托订单数据不再发送;
    - 涉及交易时段改变产生的集中撮合成交数据在产品状态订单之前发布。

    @note 上交所老版竞价行情(非逐笔合并数据)中的逐笔委托消息的说明:
    - 新增委托订单仅在首次撮合后发布, 之后在被动成交的过程中, 均不再发布该笔委托的新增订单;
    - 在集合竞价或停牌阶段, 发布的委托数量为原始委托数量。
        - 集合竞价及停牌阶段接收到的有效委托不会实时发布, 将在集合竞价或停牌阶段结束后统一发布。
          若停牌至收盘, 将不再发布停牌期间的逐笔委托消息;
        - 在连续竞价阶段, 发布的委托数量为订单被撮合后剩余的委托数量。
          若一笔订单被一次性全部撮合, 则不会发布该订单的剩余委托数量;
        - 在盘后固定价格交易阶段, 不会发布逐笔委托消息。
    - 竞价逐笔委托消息与竞价逐笔成交消息属于不同的消息, 没有固定的到达先后次序关系。
      BizIndex 字段为竞价逐笔委托消息和竞价逐笔成交消息合并后的连续编号,
      故可以通过 BizIndex 字段判断竞价逐笔委托消息与竞价逐笔成交消息产生的先后顺序。
    """
    _fields_ = (
        ("exchId", c_uint8),                    # 交易所代码(沪/深) @see eMdsExchangeIdT
        ("mdProductType", c_uint8),             # 行情产品类型 (股票/指数/期权) @see eMdsMdProductTypeT
        ("_isRepeated", c_int8),                # 是否是重复的行情 (内部使用, 小于0表示数据倒流)
        ("origMdSource", c_uint8),              # 原始行情数据来源 @see eMdsMsgSourceT

        ("tradeDate", c_int32),                 # 交易日期 (YYYYMMDD, 8位整型数值)
        ("TransactTime", c_int32),              # 成交时间 (HHMMSSsss)

        ("instrId", c_int32),                   # 证券代码 (转换为整数类型的证券代码)
        ("ChannelNo", c_uint16),                # 频道代码 [0..9999]
        ("__reserve", c_uint16),                # 按64位对齐的保留字段

        # 深交所消息记录号 / 上交所成交序号(从1开始, 按频道连续)
        # - 深交所为逐笔成交 + 逐笔委托统一编号
        # - 上交所债券行情和逐笔合并数据为逐笔成交 + 逐笔委托统一编号(TickIndex / BizIndex)
        # - 上交所老版竞价行情(非逐笔合并数据)为逐笔成交独立编号 (TradeIndex)
        ("ApplSeqNum", c_uint32),

        # 证券代码 C6 / C8 (如: '600000' 等)
        ("SecurityID", c_char * MDS_MAX_INSTR_CODE_LEN),

        # 买卖方向
        # - 深交所: '1'=买, '2'=卖, 'G'=借入, 'F'=出借 @see eMdsL2OrderSideT
        # - 上交所: '1'=买, '2'=卖
        #   - @note 对于上交所产品状态订单(OrderType='S'), Side 字段取值含义如下: @see eMdsL2SseStatusOrderSideT
        #     - 'A': ADD   – 产品未上市
        #     - 'S': START – 启动
        #     - 'O': OCALL – 开市集合竞价
        #     - 'T': TRADE – 连续自动撮合
        #     - 'P': SUSP  – 停牌
        #     - 'L': CCALL – 收盘集合竞价
        #     - 'C': CLOSE – 闭市
        #     - 'E': ENDTR – 交易结束
        ("Side", c_char),

        # 订单类型
        # - 深交所: '1'=市价, '2'=限价, 'U'=本方最优 @see eMdsL2OrderTypeT
        # - 上交所: 'A'=委托订单-增加(新订单), 'D'=委托订单-删除(撤单), 'S'=产品状态订单 @see eMdsL2SseOrderTypeT
        ("OrderType", c_char),
        # 行情数据类别 @see eMdsSubStreamTypeT
        ("subStreamType", c_uint8),

        # 业务序列号 (仅适用于上交所)
        # - 仅适用于上交所, 逐笔成交+逐笔委托统一编号, 从1开始, 按频道连续
        # - 对于深交所, 该字段将固定为 0
        # - 对于上交所债券行情和逐笔合并数据, 该字段的取值将与 ApplSeqNum 相同
        ("SseBizIndex", c_uint32),

        # 原始订单号 (仅适用于上交所)
        # - 仅适用于上交所, 用于和逐笔成交中的买方/卖方订单号相对应
        # - 对于深交所, 该字段将固定为 0
        ("SseOrderNo", c_int64),

        # 委托价格 (价格单位精确到元后四位, 即: 1元=10000)
        ("Price", c_int32),
        # 委托数量 (@note 仅上交所债券的数量单位为手, 其它均为股或张)
        # - 对于上交所, 该字段的取值比较特殊:
        #   - 对于上交所, 当 OrderType='A' 时, 该字段表示的是剩余委托量 (竞价撮合成交后的剩余委托数量)
        #     - @note 对于上交所老版竞价行情(非债券行情)和逐笔合并数据, 该字段的含义为剩余委托量
        #     - @note 对于上交所债券行情, 该字段的含义为原始委托数量
        #   - 对于上交所, 当 OrderType='D' 时, 该字段表示的是撤单数量
        ("OrderQty", c_int32),

        # 消息原始接收时间 (从网络接收到数据的最初时间)
        ("origNetTime", STimespec32T),
        # 消息实际接收时间 (开始解码等处理之前的时间)
        ("recvTime", STimespec32T),
        # 消息采集处理完成时间
        ("collectedTime", STimespec32T),
        # 消息加工处理完成时间
        ("processedTime", STimespec32T),
        # 消息推送时间 (写入推送缓存以后, 实际网络发送之前)
        ("pushingTime", STimespec32T)
    )


class MdsTickChannelHeartbeatT(Structure):
    """
    Level2 逐笔频道心跳消息定义

    关于逐笔频道心跳消息说明如下:
    - 逐笔频道心跳消息用于发送和告知数据接收者当前逐笔频道上已发送的最后一笔逐笔数据消息对应的序号,
      以方便下游系统检查和识别逐笔行情消息是否出现丢失。
    - 逐笔频道心跳消息只在空闲时 (3 秒内该通道无逐笔消息) 才发布, 下游可以不处理该消息。

    关于逐笔数据的缺口检查和数据重传补充说明如下:
    - 逐笔成交/逐笔委托中的 ApplSeqNum 字段含义为逐笔数据序号, 该序号在一个频道内从 1 开始顺序递增,
      如出现序号跳变的情况, 则说明逐笔数据发生丢失。
    - 对于丢失的逐笔数据, 可以通过逐笔数据重传接口进行回补。
    """
    _fields_ = (
        ("exchId", c_uint8),                    # 交易所代码(沪/深) @see eMdsExchangeIdT
        ("origMdSource", c_uint8),              # 原始行情数据来源 @see eMdsMsgSourceT
        ("__filler1", c_uint8 * 6),             # 按64位对齐的填充域

        ("ChannelNo", c_uint16),                # 频道代码 [0..9999]
        ("__filler2", c_uint16),                # 按64位对齐的填充域
        ("ApplLastSeqNum", c_uint32),           # 最后一条逐笔数据的记录号
                                                # (即:当前最大的逐笔序号, 对应于逐笔成交/逐笔委托的 ApplSeqNum 字段)

        # 频道结束标志
        # - 仅适用于深交所, 用于标识该频道的逐笔行情消息已经发送完毕 (0:未发送完毕, 1:已发送完毕)
        # - 对于上交所该字段将固定为 0
        ("EndOfChannel", c_uint8),
        ("__filler3", c_uint8 * 7),             # 按64位对齐的填充域
        ("__reserve", c_char * 16),             # 按64位对齐的保留字段

        # 消息原始接收时间 (从网络接收到数据的最初时间)
        ("origNetTime", STimespec32T)
    )
# -------------------------


# ===================================================================
# 汇总的行情数据定义
# ===================================================================

class MdsWholeMktMsgBodyT(Union):
    """
    完整的行情数据消息体定义
    """
    _fields_ = [
        # 快照行情 (Level1 快照 / Level2 快照 / 指数行情 / 期权行情)
        ('mktDataSnapshot', MdsMktDataSnapshotT),

        # Level2 逐笔成交行情
        ('trade', MdsL2TradeT),

        # Level2 逐笔委托行情
        ('order', MdsL2OrderT),

        # Level2 逐笔频道心跳消息
        ('tickChannelHeartbeat', MdsTickChannelHeartbeatT),

        # 市场状态消息 (仅适用于上交所)
        ('trdSessionStatus', MdsTradingSessionStatusMsgT),

        # 证券实时状态消息 (仅适用于深交所)
        ('securityStatus', MdsSecurityStatusMsgT)
    ]
# -------------------------


# ===================================================================
# 证券信息等静态数据定义
# ===================================================================

class MdsStockStaticInfoT(Structure):
    """
    证券信息(股票/基金/债券)的静态数据结构体定义
    """
    _fields_ = [
        # 证券代码 C6 / C8 (如: '600000' 等)
        ("securityId", c_char * MDS_MAX_INSTR_CODE_LEN),
        ("exchId", c_uint8),                    # 交易所代码 (沪/深) @see eMdsExchangeIdT
        ("mdProductType", c_uint8),             # 行情产品类型 (股票/期权/指数) @see eMdsMdProductTypeT
        ("oesSecurityType", c_uint8),           # 证券类型 (股票/债券/基金/...) @see eOesSecurityTypeT
        ("subSecurityType", c_uint8),           # 证券子类型 @see eOesSubSecurityTypeT
        ("currType", c_uint8),                  # 币种 @see eOesCurrTypeT
        ("qualificationClass", c_uint8),        # 投资者适当性管理分类 @see eOesQualificationClassT
        ("__filler1", c_uint8 * 5),             # 按64位对齐的填充域
        ("instrId", c_int32),                   # 证券代码 (转换为整数类型的证券代码)

        ("securityStatus", c_uint32),           # 证券状态 @see eOesSecurityStatusT
        ("securityAttribute", c_uint32),        # 证券属性 @see eOesSecurityAttributeT

        ("suspFlag", c_uint8),                  # 连续停牌标识 (0:未停牌, 1:已停牌)
        ("isDayTrading", c_uint8),              # 是否支持当日回转交易 (0:不支持, 1:支持)
        ("isRegistration", c_uint8),            # 是否注册制 (0:核准制, 1:注册制)
        ("isCrdCollateral", c_uint8),           # 是否为融资融券可充抵保证金证券 (0:不可充抵保证金, 1:可充抵保证金)
        # 是否为融资标的 (0:不是融资标的, 1:是融资标的)
        ("isCrdMarginTradeUnderlying", c_uint8),
        # 是否为融券标的 (0:不是融券标的, 1:是融券标的)
        ("isCrdShortSellUnderlying", c_uint8),
        ("isNoProfit", c_uint8),                # 是否尚未盈利 (0:已盈利, 1:未盈利 (仅适用于科创板和创业板产品))
        ("isWeightedVotingRights", c_uint8),    # 是否存在投票权差异 (0:无差异, 1:存在差异 (仅适用于科创板和创业板产品))
        ("isVie", c_uint8),                     # 是否具有协议控制框架 (0:没有, 1:有 (仅适用于创业板产品))
        ("pricingMethod", c_uint8),             # 计价方式 (仅适用于债券 @see eOesPricingMethodT)
        ("__filler2", c_uint8 * 6),             # 按64位对齐的填充域

        ("upperLimitPrice", c_int32),           # 涨停价 (单位精确到元后四位, 即: 1元=10000)
        ("lowerLimitPrice", c_int32),           # 跌停价 (单位精确到元后四位, 即: 1元=10000)
        ("priceTick", c_int32),                 # 最小报价单位 (单位精确到元后四位, 即1元 = 10000)
        ("prevClose", c_int32),                 # 前收盘价, 单位精确到元后四位, 即1元 = 10000

        ("lmtBuyMaxQty", c_int32),              # 单笔限价买委托数量上限
        ("lmtBuyMinQty", c_int32),              # 单笔限价买委托数量下限
        ("lmtBuyQtyUnit", c_int32),             # 单笔限价买入单位

        ("mktBuyQtyUnit", c_int32),             # 单笔市价买入单位
        ("mktBuyMaxQty", c_int32),              # 单笔市价买委托数量上限
        ("mktBuyMinQty", c_int32),              # 单笔市价买委托数量下限

        ("lmtSellMaxQty", c_int32),             # 单笔限价卖委托数量上限
        ("lmtSellMinQty", c_int32),             # 单笔限价卖委托数量下限
        ("lmtSellQtyUnit", c_int32),            # 单笔限价卖出单位

        ("mktSellQtyUnit", c_int32),            # 单笔市价卖出单位
        ("mktSellMaxQty", c_int32),             # 单笔市价卖委托数量上限
        ("mktSellMinQty", c_int32),             # 单笔市价卖委托数量下限

        ("bondInterest", c_int64),              # 债券的每张应计利息, 单位精确到元后八位, 即应计利息1元 = 100000000
        ("parValue", c_int64),                  # 面值, 单位精确到元后四位, 即1元 = 10000

        ("auctionLimitType", c_uint8),          # 连续交易时段的有效竞价范围限制类型 @see eOesAuctionLimitTypeT
        ("auctionReferPriceType", c_uint8),     # 连续交易时段的有效竞价范围基准价类型 @see eOesAuctionReferPriceTypeT
        ("__filler3", c_uint8 * 2),             # 按64位对齐的填充域
        ("auctionUpDownRange", c_int32),        # 连续交易时段的有效竞价范围涨跌幅度 (百分比或绝对价格, 取决于'有效竞价范围限制类型')

        ("listDate", c_int32),                  # 上市日期
        ("maturityDate", c_int32),              # 到期日期 (仅适用于债券等有发行期限的产品)
        ("outstandingShare", c_int64),          # 总股本 (即: 总发行数量, 上证无该字段, 未额外维护时取值为0)
        ("publicFloatShare", c_int64),          # 流通股数量

        # 基础证券代码 (标的产品代码)
        ("underlyingSecurityId", c_char * MDS_MAX_INSTR_CODE_LEN),
        # 按64位对齐的填充域
        ("__filler4", c_uint8 * 7),
        # 证券名称 (UTF-8 编码)
        ("securityName", c_char * MDS_MAX_SECURITY_NAME_LEN),
        # 证券长名称 (UTF-8 编码)
        ("securityLongName", c_char * MDS_MAX_SECURITY_LONG_NAME_LEN),
        # 证券英文名称
        ("securityEnglishName", c_char * MDS_MAX_SECURITY_ENGLISH_NAME_LEN),
        # ISIN代码
        ("securityIsinCode", c_char * MDS_MAX_SECURITY_ISIN_CODE_LEN),

        # 预留的备用字段1
        ("__reserve1", c_char * 24),
        # 预留的备用字段2
        ("__reserve2", c_char * 64)
    ]


class MdsOptionStaticInfoT(Structure):
    """
    期权合约信息的静态数据结构体定义
    """
    _fields_ = [
        # 期权合约代码 C8 (如: '10001230' 等)
        ("securityId", c_char * MDS_MAX_INSTR_CODE_LEN),
        ("exchId", c_uint8),                    # 交易所代码 (沪/深) @see eMdsExchangeIdT
        ("mdProductType", c_uint8),             # 行情产品类型 (股票/期权/指数) @see eMdsMdProductTypeT
        ("oesSecurityType", c_uint8),           # 证券类型 (股票/债券/基金/...) @see eOesSecurityTypeT
        ("subSecurityType", c_uint8),           # 证券子类型 @see eOesSubSecurityTypeT
        ("contractType", c_uint8),              # 合约类型 (认购/认沽) @see eOesOptContractTypeT
        ("exerciseType", c_uint8),              # 行权方式 @see eOesOptExerciseTypeT
        ("deliveryType", c_uint8),              # 交割方式 @see eOesOptDeliveryTypeT
        ("__filler1", c_uint8 * 4),             # 按64位对齐的填充域
        ("instrId", c_int32),                   # 证券代码 (转换为整数类型的证券代码)

        ("contractUnit", c_uint32),             # 合约单位 (经过除权除息调整后的单位)
        ("exercisePrice", c_uint32),            # 期权行权价 (经过除权除息调整后的价格. 单位精确到元后四位, 即: 1元=10000)
        ("deliveryDate", c_uint32),             # 交割日期 (格式为YYYYMMDD)
        ("deliveryMonth", c_uint32),            # 交割月份 (格式为YYYYMM)

        ("listDate", c_int32),                  # 上市日期
        ("lastTradeDay", c_int32),              # 最后交易日 (格式为YYYYMMDD)
        ("exerciseBeginDate", c_int32),         # 行权起始日期 (格式为YYYYMMDD)
        ("exerciseEndDate", c_int32),           # 行权结束日期 (格式为YYYYMMDD)

        ("prevClosePrice", c_int32),            # 合约前收盘价 (单位精确到元后四位, 即: 1元=10000)
        ("prevSettlPrice", c_int32),            # 合约前结算价 (单位精确到元后四位, 即: 1元=10000)
        ("underlyingClosePrice", c_int32),      # 标的证券前收盘价 (单位精确到元后四位, 即: 1元=10000)

        ("priceTick", c_int32),                 # 最小报价单位 (单位精确到元后四位, 即1元 = 10000)
        ("upperLimitPrice", c_int32),           # 涨停价 (单位精确到元后四位, 即: 1元=10000)
        ("lowerLimitPrice", c_int32),           # 跌停价 (单位精确到元后四位, 即: 1元=10000)

        ("buyQtyUnit", c_int32),                # 买入单位
        ("lmtBuyMaxQty", c_int32),              # 限价买数量上限 (单笔申报的最大张数)
        ("lmtBuyMinQty", c_int32),              # 限价买数量下限 (单笔申报的最大张数)
        ("mktBuyMaxQty", c_int32),              # 市价买数量上限 (单笔申报的最大张数)
        ("mktBuyMinQty", c_int32),              # 市价买数量下限 (单笔申报的最大张数)

        ("mktSellQtyUnit", c_int32),            # 卖出单位
        ("lmtSellMaxQty", c_int32),             # 限价卖数量上限 (单笔申报的最大张数)
        ("lmtSellMinQty", c_int32),             # 限价卖数量下限 (单笔申报的最大张数)
        ("mktSellMaxQty", c_int32),             # 市价卖数量上限 (单笔申报的最大张数)
        ("mktSellMinQty", c_int32),             # 市价卖数量下限 (单笔申报的最大张数)

        ("sellMargin", c_int64),                # 单位保证金 (未上调的今卖开每张保证金. 单位精确到元后四位, 即: 1元=10000)

        # 期权合约交易所代码
        ("contractId", c_char * MDS_MAX_CONTRACT_EXCH_ID_LEN),
        # 期权合约名称 (UTF-8 编码)
        ("securityName", c_char * MDS_MAX_CONTRACT_SYMBOL_LEN),
        # 标的证券代码
        ("underlyingSecurityId", c_char * MDS_MAX_INSTR_CODE_LEN),
        # 按64位对齐的填充域
        ("__filler2", c_uint8 * 7),

        ("__reserve", c_char * 16)              # 预留的备用字段
    ]
# -------------------------
