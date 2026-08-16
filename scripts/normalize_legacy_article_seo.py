#!/usr/bin/env python3
import html
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://www.dupontmaster.com"
CATALOG = ROOT / "blog" / "articles.json"
TOPICS = ROOT / "blog" / "topics.json"

articles = json.loads(CATALOG.read_text(encoding="utf-8"))
topics = json.loads(TOPICS.read_text(encoding="utf-8"))
article_map = {item.get("slug"): item for item in articles if item.get("slug")}


def article_path(item):
    return ROOT / "blog" / "articles" / f"{item['slug']}.html"


def canonical_for(item):
    return f"{SITE_URL}/blog/articles/{quote(str(item['slug']))}.html"


def upsert_meta(text, *, attr, key, value):
    if not value:
        return text
    escaped = html.escape(str(value), quote=True)
    pattern = re.compile(rf'<meta\s+{attr}=["\']{re.escape(key)}["\'][^>]*>', re.I)
    tag = f'  <meta {attr}="{html.escape(key, quote=True)}" content="{escaped}">'
    if pattern.search(text):
        return pattern.sub(tag.strip(), text, count=1)
    return text.replace('</head>', tag + '\n</head>', 1)


def upsert_canonical(text, canonical):
    pattern = re.compile(r'<link\s+rel=["\']canonical["\'][^>]*>', re.I)
    tag = f'  <link rel="canonical" href="{html.escape(canonical, quote=True)}">'
    if pattern.search(text):
        return pattern.sub(tag.strip(), text, count=1)
    return text.replace('</head>', tag + '\n</head>', 1)


def ensure_blogposting(text, item, canonical):
    if 'id="dm-static-blogposting-v1"' in text:
        return text
    image = item.get("image") or f"{SITE_URL}/icon-512.png"
    structured = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "@id": canonical + "#article",
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "headline": item.get("title", item.get("slug", "")),
        "description": item.get("description", ""),
        "image": [image],
        "datePublished": item.get("date", ""),
        "dateModified": item.get("date", ""),
        "articleSection": item.get("tag", "企业分析"),
        "inLanguage": "zh-CN",
        "author": {"@type": "Organization", "name": "DupontMaster 研究院", "url": f"{SITE_URL}/blog/"},
        "publisher": {
            "@type": "Organization",
            "name": "DupontMaster 杜邦大师",
            "url": f"{SITE_URL}/",
            "logo": {"@type": "ImageObject", "url": f"{SITE_URL}/icon-512.png"},
        },
        "isPartOf": {"@type": "Blog", "@id": f"{SITE_URL}/blog/#blog"},
    }
    script = '  <script id="dm-static-blogposting-v1" type="application/ld+json">' + json.dumps(structured, ensure_ascii=False, separators=(",", ":")) + '</script>'
    return text.replace('</head>', script + '\n</head>', 1)


changed = 0
for item in articles:
    path = article_path(item)
    if not path.exists():
        continue
    text = path.read_text(encoding="utf-8")
    original = text
    canonical = canonical_for(item)
    title = item.get("title", item.get("slug", ""))
    desc = item.get("description", "")
    image = item.get("image") or f"{SITE_URL}/icon-512.png"
    tag = item.get("tag", "企业分析")
    date = item.get("date", "")

    text = upsert_meta(text, attr="name", key="description", value=desc)
    text = upsert_meta(text, attr="name", key="robots", value="index, follow")
    text = upsert_meta(text, attr="name", key="author", value="DupontMaster 研究院")
    text = upsert_canonical(text, canonical)
    text = upsert_meta(text, attr="property", key="og:type", value="article")
    text = upsert_meta(text, attr="property", key="og:title", value=title)
    text = upsert_meta(text, attr="property", key="og:description", value=desc)
    text = upsert_meta(text, attr="property", key="og:url", value=canonical)
    text = upsert_meta(text, attr="property", key="og:image", value=image)
    text = upsert_meta(text, attr="property", key="article:published_time", value=date)
    text = upsert_meta(text, attr="property", key="article:section", value=tag)
    text = ensure_blogposting(text, item, canonical)

    if text != original:
        path.write_text(text, encoding="utf-8")
        changed += 1

# Refresh static topic excerpts from the recovered catalog metadata.
for topic in topics:
    topic_id = topic.get("id", "")
    path = ROOT / "blog" / "topics" / f"{topic_id}.html"
    if not topic_id or not path.exists():
        continue
    rows = []
    for index, slug in enumerate(topic.get("slugs", []), start=1):
        item = article_map.get(slug)
        if not item:
            continue
        desc = item.get("description", "") or f"继续理解这家公司的经营、竞争与长期价值。"
        rows.append(
            f'<a class="topic-article" href="/blog/articles/{quote(slug)}.html">'
            f'<span class="topic-article-no">{index:02d}</span>'
            f'<span><h3>{html.escape(item.get("title", slug))}</h3><p>{html.escape(desc)}</p></span>'
            f'<time datetime="{html.escape(item.get("date", ""))}">{html.escape(item.get("date", ""))}</time></a>'
        )
    if not rows:
        continue
    text = path.read_text(encoding="utf-8")
    text, count = re.subn(
        r'(<div class="topic-list">).*?(</div><div class="topic-more">)',
        r'\1\n' + "\n".join(rows) + r'\n\2',
        text,
        count=1,
        flags=re.S,
    )
    if count:
        path.write_text(text, encoding="utf-8")

print(f"normalized legacy articles={changed}; topics={len(topics)}")
