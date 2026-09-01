#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import quote
import io
import json
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

SOURCE_PATH = "专题/成熟企业的价值创造/05_内容制作/深度文章/01_文章母稿/松下为什么从一家伟大的公司变成了一笔平庸的投资_v03_2026-08-29.md"
SOURCE_URL = "https://raw.githubusercontent.com/richardsun1990/dupontmaster-research-workbench/main/" + quote(SOURCE_PATH)

out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assets")
out_dir.mkdir(parents=True, exist_ok=True)
project_dir = out_dir.parent

# 1) 下载并规范化本次发布图片，供工作流本地校验。
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

# 2) 正式发布前从研究仓库 main 回读最终稿，确保官网不是旧副本。
source_response = requests.get(SOURCE_URL, timeout=60)
source_response.raise_for_status()
article = source_response.text.strip()

# 3) 只插入用户已确认的年代配图，不改写研究正文观点。
insertions = [
    (
        "1918年，23岁的松下幸之助与妻子、妻弟在大阪创办松下电气器具制作所。",
        "\n\n![创业与起步｜1918–1950s]({{image:startup.webp}})",
    ),
    (
        "战后日本经济高速增长，居民收入快速提高，家庭电气化全面普及。电视、冰箱、洗衣机、空调从少数家庭的奢侈品，逐渐变成普通家庭的标配。",
        "\n\n![制造黄金时代｜1950s–1970s]({{image:golden-manufacturing.webp}})",
    ),
    (
        "家电品类越来越多，就向电机、电池、零部件延伸。",
        "\n\n![全球化扩张｜1970s–1980s]({{image:global-expansion.webp}})",
    ),
    (
        "1989年是一个很有象征意义的节点。",
        "\n\n![品牌转型｜1980s–1990s]({{image:brand-transition.webp}})",
    ),
    (
        "2005年前后，松下在尼崎建设大型等离子面板工厂，随后继续扩大产能。",
        "\n\n![等离子赌注｜2000s]({{image:plasma.webp}})",
    ),
    (
        "2012年，津贺一宏出任社长。",
        "\n\n![转型与当下｜2010s–至今]({{image:modern.webp}})",
    ),
]

for marker, insertion in insertions:
    if marker not in article:
        raise RuntimeError(f"未找到插图锚点：{marker}")
    article = article.replace(marker, marker + insertion, 1)

risk_notice = "免责声明：本文仅为个人研究与思考记录，不构成任何投资建议或证券买卖依据。市场有风险，投资需谨慎。"
if risk_notice not in article:
    article += "\n\n---\n\n" + risk_notice

manifest_path = project_dir / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["markdown"] = article
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"source article loaded from: {SOURCE_URL}")
