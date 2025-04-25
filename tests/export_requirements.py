import subprocess
from pathlib import Path

def export_requirements(output_path="requirements.txt"):
    output_path = Path(output_path).resolve()
    print(f"📦 正在导出依赖列表到: {output_path}")
    try:
        subprocess.run(["pip", "freeze"], stdout=open(output_path, "w"), check=True)
        print("✅ 导出成功！")
    except Exception as e:
        print("❌ 导出失败:", e)

if __name__ == "__main__":
    export_requirements()
