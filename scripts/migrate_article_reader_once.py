#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
articles_dir = ROOT / 'blog' / 'articles'
updated = []

for html_path in sorted(articles_dir.glob('*.html')):
    text = html_path.read_text(encoding='utf-8')
    original = text

    if '/assets/article-v2.css' not in text:
        text = text.replace(
            '</head>',
            '  <link rel="stylesheet" href="/assets/article-v2.css">\n</head>',
            1,
        )

    if '/assets/article-v2.js' not in text:
        text = text.replace(
            '</body>',
            '  <script src="/assets/article-v2.js"></script>\n</body>',
            1,
        )

    if text != original:
        html_path.write_text(text, encoding='utf-8')
        updated.append(str(html_path.relative_to(ROOT)))

print(f'updated={len(updated)}')
for item in updated:
    print(item)
