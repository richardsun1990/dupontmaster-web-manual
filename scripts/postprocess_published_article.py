#!/usr/bin/env python3
import html
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://www.dupontmaster.com"
result_path = ROOT / "publishing-result.json"
if not result_path.exists():
    raise RuntimeError("publishing-result.json 不存在，无法执行发布后处理")

result = json.loads(result_path.read_text(encoding="utf-8"))
slug = result["slug"]
md_path = ROOT / "content" / "articles" / f"{slug}.md"
html_path = ROOT / "blog" / "articles" / f"{slug}.html"
articles_path = ROOT / "blog" / "articles.json"
articles = json.loads(articles_path.read_text(encoding="utf-8")) if articles_path.exists() else []
article_meta = next((item for item in articles if item.get("slug") == slug), {})

# 所有新发布文章都挂上统一正文视觉、分享与 GA 阅读统计，并写入静态 SEO 元数据。
if html_path.exists():
    html_text = html_path.read_text(encoding="utf-8")
    if '/assets/article-v2.css' not in html_text:
        html_text = html_text.replace(
            '</head>',
            '  <link rel="stylesheet" href="/assets/article-v2.css">\n</head>',
            1,
        )
    if '/assets/article-v2.js' not in html_text:
        html_text = html_text.replace(
            '</body>',
            '  <script src="/assets/article-v2.js"></script>\n</body>',
            1,
        )

    title = article_meta.get("title", slug)
    description = article_meta.get("description", "")
    date = article_meta.get("date", "")
    tag = article_meta.get("tag", "企业研究")
    image = article_meta.get("image") or f"{SITE_URL}/icon-512.png"
    canonical = f"{SITE_URL}/blog/articles/{quote(slug)}.html"

    head_bits = []
    if '<meta name="robots"' not in html_text:
        head_bits.append('  <meta name="robots" content="index, follow">')
    if '<meta name="author"' not in html_text:
        head_bits.append('  <meta name="author" content="DupontMaster 研究院">')
    if date and 'property="article:published_time"' not in html_text:
        head_bits.append(f'  <meta property="article:published_time" content="{html.escape(date)}">')
    if tag and 'property="article:section"' not in html_text:
        head_bits.append(f'  <meta property="article:section" content="{html.escape(tag)}">')

    if '"@type": "BlogPosting"' not in html_text and "'@type': 'BlogPosting'" not in html_text:
        structured = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "@id": canonical + "#article",
            "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
            "headline": title,
            "description": description,
            "image": [image],
            "datePublished": date,
            "dateModified": date,
            "articleSection": tag,
            "inLanguage": "zh-CN",
            "author": {
                "@type": "Organization",
                "name": "DupontMaster 研究院",
                "url": f"{SITE_URL}/blog/",
            },
            "publisher": {
                "@type": "Organization",
                "name": "DupontMaster 杜邦大师",
                "url": f"{SITE_URL}/",
                "logo": {"@type": "ImageObject", "url": f"{SITE_URL}/icon-512.png"},
            },
            "isPartOf": {"@type": "Blog", "@id": f"{SITE_URL}/blog/#blog"},
        }
        head_bits.append(
            '  <script type="application/ld+json">'
            + json.dumps(structured, ensure_ascii=False, separators=(",", ":"))
            + '</script>'
        )

    if head_bits:
        html_text = html_text.replace('</head>', "\n".join(head_bits) + '\n</head>', 1)
    html_path.write_text(html_text, encoding="utf-8")

# 如果正文已经包含统一的“投研说明”，则删除旧模板在正文末尾重复追加的资料来源与 CTA。
if md_path.exists() and html_path.exists():
    md_text = md_path.read_text(encoding="utf-8")
    html_text = html_path.read_text(encoding="utf-8")
    if "## 投研说明" in md_text:
        html_text = re.sub(
            r'\s*<div class="source-box">.*?</div>\s*<div class="cta-box">.*?</div>',
            "",
            html_text,
            flags=re.S,
        )
        html_path.write_text(html_text, encoding="utf-8")

