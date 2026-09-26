#!/usr/bin/env python3
import hashlib
import io
import json
import os
import re
from pathlib import Path
from urllib.parse import quote

import oss2
import requests
from PIL import Image, ImageOps

manifest_path = Path(os.environ["ASSET_MANIFEST"])
result_path = Path(os.environ["ASSET_RESULT"])
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

ak = os.environ["ALIYUN_OSS_ACCESS_KEY_ID"]
sk = os.environ["ALIYUN_OSS_ACCESS_KEY_SECRET"]
bucket_name = os.environ["ALIYUN_OSS_BUCKET"].strip()
endpoint = os.environ["ALIYUN_OSS_ENDPOINT"].strip().replace("https://", "").replace("http://", "").rstrip("/")
public_base = os.environ.get("ALIYUN_OSS_PUBLIC_BASE_URL", "").strip().rstrip("/")
prefix = os.environ.get("ALIYUN_OSS_PREFIX", "art-theme-navigator/assets").strip().strip("/")

session = requests.Session()
session.headers.update({"User-Agent": "ArtThemeNavigatorAssetMirror/1.0"})
bucket = oss2.Bucket(oss2.Auth(ak, sk), "https://" + endpoint, bucket_name)

def to_webp(url: str) -> tuple[bytes, int, int]:
    response = session.get(url, timeout=120, allow_redirects=True)
    response.raise_for_status()
    with Image.open(io.BytesIO(response.content)) as source:
        image = ImageOps.exif_transpose(source)
        image.load()
        if image.mode in ("RGBA", "LA"):
            canvas = Image.new("RGB", image.size, "white")
            canvas.paste(image.convert("RGB"), mask=image.getchannel("A"))
            image = canvas
        elif image.mode != "RGB":
            image = image.convert("RGB")
        image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
        width, height = image.size
        output = io.BytesIO()
        image.save(output, "WEBP", quality=84, method=6, optimize=True)
        return output.getvalue(), width, height

results = []
for asset in manifest["assets"]:
    raw, width, height = to_webp(asset["source_url"])
    digest = hashlib.sha256(raw).hexdigest()[:12]
    safe_key = re.sub(r"[^a-z0-9-]+", "-", asset["key"].lower()).strip("-")
    object_key = f"{prefix}/{safe_key}-{digest}.webp"
    bucket.put_object(object_key, raw, headers={
        "Content-Type": "image/webp",
        "Cache-Control": "public, max-age=31536000, immutable",
    })
    encoded = "/".join(quote(part, safe="") for part in object_key.split("/"))
    public_url = f"{public_base}/{encoded}" if public_base else f"https://{bucket_name}.{endpoint}/{encoded}"
    results.append({
        **asset,
        "oss_url": public_url,
        "object_key": object_key,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "width": width,
        "height": height,
        "bytes": len(raw),
        "format": "webp",
    })
    print(f"uploaded {asset['key']} -> {public_url}")

result_path.parent.mkdir(parents=True, exist_ok=True)
result_path.write_text(json.dumps({
    "schema_version": 1,
    "purpose": manifest["purpose"],
    "assets": results,
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
