# -*- coding: utf-8 -*-
"""
行情api使用样例 (数据订阅)
"""
import sys
import time
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

    ## @note 仅供参考, 请结合 MdsClientMySpi.on_connect 函数实现, 自定义user_info取值

    # 1) 通过查询证券静态信息来订阅行情
    # user_info :Any = "subscribe_by_query"

    # 2) 订阅全市场行情成功
    user_info: Any = "subscribe_all"

    # 3) 不订阅任何行情数据
    # user_info: Any = "subscribe_nothing_on_connect"

    # 4) 根据配置文件中的参数, 订阅行情数据 (默认行为)
    # user_info: Any = "subscribe_by_cfg"
    # -------------------------

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

    # 7. 等待处理结束
    # @note 提示:
    # - 只是出于演示的目的才如此处理, 实盘程序可以根据需要自行实现
    while api.is_api_running() and api.get_total_picked() < 10000:
        time.sleep(0.1)

    print("\n行情API运行结束, 即将退出! totalPicked[{}]\n".format(
        api.get_total_picked()))

    # 8. 释放资源
    api.release()

if __name__ == "__main__":
    main()
