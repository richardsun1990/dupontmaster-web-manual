#!/usr/bin/env python3
"""
Import a Notion Markdown export, upload local images to Aliyun OSS,
rewrite image links, and place the final Markdown into content/articles.

Usage:
  python3 scripts/import_notion_article.py ~/Downloads/notion-export.zip --slug maotai-2026-analysis
  python3 scripts/import_notion_article.py ~/Downloads/notion-export-folder

Required environment variables:
  ALIYUN_OSS_ACCESS_KEY_ID
  ALIYUN_OSS_ACCESS_KEY_SECRET
  ALIYUN_OSS_BUCKET
  ALIYUN_OSS_ENDPOINT

Optional:
  ALIYUN_OSS_PUBLIC_BASE_URL
  ALIYUN_OSS_PREFIX
"""

from __future__ import annotations

import argparse
import base64
import email.utils
import hashlib
import hmac
import mimetypes
import os
import re
import shutil
import tempfile
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "content" / "articles"
IMAGE_PATTERN = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def load_env_file() -> None:
    env_file = ROOT / ".oss.env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def env(name: str, required: bool = True, default: str = "") -> str:
    value = os.environ.get(name, default).strip()
    if required and not value:
        raise SystemExit(f"缺少环境变量：{name}")
    return value


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"\.md$", "", value)
    value = value.replace("_", "-")
    value = re.sub(r"[^a-z0-9-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "notion-article"


def extract_source(source: Path) -> tuple[Path, tempfile.TemporaryDirectory[str] | None]:
    source = source.expanduser().resolve()
    if source.is_dir():
        return source, None
    if source.suffix.lower() != ".zip":
        raise SystemExit("请输入 Notion 导出的 zip，或解压后的文件夹。")
    temp_dir = tempfile.TemporaryDirectory(prefix="notion-export-")
    with zipfile.ZipFile(source) as zf:
        zf.extractall(temp_dir.name)
    return Path(temp_dir.name), temp_dir


def find_markdown_file(folder: Path, preferred: str | None = None) -> Path:
    markdown_files = sorted(folder.rglob("*.md"))
    if not markdown_files:
        raise SystemExit("导出包里没有找到 Markdown 文件。")
    if preferred:
        preferred_path = Path(preferred)
        for item in markdown_files:
            if item.name == preferred_path.name or item.relative_to(folder).as_posix() == preferred:
                return item
        raise SystemExit(f"没有找到指定 Markdown 文件：{preferred}")
    return markdown_files[0]


def is_external_url(value: str) -> bool:
    return bool(re.match(r"^(https?:)?//", value)) or value.startswith("/")


def quoted_path(value: str) -> str:
    return "/".join(urllib.parse.quote(part) for part in value.split("/"))


def public_url(bucket: str, endpoint: str, object_key: str) -> str:
    base = env("ALIYUN_OSS_PUBLIC_BASE_URL", required=False)
    if not base:
        base = f"https://{bucket}.{endpoint}"
    return f"{base.rstrip('/')}/{quoted_path(object_key)}"


def oss_put(file_path: Path, object_key: str) -> str:
    access_key_id = env("ALIYUN_OSS_ACCESS_KEY_ID")
    access_key_secret = env("ALIYUN_OSS_ACCESS_KEY_SECRET")
    bucket = env("ALIYUN_OSS_BUCKET")
    endpoint = env("ALIYUN_OSS_ENDPOINT").replace("https://", "").replace("http://", "").strip("/")

    body = file_path.read_bytes()
    content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    content_md5 = base64.b64encode(hashlib.md5(body).digest()).decode("ascii")
    date_header = email.utils.formatdate(usegmt=True)
    canonical_resource = f"/{bucket}/{object_key}"
    string_to_sign = f"PUT\n{content_md5}\n{content_type}\n{date_header}\n{canonical_resource}"
    signature = base64.b64encode(
        hmac.new(access_key_secret.encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha1).digest()
    ).decode("ascii")

    url = f"https://{bucket}.{endpoint}/{quoted_path(object_key)}"
    request = urllib.request.Request(url, data=body, method="PUT")
    request.add_header("Authorization", f"OSS {access_key_id}:{signature}")
    request.add_header("Date", date_header)
    request.add_header("Content-Type", content_type)
    request.add_header("Content-MD5", content_md5)
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status not in (200, 201):
            raise RuntimeError(f"OSS 上传失败：{response.status}")
    return public_url(bucket, endpoint, object_key)


def resolve_asset(markdown_file: Path, raw_path: str) -> Path | None:
    decoded = urllib.parse.unquote(raw_path).strip()
    if is_external_url(decoded):
        return None
    candidate = (markdown_file.parent / decoded).resolve()
    if candidate.exists():
        return candidate
    fallback = next((item for item in markdown_file.parent.rglob(Path(decoded).name) if item.is_file()), None)
    return fallback.resolve() if fallback else None


def rewrite_images(markdown_text: str, markdown_file: Path, slug: str) -> str:
    uploaded: dict[Path, str] = {}
    prefix = env("ALIYUN_OSS_PREFIX", required=False, default="blog/notion").strip("/")
    date_part = datetime.now().strftime("%Y%m%d")

    def replace(match: re.Match[str]) -> str:
        alt, src = match.group(1), match.group(2)
        if is_external_url(src):
            return match.group(0)
        asset = resolve_asset(markdown_file, src)
        if not asset:
            print(f"未找到图片，保持原路径：{src}")
            return match.group(0)
        if asset not in uploaded:
            suffix = asset.suffix.lower() or ".png"
            digest = hashlib.sha1(asset.read_bytes()).hexdigest()[:10]
            safe_name = slugify(asset.stem) or "image"
            object_key = f"{prefix}/{slug}/{date_part}-{safe_name}-{digest}{suffix}"
            uploaded[asset] = oss_put(asset, object_key)
            print(f"已上传图片：{asset.name} -> {uploaded[asset]}")
        return f"![{alt}]({uploaded[asset]})"

    return IMAGE_PATTERN.sub(replace, markdown_text)


def ensure_frontmatter(markdown_text: str, slug: str) -> str:
    if markdown_text.startswith("---\n"):
        return markdown_text
    first_title = next((line[2:].strip() for line in markdown_text.splitlines() if line.startswith("# ")), slug)
    today = datetime.now().strftime("%Y-%m-%d")
    frontmatter = (
        "---\n"
        f"title: {first_title}\n"
        f"date: {today}\n"
        "tag: 企业分析\n"
        f"description: {first_title}\n"
        "source: 公司公告、年报、交易所披露文件及 DupontMaster 整理。\n"
        "---\n\n"
    )
    return frontmatter + markdown_text


def main() -> None:
    load_env_file()
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Notion 导出的 zip，或解压后的文件夹")
    parser.add_argument("--slug", help="输出文章文件名，不含 .md")
    parser.add_argument("--file", help="导出包里要导入的 Markdown 文件名")
    args = parser.parse_args()

    folder, temp_dir = extract_source(Path(args.source))
    try:
        markdown_file = find_markdown_file(folder, preferred=args.file)
        slug = slugify(args.slug or markdown_file.stem)
        markdown_text = markdown_file.read_text(encoding="utf-8")
        markdown_text = rewrite_images(markdown_text, markdown_file, slug)
        markdown_text = ensure_frontmatter(markdown_text, slug)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output = OUTPUT_DIR / f"{slug}.md"
        output.write_text(markdown_text, encoding="utf-8")
        print(f"已生成文章：{output.relative_to(ROOT)}")
    finally:
        if temp_dir:
            temp_dir.cleanup()


if __name__ == "__main__":
    main()
