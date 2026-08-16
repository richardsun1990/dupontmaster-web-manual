# DupontMaster 文章发布方式

以后官网文章统一以「文章同步助手」为主入口，不再为每篇文章临时制作 HTML。

## 统一发布链路

推荐把微信公众号编辑器作为文章排版母版：

1. 在微信公众号里完成标题、正文、段落层级和全部配图。
2. 打开浏览器里的「文章同步助手」。
3. 勾选需要同步的平台。
4. **固定同时勾选「Markdown 压缩包」**。
5. 点击同步。

文章同步助手会把其他平台按各自能力同步/保存草稿，同时下载一个 Markdown 压缩包。这个压缩包包含：

```text
article.md
images/
  image_....jpg
  image_....png
  ...
```

Mac 上的 DupontMaster 发布桥会自动发现这个 ZIP，并完成：

```text
同步助手 ZIP
→ 读取 article.md
→ 检查正文图片
→ 全部图片上传阿里云 OSS
→ 图片地址改为 OSS URL
→ 保存 Markdown 母稿
→ 生成静态 HTML
→ 更新 articles.json
→ 自动加入匹配专题
→ 更新博客首页 / 官网案例 / sitemap
→ 校验正文图片数量
→ Git commit + push main
→ Vercel 自动部署
```

**图片完整性是硬校验。** 如果同步助手压缩包里有 8 张正文图片，而官网生成页只有 7 张，发布桥会停止 Git 推送，不允许缺图文章上线。

## 第一次安装

前提：本地官网仓库已经配置好 `.oss.env`。如果没有：

```bash
cd /Users/Richard/Downloads/codex_dupontmaster/dupontmaster-web-manual-work
cp .oss.env.example .oss.env
```

填好阿里云 OSS 配置后，在官网仓库执行一次：

```bash
cd /Users/Richard/Downloads/codex_dupontmaster/dupontmaster-web-manual-work
git pull --ff-only origin main
bash scripts/install_wechatsync_watcher.sh
```

安装器会创建 macOS LaunchAgent，大约每 30 秒检查一次 `~/Downloads`。它只处理真正包含 `article.md` 的文章同步助手 ZIP，普通下载压缩包会忽略。

日志：

```text
~/Library/Logs/dupontmaster-wechatsync.log
~/Library/Logs/dupontmaster-wechatsync-error.log
```

## 手动发布 / 调试

如果暂时不启用自动监听，也可以直接运行：

```bash
cd /Users/Richard/Downloads/codex_dupontmaster/dupontmaster-web-manual-work
python3 scripts/publish_wechatsync_zip.py "$HOME/Downloads/文章标题.zip"
```

需要固定英文 URL 时：

```bash
python3 scripts/publish_wechatsync_zip.py "$HOME/Downloads/文章标题.zip" \
  --slug tencent-ai-capital-allocation-2026
```

只生成网站文件、不推 GitHub：

```bash
python3 scripts/publish_wechatsync_zip.py "$HOME/Downloads/文章标题.zip" --no-git
```

## 什么会保留，什么不会 1:1 保留

官网会可靠保留文章的：

- 标题和正文顺序；
- H1/H2/H3 层级；
- 粗体、引用、列表和普通链接；
- 正文图片及图片顺序；
- 图片说明文字。

微信公众号编辑器里的特殊字体、复杂背景框、第三方 SVG 装饰、平台私有组件等，不承诺 1:1 搬到官网。官网统一使用 DupontMaster 自己的文章 CSS，以保证电脑、手机、SEO 和长期维护的一致性。

所以原则是：**内容和图片跟着微信公众号走，官网视觉跟着 DupontMaster 设计系统走。**

## 为什么不直接把官网伪装成 WordPress

文章同步助手原生支持 WordPress / Typecho CMS，并会通过 CMS 接口上传图片。但 DupontMaster 当前是静态站点，并不是 WordPress。

为了让插件直接识别而给官网增加一套假的 WordPress XML-RPC、写入权限、GitHub Token 和图片上传接口，会增加安全面和维护成本。当前方案使用文章同步助手已经提供的「Markdown 压缩包」出口，再由本地发布桥接现有 OSS + GitHub + Vercel 链路，更简单也更稳定。

从使用体验上仍然是一次同步：只要「Markdown 压缩包」被选中，下载完成后官网发布桥会自动接管。

## 老铺黄金这次为什么缺图

当前官网的老铺黄金 HTML 正文里实际上只写入了 1 张图片，也就是封面。缺失的公众号正文配图从一开始就没有进入网站发布源，因此不是 CSS 隐藏或浏览器加载失败。

新的发布桥不会再依赖“人工记得上传图片”：同步助手 ZIP 自带正文图片，发布前又会做图片数量校验，少图即停止。

## Notion 仍可作为备用入口

如果某篇文章不经过微信公众号，仍然可以用旧的 Notion Markdown 导出方式：

```bash
python3 scripts/import_notion_article.py ~/Downloads/Notion导出的文件.zip --slug article-slug
python3 scripts/publish_article.py content/articles/article-slug.md
```

但默认工作流统一使用：

**微信公众号排版 → 文章同步助手 → Markdown 压缩包 → DupontMaster 自动发布桥。**

## 发布原则

- 不写“必涨”“稳赚”等确定性收益承诺。
- 财务数据尽量注明公司公告、年报、交易所披露或其他可验证来源。
- 官网继续保留研究免责声明。
- 发布桥只在 Git 工作区干净时自动提交，避免把其他开发修改混入文章发布。
