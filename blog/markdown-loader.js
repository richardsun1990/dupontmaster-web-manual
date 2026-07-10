(function () {
  const repo = 'richardsun1990/dupontmaster-web-manual';
  const branch = 'main';
  const contentDir = 'content/articles';
  const apiUrl = `https://api.github.com/repos/${repo}/contents/${contentDir}?ref=${branch}`;
  const rawBase = `https://raw.githubusercontent.com/${repo}/${branch}/${contentDir}`;

  function parseFrontmatter(text) {
    if (!text.startsWith('---')) return [{}, text];
    const end = text.indexOf('\n---', 3);
    if (end === -1) return [{}, text];
    const raw = text.slice(3, end).trim();
    const body = text.slice(text.indexOf('\n', end + 4) + 1);
    const meta = {};
    raw.split('\n').forEach((line) => {
      const index = line.indexOf(':');
      if (index === -1) return;
      const key = line.slice(0, index).trim().toLowerCase();
      const value = line.slice(index + 1).trim().replace(/^['"]|['"]$/g, '');
      meta[key] = value;
    });
    return [meta, body];
  }

  function stripMarkdown(value) {
    return value
      .replace(/!\[[^\]]*\]\([^)]+\)/g, '')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/[*_`>#-]/g, '')
      .replace(/\s+/g, ' ')
      .trim();
  }

  function firstHeading(body) {
    const found = body.split('\n').find((line) => line.startsWith('# '));
    return found ? stripMarkdown(found.slice(2)) : '';
  }

  function firstParagraph(body) {
    const block = body.split(/\n\s*\n/).find((item) => {
      const text = stripMarkdown(item);
      return text && !text.startsWith('#');
    });
    return block ? stripMarkdown(block).slice(0, 140) : '';
  }

  function escapeHtml(value) {
    return String(value || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function isExternalUrl(value) {
    return /^(https?:)?\/\//i.test(value) || value.startsWith('/');
  }

  function rawContentUrl(value) {
    if (isExternalUrl(value)) return value;
    const clean = value.replace(/^\.\//, '');
    return `${rawBase}/${clean.split('/').map(encodeURIComponent).join('/')}`;
  }

  function inlineMarkdown(value) {
    return escapeHtml(value)
      .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (_, alt, src) => `<img src="${rawContentUrl(src)}" alt="${alt}">`)
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>')
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/`([^`]+)`/g, '<code>$1</code>');
  }

  function markdownToHtml(body) {
    const blocks = [];
    const lines = body.split('\n');
    let i = 0;
    while (i < lines.length) {
      const line = lines[i].trimEnd();
      if (!line) {
        i += 1;
        continue;
      }
      if (line.startsWith('# ')) {
        i += 1;
        continue;
      }
      if (line.startsWith('## ')) {
        blocks.push(`<h2>${inlineMarkdown(line.slice(3).trim())}</h2>`);
        i += 1;
        continue;
      }
      if (line.startsWith('### ')) {
        blocks.push(`<h3>${inlineMarkdown(line.slice(4).trim())}</h3>`);
        i += 1;
        continue;
      }
      if (/^[-*]\s+/.test(line)) {
        const items = [];
        while (i < lines.length && /^[-*]\s+/.test(lines[i].trim())) {
          items.push(`<li>${inlineMarkdown(lines[i].trim().replace(/^[-*]\s+/, ''))}</li>`);
          i += 1;
        }
        blocks.push(`<ul>${items.join('')}</ul>`);
        continue;
      }
      const paragraph = [line.trim()];
      i += 1;
      while (i < lines.length && lines[i].trim() && !/^(#{1,3} |[-*]\s+)/.test(lines[i].trim())) {
        paragraph.push(lines[i].trim());
        i += 1;
      }
      blocks.push(`<p>${inlineMarkdown(paragraph.join(' '))}</p>`);
    }
    return blocks.join('\n');
  }

  function slugFromFileName(name) {
    return name.replace(/\.md$/i, '');
  }

  function articleUrl(slug) {
    return `/blog/article.html?slug=${encodeURIComponent(slug)}`;
  }

  async function fetchArticles() {
    const listResponse = await fetch(apiUrl);
    if (!listResponse.ok) return [];
    const files = await listResponse.json();
    const markdownFiles = files
      .filter((file) => file.type === 'file' && /\.md$/i.test(file.name) && !file.name.startsWith('_'))
      .slice(0, 30);
    const articles = await Promise.all(markdownFiles.map(async (file) => {
      const response = await fetch(`${rawBase}/${encodeURIComponent(file.name)}`);
      if (!response.ok) return null;
      const text = await response.text();
      const [meta, body] = parseFrontmatter(text);
      const slug = meta.slug || slugFromFileName(file.name);
      return {
        slug,
        title: meta.title || firstHeading(body) || slug,
        date: meta.date || '',
        tag: meta.tag || '企业分析',
        description: meta.description || firstParagraph(body),
        source: meta.source || '公司公告、年报、交易所披露文件及 DupontMaster 整理。',
        body,
      };
    }));
    return articles
      .filter(Boolean)
      .sort((a, b) => String(b.date).localeCompare(String(a.date)));
  }

  function card(article, homepage) {
    const margin = homepage ? ' margin-bottom: 12px;' : ' transition: all 0.2s;';
    return `<a href="${articleUrl(article.slug)}" style="display: block; background: white; border-radius: 12px; padding: 20px; text-decoration: none; color: inherit;${margin}">
      <span style="display: inline-block; background: rgba(0,113,227,0.1); color: #0071e3; padding: 4px 10px; border-radius: 4px; font-size: 12px; margin-bottom: 8px;">${escapeHtml(article.tag)}</span>
      <h3 style="font-size: 18px; font-weight: 600; margin-bottom: 8px;">${escapeHtml(article.title)}</h3>
      <p style="color: #86868b; font-size: 14px;">${escapeHtml(article.date)}</p>
    </a>`;
  }

  async function renderArticleList() {
    const target = document.querySelector('[data-md-articles]');
    if (!target) return;
    const homepage = target.getAttribute('data-md-articles') === 'home';
    const limit = Number(target.getAttribute('data-limit') || (homepage ? 5 : 30));
    try {
      const articles = await fetchArticles();
      if (!articles.length) return;
      target.insertAdjacentHTML('afterbegin', articles.slice(0, limit).map((item) => card(item, homepage)).join(''));
    } catch (error) {
      console.warn('Markdown articles load failed:', error);
    }
  }

  async function renderArticlePage() {
    const target = document.querySelector('[data-md-article-page]');
    if (!target) return;
    const params = new URLSearchParams(window.location.search);
    const slug = params.get('slug');
    if (!slug) return;
    try {
      const articles = await fetchArticles();
      const article = articles.find((item) => item.slug === slug);
      if (!article) {
        target.innerHTML = '<p>文章不存在或尚未发布。</p>';
        return;
      }
      document.title = `${article.title} - DupontMaster 杜邦大师`;
      const title = document.querySelector('[data-md-title]');
      const meta = document.querySelector('[data-md-meta]');
      const tag = document.querySelector('[data-md-tag]');
      if (title) title.textContent = article.title;
      if (meta) meta.textContent = `${article.date} · ${article.tag}`;
      if (tag) tag.textContent = article.tag;
      target.innerHTML = `${markdownToHtml(article.body)}
        <div class="source-box">
          <p><strong>数据来源：</strong>${escapeHtml(article.source)}</p>
          <p><strong>免责声明：</strong>本文仅供学习研究参考，不构成任何证券投资建议、投资顾问服务或买卖依据。投资有风险，决策需谨慎。</p>
        </div>`;
    } catch (error) {
      target.innerHTML = '<p>文章加载失败，请稍后重试。</p>';
      console.warn('Markdown article page load failed:', error);
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    renderArticleList();
    renderArticlePage();
  });
})();
