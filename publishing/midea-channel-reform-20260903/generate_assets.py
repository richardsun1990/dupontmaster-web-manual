#!/usr/bin/env python3
import io, zipfile, urllib.request, json, sys
from pathlib import Path

ZIP_URL = 'https://at.adobe.com/PJMS9LvVntfBsOoF'
MAPPING = {
    "images/image_1788398395_004.png": "cover.webp",
    "images/image_1788398395_003.webp": "chart-01.webp",
    "images/image_1788398395_002.webp": "chart-02.webp",
    "images/image_1788398395_001.webp": "chart-03.webp",
    "images/image_1788398395_006.png": "chart-04.webp",
    "images/image_1788398395_005.png": "chart-05.webp",
    "images/image_1788398395_007.webp": "chart-06.webp",
}

out = Path(sys.argv[1])
project_dir = out.parent
manifest_path = project_dir / "manifest.json"
out.mkdir(parents=True, exist_ok=True)

with urllib.request.urlopen(ZIP_URL, timeout=90) as r:
    payload = r.read()

with zipfile.ZipFile(io.BytesIO(payload)) as zf:
    names = set(zf.namelist())
    expected = set(MAPPING) | {"article.md"}
    missing = sorted(expected - names)
    if missing:
        raise RuntimeError(f"ZIP missing expected files: {missing}")

    for src, dst in MAPPING.items():
        (out / dst).write_bytes(zf.read(src))

    article = zf.read("article.md").decode("utf-8")
    for src, dst in MAPPING.items():
        article = article.replace(f"![图片]({src})", "![图片]({{image:" + dst + "}})")

manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["markdown"] = article.strip()
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

placeholders = ["{{image:" + name + "}}" for name in manifest["assets"]]
missing_placeholders = [p for p in placeholders if p not in article]
if missing_placeholders:
    raise RuntimeError(f"Article missing placeholders: {missing_placeholders}")
print(f"prepared {len(MAPPING)} user-supplied assets and markdown image placeholders")
