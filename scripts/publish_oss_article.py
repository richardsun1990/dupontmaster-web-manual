#!/usr/bin/env python3
import hashlib
import html
import io
import json
import os
import re
import shutil
from pathlib import Path
from urllib.parse import quote

import markdown as md
import oss2
import requests
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
manifest_path = ROOT / os.environ.get("PUBLISH_MANIFEST", "publishing/aima-tech/manifest.json")
if not manifest_path.exists():
    print(f"No pending manifest: {manifest_path}")
    raise SystemExit(0)

manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
slug = manifest["slug"].strip()
title = manifest["title"].strip()
date = manifest["date"].strip()
tag = manifest.get("tag", "企业分析").strip()
description = manifest.get("description", "").strip()
source = manifest.get("source", "公司公告、年报、交易所披露文件及 DupontMaster 整理。").strip()
author = manifest.get("author", "DupontMaster 研究院").strip()
cover_name = manifest["cover"]
body = manifest["markdown"].strip()
asset_urls = manifest.get("asset_urls", {})

ak = os.environ["ALIYUN_OSS_ACCESS_KEY_ID"]
sk = os.environ["ALIYUN_OSS_ACCESS_KEY_SECRET"]
bucket_name = os.environ["ALIYUN_OSS_BUCKET"].strip()
endpoint = os.environ["ALIYUN_OSS_ENDPOINT"].strip().replace("https://", "").replace("http://", "").rstrip("/")
public_base = os.environ.get("ALIYUN_OSS_PUBLIC_BASE_URL", "").strip().rstrip("/")
prefix = os.environ.get("ALIYUN_OSS_PREFIX", "blog/admin").strip().strip("/")

if not asset_urls:
    raise RuntimeError("manifest.json 缺少 asset_urls")

auth = oss2.Auth(ak, sk)
bucket = oss2.Bucket(auth, "https://" + endpoint, bucket_name)

