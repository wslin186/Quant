"""
MDS SPI回调函数类
"""

from typing import Any

from quote_api import (
    # spk_util.py
    SMsgHeadT, MdsAsyncApiChannelT,

    # mds_base_model.py
    MDS_MAX_SECURITY_CNT_PER_SUBSCRIBE,

    eMdsExchangeIdT, eMdsMdProductTypeT,
    MdsTradingSessionStatusMsgT, MdsSecurityStatusMsgT, MdsL1SnapshotT,
    MdsL2StockSnapshotBodyT, MdsL2BestOrdersSnapshotBodyT, MdsL2MarketOverviewT,
    MdsMktDataSnapshotT, MdsL2TradeT, MdsL2OrderT, MdsTickChannelHeartbeatT,
    MdsStockStaticInfoT, MdsOptionStaticInfoT,

    # mds_qry_packets.py
    MdsQryCursorT, MdsQryStockStaticInfoListFilterT,

    # mds_mkt_pachets.py
    eMdsMsgTypeT, eMdsSubscribeModeT, eMdsSubscribeDataTypeT,
    MdsApiSubscribeInfoT, MdsMktDataRequestRspT,
    MdsTestRequestRspT, MdsChangePasswordRspT,
    MdsTickResendRequestRspT, MdsMktRspMsgBodyT,

    # mds_spi.py
    MdsClientSpi
)


