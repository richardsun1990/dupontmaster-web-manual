# Notion 文章上传说明

以后可以直接在 Notion 写文章，再导出 Markdown 上传。

## 最简单方式

1. 在 Notion 写好文章
2. 右上角 `...` → `Export`
3. 格式选择 `Markdown & CSV`
4. 勾选 `Include subpages` 可以关闭
5. 导出后解压 zip
6. 把 `.md` 文件上传到 GitHub 的 `content/articles/` 目录
7. 如果有图片，把 Notion 导出的同名图片文件夹也一起上传到 `content/articles/`
8. 网站会自动读取 Markdown，并展示在博客页和首页文章区

不需要配置 GitHub Actions，也不需要额外创建 HTML 文件。

## 推荐文件名

Notion 导出的文件名可以直接用，但更建议改成英文短横线：

```text
maotai-2026-analysis.md
guming-reunderstanding.md
```

图片文件夹可以保持 Notion 导出的名字，只要 Markdown 里的图片路径和文件夹对应即可。

## 可选：文章头部信息

如果希望标题、日期、标签更准确，可以在 Markdown 最前面加：

```markdown
---
title: 文章标题
date: 2026-07-10
tag: 企业分析
description: 用一句话说明这篇文章在分析什么。
source: 公司公告、年报、交易所披露文件及 DupontMaster 整理。
---
```

如果不加，网站会自动用 Markdown 的一级标题作为文章标题。

## 本地方式

如果你在电脑本地更新文章：

```bash
cd /Users/Richard/Downloads/codex_dupontmaster/dupontmaster-web-manual-work
python3 scripts/publish_article.py --all
git add .
git commit -m "发布文章：文章标题"
git push origin main
```

本地方式会额外生成静态 HTML 文章页，适合你想提前检查页面效果时使用。

只要正文写好，数据来源和免责声明会自动追加到文章底部。

## 注意

- 不要写确定性投资建议，例如“必涨”“稳赚”“绝对低估”。
- 财务数据尽量写清楚来源。
- Notion 导出的图片相对路径可以保留，网站会自动转换为可访问路径。
