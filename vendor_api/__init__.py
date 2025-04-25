import os
import sys
import platform
from pathlib import Path

_base = Path(__file__).parent.resolve()
lib_dir = _base / "libs" / "win64"  # Windows 平台请保留 win64，如果你是 Linux 改为 linux64

# 加载 DLL 到环境变量
if platform.system() == "Windows":
    os.environ["PATH"] = str(lib_dir) + ";" + os.environ.get("PATH", "")
else:
    os.environ["LD_LIBRARY_PATH"] = str(lib_dir) + ":" + os.environ.get("LD_LIBRARY_PATH", "")

# 确保 quote_api 可以被 import
sys.path.append(str(_base))