class MdsClientMySpi(MdsClientSpi):
    """
    MDS-SPI回调函数类
    """
    def __init__(self):
        super().__init__()

        # 自定义属性
        self.something: Any = None

    def __sample_subscribe_market_data(self,
            channel: MdsAsyncApiChannelT) -> int:
        """
        连接完成后, 发送证券行情实时订阅请求样例展示 (仅供参考)

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
        """
        subscribe_info: MdsApiSubscribeInfoT = MdsApiSubscribeInfoT()

        subscribe_info.mktDataRequestReq.subMode = \
            eMdsSubscribeModeT.MDS_SUB_MODE_BATCH_END
        subscribe_info.mktDataRequestReq.dataTypes = \
            eMdsSubscribeDataTypeT.MDS_SUB_DATA_TYPE_L2_TRADE
        subscribe_info.mktDataRequestReq.subSecurityCnt = 2

        subscribe_info.entries[0].exchId = eMdsExchangeIdT.MDS_EXCH_SSE
        subscribe_info.entries[0].mdProductType = \
            eMdsMdProductTypeT.MDS_MD_PRODUCT_TYPE_STOCK
        subscribe_info.entries[0].instrId = 600000

        subscribe_info.entries[1].exchId = eMdsExchangeIdT.MDS_EXCH_SZSE
        subscribe_info.entries[1].mdProductType = \
            eMdsMdProductTypeT.MDS_MD_PRODUCT_TYPE_STOCK
        subscribe_info.entries[1].instrId = 1

        # 发送证券行情实时订阅请求
        ret = self.mds_api.subscribe_market_data(channel,
            subscribe_info)
        if ret < 0:
            print("... 发送证券行情实时订阅请求失败! ret[{}]".format(ret))
            # 返回大于0的值, 表示需要继续执行默认的 OnConnect 回调处理
            return 1

        print("... 发送证券行情实时订阅请求成功! channel_tag[{}]".format(
            channel.pChannelCfg.contents.channelTag.decode()))
        return 0

    def __sample_subscribe_by_string_and_prefixes(self,
            channel: MdsAsyncApiChannelT) -> int:
        """
        连接完成后, 通过证券代码前缀来订阅行情样例展示 (仅供参考)

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
        """
        data_types = eMdsSubscribeDataTypeT.MDS_SUB_DATA_TYPE_L2_TRADE

        # 订阅6000, 00000前缀的股票行情
        ret = self.mds_api.subscribe_by_string_and_prefixes(
            channel,
            security_list = "600000, 600010, 000001, 0000002.SZ",
            sse_code_prefixes = "6000",
            szse_code_prefixes = "00000",
            product_type = eMdsMdProductTypeT.MDS_MD_PRODUCT_TYPE_STOCK,
            sub_mode = eMdsSubscribeModeT.MDS_SUB_MODE_BATCH_END,
            data_types = data_types)
        if ret < 0:
            print("... 通过证券代码前缀订阅行情失败! ret[{}]".format(ret))
            # 返回大于0的值, 表示需要继续执行默认的 OnConnect 回调处理
            return 1

        print("... 通过证券代码前缀订阅行情成功! channel_tag[{}]".format(
            channel.pChannelCfg.contents.channelTag.decode()))
        return 0

    def __sample_subscribe_all(self,
            channel: MdsAsyncApiChannelT) -> int:
        """
        连接完成后, 订阅全市场行情 (仅供参考)

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
        """
        # 订阅的数据类型 (dataTypes) 会以最后一次订阅为准, 所以每次都需要指定为所有待订阅的数据类型
        data_types = eMdsSubscribeDataTypeT.MDS_SUB_DATA_TYPE_INDEX_SNAPSHOT \
            | eMdsSubscribeDataTypeT.MDS_SUB_DATA_TYPE_OPTION_SNAPSHOT \
            | eMdsSubscribeDataTypeT.MDS_SUB_DATA_TYPE_L2_SNAPSHOT \
            | eMdsSubscribeDataTypeT.MDS_SUB_DATA_TYPE_L2_BEST_ORDERS \
            | eMdsSubscribeDataTypeT.MDS_SUB_DATA_TYPE_L2_ORDER \
            | eMdsSubscribeDataTypeT.MDS_SUB_DATA_TYPE_L2_SSE_ORDER \
            | eMdsSubscribeDataTypeT.MDS_SUB_DATA_TYPE_L2_TRADE

        if self.mds_api.subscribe_by_string(
                channel, None, None,
                eMdsExchangeIdT.MDS_EXCH_SSE,
                eMdsMdProductTypeT.MDS_MD_PRODUCT_TYPE_STOCK,
                eMdsSubscribeModeT.MDS_SUB_MODE_SET,
                data_types) is False:
            print("... 订阅上海股票行情失败!")
            # 返回大于0的值, 表示需要继续执行默认的 OnConnect 回调处理
            return 1

        if self.mds_api.subscribe_by_string(
                channel, None, None,
                eMdsExchangeIdT.MDS_EXCH_SSE,
                eMdsMdProductTypeT.MDS_MD_PRODUCT_TYPE_INDEX,
                eMdsSubscribeModeT.MDS_SUB_MODE_APPEND,
                data_types) is False:
            print("... 订阅上海指数行情失败!")
            # 返回大于0的值, 表示需要继续执行默认的 OnConnect 回调处理
            return 1

        if self.mds_api.subscribe_by_string(
                channel, None, None,
                eMdsExchangeIdT.MDS_EXCH_SSE,
                eMdsMdProductTypeT.MDS_MD_PRODUCT_TYPE_OPTION,
                eMdsSubscribeModeT.MDS_SUB_MODE_APPEND,
                data_types) is False:
            print("... 订阅上海期权行情失败!")
            # 返回大于0的值, 表示需要继续执行默认的 OnConnect 回调处理
            return 1

        if self.mds_api.subscribe_by_string(
                channel, None, None,
                eMdsExchangeIdT.MDS_EXCH_SZSE,
                eMdsMdProductTypeT.MDS_MD_PRODUCT_TYPE_STOCK,
                eMdsSubscribeModeT.MDS_SUB_MODE_APPEND,
                data_types) is False:
            print("... 订阅深圳股票行情失败!")
            # 返回大于0的值, 表示需要继续执行默认的 OnConnect 回调处理
            return 1

        if self.mds_api.subscribe_by_string(
                channel, None, None,
                eMdsExchangeIdT.MDS_EXCH_SZSE,
                eMdsMdProductTypeT.MDS_MD_PRODUCT_TYPE_INDEX,
                eMdsSubscribeModeT.MDS_SUB_MODE_APPEND,
                data_types) is False:
            print("... 订阅深圳指数行情失败!")
            # 返回大于0的值, 表示需要继续执行默认的 OnConnect 回调处理
            return 1

        if self.mds_api.subscribe_by_string(
                channel, None, None,
                eMdsExchangeIdT.MDS_EXCH_SZSE,
                eMdsMdProductTypeT.MDS_MD_PRODUCT_TYPE_OPTION,
                eMdsSubscribeModeT.MDS_SUB_MODE_APPEND,
                data_types) is False:
            print("... 订阅深圳期权行情失败!")
            # 返回大于0的值, 表示需要继续执行默认的 OnConnect 回调处理
            return 1

        print("... 订阅全市场行情成功! channel_tag[{}]".format(
            channel.pChannelCfg.contents.channelTag.decode()))
        return 0

    def __sample_subscribe_by_query(self,
            channel: MdsAsyncApiChannelT) -> int:
        """
        连接完成后, 通过查询证券静态信息来订阅行情样例展示 (仅供参考)

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
        """
        data_types = eMdsSubscribeDataTypeT.MDS_SUB_DATA_TYPE_L2_SNAPSHOT \
            | eMdsSubscribeDataTypeT.MDS_SUB_DATA_TYPE_L2_ORDER \
            | eMdsSubscribeDataTypeT.MDS_SUB_DATA_TYPE_L2_SSE_ORDER \
            | eMdsSubscribeDataTypeT.MDS_SUB_DATA_TYPE_L2_TRADE

        qry_filter: MdsQryStockStaticInfoListFilterT = \
            MdsQryStockStaticInfoListFilterT()

        # 依次订阅 (1-股票, 2-债券, 3-ETF, 4-基金) 的L2快照行情与L2逐笔行情
        for security_type in (1, 2, 3, 4):
            qry_filter.exchId = 0
            qry_filter.oesSecurityType = security_type
            qry_filter.subSecurityType = 0

            if security_type == 1:
                sub_mode: int = eMdsSubscribeModeT.MDS_SUB_MODE_BATCH_BEGIN
            elif security_type == 4:
                sub_mode: int = eMdsSubscribeModeT.MDS_SUB_MODE_BATCH_END
            else:
                sub_mode: int = eMdsSubscribeModeT.MDS_SUB_MODE_BATCH_APPEND

            ret = self.mds_api.subscribe_by_query(
                channel, sub_mode, data_types, qry_filter)
            if ret < 0:
                print("... 查询或订阅行情失败! ret[{}]".format(ret))
                # 返回大于0的值, 表示需要继续执行默认的 OnConnect 回调处理
                return 1

        print("... 通过查询证券静态信息订阅行情成功! channel_tag[{}]".format(
            channel.pChannelCfg.contents.channelTag.decode()))
        return 0

    def __sample_subscribe_on_connect(self,
            channel: MdsAsyncApiChannelT,
            user_info: Any) -> int:
        """
        连接完成后, 行情订阅的样例展示 (仅供参考)

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            user_info (Any): [用户回调参数]
        """
        # @note 提示:
        # - 只是出于演示的目的才如此处理, 实盘程序根据需要自行实现
        if user_info == "subscribe_by_query":
            # 通过查询证券静态信息来订阅行情
            return self.__sample_subscribe_by_query(channel)

        elif user_info == "subscribe_all":
            # 订阅全市场行情
            return self.__sample_subscribe_all(channel)

        elif user_info == "subscribe_market_data":
            # 发送证券行情实时订阅请求
            return self.__sample_subscribe_market_data(channel)

        elif user_info == "subscribe_by_string_and_prefixes":
            # 通过证券代码前缀订阅行情
            return self.__sample_subscribe_by_string_and_prefixes(channel)

        elif user_info == "subscribe_nothing_on_connect":
            # 连接完成后, 不订阅任何行情数据
            return self.mds_api.subscribe_nothing_on_connect(channel)

        elif user_info == "subscribe_by_cfg":
            # 连接完成后, 根据配置文件中的参数, 订阅行情数据
            return self.mds_api.default_on_connect(channel)

        else:
            # 默认连接完成后, 根据配置文件中的参数, 订阅行情数据
            return self.mds_api.default_on_connect(channel)

    def on_connect(self,
            channel: MdsAsyncApiChannelT,
            user_info: Any) -> int:
        """
        异步API线程连接或重新连接完成后的回调函数

        Args:
            channel (MdsAsyncApiChannelT): [行情订阅通道]
            user_info (Any): [用户回调参数]
        """
        print("... on_connect! channel_tag[{}], user_info[{}]".format(
            channel.pChannelCfg.contents.channelTag.decode(), user_info))

        # 返回值说明:
        # - 返回大于0的值, 表示需要继续执行默认的 OnConnect 回调处理
        #   - 对于行情订阅通道, 将使用配置文件中的订阅参数订阅回报
        # - 若返回0, 表示已经处理成功
        #   - 包括行情订阅通道的数据订阅操作也需要显式的调用并执行成功, 将不再执行默认的回调处理
        # - 返回小于0的值, 处理失败, 异步API将中止运行
        return self.__sample_subscribe_on_connect(channel, user_info)

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
        err_code = self.mds_api.get_last_error()

        print("... on_connect_failed! err_code[{}], err_msg[{}], "
                "channel_tag[{}], user_info[{}]".format(
            err_code, self.mds_api.get_error_msg(err_code),
            channel.pChannelCfg.contents.channelTag.decode(), user_info))

        return 0

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
        print("... on_disconnect! channel_tag[{}], user_info[{}]".format(
            channel.pChannelCfg.contents.channelTag.decode(), user_info))

        return 0


    # ===================================================================
    # MDS行情订阅接口对应的回调函数
    # ===================================================================

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
        print("... recv Lv2 TickTrade: "
                "msgId[{}], "
                "exchId[{}], "
                "SecurityID[{}], "
                "TradePrice[{}], "
                "TradeQty[{}],"
                "user_info[{}]".format(
            msg_head.msgId,
            msg_body.exchId,
            msg_body.SecurityID.decode(),
            msg_body.TradePrice,
            msg_body.TradeQty,
            user_info))

        return 0

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
        print("... recv Lv2 TickOrder: "
                "msgId[{}], "
                "exchId[{}], "
                "SecurityID[{}], "
                "Price[{}], "
                "OrderQty[{}], "
                "user_info[{}]".format(
            msg_head.msgId,
            msg_body.exchId,
            msg_body.SecurityID.decode(),
            msg_body.Price,
            msg_body.OrderQty,
            user_info))

        return 0

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
        print("... recv Lv2 Snapshot: "
                "msgId[{}], "
                "exchId[{}], "
                "SecurityID[{}], "
                "TradePx[{}], "
                "IOPV[{}], "
                "NAV[{}], "
                "TotalLongPosition[{}], "
                "BondWeightedAvgPx[{}], "
                "BondAuctionTradePx[{}], "
                "BondAuctionVolumeTraded[{}], "
                "BidPrice1~10[{}, {}, ..., {}], "
                "OfferPrice1~10[{}, {}, ..., {}], "
                "user_info[{}]".format(
            msg_head.msgId,
            msg_body.head.exchId,
            msg_body.l2Stock.SecurityID.decode(),
            msg_body.l2Stock.TradePx,
            msg_body.l2Stock.IOPV,
            msg_body.l2Stock.NAV,
            msg_body.l2Stock.TotalLongPosition,
            msg_body.l2Stock.BondWeightedAvgPx,
            msg_body.l2Stock.BondAuctionTradePx,
            msg_body.l2Stock.BondAuctionVolumeTraded,
            msg_body.l2Stock.BidLevels[0].Price,
            msg_body.l2Stock.BidLevels[1].Price,
            msg_body.l2Stock.BidLevels[9].Price,
            msg_body.l2Stock.OfferLevels[0].Price,
            msg_body.l2Stock.OfferLevels[1].Price,
            msg_body.l2Stock.OfferLevels[9].Price,
            user_info))

        return 0

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
        print("... recv Lv2 Best Orders Snapshot: "
                "msgId[{}], "
                "exchId[{}], "
                "SecurityID[{}], "
                "NoBidOrders[{}], "
                "NoOfferOrders[{}], "
                "BidOrderQty1~10[{}, {}, ..., {}], "
                "OfferOrderQty1~10[{}, {}, ..., {}], "
                "user_info[{}]".format(
            msg_head.msgId,
            msg_body.head.exchId,
            msg_body.l2BestOrders.SecurityID.decode(),
            msg_body.l2BestOrders.NoBidOrders,
            msg_body.l2BestOrders.NoOfferOrders,
            msg_body.l2BestOrders.BidOrderQty[0],
            msg_body.l2BestOrders.BidOrderQty[1],
            msg_body.l2BestOrders.BidOrderQty[9],
            msg_body.l2BestOrders.OfferOrderQty[0],
            msg_body.l2BestOrders.OfferOrderQty[1],
            msg_body.l2BestOrders.OfferOrderQty[9],
            user_info))

        return 0

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
        print("... recv Lv2 Market Overview: "
                "msgId[{}], "
                "exchId[{}], "
                "OrigDate[{}], "
                "OrigTime[{}], "
                "user_info[{}]".format(
            msg_head.msgId,
            msg_body.head.exchId,
            msg_body.l2MarketOverview.OrigDate,
            msg_body.l2MarketOverview.OrigTime,
            user_info))

        return 0

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

        print("... recv Lv1 Snapshot: "
                "msgId[{}], "
                "exchId[{}], "
                "SecurityID[{}], "
                "TradePx[{}], "
                "IOPV[{}], "
                "NAV[{}], "
                "TotalLongPosition[{}], "
                "BondWeightedAvgPx[{}], "
                "BondAuctionTradePx[{}], "
                "BondAuctionVolumeTraded[{}], "
                "BidPrice1~5[{}, {}, ..., {}], "
                "OfferPrice1~5[{}, {}, ..., {}], "
                "user_info[{}]".format(
            msg_head.msgId,
            msg_body.head.exchId,
            msg_body.stock.SecurityID.decode(),
            msg_body.stock.TradePx,
            msg_body.stock.IOPV,
            msg_body.stock.NAV,
            msg_body.stock.TotalLongPosition,
            msg_body.stock.BondWeightedAvgPx,
            msg_body.stock.BondAuctionTradePx,
            msg_body.stock.BondAuctionVolumeTraded,
            msg_body.stock.BidLevels[0].Price,
            msg_body.stock.BidLevels[1].Price,
            msg_body.stock.BidLevels[4].Price,
            msg_body.stock.OfferLevels[0].Price,
            msg_body.stock.OfferLevels[1].Price,
            msg_body.stock.OfferLevels[4].Price,
            user_info))

        return 0

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

        print("... recv Index Snapshot: "
                "msgId[{}], "
                "exchId[{}], "
                "SecurityID[{}], "
                "OpenPx[{}], "
                "HighPx[{}], "
                "LowPx[{}], "
                "TradePx[{}], "
                "ClosePx[{}], "
                "user_info[{}]".format(
            msg_head.msgId,
            msg_body.head.exchId,
            msg_body.index.SecurityID.decode(),
            msg_body.index.OpenPx,
            msg_body.index.HighPx,
            msg_body.index.LowPx,
            msg_body.index.TradePx,
            msg_body.index.ClosePx,
            user_info))

        return 0

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

        print("... recv Option Snapshot: "
                "msgId[{}], "
                "exchId[{}], "
                "SecurityID[{}], "
                "TradePx[{}], "
                "BidPrice1~5[{}, {}, ..., {}], "
                "OfferPrice1~5[{}, {}, ..., {}], "
                "user_info[{}]".format(
            msg_head.msgId,
            msg_body.head.exchId,
            msg_body.option.SecurityID.decode(),
            msg_body.option.TradePx,
            msg_body.option.BidLevels[0].Price,
            msg_body.option.BidLevels[1].Price,
            msg_body.option.BidLevels[4].Price,
            msg_body.option.OfferLevels[0].Price,
            msg_body.option.OfferLevels[1].Price,
            msg_body.option.OfferLevels[4].Price,
            user_info))

        return 0

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
        if msg_body.switches[1].switchFlag:
            if msg_body.switches[1].switchStatus:
                switch_status1: str = "Enabled"
            else:
                switch_status1: str = "Disabled"
        else:
            switch_status1: str = "Unused"

        if msg_body.switches[33].switchFlag:
            if msg_body.switches[33].switchStatus:
                switch_status33: str = "Enabled"
            else:
                switch_status33: str = "Disabled"
        else:
            switch_status33: str = "Unused"

        print("... recv Szse Security Status: "
                "msgId[{}], "
                "exchId[{}], "
                "SecurityID[{}], "
                "NoSwitch[{}], "
                "switch1[{}], ..., switch33[{}], "
                "user_info[{}]".format(
            msg_head.msgId,
            msg_body.exchId,
            msg_body.SecurityID.decode(),
            msg_body.NoSwitch,
            switch_status1, switch_status33,
            user_info))

        return 0

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
        print("... recv Sse Trading Session Status: "
                "msgId[{}], "
                "exchId[{}], "
                "TradingSessionID[{}], "
                "user_info[{}]".format(
            msg_head.msgId,
            msg_body.exchId,
            msg_body.TradingSessionID.decode(),
            user_info))

        return 0

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
        print("... recv Tick Channel Heart Beat: "
                "msgId[{}], "
                "exchId[{}], "
                "ChannelNo[{}], "
                "ApplLastSeqNum[{}], "
                "EndOfChannel[{}], "
                "user_info[{}]".format(
            msg_head.msgId,
            msg_body.exchId,
            msg_body.ChannelNo,
            msg_body.ApplLastSeqNum,
            msg_body.EndOfChannel,
            user_info))

        return 0

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
        if msg_head.status == 0:
            print("... recv subscribe-request response, subscribed successfully: "
                    "sseStock[{}], sseIndex[{}], sseOption[{}], "
                    "szseStock[{}], szseIndex[{}], szseOption[{}], "
                    "user_info[{}]".format(
                msg_body.sseStockSubscribed,
                msg_body.sseIndexSubscribed,
                msg_body.sseOptionSubscribed,

                msg_body.szseStockSubscribed,
                msg_body.szseIndexSubscribed,
                msg_body.szseOptionSubscribed,

                user_info))

        else:
            print("... recv subscribe-request response, subscribed failed: "
                    "err_code[{}{}], user_info[{}]".format(
                msg_head.status, msg_head.detailStatus, user_info))

        return 0

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
        print("... recv Test Request Rsp: "
                "msgId[{}], "
                "origSendTime[{}], "
                "respTime[{}], "
                "user_info[{}]".format(
            msg_head.msgId,
            msg_body.origSendTime.decode(),
            msg_body.respTime.decode(),
            user_info))

        return 0

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
        print("... recv Heart Beat: msgId[{}]".format(msg_head.msgId))
        
        return 0

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
        print("... recv Compressed Packets: msgId[{}]".format(msg_head.msgId))

        return 0
    # -------------------------


    # ===================================================================
    # MDS查询接口对应的回调函数
    # ===================================================================

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
        if msg_body.switches[1].switchFlag:
            if msg_body.switches[1].switchStatus:
                switch_status1: str = "Enabled"
            else:
                switch_status1: str = "Disabled"
        else:
            switch_status1: str = "Unused"

        if msg_body.switches[33].switchFlag:
            if msg_body.switches[33].switchStatus:
                switch_status33: str = "Enabled"
            else:
                switch_status33: str = "Disabled"
        else:
            switch_status33: str = "Unused"

        print("... query Security Status: "
                "exchId[{}], "
                "SecurityID[{}], "
                "NoSwitch[{}], "
                "switch1[{}], ..., switch33[{}], "
                "user_info[{}]".format(
            msg_body.exchId,
            msg_body.SecurityID.decode(),
            msg_body.NoSwitch,
            switch_status1, switch_status33,
            user_info))

        return 0

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
        print("... query Trd Session Status: "
                "exchId[{}], "
                "TradingSessionID[{}], "
                "user_info[{}]".format(
            msg_body.exchId,
            msg_body.TradingSessionID.decode(),
            user_info))

        return 0

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
        print("... query Lv1 Mkt Data Snapshot: "
                "exchId[{}], "
                "SecurityID[{}], "
                "TradePx[{}], "
                "IOPV[{}], "
                "NAV[{}], "
                "TotalLongPosition[{}], "
                "BondWeightedAvgPx[{}], "
                "BondAuctionTradePx[{}], "
                "BondAuctionVolumeTraded[{}], "
                "BidPrice1~5[{}, {}, ..., {}], "
                "OfferPrice1~5[{}, {}, ..., {}], "
                "user_info[{}]".format(
            msg_body.head.exchId,
            msg_body.stock.SecurityID.decode(),
            msg_body.stock.TradePx,
            msg_body.stock.IOPV,
            msg_body.stock.NAV,
            msg_body.stock.TotalLongPosition,
            msg_body.stock.BondWeightedAvgPx,
            msg_body.stock.BondAuctionTradePx,
            msg_body.stock.BondAuctionVolumeTraded,
            msg_body.stock.BidLevels[0].Price,
            msg_body.stock.BidLevels[1].Price,
            msg_body.stock.BidLevels[4].Price,
            msg_body.stock.OfferLevels[0].Price,
            msg_body.stock.OfferLevels[1].Price,
            msg_body.stock.OfferLevels[4].Price,
            user_info))

        return 0

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
        print("... query Snapshot List: "
                "exchId[{}], "
                "SecurityID[{}], "
                "TradePx[{}], "
                "IOPV[{}], "
                "NAV[{}], "
                "TotalLongPosition[{}], "
                "BondWeightedAvgPx[{}], "
                "BondAuctionTradePx[{}], "
                "BondAuctionVolumeTraded[{}], "
                "BidPrice1~5[{}, {}, ..., {}], "
                "OfferPrice1~5[{}, {}, ..., {}], "
                "QryCursor.seqNo[{}], "
                "QryCursor.isEnd[{}], "
                "QryCursor.userInfo[{}], "
                "user_info[{}]".format(
            msg_body.head.exchId,
            msg_body.stock.SecurityID.decode(),
            msg_body.stock.TradePx,
            msg_body.stock.IOPV,
            msg_body.stock.NAV,
            msg_body.stock.TotalLongPosition,
            msg_body.stock.BondWeightedAvgPx,
            msg_body.stock.BondAuctionTradePx,
            msg_body.stock.BondAuctionVolumeTraded,
            msg_body.stock.BidLevels[0].Price,
            msg_body.stock.BidLevels[1].Price,
            msg_body.stock.BidLevels[4].Price,
            msg_body.stock.OfferLevels[0].Price,
            msg_body.stock.OfferLevels[1].Price,
            msg_body.stock.OfferLevels[4].Price,
            qry_cursor.seqNo,
            qry_cursor.isEnd,
            qry_cursor.userInfo,
            user_info))

        return 0

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
        print("... query Stock Static Info List: "
                "exchId[{}], "
                "securityId[{}], "
                "securityName[{}], "
                "QryCursor.seqNo[{}], "
                "QryCursor.isEnd[{}], "
                "QryCursor.userInfo[{}], "
                "user_info[{}]]".format(
            msg_body.exchId,
            msg_body.securityId.decode(),
            msg_body.securityName.decode(),
            qry_cursor.seqNo,
            qry_cursor.isEnd,
            qry_cursor.userInfo,
            user_info))

        return 0

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
        print("... query Option Static Info List: "
                "exchId[{}], "
                "securityId[{}], "
                "securityName[{}], "
                "QryCursor.seqNo[{}], "
                "QryCursor.isEnd[{}], "
                "QryCursor.userInfo[{}], "
                "user_info[{}]]".format(
            msg_body.exchId,
            msg_body.securityId.decode(),
            msg_body.securityName.decode(),
            qry_cursor.seqNo,
            qry_cursor.isEnd,
            qry_cursor.userInfo,
            user_info))

        return 0
    # -------------------------


    # ===================================================================
    # MDS逐笔数据重传结果应答的回调处理函数
    # ===================================================================

    def on_tick_resend_rsp(self,
            channel: MdsAsyncApiChannelT,
            msg_head: SMsgHeadT,
            msg_body: MdsMktRspMsgBodyT,
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
        if msg_head.msgId == eMdsMsgTypeT.MDS_MSGTYPE_L2_TRADE:
            # 处理Level2逐笔成交消息 @see MdsL2TradeT
            print("... recv Resend TickTrade: "
                    "exchId[{}], "
                    "SecurityID[{}], "
                    "TradePrice[{}], "
                    "TradeQty[{}], "
                    "qryCursor.seqNo[{}], "
                    "qryCursor.isEnd[{}], "
                    "qryCursor.userInfo[{}], "
                    "user_info[{}]".format(
                msg_body.trade.exchId,
                msg_body.trade.SecurityID.decode(),
                msg_body.trade.TradePrice,
                msg_body.trade.TradeQty,
                qry_cursor.seqNo,
                qry_cursor.isEnd,
                qry_cursor.userInfo,
                user_info))

        elif msg_head.msgId == eMdsMsgTypeT.MDS_MSGTYPE_L2_ORDER \
                or msg_head.msgId == eMdsMsgTypeT.MDS_MSGTYPE_L2_SSE_ORDER:
            # 处理Level2逐笔委托消息 @see MdsL2OrderT
            print("... recv Resend TickOrder: "
                    "exchId[{}], "
                    "SecurityID[{}], "
                    "Price[{}], "
                    "OrderQty[{}], "
                    "qryCursor.seqNo[{}], "
                    "qryCursor.isEnd[{}], "
                    "qryCursor.userInfo[{}], "
                    "user_info[{}]".format(
                msg_body.order.exchId,
                msg_body.order.SecurityID.decode(),
                msg_body.order.Price,
                msg_body.order.OrderQty,
                qry_cursor.seqNo,
                qry_cursor.isEnd,
                qry_cursor.userInfo,
                user_info))

        elif msg_head.msgId == eMdsMsgTypeT.MDS_MSGTYPE_TICK_RESEND_REQUEST:
            # 处理逐笔数据重传请求的应答消息 @see MdsTickResendRequestRspT
            print("... recv Resend TickResendRsp: "
                    "exchId[{}], "
                    "isSseOldTickOrder[{}], "
                    "channelNo[{}], "
                    "beginApplSeqNum[{}], "
                    "endApplSeqNum[{}], "
                    "resendMsgCount[{}], "
                    "resendStatus[{}], "
                    "userInfo.u64[{}], "
                    "qryCursor.seqNo[{}], "
                    "qryCursor.isEnd[{}], "
                    "qryCursor.userInfo[{}],"
                    "user_info[{}]".format(
                msg_body.tickResendRsp.exchId,
                msg_body.tickResendRsp.isSseOldTickOrder,
                msg_body.tickResendRsp.channelNo,
                msg_body.tickResendRsp.beginApplSeqNum,
                msg_body.tickResendRsp.endApplSeqNum,
                msg_body.tickResendRsp.resendMsgCount,
                msg_body.tickResendRsp.resendStatus,
                msg_body.tickResendRsp.userInfo.u64,
                qry_cursor.seqNo,
                qry_cursor.isEnd,
                qry_cursor.userInfo,
                user_info))

        else:
            print("Invalid message type, Ignored! msgId[{}]".format(
                msg_head.msgId))

        return 0
    # -------------------------


    # ===================================================================
    # MDS密码修改结果应答的回调处理函数
    # ===================================================================

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
        print("... recv Change Password Rsp: "
                "encryptMethod[{}], "
                "username[{}], "
                "userInfo[{}], "
                "transDate[{}], "
                "transTime[{}], "
                "rejReason[{}]".format(
            msg_body.encryptMethod,
            msg_body.username,
            msg_body.userInfo,
            msg_body.transDate,
            msg_body.transTime,
            msg_body.rejReason))

        return 0
    # -------------------------
