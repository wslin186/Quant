# -*- coding: utf-8 -*-
"""
查询消息的报文定义
"""

from ctypes import (
    c_char, c_uint8, c_int8, c_uint16, c_int16, c_uint32, c_int32,
    c_uint64, c_int64, Structure, Union
)

from .mds_base_model import (
    SPK_MAX_PATH_LEN,

    MDS_MAX_SECURITY_CNT_PER_SUBSCRIBE,
    MDS_MAX_OPTION_CNT_TOTAL_SUBSCRIBED,

    MDS_MAX_USERNAME_LEN,
    MDS_MAX_PASSWORD_LEN,
    MDS_CLIENT_TAG_MAX_LEN,
    MDS_VER_ID_MAX_LEN,
    MDS_MAX_TEST_REQ_ID_LEN,
    MDS_MAX_COMP_ID_LEN,

    MDS_MAX_IP_LEN,
    MDS_MAX_INSTR_CODE_LEN,
    MDS_MAX_SENDING_TIME_LEN,
    MDS_REAL_SENDING_TIME_LEN,
    MDS_MAX_TRADING_SESSION_ID_LEN,
    MDS_REAL_TRADING_SESSION_ID_LEN,
    MDS_MAX_TRADING_PHASE_CODE_LEN,
    MDS_MAX_FINANCIAL_STATUS_LEN,
    MDS_REAL_FINANCIAL_STATUS_LEN,

    MDS_APPL_DISCARD_VERSION_MAX_COUNT,
    MDS_APPL_UPGRADE_PROTOCOL_MAX_LEN,
    MdsL1SnapshotT, MdsMktDataSnapshotT,
    MdsSecurityStatusMsgT, MdsTradingSessionStatusMsgT,
    MdsStockStaticInfoT, MdsOptionStaticInfoT,
    STimespec32T, UnionForUserInfo
)


# ===================================================================
# 常量定义
# ===================================================================

# 查询应答报文中的最大证券静态信息数量
MDS_QRYRSP_MAX_STOCK_CNT                        = 100
# -------------------------


# ===================================================================
# 单条查询的查询消息定义
# ===================================================================

class MdsQryMktDataSnapshotReqT(Structure):
    """
    查询定位的游标结构
    """
    _fields_ = [
        ("exchId", c_uint8),                    # 交易所代码 @see eMdsExchangeIdT
        ("mdProductType", c_uint8),             # 行情产品类型 (股票/期权/指数) @see eMdsMdProductTypeT
        ("__filler", c_uint8 * 2),              # 按64位对齐的填充域
        ("instrId", c_int32)                    # 证券代码 (转换为整数类型的证券代码)
    ]


# (深圳)证券实时状态查询的请求报文
MdsQrySecurityStatusReqT = MdsQryMktDataSnapshotReqT


class MdsQryTrdSessionStatusReqT(Structure):
    """
    (上证)市场状态查询的请求报文
    """
    _fields_ = [
        ("exchId", c_uint8),                    # 交易所代码 @see eMdsExchangeIdT
        ("mdProductType", c_uint8),             # 行情产品类型 (股票/期权/指数) @see eMdsMdProductTypeT
        ("__filler", c_uint8 * 6)               # 按64位对齐的填充域
    ]
# -------------------------


# ===================================================================
# 批量查询的查询消息头定义
# ===================================================================

class MdsQryReqHeadT(Structure):
    """
    查询请求的消息头定义
    """
    _fields_ = [
        ("maxPageSize", c_int32),               # 最大分页大小
        ("lastPosition", c_int32)               # 查询起始位置
    ]


class MdsQryRspHeadT(Structure):
    """
    查询应答的消息头定义
    """
    _fields_ = [
        ("maxPageSize", c_int32),               # 最大分页大小
        ("lastPosition", c_int32),              # 查询起始位置

        ("isEnd", c_int8),                      # 是否是当前最后一个包
        ("__filler", c_int8 * 7),               # 按64位对齐的填充域

        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64)
    ]


class MdsQryCursorT(Structure):
    """
    查询定位的游标结构
    """
    _fields_ = [
        ("seqNo", c_int32),                     # 查询位置
        ("isEnd", c_int8),                      # 是否是当前最后一个包
        ("__filler", c_int8 * 3),               # 按64位对齐的填充域
        ("userInfo", c_int64)                   # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
    ]


