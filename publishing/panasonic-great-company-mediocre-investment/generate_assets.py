#!/usr/bin/env python3
from pathlib import Path
from urllib.parse import quote
import io
import json
import sys
import requests
from PIL import Image, ImageOps, ImageDraw, ImageFont

SOURCE_PATH = "专题/成熟企业的价值创造/05_内容制作/深度文章/01_文章母稿/松下为什么从一家伟大的公司变成了一笔平庸的投资_v03_2026-08-29.md"
SOURCE_URL = "https://raw.githubusercontent.com/richardsun1990/dupontmaster-research-workbench/main/" + quote(SOURCE_PATH)

# Panasonic Holdings 官方历史档案原图。正式发布时统一转存至 DupontMaster 自有 OSS。
OFFICIAL_IMAGES = {
    "startup.webp": (
        "https://holdings.panasonic/content/dam/holdings/global/en/corporate/about/history/chronicle/img/1933-01_01.jpg",
        "FOUNDING | 1933",
    ),
    "golden-manufacturing.webp": (
        "https://holdings.panasonic/content/dam/holdings/global/en/corporate/about/history/chronicle/img/1956-03_03.jpg",
        "MANUFACTURING BOOM | 1950s",
    ),
    "global-expansion.webp": (
        "https://holdings.panasonic/content/dam/holdings/global/en/corporate/about/history/chronicle/img/1959-01_01.jpg",
        "GLOBAL EXPANSION | 1959-1980s",
    ),
    "brand-transition.webp": (
        "https://holdings.panasonic/content/dam/holdings/global/en/corporate/about/history/chronicle/img/2008-01_01.jpg",
        "BRAND TRANSITION | 2008",
    ),
    "plasma.webp": (
        "https://holdings.panasonic/content/dam/holdings/global/en/corporate/about/history/chronicle/img/2005-01.jpg",
        "PLASMA BET | 2000s",
    ),
    "modern.webp": (
        "https://holdings.panasonic/content/dam/holdings/global/en/corporate/about/history/chronicle/img/2014-02_01.jpg",
        "TRANSFORMATION | 2010s-PRESENT",
    ),
}
LOGO_URL = "https://holdings.panasonic/content/dam/holdings/global/en/corporate/brand/history/panasoniclogo_img_pc.png"

out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assets")
out_dir.mkdir(parents=True, exist_ok=True)
project_dir = out_dir.parent

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 DupontMasterPublisher/1.2"})


def download_image(url: str) -> Image.Image:
    r = session.get(url, timeout=90, allow_redirects=True)
    r.raise_for_status()
    img = Image.open(io.BytesIO(r.content))
    img.load()
    return img.convert("RGB")


def cover_crop(img: Image.Image, size=(1600, 900)) -> Image.Image:
    return ImageOps.fit(img, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))


def label_image(img: Image.Image, label: str) -> Image.Image:
    canvas = cover_crop(img)
    draw = ImageDraw.Draw(canvas, "RGBA")
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try:
        font = ImageFont.truetype(font_path, 28)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 24, 14
    x2, y2 = 1570, 870
    x1, y1 = x2 - tw - pad_x * 2, y2 - th - pad_y * 2
    draw.rounded_rectangle((x1, y1, x2, y2), radius=10, fill=(5, 12, 22, 155))
    draw.text((x1 + pad_x, y1 + pad_y - 2), label, fill=(255, 255, 255, 235), font=font)
    return canvas


# 1) 官方历史图 -> 统一横版 + 年代角标。
raw_images = {}
for name, (url, label) in OFFICIAL_IMAGES.items():
    img = download_image(url)
    raw_images[name] = img
    final = label_image(img, label)
    final.save(out_dir / name, "WEBP", quality=88, method=6, optimize=True)
    print(f"generated {name} from Panasonic official archive")

# 2) 封面：1933 工厂与现代 Panasonic 项目左右融合，并自然加入官方 Logo；不放文章标题或图表。
history = cover_crop(raw_images["startup.webp"], (800, 900))
modern = cover_crop(raw_images["modern.webp"], (800, 900))
cover = Image.new("RGB", (1600, 900), "white")
cover.paste(history, (0, 0))
cover.paste(modern, (800, 0))
# 中缝柔和过渡
blend_w = 180
left_strip = cover.crop((800 - blend_w // 2, 0, 800 + blend_w // 2, 900))
mask = Image.new("L", (blend_w, 900))
md = ImageDraw.Draw(mask)
for x in range(blend_w):
    md.line((x, 0, x, 900), fill=int(255 * x / (blend_w - 1)))
old_side = history.crop((800 - blend_w, 0, 800, 900)).resize((blend_w, 900))
new_side = modern.crop((0, 0, blend_w, 900)).resize((blend_w, 900))
transition = Image.composite(new_side, old_side, mask)
cover.paste(transition, (800 - blend_w // 2, 0))

# 官方 Panasonic Logo
logo_resp = session.get(LOGO_URL, timeout=60)
logo_resp.raise_for_status()
logo = Image.open(io.BytesIO(logo_resp.content)).convert("RGBA")
logo.thumbnail((440, 170), Image.Resampling.LANCZOS)
# 给 Logo 一块低调半透明浅底，增强识别但不做海报式装饰
panel = Image.new("RGBA", (logo.width + 54, logo.height + 38), (255, 255, 255, 205))
panel.alpha_composite(logo, (27, 19))
cover_rgba = cover.convert("RGBA")
cover_rgba.alpha_composite(panel, (1600 - panel.width - 54, 52))
cover = cover_rgba.convert("RGB")
cover.save(out_dir / "cover.webp", "WEBP", quality=90, method=6, optimize=True)
print("generated cover.webp from official Panasonic historical + modern imagery")

# 3) 正式发布前从研究仓库 main 回读最终稿，确保官网不是旧副本。
source_response = session.get(SOURCE_URL, timeout=60)
source_response.raise_for_status()
article = source_response.text.strip()

# 4) 插入年代配图，不改写研究正文观点。
insertions = [
    (
        "1918年，23岁的松下幸之助与妻子、妻弟在大阪创办松下电气器具制作所。",
        "\n\n![创业与起步｜1918–1950s]({{image:startup.webp}})\n\n*创业与起步｜1918–1950s*",
    ),
    (
        "战后日本经济高速增长，居民收入快速提高，家庭电气化全面普及。电视、冰箱、洗衣机、空调从少数家庭的奢侈品，逐渐变成普通家庭的标配。",
        "\n\n![制造黄金时代｜1950s–1970s]({{image:golden-manufacturing.webp}})\n\n*制造黄金时代｜1950s–1970s*",
    ),
    (
        "家电品类越来越多，就向电机、电池、零部件延伸。",
        "\n\n![全球化扩张｜1970s–1980s]({{image:global-expansion.webp}})\n\n*全球化扩张｜1970s–1980s*",
    ),
    (
        "1989年是一个很有象征意义的节点。",
        "\n\n![品牌转型｜1980s–1990s]({{image:brand-transition.webp}})\n\n*品牌转型｜1980s–1990s*",
    ),
    (
        "2005年前后，松下在尼崎建设大型等离子面板工厂，随后继续扩大产能。",
        "\n\n![等离子赌注｜2000s]({{image:plasma.webp}})\n\n*等离子赌注｜2000s*",
    ),
    (
        "2012年，津贺一宏出任社长。",
        "\n\n![转型与当下｜2010s–至今]({{image:modern.webp}})\n\n*转型与当下｜2010s–至今*",
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
