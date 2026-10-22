#!/usr/bin/env python3
"""Dependency-free QA for the static creator landing page."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

class PageLinks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.references = []
        self.ids = []
        self.images = []
        self.links = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if d.get('id'):
            self.ids.append(d['id'])
        if tag == 'img':
            self.images.append(d)
        if tag in ('a', 'link', 'script', 'img'):
            for field in ('href', 'src'):
                if d.get(field):
                    self.references.append((tag, field, d[field]))
        if tag == 'a':
            self.links.append(d)

def load(path):
    return (ROOT / path).read_text('utf-8')

def parse(path):
    p = PageLinks()
    p.feed(load(path))
    return p

home = parse('index.html')
creator = parse('creator/index.html')
html = load('creator/index.html')
css = load('assets/creator-v1.css')
analytics = load('assets/analytics-v1.js')
errors = []

for entry, p in [('index.html', home), ('creator/index.html', creator)]:
    if len(p.ids) != len(set(p.ids)):
        errors.append(f'{entry}: duplicate element ID')
    for img in p.images:
        if 'alt' not in img:
            errors.append(f'{entry}: missing alt attribute (empty alt is valid for decorative logos)')
    for _, _, link in p.references:
        if link.startswith(('mailto:', 'https:', 'http:', 'data:', 'javascript:', '//')):
            continue
        url = urlsplit(link)
        path = url.path
        if not path:
            if url.fragment and url.fragment not in p.ids:
                errors.append(f'{entry}: unresolved fragment #{url.fragment}')
            continue
        dest = (ROOT / path.lstrip('/')) if path.startswith('/') else (ROOT / Path(entry).parent / path)
        if dest.is_dir():
            dest /= 'index.html'
        if not dest.is_file():
            errors.append(f'{entry}: nonexistent local URL {link}')
        if url.fragment and path == '/' and url.fragment not in home.ids:
            errors.append(f'{entry}: missing homepage fragment {url.fragment}')

required_creator = ('申请创作者体验', '真实研究与反馈', '一次性体验码',
                    '一个账号只支持兑换一次', '14 天 Pro', '不要求好评', 'mailto:crazymanrichard1990@gmail.com')
for phrase in required_creator:
    if phrase not in html:
        errors.append(f'creator page missing: {phrase}')
if sum(x.get('href') == '/creator/' for x in home.links) < 2:
    errors.append('homepage should link to creator page at least twice')
if not re.search(r'<link rel="canonical" href="https://www\.dupontmaster\.com/creator/"', html):
    errors.append('missing canonical URL')
if 'pageType = location.pathname === \'/creator/\'' not in analytics:
    errors.append('creator page missing GA4 page type')
if '@media(max-width:760px)' not in css:
    errors.append('creator mobile breakpoint missing')
if '不能构成投资建议' in html:
    errors.append('check legal disclaimer language for consistency')
if errors:
    print('\n'.join('FAIL: ' + e for e in errors))
    sys.exit(1)
print(f'PASS: homepage and creator page, {len(creator.references)} creator references, {len(creator.images)} real product images.')