class MdsQrySecurityCodeEntryT(Structure):
    """
    行情查询请求中的证券代码信息
    """
    _fields_ = [
        ("instrId", c_int32),                   # 证券代码 (转换为整数类型的证券代码)
        ("exchId", c_uint8),                    # 交易所代码 @see eMdsExchangeIdT
        ("mdProductType", c_uint8),             # 行情产品类型 (股票/期权/指数) @see eMdsMdProductTypeT
        ("__filler", c_uint8 * 2)               # 按64位对齐的填充域
    ]
# -------------------------


# ===================================================================
# 证券静态信息查询相关结构体定义 (已废弃)
# ===================================================================

# 证券静态信息查询的过滤条件定义 - MdsQryStockStaticInfoFilterT
# 证券静态信息查询的请求报文 - MdsQryStockStaticInfoReqT
# 证券静态信息查询的应答报文 - MdsQryStockStaticInfoRspT

# 期权合约静态信息查询的过滤条件定义 - MdsQryOptionStaticInfoFilterT
# 期权合约静态信息查询的请求报文 - MdsQryOptionStaticInfoReqT
# 期权合约静态信息查询的应答报文 - MdsQryOptionStaticInfoRspT
# -------------------------


# ===================================================================
# 证券静态信息列表批量查询相关结构体定义
# ===================================================================

class MdsQryStockStaticInfoListFilterT(Structure):
    """
    证券静态信息查询的过滤条件定义
    """
    _fields_ = [
        ("exchId", c_uint8),                    # 交易所代码 @see eMdsExchangeIdT
        ("oesSecurityType", c_uint8),           # 证券类型 (股票/债券/基金/...) @see eOesSecurityTypeT
        ("subSecurityType", c_uint8),           # 证券子类型 @see eOesSubSecurityTypeT
        ("__filler", c_uint8 * 5),              # 按64位对齐的填充域

        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64)
    ]


class MdsQryStockStaticInfoListReqT(Structure):
    """
    证券静态信息查询的请求报文
    """
    _fields_ = [
        # 查询请求的消息头
        ("reqHead", MdsQryReqHeadT),
        # 查询请求的消息头
        ("qryFilter", MdsQryStockStaticInfoListFilterT),

        # 待查询的证券代码数量
        ("securityCodeCnt", c_int32),
        # 按64位对齐的填充域
        ("__filler", c_int32),

        # 待查询的证券代码列表 (最大大小为 MDS_QRYRSP_MAX_STOCK_CNT)
        ("securityCodeList", MdsQrySecurityCodeEntryT * 1)
    ]


class MdsQryStockStaticInfoListRspT(Structure):
    """
    证券静态信息查询的应答报文
    """
    _fields_ = [
        # 查询请求的消息头
        ("rspHead", MdsQryRspHeadT),
        # 证券静态信息数组 (最大大小为 MDS_QRYRSP_MAX_STOCK_CNT)
        ("qryItems", MdsStockStaticInfoT * 1)
    ]


# 期权合约静态信息查询的过滤条件定义
MdsQryOptionStaticInfoListFilterT = MdsQryStockStaticInfoListFilterT


# 期权合约静态信息查询的请求报文
MdsQryOptionStaticInfoListReqT = MdsQryStockStaticInfoListReqT


class MdsQryOptionStaticInfoListRspT(Structure):
    """
    期权合约静态信息查询的应答报文
    """
    _fields_ = [
        # 查询请求的消息头
        ("rspHead", MdsQryRspHeadT),
        # 期权静态信息数组 (最大大小为 MDS_QRYRSP_MAX_STOCK_CNT)
        ("qryItems", MdsOptionStaticInfoT * 1)
    ]
# -------------------------


# ===================================================================
# 行情快照信息批量查询相关结构体定义
# ===================================================================

class MdsQrySnapshotListFilterT(Structure):
    """
    行情快照信息查询的过滤条件定义
    """
    _fields_ = [
        ("exchId", c_uint8),                    # 交易所代码 @see eMdsExchangeIdT
        ("mdProductType", c_uint8),             # 行情产品类型 (股票/期权/指数) @see eMdsMdProductTypeT
        ("oesSecurityType", c_uint8),           # 证券类型 (股票/债券/基金/...) @see eOesSecurityTypeT
        ("subSecurityType", c_uint8),           # 证券子类型 @see eOesSubSecurityTypeT
        ("mdLevel", c_uint8),                   # 行情数据级别 (Level1 / Level2) @see eMdsMdLevelT
        ("__filler", c_uint8 * 11),             # 按64位对齐的填充域

        # 用户私有信息 (由客户端自定义填充, 并在应答数据中原样返回)
        ("userInfo", c_int64)
    ]


