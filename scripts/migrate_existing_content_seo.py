#!/usr/bin/env python3
import html
import json
import re
from pathlib import Path
from urllib.parse import quote

import markdown

ROOT = Path(__file__).resolve().parents[1]
SITE_URL = "https://www.dupontmaster.com"
CHANGXIN_SLUG = "changxin-technology-cycle-and-qimonda"


def article_href(item):
    href = str(item.get("href", "")).strip()
    if href:
        return href
    return f"/blog/articles/{quote(str(item.get('slug', '')))}.html"


def parse_frontmatter(text):
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, flags=re.S)
    if not match:
        return {}, text
    meta = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip().lower()] = value.strip().strip('"\'')
    return meta, match.group(2)


def write_changxin_static():
    md_path = ROOT / "content" / "articles" / f"{CHANGXIN_SLUG}.md"
    if not md_path.exists():
        raise RuntimeError("长鑫科技 Markdown 源文件不存在")

    meta, body = parse_frontmatter(md_path.read_text(encoding="utf-8"))
    title = meta.get("title", "长鑫科技：借奇梦达的遗产入场，能否避开奇梦达的命运？")
    description = meta.get("description", "从DRAM工作原理、奇梦达倒闭、专利路径、AI红利、资本结构、经营杠杆与估值，系统分析长鑫科技能否穿越下一轮存储周期。")
    date = meta.get("date", "2026-07-22")
    tag = meta.get("tag", "企业分析")
    source = meta.get("source", "长鑫科技公开资料及 DupontMaster 整理。")
    canonical = f"{SITE_URL}/blog/articles/{CHANGXIN_SLUG}.html"
    cover = f"{SITE_URL}/blog/assets/changxin/dram-principle-published.svg"

    rendered = markdown.markdown(
        body,
        extensions=["tables", "fenced_code", "sane_lists"],
        output_format="html5",
    )

    structured = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "@id": canonical + "#article",
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "headline": title,
        "description": description,
        "image": [cover],
        "datePublished": date,
        "dateModified": date,
        "articleSection": tag,
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

    page = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)} - DupontMaster 杜邦大师</title>
  <meta name="description" content="{html.escape(description)}">
  <meta name="robots" content="index, follow">
  <meta name="author" content="DupontMaster 研究院">
  <link rel="canonical" href="{canonical}">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{cover}">
  <meta property="article:published_time" content="{html.escape(date)}">
  <meta property="article:section" content="{html.escape(tag)}">
  <script type="application/ld+json">{json.dumps(structured, ensure_ascii=False, separators=(',', ':'))}</script>
  <link rel="stylesheet" href="/assets/article-v2.css">
</head>
<body>
  <nav class="nav"><a href="/blog/">← 返回研究与文章</a><a href="https://app.dupontmaster.com/">开始分析公司</a></nav>
  <div class="box">
    <header class="header">
      <span class="tag">{html.escape(tag)}</span>
      <h1 class="title">{html.escape(title)}</h1>
      <p class="desc">{html.escape(description)}</p>
      <div class="meta">作者：DupontMaster 研究院 · {html.escape(date)}</div>
    </header>
    <article class="content">
      {rendered}
      <div class="source-box"><p><strong>数据来源：</strong>{html.escape(source)}</p><p><strong>免责声明：</strong>本文仅供学习研究参考，不构成任何证券投资建议、投资顾问服务或买卖依据。投资有风险，决策需谨慎。</p></div>
    </article>
    <div class="cta-box">
      <h3>把文章里的判断，放回真实财务数据里</h3>
      <p>用 DupontMaster 查看公司的杜邦分析、利润与现金流、资产结构、自定义图表和长期表现。</p>
      <a href="https://app.dupontmaster.com/">开始分析公司 →</a>
    </div>
  </div>
  <footer><strong>DupontMaster 杜邦大师</strong> · 文章与数据仅供研究参考，不构成投资建议。</footer>
  <script src="/assets/article-v2.js"></script>
</body>
</html>
'''
    out_path = ROOT / "blog" / "articles" / f"{CHANGXIN_SLUG}.html"
    out_path.write_text(page, encoding="utf-8")
    return {
        "id": CHANGXIN_SLUG,
        "title": title,
        "tag": tag,
        "date": date,
        "image": cover,
        "slug": CHANGXIN_SLUG,
        "description": description,
    }


def update_catalog(changxin_item):
    articles_path = ROOT / "blog" / "articles.json"
    topics_path = ROOT / "blog" / "topics.json"
    articles = json.loads(articles_path.read_text(encoding="utf-8"))
    articles = [item for item in articles if item.get("slug") != CHANGXIN_SLUG]
    articles.append(changxin_item)
    articles.sort(key=lambda item: item.get("date", ""), reverse=True)
    articles_path.write_text(json.dumps(articles, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    topics = json.loads(topics_path.read_text(encoding="utf-8"))
    article_map = {item.get("slug"): item for item in articles if item.get("slug")}
    for topic in topics:
        slugs = list(topic.get("slugs", []))
        if topic.get("id") == "semiconductors-ai" and CHANGXIN_SLUG not in slugs:
            slugs.append(CHANGXIN_SLUG)
        if topic.get("id") == "consumer-brands" and "dongao-yanji" not in slugs:
            slugs.append("dongao-yanji")
        seen = set()
        slugs = [slug for slug in slugs if not (slug in seen or seen.add(slug))]
        slugs.sort(key=lambda slug: article_map.get(slug, {}).get("date", ""), reverse=True)
        topic["slugs"] = slugs
    topics_path.write_text(json.dumps(topics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return articles, topics


def wire_related_reading():
    path = ROOT / "assets" / "article-v2.js"
    text = path.read_text(encoding="utf-8")
    if "/assets/article-related-v1.js" not in text:
        needle = "  const progress = document.createElement('div');"
        block = '''  const relatedSrc = '/assets/article-related-v1.js';
  if (!document.querySelector(`script[src="${relatedSrc}"]`)) {
    const relatedScript = document.createElement('script');
    relatedScript.src = relatedSrc;
    relatedScript.async = true;
    document.body.appendChild(relatedScript);
  }

