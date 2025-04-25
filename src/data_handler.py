from pathlib import Path
from datetime import datetime
import csv
import gzip

class MarketDataSaver:
    def __init__(self, compress=False):
        project_root = Path(__file__).resolve().parent.parent
        self.root_dir = project_root / "data" / "snapshot"
        self.compress = compress
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def save_snapshot(self, data: dict):
        code = data.get("SecurityID")
        if not code:
            return

        today = datetime.now().strftime("%Y%m%d")
        filename = f"{today}.csv.gz" if self.compress else f"{today}.csv"
        path = self.root_dir / code / filename
        path.parent.mkdir(parents=True, exist_ok=True)

        file_exists = path.exists()
        open_fn = gzip.open if self.compress else open

        with open_fn(path, mode="at", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)

        print(f"💾 已保存快照至 {path}")