class MdsQrySnapshotListReqT(Structure):
    """
    行情快照信息查询的请求报文
    """
    _fields_ = [
        # 查询请求的消息头
        ("reqHead", MdsQryReqHeadT),
        # 查询请求的消息头
        ("qryFilter", MdsQrySnapshotListFilterT),

        # 待查询的证券代码数量
        ("securityCodeCnt", c_int32),
        # 按64位对齐的填充域
        ("__filler", c_int32),
        # 待查询的证券代码列表 (最大大小为 MDS_QRYRSP_MAX_STOCK_CNT)
        ("securityCodeList", MdsQrySecurityCodeEntryT * 1)
    ]


class MdsQrySnapshotListRspT(Structure):
    """
    行情快照信息查询的应答报文
    """
    _fields_ = [
        # 查询请求的消息头
        ("rspHead", MdsQryRspHeadT),
        # 五档快照信息数组 (最大大小为 MDS_QRYRSP_MAX_STOCK_CNT)
        ("qryItems", MdsL1SnapshotT * 1)
    ]
# -------------------------


# ===================================================================
# 周边应用升级配置信息相关结构体定义 (暂不开启使用)
# ===================================================================

class MdsApplUpgradeSourceT(Structure):
    """
    应用程序升级源信息
    """
    _fields_ = [
        # IP地址
        ("ipAddress", c_char * MDS_MAX_IP_LEN),
        # 协议名称
        ("protocol", c_char * MDS_APPL_UPGRADE_PROTOCOL_MAX_LEN),
        # 用户名
        ("username", c_char * MDS_MAX_USERNAME_LEN),
        # 用户密码
        ("password", c_char * MDS_MAX_PASSWORD_LEN),
        # 登录密码的加密方法
        ("encryptMethod", c_int32),
        # 按64位对齐的填充域
        ("__filler", c_int32),

        # 根目录地址
        ("homePath", c_char * SPK_MAX_PATH_LEN),
        # 文件名称
        ("fileName", c_char * SPK_MAX_PATH_LEN)
    ]


class MdsApplUpgradeItemT(Structure):
    """
    单个应用程序升级信息
    """
    _fields_ = [
        # 应用程序名称
        ("applName", c_char * MDS_MAX_COMP_ID_LEN),

        # 应用程序的最低协议版本号
        ("minApplVerId", c_char * MDS_VER_ID_MAX_LEN),
        # 应用程序的最高协议版本号
        ("maxApplVerId", c_char * MDS_VER_ID_MAX_LEN),
        # 废弃的应用版本号列表
        ("discardApplVerId", (c_char * MDS_APPL_DISCARD_VERSION_MAX_COUNT)
                                     * MDS_VER_ID_MAX_LEN),
        # 废弃版本号的数目
        ("discardVerCount", c_int32),

        # 最新协议版本的日期
        ("newApplVerDate", c_int32),
        # 应用程序的最新协议版本号
        ("newApplVerId", c_char * MDS_VER_ID_MAX_LEN),
        # 最新协议版本的标签信息
        ("newApplVerTag", c_char * MDS_CLIENT_TAG_MAX_LEN),

        # 主用升级源配置信息
        ("primarySource", MdsApplUpgradeSourceT),
        # 备用升级源配置信息
        ("secondarySource", MdsApplUpgradeSourceT)
    ]


class MdsApplUpgradeInfoT(Structure):
    """
    MDS周边应用程序升级信息
    """
    _fields_ = [
        # 客户端升级配置信息
        ("clientUpgradeInfo", MdsApplUpgradeItemT),
        # C_API升级配置信息
        ("cApiUpgradeInfo", MdsApplUpgradeItemT),
        # JAVA_API升级配置信息
        ("javaApiUpgradeInfo", MdsApplUpgradeItemT)
    ]


class MdsQryApplUpgradeInfoRspT(Structure):
    """
    查询周边应用升级配置信息应答
    """
    _fields_ = [
        ("applUpgradeInfo", MdsApplUpgradeInfoT)
    ]
# -------------------------
