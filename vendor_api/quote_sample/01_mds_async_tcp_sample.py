# -*- coding: utf-8 -*-
"""
行情api使用样例 (TCP)
"""
import sys
import time

sys.path.append('../')

"""
@note 请从 quote_api 中引入行情API相关的结构体, 否则兼容性将无法得到保证
"""
from quote_api import (
    MdsClientApi, MdsAsyncApiChannelT, MdsApiRemoteCfgT,

    MDSAPI_CFG_DEFAULT_SECTION,
    MDSAPI_CFG_DEFAULT_KEY_TCP_ADDR
)

from quote_sample.my_spi import (
    MdsClientMySpi
)


def tcp_sample_main() -> None:
    """
    TCP行情对接的样例代码
    - 通过不同方式添加多个行情订阅通道, 每个通道订阅不同的行情信息
      - add_channel_from_file
      - add_channel
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

    # 5. 添加多个TCP行情订阅通道
    # - @note 仅供参考, 请结合 MdsClientMySpi.on_connect 函数实现, 自定义user_info取值
    tcp_channel1: MdsAsyncApiChannelT = api.add_channel_from_file(
        "tcp_channel1",
        config_file_name,
        MDSAPI_CFG_DEFAULT_SECTION,
        MDSAPI_CFG_DEFAULT_KEY_TCP_ADDR,
        None, None, True)
    if not tcp_channel1:
        api.release()
        return

    # (出于演示的目的) 再添加两个自定义的通道配置信息
    #
    # @note 只是出于演示的目的才如此处理, 包括以下方面的演示:
    # 1. 从配置文件中加载服务器地址、初始订阅参数等配置信息, 作为配置模版
    # 2. 通过代码改写服务器地址配置、用户名、密码等配置信息
    # 3. 添加多个通道配置到异步API实例中, 异步API会同时对接和管理这些通道
    if True:
        remote_cfg: MdsApiRemoteCfgT = MdsApiRemoteCfgT()

        # 1. 从配置文件中加载服务器地址、初始订阅参数等配置信息, 作为配置模版
        if api.parse_config_from_file(
            config_file_name, MDSAPI_CFG_DEFAULT_SECTION,
            MDSAPI_CFG_DEFAULT_KEY_TCP_ADDR, remote_cfg) is False:
            api.release()
            return

        # 2. 通过代码改写服务器地址配置、用户名、密码等配置信息
        # remote_cfg.username = b"xxxxxx"
        # remote_cfg.password = b"654321"
        # remote_cfg.addrCnt = api.parse_addr_list_string(
        #     "tcp://139.196.228.232:5403, tcp://192.168.0.11:5401",
        #     remote_cfg.addrList)

        # 3. 添加两个通道配置到异步API实例中, 异步API会同时对接和管理这些通道
        tcp_channel2: MdsAsyncApiChannelT = api.add_channel(
            "tcp_channel2", remote_cfg, None, None, True)
        if not tcp_channel2:
            api.release()
            return

        tcp_channel3: MdsAsyncApiChannelT = api.add_channel(
            "tcp_channel3", remote_cfg, None, None, True)
        if not tcp_channel3:
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


def tcp_minimal_sample_main() -> None:
    """
    TCP行情对接的样例代码 (精简版本)
    - 根据配置文件中的内容, 添加一个TCP行情订阅通道
    - 根据配置文件中的内容, 订阅行情数据
    """
    config_file_name: str = './mds_client_sample.conf'

    # 1. 创建行情API实例
    api: MdsClientApi = MdsClientApi(config_file_name)
    # 2. 创建自定义的SPI回调实例
    spi: MdsClientMySpi = MdsClientMySpi()

    # 3. 将SPI实例注册至API实例中, 以达到通过自定义的回调函数收取行情数据的效果
    if api.register_spi(spi, add_default_channel=True) is False:
        return

    # 4. 启动行情API接口
    if api.start() is False:
        return

    # 5. 等待处理结束
    # @note 提示:
    # - 只是出于演示的目的才如此处理, 实盘程序可以根据需要自行实现
    while api.is_api_running() and api.get_total_picked() < 10000:
        time.sleep(0.1)

    print("\n行情API运行结束, 即将退出! totalPicked[{}]\n".format(
        api.get_total_picked()))

    # 6. 释放资源
    api.release()

if __name__ == "__main__":
    # TCP行情对接的样例代码 (精简版本)
    # - 根据配置文件中的内容, 添加一个TCP行情订阅通道
    # - 根据配置文件中的内容, 订阅行情数据
    tcp_minimal_sample_main()

    # TCP行情对接的样例代码 (多通道)
    # - 通过不同方式添加多个行情订阅通道, 每个通道订阅不同的行情信息
    #   - add_channel_from_file
    #   - add_channel
    # tcp_sample_main()
