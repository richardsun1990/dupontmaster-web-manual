# DupontMaster 官网文章发布手册

> 最后更新：2026-08-16
>
> 当前正式流程已经真实验收通过：**微信公众号排版 → 文章同步助手 → Markdown 压缩包 → Mac 自动发布桥 → 阿里云 OSS → GitHub → Vercel**。

---

## 1. 最终固定发布方式

以后官网文章默认不再手工制作 HTML，也不再单独为官网整理一套正文。

统一以 **微信公众号编辑器作为文章排版母版**：

1. 在微信公众号里完成标题、正文、段落层级、粗体、引用和全部配图。
2. 打开浏览器插件「文章同步助手」。
3. 勾选需要同步的平台。
4. **固定同时勾选「Markdown 压缩包」**。
5. 点击同步。

文章同步助手会下载一个 ZIP，典型结构：

```text
文章标题.zip
├── article.md
└── images/
    ├── image_001.png
    ├── image_002.jpg
    └── ...
```

Mac 上的 DupontMaster 发布桥会自动接管：

```text
文章同步助手 ZIP
→ 读取 article.md
→ 识别正文图片
→ 图片上传阿里云 OSS
→ Markdown 图片地址改写为 OSS URL
→ 保存 Markdown 母稿
→ 生成静态 HTML
→ 更新 articles.json
→ 自动加入匹配专题
→ 更新博客首页
→ 更新官网首页案例
→ 更新 sitemap
→ 写入 canonical / OG / BlogPosting SEO
→ 校验正文图片数量
→ Git commit
→ Git push main
→ Vercel 自动部署
```

### 核心原则

**内容和图片跟着微信公众号走，官网视觉跟着 DupontMaster 自己的文章设计系统走。**

微信公众号里的特殊字体、复杂背景框、第三方 SVG 装饰和平台私有组件不保证 1:1 搬运；标题、正文结构、图片和顺序必须完整保留。

---

## 2. 本地正式工作目录

当前 Mac 固定工作目录：

```text
~/Downloads/dupontmaster-web-manual-work
```

进入目录：

```bash
cd ~/Downloads/dupontmaster-web-manual-work
```

检查仓库：

```bash
git status -sb
```

正常应看到：

```text
## main...origin/main
```

---

## 3. 阿里云 OSS 配置

### 3.1 `.oss.env` 是隐藏文件

文件位置：

```text
~/Downloads/dupontmaster-web-manual-work/.oss.env
```

Finder 默认不显示以 `.` 开头的文件。

显示/隐藏文件快捷键：

```text
Command + Shift + .
```

也可以直接编辑：

```bash
cd ~/Downloads/dupontmaster-web-manual-work
open -a TextEdit .oss.env
```

### 3.2 `.oss.env` 格式

```text
ALIYUN_OSS_ACCESS_KEY_ID=真实AccessKeyID
ALIYUN_OSS_ACCESS_KEY_SECRET=真实AccessKeySecret
ALIYUN_OSS_BUCKET=dupontmaster
ALIYUN_OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
ALIYUN_OSS_PREFIX=blog/wechatsync
```

注意：

- `=` 两边不要加空格。
- 不要加中文引号。
- AccessKey Secret 不要提交到 GitHub。
- `.oss.env` 已在 `.gitignore` 中。
- 不要把 `.oss.env` 截图或发给别人。

检查是否还残留示例文字：

```bash
grep -n "你的" .oss.env
```

无输出表示占位文字已清理。

检查非敏感项：

```bash
grep -E 'ALIYUN_OSS_(BUCKET|ENDPOINT|PREFIX)' .oss.env
```

---

## 4. RAM 用户与最小 OSS 权限

官网发布器使用独立 RAM 用户 AccessKey，不使用主账号 AccessKey。

### 4.1 AccessKey 创建方式

阿里云：

```text
RAM 访问控制
→ 身份管理
→ 用户
→ DupontMaster / OSS 对应 RAM 用户
→ 凭证管理
→ 创建 AccessKey
```

使用场景选择：

```text
本地开发环境中使用
```

创建完成后立即保存：

```text
AccessKey ID
AccessKey Secret
```

Secret 创建后无法再次查看；丢失就重新创建，不要尝试恢复。

### 4.2 推荐最小权限

策略名称：

```text
DupontMasterBlogPublisher
```

JSON：

