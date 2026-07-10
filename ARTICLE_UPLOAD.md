# 文章上传说明

以后发新文章，只需要上传一个 Markdown 文件。

## 最简单方式

1. 复制 `content/articles/_template.md`
2. 改成你的文章文件名，例如 `maotai-2026-analysis.md`
3. 填好文章标题、日期、标签和正文
4. 上传到 GitHub 的 `content/articles/` 目录
5. 网站会自动读取 `content/articles/` 下的 Markdown，并展示在博客页和首页文章区

不需要配置 GitHub Actions，也不需要额外创建 HTML 文件。

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

## Markdown 头部信息

```markdown
---
title: 文章标题
date: 2026-07-10
tag: 企业分析
description: 用一句话说明这篇文章在分析什么。
source: 公司公告、年报、交易所披露文件及 DupontMaster 整理。
---
```

只要正文写好，数据来源和免责声明会自动追加到文章底部。

## 注意

- 不要写确定性投资建议，例如“必涨”“稳赚”“绝对低估”。
- 财务数据尽量写清楚来源。
- 图片可以放在 `blog/articles/images/文章名/`，正文里用 `/blog/articles/images/文章名/图片.png` 引用。