# 新版首页使用最新三篇文章作为真实企业分析案例。
index_path = ROOT / "index.html"
if articles and index_path.exists():
    cards = []
    for item in articles[:3]:
        item_slug = item.get("slug", "")
        title = item.get("title", "")
        tag = item.get("tag", "企业分析")
        desc = item.get("description", "")
        image = item.get("image", "")
        image_html = ""
        if image:
            image_html = (
                f'<img src="{html.escape(image)}" alt="{html.escape(title)}" '
                'style="width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:8px;margin-bottom:14px;">'
            )
        cards.append(
            f'          <a class="case-item" href="/blog/articles/{quote(item_slug)}.html">'
            f'{image_html}<span>{html.escape(tag)}</span>'
            f'<h3>{html.escape(title)}</h3>'
            f'<p>{html.escape(desc)}</p></a>'
        )

    index_text = index_path.read_text(encoding="utf-8")
    start_marker = '<div class="case-list">'
    start = index_text.find(start_marker)
    if start < 0:
        raise RuntimeError("新版首页缺少 case-list 锚点")
    content_start = index_text.find(">", start) + 1
    end_marker = '\n        </div>\n      </div>\n    </section>\n\n    <section class="section-tight" id="source">'
    end = index_text.find(end_marker, content_start)
    if end < 0:
        raise RuntimeError("无法定位新版首页 case-list 结束位置")
    index_text = index_text[:content_start] + "\n" + "\n".join(cards) + index_text[end:]
    index_path.write_text(index_text, encoding="utf-8")

# 同步生成博客静态 fallback。JS 仍以 articles.json 为运行时唯一数据源；
# 静态列表用于搜索引擎、禁用 JS 的访问者以及加载失败时兜底。
blog_index_path = ROOT / "blog" / "index.html"
if articles and blog_index_path.exists():
    rows = []
    for item in articles:
        item_slug = item.get("slug", "")
        title = item.get("title", "")
        tag = item.get("tag", "文章")
        date = item.get("date", "")
        desc = item.get("description", "")
        image = item.get("image", "")
        placeholder = not image or image.endswith("/icon-512.png")
        image_src = "/logo.svg" if placeholder else image
        thumb_class = "article-thumb placeholder" if placeholder else "article-thumb"
        desc_html = f'<p>{html.escape(desc)}</p>' if desc else ""
        rows.append(
            f'          <a class="article-row" data-tag="{html.escape(tag)}" href="/blog/articles/{quote(item_slug)}.html">'
            f'<span class="{thumb_class}"><img src="{html.escape(image_src)}" alt="{html.escape(title)}" loading="lazy"></span>'
            f'<span class="article-main"><span class="article-kicker">{html.escape(tag)}</span>'
            f'<h3>{html.escape(title)}</h3>{desc_html}</span>'
            f'<time class="article-date" datetime="{html.escape(date)}">{html.escape(date)}</time></a>'
        )

    blog_text = blog_index_path.read_text(encoding="utf-8")
    blog_text = re.sub(
        r'(<p data-article-count>).*?(</p>)',
        rf'\g<1>{len(articles)} 篇\g<2>',
        blog_text,
        count=1,
    )
    list_marker = '<div class="article-list" data-md-articles="blog">'
    list_start = blog_text.find(list_marker)
    if list_start < 0:
        raise RuntimeError("博客首页缺少 article-list 锚点")
    list_content_start = blog_text.find(">", list_start) + 1
    list_end_marker = '\n        </div>\n        <div class="empty-state"'
    list_end = blog_text.find(list_end_marker, list_content_start)
    if list_end < 0:
        raise RuntimeError("无法定位博客 article-list 结束位置")
    blog_text = blog_text[:list_content_start] + "\n" + "\n".join(rows) + blog_text[list_end:]
    blog_index_path.write_text(blog_text, encoding="utf-8")

# 每次发布后自动重建 sitemap，避免旧 URL、漏文章和过期 lastmod。
sitemap_path = ROOT / "sitemap.xml"
if articles:
    latest_date = max((item.get("date", "") for item in articles), default="")
    urls = [
        (f"{SITE_URL}/", latest_date, "weekly", "1.0"),
        (f"{SITE_URL}/blog/", latest_date, "weekly", "0.9"),
    ]

    changxin_path = ROOT / "content" / "articles" / "changxin-technology-cycle-and-qimonda.md"
    if changxin_path.exists():
        urls.append((
            f"{SITE_URL}/blog/article.html?slug=changxin-technology-cycle-and-qimonda",
            "2026-07-22",
            "monthly",
            "0.8",
        ))

    for item in articles:
        item_slug = item.get("slug")
        if not item_slug:
            continue
        urls.append((
            f"{SITE_URL}/blog/articles/{quote(item_slug)}.html",
            item.get("date", ""),
            "monthly",
            "0.8",
        ))

    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod, changefreq, priority in urls:
        lines.append('  <url>')
        lines.append(f'    <loc>{html.escape(loc)}</loc>')
        if lastmod:
            lines.append(f'    <lastmod>{html.escape(lastmod)}</lastmod>')
        lines.append(f'    <changefreq>{changefreq}</changefreq>')
        lines.append(f'    <priority>{priority}</priority>')
        lines.append('  </url>')
    lines.append('</urlset>')
    sitemap_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

print(f"postprocessed slug={slug}")