```json
{
  "Version": "1",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "oss:PutObject"
      ],
      "Resource": [
        "acs:oss:*:*:dupontmaster/blog/wechatsync/*"
      ]
    }
  ]
}
```

然后：

```text
RAM 用户
→ 权限管理
→ 新增授权
→ DupontMasterBlogPublisher
```

长期不建议给 `AliyunOSSFullAccess`。

---

## 5. GitHub SSH 配置

自动发布必须能够无人值守 `git push`，所以本机使用 SSH，不使用 GitHub 用户名+密码。

### 5.1 SSH 公钥

如第一次配置：

```bash
ssh-keygen -t ed25519 -C "richardsun1990@github"
```

为了后台自动发布，文件位置和 passphrase 均可直接回车使用默认值。

启动 agent：

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

复制公钥：

```bash
pbcopy < ~/.ssh/id_ed25519.pub
```

GitHub：

```text
Settings
→ SSH and GPG keys
→ New SSH key
→ Authentication Key
```

测试：

```bash
ssh -T git@github.com
```

成功时会看到类似：

```text
Hi richardsun1990! You've successfully authenticated...
```

### 5.2 仓库必须使用 SSH remote

```bash
cd ~/Downloads/dupontmaster-web-manual-work
git remote set-url origin git@github.com:richardsun1990/dupontmaster-web-manual.git
```

检查：

```bash
git remote -v
```

应该是：

```text
origin  git@github.com:richardsun1990/dupontmaster-web-manual.git (fetch)
origin  git@github.com:richardsun1990/dupontmaster-web-manual.git (push)
```

---

## 6. 安装自动监听器

首次安装：

```bash
cd ~/Downloads/dupontmaster-web-manual-work
git pull --ff-only origin main
bash scripts/install_wechatsync_watcher.sh
```

监听器使用 macOS LaunchAgent，约每 30 秒扫描一次：

```text
~/Downloads
```

它只处理真正包含 `article.md` 的文章同步助手 ZIP，普通 ZIP 会自动忽略。

查看 LaunchAgent：

```bash
launchctl print gui/$(id -u)/com.dupontmaster.wechatsync-publisher | head -30
```

日志：

```text
~/Library/Logs/dupontmaster-wechatsync.log
~/Library/Logs/dupontmaster-wechatsync-error.log
```

查看日志：

```bash
tail -50 ~/Library/Logs/dupontmaster-wechatsync.log
```

```bash
tail -80 ~/Library/Logs/dupontmaster-wechatsync-error.log
```

---

## 7. 正常日常发布：以后只做这几步

日常情况下不需要打开终端。

```text
① 微信公众号编辑器排好文章
② 图片全部放好
③ 打开文章同步助手
④ 勾选目标平台
⑤ 固定勾选 Markdown 压缩包
⑥ 点击同步
⑦ ZIP 下载到 ~/Downloads
⑧ 等待约 30 秒
⑨ 官网发布桥自动完成剩余步骤
```

如果 Vercel 当时存在 Free 计划构建频率限制，GitHub 可能已经成功更新，但 Production 页面会延迟部署。这不是文章发布器失败。

---

## 8. 图片完整性硬校验

这是整个流程最重要的保护。

假设同步助手 ZIP 中正文有：

```text
8 张图片
```

官网最终生成页必须至少有：

```text
8 张正文图片
```

否则发布器停止，不允许继续推 GitHub。

成功时会看到：

```text
图片完整性通过：8 / 8
```

这条机制是为了解决曾经出现的“老铺黄金文章发布成功，但公众号正文图片没有同步进官网”的问题。

---

## 9. 手动发布 / 调试

如果自动监听器暂时没有触发，可手动指定 ZIP：

```bash
cd ~/Downloads/dupontmaster-web-manual-work
python3 scripts/publish_wechatsync_zip.py "$HOME/Downloads/文章标题.zip"
```

如果要强制指定 slug：

```bash
python3 scripts/publish_wechatsync_zip.py "$HOME/Downloads/文章标题.zip" \
  --slug article-slug
```

只生成网站文件、不提交 Git：

```bash
python3 scripts/publish_wechatsync_zip.py "$HOME/Downloads/文章标题.zip" --no-git
```

手动运行监听器：

```bash
python3 scripts/watch_wechatsync_downloads.py
```

---

## 10. 重新发布已有文章

