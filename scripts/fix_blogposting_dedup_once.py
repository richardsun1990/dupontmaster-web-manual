#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POST = ROOT / "scripts" / "postprocess_published_article.py"

text = POST.read_text(encoding="utf-8")
old = "if '\"@type\": \"BlogPosting\"' not in html_text and \"'@type': 'BlogPosting'\" not in html_text:"
new = "if not re.search(r'[\\\"\\\']@type[\\\"\\\']\\\\s*:\\s*[\\\"\\\']BlogPosting[\\\"\\\']', html_text):"
if old in text:
    text = text.replace(old, new, 1)
    POST.write_text(text, encoding="utf-8")

pattern = re.compile(r'\s*<script type="application/ld\+json">.*?</script>\s*', re.S)
changed = 0
for path in (ROOT / "blog" / "articles").glob("*.html"):
    html = path.read_text(encoding="utf-8")
    seen_blogposting = False
    pieces = []
    last = 0
    modified = False
    for match in pattern.finditer(html):
        block = match.group(0)
        is_blogposting = bool(re.search(r'["\']@type["\']\s*:\s*["\']BlogPosting["\']', block))
        if is_blogposting:
            if seen_blogposting:
                pieces.append(html[last:match.start()])
                last = match.end()
                modified = True
                continue
            seen_blogposting = True
    if modified:
        pieces.append(html[last:])
        path.write_text(''.join(pieces), encoding="utf-8")
        changed += 1

print(f"deduped BlogPosting in {changed} article(s)")
