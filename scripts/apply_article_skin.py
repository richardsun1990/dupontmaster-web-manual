#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLE_DIR = ROOT / "blog" / "articles"
ARTICLE_TEMPLATE = ROOT / "blog" / "article.html"
PUBLISH_SCRIPT = ROOT / "scripts" / "publish_oss_article.py"

CSS_LINK = '  <link rel="stylesheet" href="/assets/article-v2.css">\n'
JS_LINK = '  <script src="/assets/article-v2.js"></script>\n'


def patch_html(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text

    if '/assets/article-v2.css' not in text and '</head>' in text:
        text = text.replace('</head>', CSS_LINK + '</head>', 1)

    if '/assets/article-v2.js' not in text and '</body>' in text:
        text = text.replace('</body>', JS_LINK + '</body>', 1)

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def patch_publish_script(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text

    if '/assets/article-v2.css' not in text:
        marker = "  </style>\n</head>"
        replacement = "  </style>\n  <link rel=\"stylesheet\" href=\"/assets/article-v2.css\">\n</head>"
        if marker not in text:
            raise RuntimeError('publish script article template style marker not found')
        text = text.replace(marker, replacement, 1)

    if '/assets/article-v2.js' not in text:
        marker = "  <footer>© 2026 DupontMaster · 本文不构成投资建议</footer>\n</body>"
        replacement = "  <footer>© 2026 DupontMaster · 本文不构成投资建议</footer>\n  <script src=\"/assets/article-v2.js\"></script>\n</body>"
        if marker not in text:
            raise RuntimeError('publish script article template footer marker not found')
        text = text.replace(marker, replacement, 1)

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


changed = []

for path in sorted(ARTICLE_DIR.glob('*.html')):
    if path.name == 'share-component.html':
        continue
    if patch_html(path):
        changed.append(str(path.relative_to(ROOT)))

if patch_html(ARTICLE_TEMPLATE):
    changed.append(str(ARTICLE_TEMPLATE.relative_to(ROOT)))

if patch_publish_script(PUBLISH_SCRIPT):
    changed.append(str(PUBLISH_SCRIPT.relative_to(ROOT)))

print(f'updated {len(changed)} files')
for item in changed:
    print(item)
