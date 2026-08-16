#!/usr/bin/env python3
"""Publish a Wechatsync "Markdown 压缩包" to DupontMaster.

The zip exported by 文章同步助手 contains article.md plus images/. This bridge:
1. extracts the package;
2. uploads every local body image to Aliyun OSS;
3. writes a canonical Markdown source under content/articles/;
4. generates the static article page;
5. verifies that no body images were lost;
6. refreshes topics/home/blog/sitemap metadata;
7. optionally commits and pushes to GitHub.

Usage:
  python3 scripts/publish_wechatsync_zip.py ~/Downloads/文章标题.zip
  python3 scripts/publish_wechatsync_zip.py ~/Downloads/文章标题.zip --slug tencent-ai-capital-allocation-2026
  python3 scripts/publish_wechatsync_zip.py ~/Downloads/文章标题.zip --no-git
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

from import_notion_article import load_env_file, rewrite_images

ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = ROOT / "content" / "articles"
ARTICLE_DIR = ROOT / "blog" / "articles"
ARTICLES_JSON = ROOT / "blog" / "articles.json"
RESULT_JSON = ROOT / "publishing-result.json"
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=check,
    )


def extract_title(markdown: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            title = re.sub(r"[*_`]+", "", line[2:]).strip()
            if title:
                return title
    raise SystemExit("同步助手压缩包里的 article.md 没有一级标题（# 标题），无法发布。")


def first_paragraph(markdown: str) -> str:
    blocks = re.split(r"\n\s*\n", markdown)
    for block in blocks:
        text = block.strip()
        if not text or text.startswith("#") or text.startswith("!") or text.startswith("---"):
            continue
        if text.startswith(">"):
            text = re.sub(r"^>\s*", "", text)
        text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        text = re.sub(r"[*_`>#]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            return text[:140]
    return ""


def stable_slug(title: str) -> str:
    # Stable across repeated exports. If the title contains useful latin tokens, keep them;
    # otherwise use a deterministic short hash rather than a fragile filename-derived slug.
    latin = "-".join(re.findall(r"[A-Za-z0-9]+", title.lower()))
    latin = re.sub(r"-+", "-", latin).strip("-")[:42]
    digest = hashlib.sha1(title.encode("utf-8")).hexdigest()[:10]
    return f"{latin}-{digest}".strip("-") if latin else f"article-{digest}"


def yaml_safe(value: str) -> str:
    # publish_article.py uses a deliberately simple frontmatter parser. Keep each value one line
    # and avoid surrounding quotes so Chinese punctuation is preserved literally.
    return re.sub(r"\s+", " ", value).strip()


def find_article_md(folder: Path) -> Path:
    preferred = folder / "article.md"
    if preferred.exists():
        return preferred
    candidates = sorted(folder.rglob("*.md"))
    if len(candidates) == 1:
        return candidates[0]
    raise SystemExit("这不是文章同步助手的 Markdown 压缩包：未找到唯一的 article.md。")


def extract_zip(source: Path) -> tuple[tempfile.TemporaryDirectory[str], Path]:
    if source.suffix.lower() != ".zip" or not source.is_file():
        raise SystemExit("请输入文章同步助手下载的 .zip 文件。")
    temp = tempfile.TemporaryDirectory(prefix="wechatsync-")
    with zipfile.ZipFile(source) as zf:
        # Refuse path traversal from an unexpected archive.
        root = Path(temp.name).resolve()
        for member in zf.infolist():
            target = (root / member.filename).resolve()
            if root not in target.parents and target != root:
                temp.cleanup()
                raise SystemExit("压缩包包含非法路径，已停止导入。")
        zf.extractall(root)
    return temp, Path(temp.name)


def add_frontmatter(markdown: str, *, title: str, slug: str, description: str, image: str) -> str:
    today = datetime.now().astimezone().strftime("%Y-%m-%d")
    source = "公司公告、年报、交易所披露文件及 DupontMaster 整理。"
    lines = [
        "---",
        f"title: {yaml_safe(title)}",
        f"slug: {slug}",
        f"date: {today}",
        "tag: 企业分析",
        f"description: {yaml_safe(description or title)}",
    ]
    if image:
        lines.append(f"image: {image}")
    lines += [f"source: {source}", "---", ""]
    # Strip any frontmatter exported by another editor; the website metadata above is authoritative.
    if markdown.startswith("---\n"):
        end = markdown.find("\n---", 4)
        if end != -1:
            markdown = markdown[markdown.find("\n", end + 4) + 1 :]
    return "\n".join(lines) + markdown.lstrip()


def update_catalog_description(slug: str, description: str, image: str) -> None:
    data = json.loads(ARTICLES_JSON.read_text(encoding="utf-8"))
    found = False
    for item in data:
        if item.get("slug") == slug:
            item["description"] = description
            item["href"] = f"/blog/articles/{slug}.html"
            if image:
                item["image"] = image
            found = True
            break
    if not found:
        raise RuntimeError(f"articles.json 中没有找到刚发布的文章：{slug}")
    ARTICLES_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def postprocess(slug: str) -> None:
    RESULT_JSON.write_text(json.dumps({"slug": slug}, ensure_ascii=False) + "\n", encoding="utf-8")
    try:
        result = run(sys.executable, "scripts/postprocess_published_article.py")
        if result.stdout:
            print(result.stdout.strip())
    finally:
        RESULT_JSON.unlink(missing_ok=True)


def count_html_body_images(html_path: Path) -> int:
    html = html_path.read_text(encoding="utf-8")
    match = re.search(r'<div class="content">(.*?)<div class="source-box">', html, flags=re.S)
    target = match.group(1) if match else html
    return len(re.findall(r"<img\b", target, flags=re.I))


def ensure_clean_git() -> None:
    status = run("git", "status", "--porcelain").stdout.strip()
    if status:
        raise SystemExit(
            "官网仓库存在尚未提交的本地修改。为避免把别的工作混进文章发布，已停止自动发布。\n"
            + status
        )


def commit_and_push(slug: str, title: str) -> None:
    run("git", "add", "content/articles", "blog/articles", "blog/articles.json", "blog/topics.json", "blog/topics", "blog/index.html", "index.html", "sitemap.xml")
    staged = run("git", "diff", "--cached", "--name-only").stdout.strip()
    if not staged:
        print("没有新的站点文件需要提交。")
        return
    run("git", "commit", "-m", f"发布官网文章：{title}")
    push = run("git", "push", "origin", "main")
    if push.stdout:
        print(push.stdout.strip())
    print(f"已推送 GitHub：{slug}")


def main() -> None:
    parser = argparse.ArgumentParser(description="发布文章同步助手 Markdown 压缩包到 DupontMaster 官网")
    parser.add_argument("zip", help="文章同步助手下载的 Markdown 压缩包")
    parser.add_argument("--slug", help="可选：指定英文 URL slug")
    parser.add_argument("--no-git", action="store_true", help="只生成网站文件，不提交/推送 GitHub")
    args = parser.parse_args()

    source = Path(args.zip).expanduser().resolve()
    load_env_file()

    if not args.no_git:
        ensure_clean_git()
        # Pull before touching generated files so a background watcher never publishes from stale main.
        pull = run("git", "pull", "--ff-only", "origin", "main")
        if pull.stdout:
            print(pull.stdout.strip())
        ensure_clean_git()

    temp, folder = extract_zip(source)
    try:
        md_path = find_article_md(folder)
        raw = md_path.read_text(encoding="utf-8")
        title = extract_title(raw)
        slug = args.slug or stable_slug(title)
        input_image_count = len(IMAGE_RE.findall(raw))

        rewritten = rewrite_images(raw, md_path, slug)
        output_image_urls = IMAGE_RE.findall(rewritten)
        if len(output_image_urls) < input_image_count:
            raise SystemExit(
                f"图片完整性校验失败：同步助手包内 {input_image_count} 张，上传后只剩 {len(output_image_urls)} 张。已停止发布。"
            )

        description = first_paragraph(rewritten) or title
        cover = output_image_urls[0] if output_image_urls else ""
        final_md = add_frontmatter(
            rewritten,
            title=title,
            slug=slug,
            description=description,
            image=cover,
        )

        CONTENT_DIR.mkdir(parents=True, exist_ok=True)
        output_md = CONTENT_DIR / f"{slug}.md"
        output_md.write_text(final_md, encoding="utf-8")

        published = run(sys.executable, "scripts/publish_article.py", str(output_md.relative_to(ROOT)))
        if published.stdout:
            print(published.stdout.strip())

        update_catalog_description(slug, description, cover)
        postprocess(slug)

        html_path = ARTICLE_DIR / f"{slug}.html"
        if not html_path.exists():
            raise RuntimeError(f"静态文章页未生成：{html_path}")
        html_image_count = count_html_body_images(html_path)
        if html_image_count < input_image_count:
            # Do not commit a page that silently dropped inline images.
            raise SystemExit(
                f"官网正文图片校验失败：同步助手包内 {input_image_count} 张，生成页只有 {html_image_count} 张。已停止 Git 推送。"
            )

        print(f"图片完整性通过：{input_image_count} / {html_image_count}")
        print(f"官网文章：/blog/articles/{slug}.html")

        if not args.no_git:
            commit_and_push(slug, title)
    finally:
        temp.cleanup()


if __name__ == "__main__":
    main()
