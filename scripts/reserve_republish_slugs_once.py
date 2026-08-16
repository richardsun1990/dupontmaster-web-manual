#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "scripts" / "publish_wechatsync_zip.py"
text = PATH.read_text(encoding="utf-8")

anchor = 'ARTICLES_JSON = ROOT / "blog" / "articles.json"\nRESULT_JSON = ROOT / "publishing-result.json"\n'
insert = '''ARTICLES_JSON = ROOT / "blog" / "articles.json"\nRESULT_JSON = ROOT / "publishing-result.json"\nRESERVED_SLUG_BY_TITLE = {\n    "528亿之后，马化腾迎来腾讯最大的一次资本配置考试": "tencent-ai-capital-allocation-2026",\n    "老铺黄金的10亿单店：真正的考试，不在金价上涨时": "laopu-gold-10b-store-cycle-test",\n}\n'''
if 'RESERVED_SLUG_BY_TITLE' not in text:
    text = text.replace(anchor, insert, 1)

old = 'slug = args.slug or existing_slug_for_title(title) or stable_slug(title)'
new = 'slug = args.slug or existing_slug_for_title(title) or RESERVED_SLUG_BY_TITLE.get(title.strip()) or stable_slug(title)'
if old in text:
    text = text.replace(old, new, 1)

PATH.write_text(text, encoding="utf-8")
print("reserved republish slugs configured")
