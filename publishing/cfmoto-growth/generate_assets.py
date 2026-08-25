#!/usr/bin/env python3
import io
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

import requests

SOURCE_ZIP = "https://at.adobe.com/brag0vYp9LQa5QJT"


def main():
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)

    response = requests.get(SOURCE_ZIP, timeout=120, allow_redirects=True)
    response.raise_for_status()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
            zf.extractall(tmp_path)

        image_dir = tmp_path / "images"
        images = sorted(image_dir.glob("*.png"))
        if len(images) != 20:
            raise RuntimeError(f"Expected 20 images, got {len(images)}")

        for index, src in enumerate(images, start=1):
            dst = out_dir / f"chart-{index:02d}.webp"
            shutil.copyfile(src, dst)

        shutil.copyfile(images[2], out_dir / "cover.webp")


if __name__ == "__main__":
    main()
