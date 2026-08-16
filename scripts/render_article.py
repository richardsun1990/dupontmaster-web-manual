#!/usr/bin/env python3
"""Render Markdown article sources for the current DupontMaster blog layout.

This is the canonical renderer for Markdown sources. It deliberately avoids the legacy
publish_article.py card-insertion markers and instead rebuilds the current blog/home/
topic/sitemap surfaces through postprocess_published_article.py.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from publish_article import (
    ROOT,
    ARTICLE_DIR,
    ARTICLES_JSON,
    article_template,
    build_meta,
    markdown_to_html,
    update_articles_json,
    update_sitemap,
)

RESULT_JSON = ROOT / "publishing-result.json"


def enrich_catalog(meta: dict[str, str]) -> None:
    data = json.loads(ARTICLES_JSON.read_text(encoding="utf-8"))
    for item in data:
        if item.get("slug") == meta["slug"]:
            item["description"] = meta.get("description", "")
            item["href"] = f"/blog/articles/{meta['slug']}.html"
            if meta.get("image"):
                item["image"] = meta["image"]
            break
    else:
        raise RuntimeError(f"articles.json 缺少新文章：{meta['slug']}")
    ARTICLES_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_postprocess(slug: str) -> None:
    RESULT_JSON.write_text(json.dumps({"slug": slug}, ensure_ascii=False) + "\n", encoding="utf-8")
    try:
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "postprocess_published_article.py")],
            cwd=ROOT,
            check=True,
        )
    finally:
        RESULT_JSON.unlink(missing_ok=True)


def render(path: Path) -> dict[str, str]:
    if not path.is_absolute():
        path = ROOT / path
    meta, body = build_meta(path)
    # Old sources use Markdown horizontal rules heavily; the legacy parser would otherwise
    # print them as literal "---" paragraphs. They are visual separators, not content.
    body = "\n".join("" if line.strip() == "---" else line for line in body.splitlines())
    body_html = markdown_to_html(body)
    ARTICLE_DIR.mkdir(parents=True, exist_ok=True)
    output = ARTICLE_DIR / f"{meta['slug']}.html"
    output.write_text(article_template(meta, body_html), encoding="utf-8")
    update_articles_json(meta)
    enrich_catalog(meta)
    update_sitemap(meta)
    run_postprocess(meta["slug"])
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
