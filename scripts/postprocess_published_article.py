#!/usr/bin/env python3
import html
import json
import re
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
result_path = ROOT / "publishing-result.json"
if not result_path.exists():
    raise RuntimeError("publishing-result.json 不存在，无法执行发布后处理")

result = json.loads(result_path.read_text(encoding="utf-8"))
slug = result["slug"]
md_path = ROOT / "content" / "articles" / f"{slug}.md"
html_path = ROOT / "blog" / "articles" / f"{slug}.html"

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

# 新版首页已改为三栏“真实企业分析案例”，不再使用旧 data-md-articles 锚点。
# 这里用 articles.json 中最新三篇正式文章重建首页案例区，保持首页与博客列表同步。
articles_path = ROOT / "blog" / "articles.json"
index_path = ROOT / "index.html"
if articles_path.exists() and index_path.exists():
    articles = json.loads(articles_path.read_text(encoding="utf-8"))[:3]
    cards = []
    for item in articles:
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

print(f"postprocessed slug={slug}")
