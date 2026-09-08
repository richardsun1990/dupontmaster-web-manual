from pathlib import Path
import sys

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
required = [out / "cover.webp", out / "comparison.webp"]
missing = [str(p) for p in required if not p.exists()]
if missing:
    raise SystemExit("missing assets: " + ", ".join(missing))
print("assets ready")
