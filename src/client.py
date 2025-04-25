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
        subscribe_config: Optional[dict] = None  # ✅ 新增字段
    ) -> None:
        """
        :param config_file: 配置文件路径（INI 文件）
        :param strategies: 已实例化的策略类列表（每个必须实现 on_snapshot）
        :param subscribe_codes: 股票代码列表（可选）
        :param subscribe_config: 订阅配置（包含代码、数据类型、交易所等）
        """
        self.config_path = str(Path(config_file).resolve())
        self.strategies = strategies

        # 初始化行情 API
        self.api = MdsClientApi()
        self.spi = MdsSpiHandler(
            strategy_group=self.strategies,
            subscribe_codes=subscribe_codes or [],
            subscribe_config=subscribe_config or {}  # ✅ 传入完整订阅配置
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

    def start(self):
        print("🚀 启动行情接收器 ...")
        if not self.api.start():
            raise RuntimeError("❌ 启动行情失败")
