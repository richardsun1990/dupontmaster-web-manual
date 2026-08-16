from pathlib import Path
import shutil
import sys

project_dir = Path(__file__).resolve().parent
out_dir = Path(sys.argv[1])
out_dir.mkdir(parents=True, exist_ok=True)
source = project_dir / "source" / "cover.webp"
if not source.exists():
    raise FileNotFoundError(source)
shutil.copy2(source, out_dir / "cover.webp")
print(f"copied {source} -> {out_dir / 'cover.webp'}")
