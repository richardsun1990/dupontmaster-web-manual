# Notion 文章上传说明

以后可以直接在 Notion 写文章，再导出 Markdown 上传。

## 最简单方式：一键导入 Notion 导出包

第一次使用前，复制配置文件并填入 OSS 信息：

```bash
cd /Users/Richard/Downloads/codex_dupontmaster/dupontmaster-web-manual-work
cp .oss.env.example .oss.env
```

然后打开 `.oss.env`，填好你的阿里云 OSS 信息。这个文件已被 Git 忽略，不会上传到 GitHub。

之后每次发文章：

1. 在 Notion 写好文章
2. 右上角 `...` → `Export`
3. 格式选择 `Markdown & CSV`
4. 勾选 `Include subpages` 可以关闭
5. 导出后解压 zip
6. 执行：

```bash
cd /Users/Richard/Downloads/codex_dupontmaster/dupontmaster-web-manual-work
python3 scripts/import_notion_article.py ~/Downloads/Notion导出的文件.zip --slug article-slug
git add content/articles
git commit -m "发布文章：文章标题"
git push origin main
```

如果 zip 识别不到 Markdown，也可以先解压，再直接传 `.md` 文件：

```bash
python3 scripts/import_notion_article.py "$HOME/Downloads/英伟达：重新认识这家公司/英伟达：重新认识这家公司 399c4c3fa1598086a342ec54272a5010.md" --slug nvidia-reunderstanding
```

脚本会自动完成：

- 读取 Notion 导出的 Markdown
- 找到 Markdown 里引用的本地图片
- 上传图片到阿里云 OSS
- 把图片路径替换成 OSS 链接
- 把最终文章保存到 `content/articles/`
- 自动补上基础 frontmatter

不需要配置 GitHub Actions，也不需要额外创建 HTML 文件。

## 图片怎么处理

推荐图片走阿里云 OSS，不放进网站仓库。

如果你想手动处理图片，也可以：

1. 把图片上传到阿里云 OSS
2. 复制图片的公开访问链接
3. 在 Notion 里用图片链接插入图片
4. 导出 Markdown 后，网站会直接读取 OSS 图片

Markdown 中图片大概会长这样：

```markdown
![公司 ROE 趋势图](https://你的-bucket.oss-cn-hangzhou.aliyuncs.com/blog/company/roe.png)
```

这样做的好处：

- GitHub 仓库不会越来越大
- 网站页面加载图片时主要走阿里云 OSS
- 后续替换图片时，只需要换 OSS 图片链接
- Notion 导出的 Markdown 可以直接上传

如果你使用上面的一键脚本，就不需要手动复制 OSS 链接。

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
