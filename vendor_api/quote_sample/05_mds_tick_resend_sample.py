# -*- coding: utf-8 -*-
"""
行情api使用样例 (逐笔数据重传)
"""
import sys
from typing import Any

sys.path.append('../')

"""
@note 请从 quote_api 中引入行情API相关的结构体, 否则兼容性将无法得到保证
"""
from quote_api import (
    MdsClientApi, MdsAsyncApiChannelT, MdsTickResendRequestReqT,

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
    # - @note 通过 MdsClientMySpi.on_tick_resend_rsp 回调函数, 接收对应的逐笔数据重传应答信息

    print("\n当前MdsApi版本号:")
    print("... MdsApi Version[{}]".format(api.get_api_version()))

    # 1. send_tick_resend_request 接口使用样例
    print("\n发送逐笔数据重传请求:")
    print("... recv msg count[{}]".format(
        api.send_tick_resend_request(
            exchange_id = 1,
            channel_no = 1,
            begin_appl_seq_num = 1,
            end_appl_seq_num = 100,
            user_info = "send_tick_resend_request")))

    # 2. send_tick_resend_request2 接口使用样例
    tick_resend_req: MdsTickResendRequestReqT = MdsTickResendRequestReqT()
    tick_resend_req.exchId = 1
    tick_resend_req.channelNo = 1
    tick_resend_req.beginApplSeqNum = 10000
    tick_resend_req.endApplSeqNum = 10100
    tick_resend_req.userInfo.u64 = 2

    print("\n发送逐笔数据重传请求2:")
    print("... recv msg count[{}]".format(
        api.send_tick_resend_request2(
            tick_resend_req=tick_resend_req,
            user_info="send_tick_resend_request2")))

    # 3. send_tick_resend_request_hugely 接口使用样例
    tick_resend_hugely_req: MdsTickResendRequestReqT = MdsTickResendRequestReqT()
    tick_resend_hugely_req.exchId = 2
    tick_resend_hugely_req.channelNo = 2031
    tick_resend_hugely_req.beginApplSeqNum = 20000
    tick_resend_hugely_req.endApplSeqNum = 20100
    tick_resend_hugely_req.userInfo.u64 = 3

    print("\n发送超大的逐笔数据重传请求:")
    print("... recv msg count[{}]".format(
        api.send_tick_resend_request_hugely(
            tick_resend_req=tick_resend_hugely_req,
            time_out_ms=0,
            user_info="send_tick_resend_request_hugely")))


    print("\n行情API运行结束, 即将退出!\n")

    # 8. 释放资源
    api.release()

if __name__ == "__main__":
    main()
