# -*- coding: utf-8 -*-
"""
行情api使用样例 (查询相关)
"""
import sys
from typing import Any

sys.path.append('../')

"""
@note 请从 quote_api 中引入行情API相关的结构体, 否则兼容性将无法得到保证
"""
from quote_api import (
    MdsClientApi, MdsAsyncApiChannelT,

    MDSAPI_CFG_DEFAULT_SECTION,
    MDSAPI_CFG_DEFAULT_KEY_TCP_ADDR
)

from quote_sample.my_spi import (
    MdsClientMySpi
)


def main() -> None:
    """
    主函数
    """
    config_file_name: str = './mds_client_sample.conf'

    # 1. 创建行情API实例
    api: MdsClientApi = MdsClientApi()
    # 2. 创建自定义的SPI回调实例
    spi: MdsClientMySpi = MdsClientMySpi()

    # 3. 创建行情API运行时环境
    if api.create_context(config_file_name) is False:
        return

    # 4. 将SPI实例注册至API实例中, 以达到通过自定义的回调函数收取行情数据的效果
    if api.register_spi(spi) is False:
        api.release()
        return

    # 5. 添加TCP上海行情快照通道
    # - @note 仅供参考, 请结合 MdsClientMySpi.on_connect 函数实现, 自定义user_info取值
    user_info :Any = "subscribe_nothing_on_connect"

    tcp_channel: MdsAsyncApiChannelT = api.add_channel_from_file(
        "tcp_channel",
        config_file_name,
        MDSAPI_CFG_DEFAULT_SECTION,
        MDSAPI_CFG_DEFAULT_KEY_TCP_ADDR,
        user_info, None, True)
    if not tcp_channel:
        api.release()
        return

    # 6. 启动行情API接口
    if api.start() is False:
        api.release()
        return

    # 7. 执行行情API查询接口
    # - @note 通过 MdsClientMySpi.on_qry_xxxx 回调函数, 接收对应的查询应答信息
    print("\n当前MdsApi版本号:")
    print("... MdsApi Version[{}]".format(api.get_api_version()))

    print("\n开始查询证券行情快照:")
    api.query_mkt_data_snapshot(
        exchange_id=1, product_type=1, instr_id=600000)

    print("\n开始批量查询行情快照信息:")
    api.query_snapshot_list(
        security_list="600000,000001.SH,000001.SZ,000002")

    print("\n开始查询(上证)市场状态:")
    api.query_trd_session_status(
        exchange_id=1, product_type=1)

    print("\n开始查询(深圳)证券实时状态:")
    api.query_security_status(
        exchange_id=2, product_type=1, instr_id=1)

    print("\n开始批量查询查询证券(股票/债券/基金)静态信息列表:")
    api.query_stock_static_info_list(
        security_list='600000,600010.SH,000001,000002.SZ')

    print("\n开始批量查询期权合约静态信息列表:")
    api.query_option_static_info_list(security_list='')

    print("\n行情API运行结束, 即将退出!\n")

    # 8. 释放资源
    api.release()

if __name__ == "__main__":
    main()