如果公众号里重新整理了文章格式或补充了图片，可以重新同步。

发布器会优先按文章标题匹配已有 `articles.json`，复用原来的 slug 和 URL，避免重复页面。

目前两篇明确保留旧 URL 的文章：

```text
《528亿之后，马化腾迎来腾讯最大的一次资本配置考试》
→ /blog/articles/tencent-ai-capital-allocation-2026.html

《老铺黄金的10亿单店：真正的考试，不在金价上涨时》
→ /blog/articles/laopu-gold-10b-store-cycle-test.html
```

原则：**重新发布内容可以变化，正式 URL 尽量不要变化。**

---

## 11. 常见报错与处理

### 11.1 `No such file or directory`

通常是本地路径错了。

当前正确目录：

```bash
cd ~/Downloads/dupontmaster-web-manual-work
```

---

### 11.2 `fatal: not a git repository`

说明终端没有进入正式 clone 的 Git 仓库。

```bash
cd ~/Downloads/dupontmaster-web-manual-work
git status
```

---

### 11.3 `ALIYUN_OSS_BUCKET=你的 bucket 名`

说明 `.oss.env` 仍然是示例模板。

必须替换成真实配置。

---

### 11.4 `SSL: CERTIFICATE_VERIFY_FAILED`

python.org 版 Python 在 macOS 可能缺证书。

```bash
/Applications/Python\ 3.11/Install\ Certificates.command
```

测试 HTTPS：

```bash
python3 - <<'PY'
import urllib.request
print(urllib.request.urlopen("https://oss-cn-hangzhou.aliyuncs.com", timeout=10).status)
PY
```

---

### 11.5 `HTTP 403 / InvalidAccessKeyId`

AccessKey ID 无效、已删除或填写错误。

处理方式：在对应 RAM 用户下重新创建 AccessKey，并更新 `.oss.env`。

---

### 11.6 `HTTP 403 / AccessDenied`

AccessKey 有效，但 RAM 用户没有 OSS 上传权限。

检查是否授权：

```text
DupontMasterBlogPublisher
```

以及是否包含：

```text
oss:PutObject
```

---

### 11.7 GitHub 要求 Username / Password

说明 remote 仍然是 HTTPS，自动发布无法无人值守 push。

改成 SSH：

```bash
git remote set-url origin git@github.com:richardsun1990/dupontmaster-web-manual.git
```

---

### 11.8 `main...origin/main [ahead 1]`

表示文章已经 commit 到本地，但还没 push。

```bash
git push origin main
```

推送后检查：

```bash
git status -sb
```

正常为：

```text
## main...origin/main
```

---

## 12. 发布后自动维护的内容

每次成功发布后，系统会自动处理：

- `content/articles/<slug>.md`
- `blog/articles/<slug>.html`
- `blog/articles.json`
- 对应专题页
- 博客首页静态 fallback
- 官网首页最新案例
- `sitemap.xml`
- canonical
- Open Graph
- `article:published_time`
- `article:section`
- `BlogPosting` JSON-LD
- 相关阅读
- GA 阅读 / 分享 / 专题点击统计

文章正文不需要人工再补一次 SEO。

---

## 13. Notion 作为备用入口

如果某篇文章没有经过公众号，仍然可以使用 Notion Markdown：

```bash
python3 scripts/import_notion_article.py ~/Downloads/Notion导出的文件.zip --slug article-slug
python3 scripts/render_article.py content/articles/article-slug.md
```

`render_article.py` 会走当前统一博客结构和 SEO 后处理。

不要再使用旧 `publish_article.py` 作为新文章的默认入口。

---

## 14. 发布原则

- 不使用“必涨”“稳赚”等确定性投资收益承诺。
- 财务数据尽量注明公司公告、年报、交易所披露或其他可验证来源。
- 官网保留研究免责声明。
- `.oss.env`、AccessKey Secret、SSH 私钥严禁提交 GitHub。
- 发布桥仅在 Git 工作区可安全处理时提交，避免把其他开发修改混进文章提交。
- 文章可以重新发布，但正式 URL 尽量保持稳定。

---

# 一句话版本

以后发布文章，只需要记住：

> **微信公众号排好版和图片 → 文章同步助手勾选目标平台 + Markdown 压缩包 → 点击同步。剩下交给 DupontMaster 自动发布桥。**
