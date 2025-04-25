# scripts/smoke_test.py

import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))  # 关键！

from vendor_api.quote_api.mds_api import MdsClientApi

def main():
    try:
        api = MdsClientApi()
        print("✅ 成功创建 MdsClientApi 实例")
        print("📦 API Version:", api.get_api_version())
    except Exception as e:
        print("❌ 出错了:", e)

if __name__ == "__main__":
    main()
