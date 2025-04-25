
from vendor_api.quote_api.mds_api import MdsClientApi
from vendor_api.quote_sample.my_spi import MdsClientMySpi

class SimplePrintSpi(MdsClientMySpi):
    def on_market_data_snapshot_full_refresh(self, channel, msg_head, msg_body, user_info):
        print(f"📡 快照: {msg_body.stock.SecurityID.decode()} | Px: {msg_body.stock.TradePx} | Time: {msg_body.head.dataTime}")
        return 0

    def on_connect(self, channel, user_info):
        print("✅ 连接成功（测试 SPI）")
        return 0

def main():
    import time
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    config_file = root / "config" / "config_file.ini"

    api = MdsClientApi()
    spi = SimplePrintSpi()

    if not api.create_context(str(config_file)):
        print("❌ 创建上下文失败")
        return

    if not api.register_spi(spi):
        print("❌ 注册 SPI 失败")
        return

    channel = api.add_channel_from_file(
        mds_client_spi=spi,
        config_file=str(config_file)
    )

    if not channel:
        print("❌ 添加通道失败")
        return

    if not api.start():
        print("❌ 启动失败")
        return

    print("🚀 启动完成，等待快照数据...")
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