'''
        if needle not in text:
            raise RuntimeError("无法定位 article-v2.js 相关阅读插入点")
        text = text.replace(needle, block + needle, 1)
        path.write_text(text, encoding="utf-8")


def redirect_old_dynamic_url():
    path = ROOT / "blog" / "article.html"
    text = path.read_text(encoding="utf-8")
    marker = "dm-changxin-static-redirect"
    if marker in text:
        return
    script = f'''  <script id="{marker}">
    (() => {{
      const slug = new URLSearchParams(window.location.search).get('slug');
      if (slug === '{CHANGXIN_SLUG}') {{
        window.location.replace('/blog/articles/{CHANGXIN_SLUG}.html');
      }}
    }})();
  </script>\n'''
    text = text.replace("</head>", script + "</head>", 1)
    path.write_text(text, encoding="utf-8")


def remove_old_sitemap_special_case():
    path = ROOT / "scripts" / "postprocess_published_article.py"
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r'\n    changxin_path = ROOT / "content" / "articles" / "changxin-technology-cycle-and-qimonda\.md"\n    if changxin_path\.exists\(\):\n        urls\.append\(\(\n            f"\{SITE_URL\}/blog/article\.html\?slug=changxin-technology-cycle-and-qimonda",\n            "2026-07-22",\n            "monthly",\n            "0\.8",\n        \)\)\n',
        "\n",
        text,
        count=1,
    )
    path.write_text(text, encoding="utf-8")


def rebuild_blog_index(articles):
    path = ROOT / "blog" / "index.html"
    text = path.read_text(encoding="utf-8")
    rows = []
    for item in articles:
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
            f'          <a class="article-row" data-tag="{html.escape(tag)}" href="{html.escape(article_href(item))}">'
            f'<span class="{thumb_class}"><img src="{html.escape(image_src)}" alt="{html.escape(title)}" loading="lazy"></span>'
            f'<span class="article-main"><span class="article-kicker">{html.escape(tag)}</span><h3>{html.escape(title)}</h3>{desc_html}</span>'
            f'<time class="article-date" datetime="{html.escape(date)}">{html.escape(date)}</time></a>'
        )
    text = re.sub(r'(<p data-article-count>).*?(</p>)', rf'\g<1>{len(articles)} 篇\g<2>', text, count=1)
    marker = '<div class="article-list" data-md-articles="blog">'
    start = text.find(marker)
    if start < 0:
        raise RuntimeError("博客首页缺少 article-list 锚点")
    content_start = text.find(">", start) + 1
    end_marker = '\n        </div>\n        <div class="empty-state"'
    end = text.find(end_marker, content_start)
    if end < 0:
        raise RuntimeError("无法定位博客文章列表结束位置")
    text = text[:content_start] + "\n" + "\n".join(rows) + text[end:]
    path.write_text(text, encoding="utf-8")


def rebuild_topic_pages(articles, topics):
    article_map = {item.get("slug"): item for item in articles if item.get("slug")}
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
            title = item.get("title", slug)
            date = item.get("date", "")
            desc = item.get("description", "") or f"从{topic.get('title', '专题研究')}继续理解这家公司的经营、竞争与长期价值。"
            rows.append(
                f'<a class="topic-article" href="{html.escape(article_href(item))}">'
                f'<span class="topic-article-no">{index:02d}</span><span><h3>{html.escape(title)}</h3><p>{html.escape(desc)}</p></span>'
                f'<time datetime="{html.escape(date)}">{html.escape(date)}</time></a>'
            )
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


def rebuild_sitemap(articles, topics):
    latest = max((item.get("date", "") for item in articles), default="")
    article_map = {item.get("slug"): item for item in articles if item.get("slug")}
    urls = [
        (f"{SITE_URL}/", latest, "weekly", "1.0"),
        (f"{SITE_URL}/blog/", latest, "weekly", "0.9"),
    ]
    for topic in topics:
        topic_id = topic.get("id", "")
        dates = [article_map[slug].get("date", "") for slug in topic.get("slugs", []) if slug in article_map]
        urls.append((f"{SITE_URL}/blog/topics/{quote(topic_id)}.html", max(dates, default=latest), "weekly", "0.85"))
    for item in articles:
        href = article_href(item)
        loc = href if href.startswith("http") else SITE_URL + href
        urls.append((loc, item.get("date", ""), "monthly", "0.8"))

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
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    changxin = write_changxin_static()
    articles, topics = update_catalog(changxin)
    wire_related_reading()
    redirect_old_dynamic_url()
    remove_old_sitemap_special_case()
    rebuild_blog_index(articles)
    rebuild_topic_pages(articles, topics)
    rebuild_sitemap(articles, topics)
    print(f"integrated {CHANGXIN_SLUG}; articles={len(articles)}")


if __name__ == "__main__":
    main()
