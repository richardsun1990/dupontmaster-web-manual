#!/usr/bin/env python3
"""
Generate static blog pages from Markdown files in content/articles.

Usage:
  python3 scripts/publish_article.py --all
  python3 scripts/publish_article.py content/articles/my-article.md
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from datetime import date
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content" / "articles"
ARTICLE_DIR = ROOT / "blog" / "articles"
BLOG_INDEX = ROOT / "blog" / "index.html"
HOME_INDEX = ROOT / "index.html"
ARTICLES_JSON = ROOT / "blog" / "articles.json"
SITEMAP = ROOT / "sitemap.xml"

DEFAULT_TAG = "企业分析"
DEFAULT_AUTHOR = "DupontMaster 研究院"
DEFAULT_IMAGE = "https://www.dupontmaster.com/icon-512.png"
DEFAULT_SOURCE = "公司公告、年报、交易所披露文件及 DupontMaster 整理。"
DISCLAIMER = "本文仅供学习研究参考，不构成任何证券投资建议、投资顾问服务或买卖依据。投资有风险，决策需谨慎。"


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    raw = text[4:end].strip()
    body = text[text.find("\n", end + 4) + 1 :]
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip().lower()] = value.strip().strip('"').strip("'")
    return meta, body


def strip_markdown(value: str) -> str:
    value = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"[*_`>#-]", "", value)
    return re.sub(r"\s+", " ", value).strip()


def first_heading(body: str) -> str | None:
    for line in body.splitlines():
        if line.startswith("# "):
            return strip_markdown(line[2:])
    return None


def first_paragraph(body: str) -> str:
    for block in re.split(r"\n\s*\n", body):
        text = strip_markdown(block)
        if text and not text.startswith("#"):
            return text[:120]
    return ""


def make_slug(title: str, file_stem: str, explicit_slug: str | None, article_date: str) -> str:
    if explicit_slug:
        base = explicit_slug
    elif re.fullmatch(r"[a-z0-9][a-z0-9-]*", file_stem):
        base = file_stem
    else:
        digest = hashlib.sha1(title.encode("utf-8")).hexdigest()[:8]
        base = f"article-{article_date}-{digest}"
    base = base.lower().replace("_", "-")
    base = re.sub(r"[^a-z0-9-]", "-", base)
    base = re.sub(r"-+", "-", base).strip("-")
    return base or f"article-{article_date}"


def inline_markdown(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1">', escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    return escaped


def markdown_to_html(body: str) -> str:
    blocks: list[str] = []
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            i += 1
            continue
        if line.startswith("# "):
            i += 1
            continue
        if line.startswith("## "):
            blocks.append(f"<h2>{inline_markdown(line[3:].strip())}</h2>")
            i += 1
            continue
        if line.startswith("### "):
            blocks.append(f"<h3>{inline_markdown(line[4:].strip())}</h3>")
            i += 1
            continue
        if line.startswith("> "):
            quote_lines = []
            while i < len(lines) and lines[i].startswith("> "):
                quote_lines.append(lines[i][2:].strip())
                i += 1
            blocks.append(f"<blockquote>{inline_markdown(' '.join(quote_lines))}</blockquote>")
            continue
        if re.match(r"^[-*]\s+", line):
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].rstrip()):
                item_text = re.sub(r"^[-*]\s+", "", lines[i].strip())
                items.append(f"<li>{inline_markdown(item_text)}</li>")
                i += 1
            blocks.append("<ul>\n" + "\n".join(items) + "\n</ul>")
            continue
        if re.match(r"^\d+\.\s+", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].rstrip()):
                item_text = re.sub(r"^\d+\.\s+", "", lines[i].strip())
                items.append(f"<li>{inline_markdown(item_text)}</li>")
                i += 1
            blocks.append("<ol>\n" + "\n".join(items) + "\n</ol>")
            continue
        paragraph = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,3} |[-*]\s+|\d+\. |>)", lines[i]):
            paragraph.append(lines[i].strip())
            i += 1
        blocks.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")
    return "\n\n".join(blocks)


def article_template(meta: dict[str, str], body_html: str) -> str:
    title = meta["title"]
    description = meta["description"]
    tag = meta["tag"]
    article_date = meta["date"]
    author = meta.get("author", DEFAULT_AUTHOR)
    source = meta.get("source", DEFAULT_SOURCE)
    canonical = f"https://www.dupontmaster.com/blog/articles/{meta['slug']}.html"
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)} - DupontMaster 杜邦大师</title>
    <meta name="description" content="{html.escape(description)}">
    <link rel="canonical" href="{canonical}">
    <meta property="og:title" content="{html.escape(title)}">
    <meta property="og:description" content="{html.escape(description)}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{canonical}">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.8; color: #1d1d1f; background: #f5f5f7; }}
        .nav {{ background: #fff; border-bottom: 1px solid #d2d2d7; padding: 16px 24px; position: sticky; top: 0; z-index: 100; }}
        .nav a {{ color: #0066cc; text-decoration: none; font-size: 15px; margin-right: 18px; }}
        .box {{ max-width: 820px; margin: 40px auto; background: #fff; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); overflow: hidden; }}
        .header {{ padding: 48px 48px 32px; border-bottom: 1px solid #d2d2d7; }}
        .tag {{ display: inline-block; background: rgba(0,113,227,0.1); color: #0071e3; padding: 4px 12px; border-radius: 4px; font-size: 13px; margin-bottom: 16px; }}
        .title {{ font-size: 34px; font-weight: 650; line-height: 1.3; margin-bottom: 16px; color: #000; }}
        .meta {{ color: #86868b; font-size: 14px; }}
        .content {{ padding: 40px 48px; }}
        .content h2 {{ font-size: 24px; font-weight: 650; margin: 42px 0 18px; color: #000; }}
        .content h3 {{ font-size: 19px; font-weight: 650; margin: 30px 0 14px; color: #000; }}
        .content p {{ margin-bottom: 20px; font-size: 16px; color: #1d1d1f; }}
        .content img {{ max-width: 100%; height: auto; border-radius: 8px; margin: 24px 0; display: block; }}
        .content ul, .content ol {{ margin: 20px 0; padding-left: 24px; }}
        .content li {{ margin-bottom: 10px; font-size: 16px; }}
        .content blockquote {{ border-left: 4px solid #0071e3; padding-left: 20px; margin: 24px 0; color: #515154; font-style: italic; }}
        .source-box {{ background: #f8fafc; border: 1px solid #e5e7eb; border-radius: 10px; padding: 18px; margin-top: 36px; color: #515154; font-size: 14px; }}
        .cta-box {{ background: linear-gradient(135deg, #1e3a5f 0%, #3b82f6 100%); color: white; padding: 32px; border-radius: 12px; text-align: center; margin: 42px 0; }}
        .cta-box h3 {{ color: white; margin-bottom: 10px; }}
        .cta-box p {{ color: rgba(255,255,255,0.82); }}
        .cta-box a {{ display: inline-block; background: white; color: #0071e3; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; margin-top: 14px; }}
        footer {{ text-align: center; padding: 40px; color: #86868b; font-size: 13px; }}
        @media (max-width: 768px) {{
            .box {{ margin: 0; border-radius: 0; }}
            .header, .content {{ padding: 24px; }}
            .title {{ font-size: 26px; }}
            .content h2 {{ font-size: 21px; }}
        }}
    </style>
</head>
<body>
    <nav class="nav">
        <a href="/blog/">&larr; 返回博客</a>
        <a href="https://app.dupontmaster.com/">开始分析公司</a>
    </nav>
    <div class="box">
        <div class="header">
            <span class="tag">{html.escape(tag)}</span>
            <h1 class="title">{html.escape(title)}</h1>
            <div class="meta">作者：{html.escape(author)} · {html.escape(article_date)}</div>
        </div>
        <div class="content">
{body_html}

            <div class="source-box">
                <p><strong>数据来源：</strong>{html.escape(source)}</p>
                <p><strong>免责声明：</strong>{html.escape(DISCLAIMER)}</p>
            </div>

            <div class="cta-box">
                <h3>用 DupontMaster 分析更多公司</h3>
                <p>用同一套财务分析框架，拆解 ROE、利润质量、资产结构与估值逻辑。</p>
                <a href="https://app.dupontmaster.com/">开始分析公司 →</a>
            </div>
        </div>
    </div>
    <footer>
        <p><strong>DupontMaster 杜邦大师</strong> © 2026 · 仅供学习研究参考，不构成投资建议</p>
        <p><a href="https://www.dupontmaster.com">首页</a> · <a href="/blog/">博客</a> · <a href="https://app.dupontmaster.com/">控制台</a></p>
    </footer>
</body>
</html>
"""


