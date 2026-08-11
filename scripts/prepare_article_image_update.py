#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
config_path = ROOT / sys.argv[1]
config = json.loads(config_path.read_text(encoding='utf-8'))

source_path = ROOT / config['source_content_path']
text = source_path.read_text(encoding='utf-8')

# Strip YAML frontmatter but keep the Markdown title/body.
body = re.sub(r'^---\s*\n[\s\S]*?\n---\s*\n', '', text, count=1).strip()

# Remove all existing article images; the update manifest will reinsert the approved set.
body = re.sub(r'\n*!\[[^\]]*\]\([^\n\)]+\)\s*\n*', '\n\n', body)
body = re.sub(r'\n{3,}', '\n\n', body).strip()

for item in config['insertions']:
    anchor = item['anchor']
    image_md = f"![{item['alt']}]({{{{image:{item['name']}}}}})"
    lines = body.splitlines()
    idx = next((i for i, line in enumerate(lines) if anchor in line), None)
    if idx is None:
        raise RuntimeError(f"Image insertion anchor not found: {anchor}")
    lines[idx+1:idx+1] = ['', image_md, '']
    body = '\n'.join(lines)

runtime_dir = Path('/tmp/article-image-update')
runtime_dir.mkdir(parents=True, exist_ok=True)
runtime_manifest = runtime_dir / 'manifest.json'

manifest = {
    'slug': config['slug'],
    'title': config['title'],
    'date': config['date'],
    'tag': config.get('tag', '企业分析'),
    'description': config['description'],
    'source': config['source'],
    'author': config.get('author', 'DupontMaster 研究院'),
    'cover': config['cover'],
    'assets': [x['name'] for x in config['insertions']],
    'asset_urls': {x['name']: x['url'] for x in config['insertions']},
    'markdown': body,
}
runtime_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(runtime_manifest)
