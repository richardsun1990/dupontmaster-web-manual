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

# 公开可下载的 Panasonic / National 历史与现代图像源。
# GitHub Actions 只把这些地址作为临时输入；正式文章发布时统一转存至 DupontMaster 自有 OSS。
# 选择原则：历史真实性、品牌识别度、与正文年代/主题匹配、可由公共网络直接下载。
IMAGE_SOURCES = {
    "startup.webp": (
        "https://i01.fotocdn.net/s206/efeddafdac1ecfbe/public_pin_l/2401850020.jpg",
        "创业与起步 | 1918–1950s",
    ),
    "golden-manufacturing.webp": (
        "https://tospo-keiba.jp/images/articles/contents/shares/0703/%E6%99%AE%E5%8F%8A%E3%81%97%E5%A7%8B%E3%82%81%E3%81%9F%E3%82%AB%E3%83%A9%E3%83%BC%E3%83%86%E3%83%AC%E3%83%93%E3%81%8C%E4%B8%A6%E3%81%B6%E6%9D%B1%E4%BA%AC%E3%83%BB%E7%A7%8B%E8%91%89%E5%8E%9F%E3%81%AE%E9%9B%BB%E5%99%A8%E5%BA%97.jpg",
        "制造黄金时代 | 1950s–1970s",
    ),
    "global-expansion.webp": (
        "https://i3.ruliweb.com/img/18/12/23/167d8e41a1f4e7410.jpg",
        "全球化扩张 | 1970s–1980s",
    ),
    "brand-transition.webp": (
        "https://www.yamada-holdings.jp/company/img/corp200912_03.jpg",
        "品牌转型 | 1980s–1990s",
    ),
    "plasma.webp": (
        "https://cassette.sphdigital.com.sg/image/hardwarezone/e43b7ac105050bcbcd7c33426e1acdaa662d6d64cae3f50bcd568a2b9a8a0954?q=85&w=1200",
        "等离子赌注 | 2000s",
    ),
    "modern.webp": (
        "https://cdn.osaka.com/wp-content/uploads/2021/03/Panasonic-building.jpg",
        "转型与当下 | 2010s–至今",
    ),
}
LOGO_URL = "https://1000logos.net/wp-content/uploads/2017/04/Panasonic-logo.jpg"

out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assets")
out_dir.mkdir(parents=True, exist_ok=True)
project_dir = out_dir.parent

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0 Safari/537.36",
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
})


def download_image(url: str) -> Image.Image:
    r = session.get(url, timeout=90, allow_redirects=True)
    r.raise_for_status()
    content_type = (r.headers.get("content-type") or "").lower()
    if "image" not in content_type and len(r.content) < 20_000:
        raise RuntimeError(f"download did not return an image: {url} content-type={content_type}")
    img = Image.open(io.BytesIO(r.content))
    img.load()
    if img.width < 400 or img.height < 250:
        raise RuntimeError(f"source image too small: {url} size={img.size}")
    return img.convert("RGB")


def cover_crop(img: Image.Image, size=(1600, 900), centering=(0.5, 0.5)) -> Image.Image:
    return ImageOps.fit(img, size, method=Image.Resampling.LANCZOS, centering=centering)


def label_image(img: Image.Image, label: str) -> Image.Image:
    canvas = cover_crop(img)
    draw = ImageDraw.Draw(canvas, "RGBA")
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    try:
        font = ImageFont.truetype(font_path, 25)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 18, 10
    x2, y2 = 1570, 870
    x1, y1 = x2 - tw - pad_x * 2, y2 - th - pad_y * 2
    # 仅保留右下角小型年代/主题角标，不做海报式信息图。
    draw.rounded_rectangle((x1, y1, x2, y2), radius=7, fill=(5, 12, 22, 145))
    draw.text((x1 + pad_x, y1 + pad_y - 2), label, fill=(255, 255, 255, 235), font=font)
    return canvas


# 1) 公开历史/现代图 -> 统一横版 + 极简右下角年代角标。
raw_images = {}
for name, (url, label) in IMAGE_SOURCES.items():
    img = download_image(url)
    raw_images[name] = img
    final = label_image(img, label)
    final.save(out_dir / name, "WEBP", quality=88, method=6, optimize=True)
    print(f"generated {name} from public historical/editorial source")

# 2) 封面：历史制造与现代 Panasonic 左右融合；只保留自然品牌元素，不加标题、图标或股价图。
history = cover_crop(raw_images["startup.webp"], (800, 900), centering=(0.5, 0.5))
modern = cover_crop(raw_images["modern.webp"], (800, 900), centering=(0.5, 0.5))
cover = Image.new("RGB", (1600, 900), "white")
cover.paste(history, (0, 0))
cover.paste(modern, (800, 0))

blend_w = 180
mask = Image.new("L", (blend_w, 900))
md = ImageDraw.Draw(mask)
for x in range(blend_w):
    md.line((x, 0, x, 900), fill=int(255 * x / (blend_w - 1)))
old_side = history.crop((800 - blend_w, 0, 800, 900)).resize((blend_w, 900))
new_side = modern.crop((0, 0, blend_w, 900)).resize((blend_w, 900))
transition = Image.composite(new_side, old_side, mask)
cover.paste(transition, (800 - blend_w // 2, 0))

# Panasonic wordmark：自然放在现代一侧，避免封面缺少品牌识别。
logo_img = download_image(LOGO_URL).convert("RGBA")
# 去掉白边并缩放；源图本身为白底蓝色字标。
logo_rgb = logo_img.convert("RGB")
# 直接使用白底小面板，保持商标清晰而不制造额外装饰。
logo_rgb.thumbnail((360, 120), Image.Resampling.LANCZOS)
panel = Image.new("RGBA", (logo_rgb.width + 36, logo_rgb.height + 24), (255, 255, 255, 220))
panel.alpha_composite(logo_rgb.convert("RGBA"), (18, 12))
cover_rgba = cover.convert("RGBA")
cover_rgba.alpha_composite(panel, (1600 - panel.width - 42, 42))
cover = cover_rgba.convert("RGB")
cover.save(out_dir / "cover.webp", "WEBP", quality=90, method=6, optimize=True)
print("generated cover.webp from historical manufacturing + modern Panasonic imagery")

# 3) 正式发布前从研究仓库 main 回读最终稿，确保官网不是旧副本。
source_response = session.get(SOURCE_URL, timeout=60)
source_response.raise_for_status()
article = source_response.text.strip()

# 4) 插入配图，不改写研究正文观点。
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

image_source_note = (
    "配图说明：历史与品牌图片用于企业发展史研究语境，发布时均由 DupontMaster 转存至自有 OSS；"
    "图像来源包括 Panasonic 相关公开资料、Osaka.com、HardwareZone、Yamada Holdings、东スポ等公开页面。"
)
if image_source_note not in article:
    article += "\n\n" + image_source_note

risk_notice = "免责声明：本文仅为个人研究与思考记录，不构成任何投资建议或证券买卖依据。市场有风险，投资需谨慎。"
if risk_notice not in article:
    article += "\n\n---\n\n" + risk_notice

manifest_path = project_dir / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["markdown"] = article
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"source article loaded from: {SOURCE_URL}")
