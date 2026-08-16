#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLES_JSON = ROOT / "blog" / "articles.json"
TOPICS_JSON = ROOT / "blog" / "topics.json"
RESULT_JSON = ROOT / "publishing-result.json"
REMOVE_SLUGS = {
    "tencent-ai-capital-allocation-2026",
    "laopu-gold-10b-store-cycle-test",
}
KEEP_TRIGGER_SLUG = "article-264348ac3c"


def main() -> None:
    articles = json.loads(ARTICLES_JSON.read_text(encoding="utf-8"))
    before = len(articles)
    articles = [item for item in articles if item.get("slug") not in REMOVE_SLUGS]
    ARTICLES_JSON.write_text(json.dumps(articles, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    topics = json.loads(TOPICS_JSON.read_text(encoding="utf-8")) if TOPICS_JSON.exists() else []
    for topic in topics:
        slugs = topic.get("slugs", [])
        topic["slugs"] = [slug for slug in slugs if slug not in REMOVE_SLUGS]
    if TOPICS_JSON.exists():
        TOPICS_JSON.write_text(json.dumps(topics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for slug in REMOVE_SLUGS:
        for path in (
            ROOT / "content" / "articles" / f"{slug}.md",
            ROOT / "blog" / "articles" / f"{slug}.html",
        ):
            if path.exists():
                path.unlink()
                print(f"deleted {path.relative_to(ROOT)}")

    # Reuse the normal postprocessor to rebuild homepage cases, blog fallback,
    # topic lists and sitemap from the cleaned catalog.
    trigger_md = ROOT / "content" / "articles" / f"{KEEP_TRIGGER_SLUG}.md"
    trigger_html = ROOT / "blog" / "articles" / f"{KEEP_TRIGGER_SLUG}.html"
    if trigger_md.exists() and trigger_html.exists():
        RESULT_JSON.write_text(json.dumps({"slug": KEEP_TRIGGER_SLUG}, ensure_ascii=False) + "\n", encoding="utf-8")
        try:
            subprocess.run([sys.executable, "scripts/postprocess_published_article.py"], cwd=ROOT, check=True)
        finally:
            RESULT_JSON.unlink(missing_ok=True)
    else:
        raise RuntimeError("保留文章缺失，无法安全重建站点索引")

    print(f"removed {before - len(articles)} catalog entries")


if __name__ == "__main__":
    main()
