from vendor_api.quote_api.mds_api import MdsClientApi
from src.spi.mds_spi_handler import MdsSpiHandler
from pathlib import Path
from typing import List, Optional


class QuantClient:
    def __init__(
        self,
        config_file: str,
        strategies: List,
        subscribe_codes: Optional[list[str]] = None,
        subscribe_config: Optional[dict] = None,
        event_engine=None                # ⭐ 新增
    ) -> None:

        self.config_path = str(Path(config_file).resolve())
        self.strategies = strategies
        self.event_engine = event_engine

        # 初始化行情 API
        self.api = MdsClientApi()
        self.spi = MdsSpiHandler(
            strategy_group=self.strategies,
            subscribe_codes=subscribe_codes or [],
            subscribe_config=subscribe_config or {},
            event_engine=self.event_engine
        )

        # 创建 API 上下文
        if not self.api.create_context(self.config_path):
            raise RuntimeError("❌ 创建行情上下文失败")
        if not self.api.register_spi(self.spi):
            raise RuntimeError("❌ 注册 SPI 失败")

        self.channel = self.api.add_channel_from_file(
            mds_client_spi=self.spi,
            config_file=self.config_path
        )
        if not self.channel:
            raise RuntimeError("❌ 无法连接行情服务器")

    # 启动
    def start(self):
        print("🚀 启动行情接收器 ...")
        if not self.api.start():
            raise RuntimeError("❌ 启动行情失败")