def build_meta(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    today = date.today().isoformat()
    title = meta.get("title") or first_heading(body) or path.stem
    article_date = meta.get("date") or today
    slug = make_slug(title, path.stem, meta.get("slug"), article_date)
    description = meta.get("description") or first_paragraph(body) or title
    meta = {
        **meta,
        "title": title,
        "date": article_date,
        "tag": meta.get("tag", DEFAULT_TAG),
        "description": description,
        "slug": slug,
        "image": meta.get("image", DEFAULT_IMAGE),
        "source": meta.get("source", DEFAULT_SOURCE),
    }
    return meta, body


def blog_card(meta: dict[str, str], homepage: bool = False) -> str:
    href = f"/blog/articles/{meta['slug']}.html"
    margin = " margin-bottom: 12px;" if homepage else ""
    transition = "" if homepage else " transition: all 0.2s;"
    return f"""                <a href="{href}" style="display: block; background: white; border-radius: 12px; padding: 20px; text-decoration: none; color: inherit;{transition}{margin}">
                    <span style="display: inline-block; background: rgba(0,113,227,0.1); color: #0071e3; padding: 4px 10px; border-radius: 4px; font-size: 12px; margin-bottom: 8px;">{html.escape(meta['tag'])}</span>
                    <h3 style="font-size: 18px; font-weight: 600; margin-bottom: 8px;">{html.escape(meta['title'])}</h3>
                    <p style="color: #86868b; font-size: 14px;">{html.escape(meta['date'])}</p>
                </a>
"""


def insert_card_once(file_path: Path, meta: dict[str, str], marker: str, homepage: bool = False) -> None:
    text = file_path.read_text(encoding="utf-8")
    href = f"/blog/articles/{meta['slug']}.html"
    if href in text:
        return
    idx = text.find(marker)
    if idx == -1:
        raise RuntimeError(f"未找到列表插入位置：{file_path}")
    insert_at = idx + len(marker)
    text = text[:insert_at] + "\n" + blog_card(meta, homepage=homepage) + text[insert_at:]
    file_path.write_text(text, encoding="utf-8")


def update_articles_json(meta: dict[str, str]) -> None:
    if ARTICLES_JSON.exists():
        try:
            data = json.loads(ARTICLES_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = []
    else:
        data = []
    data = [item for item in data if item.get("slug") != meta["slug"]]
    data.insert(
        0,
        {
            "id": meta["slug"],
            "title": meta["title"],
            "tag": meta["tag"],
            "date": meta["date"],
            "image": meta["image"],
            "slug": meta["slug"],
        },
    )
    ARTICLES_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_sitemap(meta: dict[str, str]) -> None:
    if not SITEMAP.exists():
        return
    url = f"https://www.dupontmaster.com/blog/articles/{meta['slug']}.html"
    text = SITEMAP.read_text(encoding="utf-8")
    if url in text or "</urlset>" not in text:
        return
    item = f"""  <url>
    <loc>{url}</loc>
    <lastmod>{meta['date']}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
"""
    text = text.replace("</urlset>", item + "</urlset>")
    SITEMAP.write_text(text, encoding="utf-8")


def publish(path: Path) -> dict[str, str]:
    meta, body = build_meta(path)
    body_html = markdown_to_html(body)
    ARTICLE_DIR.mkdir(parents=True, exist_ok=True)
    output = ARTICLE_DIR / f"{meta['slug']}.html"
    output.write_text(article_template(meta, body_html), encoding="utf-8")
    insert_card_once(BLOG_INDEX, meta, '<div class="article-list" style="display: flex; flex-direction: column; gap: 16px;">')
    insert_card_once(HOME_INDEX, meta, '<div style="display: grid; gap: 12px;">', homepage=True)
    update_articles_json(meta)
    update_sitemap(meta)
    return meta


def markdown_files(args: argparse.Namespace) -> Iterable[Path]:
    if args.all:
        return sorted(path for path in CONTENT_DIR.glob("*.md") if not path.name.startswith("_"))
    return [Path(item) for item in args.files]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", help="要发布的 Markdown 文件")
    parser.add_argument("--all", action="store_true", help="发布 content/articles 下的全部文章")
    args = parser.parse_args()
    files = list(markdown_files(args))
    if not files:
        print("没有找到要发布的 Markdown 文章。")
        return
    for path in files:
        if not path.is_absolute():
            path = ROOT / path
        if path.name.startswith("_"):
            continue
        meta = publish(path)
        print(f"已发布：{meta['title']} -> /blog/articles/{meta['slug']}.html")


if __name__ == "__main__":
    main()
