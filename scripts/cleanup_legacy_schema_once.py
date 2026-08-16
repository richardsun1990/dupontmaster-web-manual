#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "blog" / "articles.json"
articles = json.loads(CATALOG.read_text(encoding="utf-8"))

script_pattern = re.compile(
    r'\s*<script(?![^>]*id=["\']dm-static-blogposting-v1["\'])[^>]*type=["\']application/ld\+json["\'][^>]*>.*?</script>\s*',
    flags=re.I | re.S,
)

changed = []
for item in articles:
    slug = item.get("slug")
    if not slug:
        continue
    path = ROOT / "blog" / "articles" / f"{slug}.html"
    if not path.exists():
        continue

    text = path.read_text(encoding="utf-8")
    original = text

    def keep_or_remove(match):
        block = match.group(0)
        # Keep non-legacy structured data. Only remove old generic Article blocks;
        # the normalized BlogPosting has a stable id and is excluded by the regex.
        if re.search(r'["\']@type["\']\s*:\s*["\']Article["\']', block, flags=re.I):
            return "\n"
        return block

    text = script_pattern.sub(keep_or_remove, text)
    if text != original:
        path.write_text(text, encoding="utf-8")
        changed.append(slug)

print(f"removed duplicate legacy Article JSON-LD from {len(changed)} articles")
for slug in changed:
    print(slug)
