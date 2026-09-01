#!/usr/bin/env python3
from pathlib import Path
import io
import sys
import requests
from PIL import Image

URLS = {
    "cover.webp": "https://files.adobe.io/external/uploads/a04c738c-b519-4f88-8262-29140335740c.png",
    "startup.webp": "https://files.adobe.io/external/uploads/c37287d0-5301-433b-a3a0-f34b2de3f79c.png",
    "golden-manufacturing.webp": "https://files.adobe.io/external/uploads/5db00dd2-db9d-4d6d-a9a5-26ab81629c91.png",
    "global-expansion.webp": "https://files.adobe.io/external/uploads/7ed13aef-9703-4f98-8f4c-fe18fa7be794.png",
    "brand-transition.webp": "https://files.adobe.io/external/uploads/5593fa74-6a15-4072-8e82-b8fefaae144b.png",
    "plasma.webp": "https://files.adobe.io/external/uploads/e9e04dab-d8d0-4cdb-ba63-fecec4c46303.png",
    "modern.webp": "https://files.adobe.io/external/uploads/ca076dc7-e9da-4b86-b419-16a7cde46575.png",
}

out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assets")
out_dir.mkdir(parents=True, exist_ok=True)

for name, url in URLS.items():
    response = requests.get(url, timeout=90, allow_redirects=True)
    response.raise_for_status()
    with Image.open(io.BytesIO(response.content)) as image:
        image.load()
        if image.mode != "RGB":
            image = image.convert("RGB")
        if image.width > 1600:
            height = round(image.height * 1600 / image.width)
            image = image.resize((1600, height), Image.Resampling.LANCZOS)
        image.save(out_dir / name, format="WEBP", quality=88, method=6, optimize=True)
    print(f"generated {name}")
