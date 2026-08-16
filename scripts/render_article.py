#!/usr/bin/env python3
"""Render Markdown article sources for the current DupontMaster blog layout.

Unlike the legacy publish_article.py entry point, this renderer does not try to inject
cards into old hard-coded HTML markers. The canonical article catalog is updated here;
postprocess_published_article.py then rebuilds the current homepage, blog fallback,
topic pages and sitemap from that catalog.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from publish_article import (
    ROOT,
    ARTICLE_DIR,
    article_template,
    build_meta,
    markdown_to_html,
    update_articles_json,
    update_sitemap,
)


def render(path: Path) -> dict[str, str]:
    if not path.is_absolute():
        path = ROOT / path
    meta, body = build_meta(path)
    body_html = markdown_to_html(body)
    ARTICLE_DIR.mkdir(parents=True, exist_ok=True)
    output = ARTICLE_DIR / f"{meta['slug']}.html"
    output.write_text(article_template(meta, body_html), encoding="utf-8")
    update_articles_json(meta)
    update_sitemap(meta)
    return meta


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+", help="要渲染的 Markdown 文章")
    args = parser.parse_args()
    for item in args.files:
        meta = render(Path(item))
        print(f"已生成：{meta['title']} -> /blog/articles/{meta['slug']}.html")


if __name__ == "__main__":
    main()
