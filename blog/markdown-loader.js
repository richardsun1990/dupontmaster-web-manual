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
    return String(value || '')
      .replace(/!\[[^\]]*\]\([^)]+\)/g, '')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
      .replace(/[\*_`>#-]/g, '')
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
      return text && !text.startsWith('#') && !text.startsWith('{{');
    });
    return block ? stripMarkdown(block).slice(0, 160) : '';
  }

  function escapeHtml(value) {
    return String(value || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function isExternalUrl(value) {
    return /^(https?:)?\/\//i.test(value) || value.startsWith('/') || value.startsWith('data:');
  }

  function rawContentUrl(value) {
    if (isExternalUrl(value)) return value;
    const clean = value.replace(/^\.\//, '');
    return `${rawBase}/${clean.split('/').map(encodeURIComponent).join('/')}`;
  }

  function inlineMarkdown(value) {
    let html = escapeHtml(value);
    html = html.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (_, alt, src) =>
      `<a class="dm-chart-link" href="https://app.dupontmaster.com/" target="_blank" rel="noopener noreferrer"><img src="${rawContentUrl(src)}" alt="${alt}" loading="lazy" decoding="async"></a>`
    );
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    return html;
  }

  function visualBlock(token) {
    if (token === '{{DRAM_PRINCIPLE}}') {
      return `<section class="dm-visual dm-memory">
        <div class="dm-visual-title"><span>01</span><div><strong>DRAM工作原理与存储位置</strong><small>从存储层级理解单位bit成本</small></div></div>
        <div class="dm-memory-grid">
          <div class="dm-panel">
            <h4>存储层级</h4>
            <div class="dm-stack">
              <div class="dm-tier cache"><b>CPU / GPU Cache</b><small>容量小 · 速度最快</small></div>
              <div class="dm-tier dram"><b>DRAM 运行内存</b><small>GB至数百GB · 纳秒级</small></div>
              <div class="dm-tier storage"><b>SSD / HDD</b><small>容量大 · 长期存储</small></div>
            </div>
          </div>
          <div class="dm-panel">
            <h4>1T1C存储单元</h4>
            <div class="dm-cell-row">
              <div class="dm-transistor">T<span>晶体管</span></div><div class="dm-wire"></div><div class="dm-capacitor">C<span>电容</span></div>
            </div>
            <div class="dm-state-row"><span class="on">有电 = 1</span><span>无电 = 0</span><span class="refresh">需要周期刷新</span></div>
          </div>
        </div>
        <div class="dm-insight"><b>核心本质：</b>DRAM竞争不只是“能不能做出来”，而是每片晶圆能生产多少合格bit。</div>
      </section>`;
    }
    if (token === '{{AI_TRANSMISSION}}') {
      return `<section class="dm-visual">
        <div class="dm-visual-title"><span>02</span><div><strong>AI红利如何传导到长鑫</strong><small>直接需求与供给挤压同时发生</small></div></div>
        <div class="dm-flow">
          <div class="dm-flow-card"><i>1</i><b>AI需求爆发</b><small>数据中心扩张<br>GPU出货增长</small></div>
          <div class="dm-arrow">→</div>
          <div class="dm-flow-card"><i>2</i><b>三巨头加码HBM</b><small>先进晶圆与封装资源<br>向高端产品集中</small></div>
          <div class="dm-arrow">→</div>
          <div class="dm-flow-card"><i>3</i><b>普通DRAM供给趋紧</b><small>DDR / LPDDR产能<br>被HBM挤占</small></div>
          <div class="dm-arrow">→</div>
          <div class="dm-flow-card benefit"><i>4</i><b>长鑫受益</b><small>普通DRAM涨价<br>服务器DDR5需求提升</small></div>
        </div>
        <div class="dm-insight"><b>当前定位：</b>普通DRAM涨价的高弹性受益者 + 服务器DDR5追赶者，而不是HBM龙头。</div>
      </section>`;
    }
    if (token === '{{CAPITAL_RETURN}}') {
      return `<section class="dm-visual">
        <div class="dm-visual-title"><span>03</span><div><strong>技术、资本与股东回报的核心矛盾</strong><small>生存能力与每股价值不是同一件事</small></div></div>
        <div class="dm-three-cols">
          <div class="dm-col"><h4>长期资本</h4><p>地方国资</p><p>产业基金</p><p>银行融资</p><b>帮助建设三座晶圆厂</b></div>
          <div class="dm-col"><h4>扩产与利润</h4><p>价格上行时经营杠杆放大</p><p>规模效应逐步体现</p><b>合并利润快速增长</b></div>
          <div class="dm-col"><h4>股东回报</h4><p>少数股东权益占比高</p><p>归母利润转化有限</p><b>回报受制于股权结构</b></div>
        </div>
        <div class="dm-profit-bridge"><div><small>合并净利润</small><strong>71.44亿</strong></div><span>→</span><div><small>少数股东损益</small><strong>52.69亿</strong></div><span>→</span><div><small>归母净利润</small><strong>18.75亿</strong></div></div>
        <div class="dm-insight warning"><b>关键判断：</b>长期资本解决了“能不能活下去”，但没有自动解决“普通股东能获得多少回报”。</div>
      </section>`;
    }
    if (token === '{{CASHFLOW_QUALITY}}') {
      return `<section class="dm-visual">
        <div class="dm-visual-title"><span>04</span><div><strong>现金流质量：经营改善，投资仍重</strong><small>单位：亿元，FCF为经营现金流减资本开支的简化口径</small></div></div>
        <div class="dm-cash-grid">
          <div class="dm-cash-year"><b>2023</b><div class="dm-bars"><span class="ocf neg" style="height:18%">-72.7</span><span class="fcf neg" style="height:80%">-509.3</span></div></div>
          <div class="dm-cash-year"><b>2024</b><div class="dm-bars"><span class="ocf pos" style="height:17%">69.0</span><span class="fcf neg" style="height:100%">-643.3</span></div></div>
          <div class="dm-cash-year"><b>2025</b><div class="dm-bars"><span class="ocf pos" style="height:57%">365.2</span><span class="fcf neg" style="height:21%">-132.2</span></div></div>
        </div>
        <div class="dm-legend"><span><i class="ocf-dot"></i>经营现金流</span><span><i class="fcf-dot"></i>自由现金流</span></div>
        <div class="dm-insight"><b>读图结论：</b>2025年经营现金流已经大幅改善，但仍未覆盖晶圆厂和技术升级所需的资本开支。</div>
      </section>`;
    }
    return '';
  }

  function splitTableRow(line) {
    return line.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((v) => v.trim());
  }

  function markdownToHtml(body) {
    const blocks = [];
    const lines = body.split('\n');
    let i = 0;
    while (i < lines.length) {
      const line = lines[i].trimEnd();
      const trimmed = line.trim();
      if (!trimmed) { i += 1; continue; }
      if (/^\{\{[A-Z_]+\}\}$/.test(trimmed)) { blocks.push(visualBlock(trimmed)); i += 1; continue; }
      if (trimmed.startsWith('# ')) { i += 1; continue; }
      if (trimmed.startsWith('## ')) { blocks.push(`<h2>${inlineMarkdown(trimmed.slice(3))}</h2>`); i += 1; continue; }
      if (trimmed.startsWith('### ')) { blocks.push(`<h3>${inlineMarkdown(trimmed.slice(4))}</h3>`); i += 1; continue; }
      if (/^---+$/.test(trimmed)) { blocks.push('<hr>'); i += 1; continue; }
      if (trimmed.startsWith('>')) {
        const quote = [];
        while (i < lines.length && lines[i].trim().startsWith('>')) {
          quote.push(lines[i].trim().replace(/^>\s?/, ''));
          i += 1;
        }
        blocks.push(`<blockquote><p>${inlineMarkdown(quote.join('<br>'))}</p></blockquote>`);
        continue;
      }
      if (/^[-*]\s+/.test(trimmed)) {
        const items = [];
        while (i < lines.length && /^[-*]\s+/.test(lines[i].trim())) {
          items.push(`<li>${inlineMarkdown(lines[i].trim().replace(/^[-*]\s+/, ''))}</li>`); i += 1;
        }
        blocks.push(`<ul>${items.join('')}</ul>`); continue;
      }
      if (/^\d+\.\s+/.test(trimmed)) {
        const items = [];
        while (i < lines.length && /^\d+\.\s+/.test(lines[i].trim())) {
          items.push(`<li>${inlineMarkdown(lines[i].trim().replace(/^\d+\.\s+/, ''))}</li>`); i += 1;
        }
        blocks.push(`<ol>${items.join('')}</ol>`); continue;
      }
      if (trimmed.startsWith('|') && i + 1 < lines.length && /^\s*\|?\s*:?-+/.test(lines[i + 1])) {
        const headers = splitTableRow(trimmed);
        i += 2;
        const rows = [];
        while (i < lines.length && lines[i].trim().startsWith('|')) { rows.push(splitTableRow(lines[i])); i += 1; }
        blocks.push(`<div class="dm-table-wrap"><table><thead><tr>${headers.map((h) => `<th>${inlineMarkdown(h)}</th>`).join('')}</tr></thead><tbody>${rows.map((r) => `<tr>${r.map((c) => `<td>${inlineMarkdown(c)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`);
        continue;
      }
      if (/^!\[[^\]]*\]\([^)]+\)$/.test(trimmed)) {
        blocks.push(`<figure class="dm-chart">${inlineMarkdown(trimmed)}</figure>`); i += 1; continue;
      }
      const paragraph = [trimmed]; i += 1;
      while (i < lines.length && lines[i].trim() && !/^(#{1,3} |[-*]\s+|\d+\.\s+|>|---+$|\| |!\[|\{\{[A-Z_]+\}\}$)/.test(lines[i].trim())) {
        paragraph.push(lines[i].trim()); i += 1;
      }
      blocks.push(`<p>${inlineMarkdown(paragraph.join(' '))}</p>`);
    }
    return blocks.join('\n');
  }

  function articleUrl(slug) { return `/blog/article.html?slug=${encodeURIComponent(slug)}`; }

  async function fetchArticles() {
    const listResponse = await fetch(apiUrl);
    if (!listResponse.ok) return [];
    const files = await listResponse.json();
    const markdownFiles = files.filter((file) => file.type === 'file' && /\.md$/i.test(file.name) && !file.name.startsWith('_')).slice(0, 40);
    const articles = await Promise.all(markdownFiles.map(async (file) => {
      const response = await fetch(`${rawBase}/${encodeURIComponent(file.name)}`);
      if (!response.ok) return null;
      const text = await response.text();
      const [meta, body] = parseFrontmatter(text);
      const slug = meta.slug || file.name.replace(/\.md$/i, '');
      return { slug, title: meta.title || firstHeading(body) || slug, date: meta.date || '', tag: meta.tag || '企业分析', description: meta.description || firstParagraph(body), source: meta.source || '公司公告、年报、交易所披露文件及 DupontMaster 整理。', body };
    }));
    return articles.filter(Boolean).sort((a, b) => String(b.date).localeCompare(String(a.date)));
  }

  function card(article, homepage) {
    const margin = homepage ? ' margin-bottom:12px;' : '';
    return `<a class="article-card" data-article-tag="${escapeHtml(article.tag)}" href="${articleUrl(article.slug)}" style="display:block;background:white;border-radius:12px;padding:20px;text-decoration:none;color:inherit;transition:all .2s;${margin}">
      <span class="card-tag" style="display:inline-block;background:rgba(0,113,227,.1);color:#0071e3;padding:4px 10px;border-radius:4px;font-size:12px;margin-bottom:8px;">${escapeHtml(article.tag)}</span>
      <h3 style="font-size:18px;font-weight:600;margin-bottom:8px;">${escapeHtml(article.title)}</h3>
      <p style="color:#86868b;font-size:14px;">${escapeHtml(article.date)}</p>
    </a>`;
  }

  function injectEnhancementStyles() {
    if (document.getElementById('dm-article-enhancements')) return;
    const style = document.createElement('style');
    style.id = 'dm-article-enhancements';
    style.textContent = `
      .content hr{border:0;height:1px;background:#e5e7eb;margin:46px 0}.content blockquote{border-left:4px solid #4f46e5;background:#f7f7ff;padding:16px 20px;margin:24px 0;border-radius:0 10px 10px 0}.content blockquote p{margin:0}.content a{color:#2563eb}.content em{color:#64748b;font-size:14px}.dm-chart{margin:30px -18px 12px}.dm-chart img{width:100%;border-radius:14px;box-shadow:0 10px 28px rgba(15,23,42,.09);border:1px solid #e5e7eb}.dm-table-wrap{overflow-x:auto;margin:24px 0}.content table{width:100%;border-collapse:collapse;font-size:14px}.content th,.content td{padding:11px 12px;border:1px solid #e5e7eb;text-align:left}.content th{background:#f8fafc}.dm-visual{margin:32px -18px 38px;padding:26px;border:1px solid #e4e8f2;border-radius:18px;background:linear-gradient(145deg,#fff,#fafbff);box-shadow:0 12px 32px rgba(15,23,42,.07)}.dm-visual-title{display:flex;align-items:center;gap:12px;margin-bottom:22px}.dm-visual-title>span{display:grid;place-items:center;width:34px;height:34px;border-radius:50%;background:#4f46e5;color:#fff;font-weight:800}.dm-visual-title strong{display:block;font-size:20px}.dm-visual-title small{display:block;color:#64748b;margin-top:2px}.dm-memory-grid{display:grid;grid-template-columns:1fr 1.15fr;gap:18px}.dm-panel,.dm-col,.dm-flow-card{border:1px solid #e5e7eb;border-radius:14px;background:#fff;padding:18px}.dm-panel h4,.dm-col h4{font-size:16px;margin-bottom:14px}.dm-stack{display:flex;flex-direction:column;align-items:center;gap:8px}.dm-tier{padding:12px 16px;text-align:center;border-radius:12px;background:#eef2ff;color:#27335b}.dm-tier b,.dm-tier small{display:block}.dm-tier small{font-size:12px;color:#64748b}.dm-tier.cache{width:55%}.dm-tier.dram{width:75%;border:2px solid #818cf8;background:#f5f3ff}.dm-tier.storage{width:95%;background:#eff6ff}.dm-cell-row{height:120px;display:flex;align-items:center;justify-content:center}.dm-transistor,.dm-capacitor{width:78px;height:78px;border:3px solid #4f46e5;border-radius:12px;display:grid;place-items:center;font-size:26px;font-weight:800;color:#4f46e5}.dm-transistor span,.dm-capacitor span{font-size:11px;font-weight:600}.dm-wire{width:70px;height:3px;background:#60a5fa}.dm-state-row{display:flex;gap:8px;flex-wrap:wrap;justify-content:center}.dm-state-row span{padding:6px 9px;border-radius:8px;background:#f1f5f9;font-size:12px}.dm-state-row .on{background:#ecfdf5;color:#047857}.dm-state-row .refresh{background:#fff7ed;color:#c2410c}.dm-flow{display:grid;grid-template-columns:1fr auto 1fr auto 1fr auto 1fr;align-items:stretch;gap:10px}.dm-flow-card{text-align:center}.dm-flow-card i{display:grid;place-items:center;width:30px;height:30px;margin:0 auto 12px;border-radius:50%;background:#4f46e5;color:#fff;font-style:normal;font-weight:800}.dm-flow-card b,.dm-flow-card small{display:block}.dm-flow-card small{color:#64748b;margin-top:8px}.dm-flow-card.benefit{background:#fffaf0;border-color:#fde68a}.dm-arrow{align-self:center;color:#6366f1;font-size:26px}.dm-insight{margin-top:18px;padding:14px 16px;border-radius:12px;background:#eef2ff;color:#30375d}.dm-insight.warning{background:#fff7ed;color:#9a3412}.dm-three-cols{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.dm-col p{padding:8px 10px;border-radius:8px;background:#f8fafc;margin-bottom:8px;font-size:13px}.dm-col b{display:block;padding:10px;border-radius:8px;background:#eef2ff;color:#4338ca;font-size:13px}.dm-profit-bridge{display:grid;grid-template-columns:1fr auto 1fr auto 1fr;align-items:center;gap:12px;margin-top:18px;padding:16px;border-radius:14px;background:#f8fafc}.dm-profit-bridge div{text-align:center}.dm-profit-bridge small,.dm-profit-bridge strong{display:block}.dm-profit-bridge strong{font-size:22px;color:#2563eb}.dm-profit-bridge span{font-size:24px;color:#94a3b8}.dm-cash-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;height:260px;align-items:end;padding:20px 10px 0;border-bottom:1px solid #cbd5e1}.dm-cash-year{text-align:center;height:100%;display:flex;flex-direction:column;justify-content:flex-end}.dm-bars{height:210px;display:flex;justify-content:center;align-items:flex-end;gap:12px}.dm-bars span{width:45px;min-height:34px;border-radius:8px 8px 3px 3px;color:#fff;font-size:11px;display:flex;align-items:flex-start;justify-content:center;padding-top:5px}.dm-bars .ocf{background:#93c5fd}.dm-bars .fcf{background:#4f46e5}.dm-bars .neg{opacity:.9}.dm-legend{display:flex;justify-content:center;gap:24px;margin-top:14px;color:#64748b;font-size:13px}.dm-legend i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px}.ocf-dot{background:#93c5fd}.fcf-dot{background:#4f46e5}@media(max-width:760px){.dm-visual{margin:28px 0;padding:18px}.dm-memory-grid,.dm-three-cols{grid-template-columns:1fr}.dm-flow{grid-template-columns:1fr}.dm-arrow{transform:rotate(90deg);text-align:center}.dm-profit-bridge{grid-template-columns:1fr}.dm-profit-bridge>span{transform:rotate(90deg)}.dm-chart{margin:26px 0}.dm-bars span{width:36px}.dm-visual-title strong{font-size:17px}}
    `;
    document.head.appendChild(style);
  }

  async function renderArticleList() {
    const target = document.querySelector('[data-md-articles]');
    if (!target) return;
    const homepage = target.getAttribute('data-md-articles') === 'home';
    const limit = Number(target.getAttribute('data-limit') || (homepage ? 5 : 40));
    try {
      const articles = await fetchArticles();
      if (!articles.length) return;
      const visible = articles.filter((item) => !target.querySelector(`a[href="${articleUrl(item.slug)}"]`));
      if (visible.length) target.insertAdjacentHTML('afterbegin', visible.slice(0, limit).map((item) => card(item, homepage)).join(''));
      if (homepage) [...target.querySelectorAll('a[href]')].filter((item) => item.getAttribute('data-more-link') !== 'true').slice(limit).forEach((item) => item.remove());
    } catch (error) { console.warn('Markdown articles load failed:', error); }
  }

  async function renderArticlePage() {
    const target = document.querySelector('[data-md-article-page]');
    if (!target) return;
    const slug = new URLSearchParams(window.location.search).get('slug');
    if (!slug) return;
    try {
      const articles = await fetchArticles();
      const article = articles.find((item) => item.slug === slug);
      if (!article) { target.innerHTML = '<p>文章不存在或尚未发布。</p>'; return; }
      injectEnhancementStyles();
      document.title = `${article.title} - DupontMaster 杜邦大师`;
      const title = document.querySelector('[data-md-title]');
      const meta = document.querySelector('[data-md-meta]');
      const tag = document.querySelector('[data-md-tag]');
      if (title) title.textContent = article.title;
      if (meta) meta.textContent = `作者：DupontMaster 研究院 · ${article.date} · ${article.tag}`;
      if (tag) tag.textContent = article.tag;
      const desc = document.querySelector('meta[name="description"]');
      if (desc) desc.setAttribute('content', article.description);
      target.innerHTML = `${markdownToHtml(article.body)}<div class="source-box"><p><strong>数据来源：</strong>${escapeHtml(article.source)}</p><p><strong>免责声明：</strong>本文仅供学习研究参考，不构成任何证券投资建议、投资顾问服务或买卖依据。投资有风险，决策需谨慎。</p></div>`;
    } catch (error) {
      target.innerHTML = '<p>文章加载失败，请稍后重试。</p>';
      console.warn('Markdown article page load failed:', error);
    }
  }

  document.addEventListener('DOMContentLoaded', () => { renderArticleList(); renderArticlePage(); });
})();