def download_and_convert(source_url: str) -> bytes:
    response = requests.get(source_url, timeout=90, allow_redirects=True)
    response.raise_for_status()
    with Image.open(io.BytesIO(response.content)) as image:
        image.load()
        if image.mode in ("RGBA", "LA"):
            canvas = Image.new("RGB", image.size, "white")
            alpha = image.getchannel("A") if image.mode == "RGBA" else image.getchannel("A")
            canvas.paste(image.convert("RGB"), mask=alpha)
            image = canvas
        elif image.mode != "RGB":
            image = image.convert("RGB")
        if image.width > 1600:
            height = round(image.height * 1600 / image.width)
            image = image.resize((1600, height), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        image.save(output, format="WEBP", quality=88, method=6, optimize=True)
        return output.getvalue()

urls = {}
date_part = date.replace("-", "")
for name in manifest["assets"]:
    source_url = asset_urls.get(name)
    if not source_url:
        raise RuntimeError(f"缺少图片地址：{name}")
    raw = download_and_convert(source_url)
    digest = hashlib.sha1(raw).hexdigest()[:10]
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-")
    object_key = f"{prefix}/{slug}/{date_part}-{safe_name}-{digest}"
    bucket.put_object(
        object_key,
        raw,
        headers={
            "Content-Type": "image/webp",
            "Cache-Control": "public, max-age=31536000, immutable",
        },
    )
    encoded_key = "/".join(quote(part, safe="") for part in object_key.split("/"))
    urls[name] = f"{public_base}/{encoded_key}" if public_base else f"https://{bucket_name}.{endpoint}/{encoded_key}"

for name, url in urls.items():
    body = body.replace(f"{{{{image:{name}}}}}", url)

cover_url = urls[cover_name]
frontmatter = "\n".join([
    "---",
    f'title: {json.dumps(title, ensure_ascii=False)}',
    f'date: {json.dumps(date)}',
    f'tag: {json.dumps(tag, ensure_ascii=False)}',
    f'description: {json.dumps(description, ensure_ascii=False)}',
    f'slug: {json.dumps(slug)}',
    f'source: {json.dumps(source, ensure_ascii=False)}',
    "---",
    "",
])
article_md = frontmatter + body + "\n"
content_path = ROOT / "content" / "articles" / f"{slug}.md"
content_path.parent.mkdir(parents=True, exist_ok=True)
content_path.write_text(article_md, encoding="utf-8")

body_for_html = re.sub(r"^# .+\n+", "", body, count=1)
body_html = md.markdown(body_for_html, extensions=["extra", "sane_lists"])
canonical = f"https://www.dupontmaster.com/blog/articles/{quote(slug)}.html"
article_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)} - DupontMaster 杜邦大师</title>
  <meta name="description" content="{html.escape(description)}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{html.escape(cover_url)}">
  <style>
    * {{ margin:0; padding:0; box-sizing:border-box; }}
    body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif; line-height:1.86; color:#172033; background:#f5f6fa; }}
    .nav {{ background:#fff; border-bottom:1px solid #e2e6ef; padding:16px 24px; position:sticky; top:0; z-index:100; }}
    .nav a {{ color:#315be8; text-decoration:none; font-size:15px; margin-right:18px; }}
    .box {{ max-width:960px; margin:40px auto; background:#fff; border-radius:16px; box-shadow:0 8px 30px rgba(25,39,75,.08); overflow:hidden; }}
    .header {{ padding:52px 58px 36px; border-bottom:1px solid #e7eaf1; }}
    .tag {{ display:inline-block; background:rgba(82,74,232,.10); color:#5148dc; padding:5px 13px; border-radius:6px; font-size:13px; margin-bottom:18px; }}
    .title {{ font-size:40px; font-weight:760; line-height:1.28; margin-bottom:16px; color:#101827; }}
    .desc {{ color:#63708a; font-size:17px; margin-bottom:14px; }}
    .meta {{ color:#8b96aa; font-size:14px; }}
    .content {{ padding:46px 58px 56px; }}
    .content h2 {{ font-size:27px; line-height:1.45; font-weight:720; margin:48px 0 20px; color:#101827; border-left:5px solid #5c55ea; padding-left:14px; }}
    .content h3 {{ font-size:21px; font-weight:680; margin:32px 0 14px; color:#101827; }}
    .content p {{ margin-bottom:21px; font-size:17px; color:#283449; }}
    .content img {{ width:100%; height:auto; border-radius:10px; margin:30px 0 34px; display:block; border:1px solid #edf0f6; }}
    .content ul,.content ol {{ margin:20px 0 24px; padding-left:28px; }}
    .content li {{ margin-bottom:10px; font-size:17px; color:#283449; }}
    .content blockquote {{ border-left:4px solid #5c55ea; background:#f5f5ff; padding:18px 22px; margin:28px 0; color:#34356f; border-radius:0 8px 8px 0; }}
    .source-box {{ background:#f8fafc; border:1px solid #e5e9f1; border-radius:10px; padding:18px; margin-top:38px; color:#5e6a7d; font-size:14px; }}
    .cta-box {{ background:linear-gradient(135deg,#252a55 0%,#5b55e7 100%); color:#fff; padding:32px; border-radius:12px; text-align:center; margin:42px 0; }}
    .cta-box h3 {{ color:#fff; margin-bottom:10px; }}
    .cta-box p {{ color:rgba(255,255,255,.83); }}
    .cta-box a {{ display:inline-block; background:#fff; color:#4f48dc; padding:11px 22px; border-radius:8px; text-decoration:none; font-weight:650; margin-top:14px; }}
    footer {{ text-align:center; padding:38px; color:#8a94a7; font-size:13px; }}
    @media(max-width:768px) {{
      .box {{ margin:0; border-radius:0; }}
      .header,.content {{ padding:26px 22px; }}
      .title {{ font-size:30px; }}
      .content h2 {{ font-size:23px; }}
      .content p,.content li {{ font-size:16px; }}
    }}
  </style>
</head>
<body>
  <nav class="nav"><a href="/blog/">&larr; 返回博客</a><a href="https://app.dupontmaster.com/">开始分析公司</a></nav>
  <div class="box">
    <div class="header">
      <span class="tag">{html.escape(tag)}</span>
      <h1 class="title">{html.escape(title)}</h1>
      <p class="desc">{html.escape(description)}</p>
      <div class="meta">作者：{html.escape(author)} · {html.escape(date)}</div>
    </div>
    <div class="content">
      {body_html}
      <div class="source-box"><strong>资料来源：</strong>{html.escape(source)}</div>
      <div class="cta-box"><h3>用 DupontMaster 拆解企业资本回报</h3><p>从利润率、资产周转和财务杠杆重新理解一家企业。</p><a href="https://app.dupontmaster.com/">开始分析</a></div>
    </div>
  </div>
  <footer>© 2026 DupontMaster · 本文不构成投资建议</footer>
</body>
</html>
'''
html_path = ROOT / "blog" / "articles" / f"{slug}.html"
html_path.parent.mkdir(parents=True, exist_ok=True)
html_path.write_text(article_html, encoding="utf-8")

json_path = ROOT / "blog" / "articles.json"
items = json.loads(json_path.read_text(encoding="utf-8"))
items = [x for x in items if x.get("slug") != slug]
items.insert(0, {"id":slug,"title":title,"tag":tag,"date":date,"image":cover_url,"slug":slug,"description":description})
json_path.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

card = f'''
                <a href="/blog/articles/{quote(slug)}.html" style="display:block;background:white;border-radius:12px;padding:20px;text-decoration:none;color:inherit;transition:all .2s;">
                    <div style="display:grid;grid-template-columns:minmax(180px,280px) 1fr;gap:20px;align-items:center;">
                      <img src="{html.escape(cover_url)}" alt="{html.escape(title)}" style="width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:9px;">
                      <div>
                        <span style="display:inline-block;background:rgba(82,74,232,.10);color:#5148dc;padding:4px 10px;border-radius:4px;font-size:12px;margin-bottom:8px;">{html.escape(tag)}</span>
                        <h3 style="font-size:20px;font-weight:650;margin-bottom:8px;">{html.escape(title)}</h3>
                        <p style="color:#657086;font-size:14px;margin-bottom:10px;">{html.escape(description)}</p>
                        <p style="color:#8b94a5;font-size:13px;">{html.escape(date)}</p>
                      </div>
                    </div>
                </a>
'''

def update_index(path, marker):
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    text = re.sub(rf'\s*<a href="/blog/articles/{re.escape(slug)}\.html"[\s\S]*?</a>', '', text)
    pos = text.find(marker)
    if pos >= 0:
        end = text.find(">", pos)
        text = text[:end+1] + card + text[end+1:]
        path.write_text(text, encoding="utf-8")

update_index(ROOT/"blog"/"index.html", '<div class="article-list" data-md-articles="blog"')
update_index(ROOT/"index.html", '<div data-md-articles="home"')

sitemap_path = ROOT/"sitemap.xml"
sitemap = sitemap_path.read_text(encoding="utf-8")
sitemap = re.sub(rf'\s*<url><loc>https://www\.dupontmaster\.com/blog/articles/{re.escape(slug)}(?:\.html)?</loc>.*?</url>', '', sitemap)
entry = f'  <url><loc>{canonical}</loc><lastmod>{date}</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>\n'
sitemap = sitemap.replace("</urlset>", entry + "</urlset>")
sitemap_path.write_text(sitemap, encoding="utf-8")

result_path = ROOT / "publishing-result.json"
result_path.write_text(json.dumps({"slug":slug,"url":canonical,"cover":cover_url,"assets":urls},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
shutil.rmtree(manifest_path.parent)
print(result_path.read_text(encoding="utf-8"))
