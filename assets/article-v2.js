(() => {
  document.body.classList.add('article-page-v2');

  const progress = document.createElement('div');
  progress.className = 'article-progress';
  document.body.appendChild(progress);

  const updateProgress = () => {
    const root = document.documentElement;
    const max = Math.max(1, root.scrollHeight - root.clientHeight);
    const pct = Math.min(100, Math.max(0, (root.scrollTop / max) * 100));
    progress.style.width = `${pct}%`;
  };
  updateProgress();
  document.addEventListener('scroll', updateProgress, { passive: true });
  window.addEventListener('resize', updateProgress);

  const nav = document.querySelector('.nav');
  if (nav) {
    nav.innerHTML = `
      <div class="article-nav-inner">
        <a class="article-brand" href="/">DupontMaster</a>
        <div class="article-nav-actions">
          <a class="article-nav-home" href="/">首页</a>
          <a class="article-nav-blog" href="/blog/">研究与文章</a>
          <a class="article-primary" href="https://app.dupontmaster.com/">开始分析</a>
        </div>
      </div>`;
  }

  const content = document.querySelector('.content');
  if (content) {
    content.querySelectorAll('table').forEach((table) => {
      if (table.parentElement?.classList.contains('article-table-wrap') || table.parentElement?.classList.contains('dm-table-wrap')) return;
      const wrap = document.createElement('div');
      wrap.className = 'article-table-wrap';
      table.parentNode.insertBefore(wrap, table);
      wrap.appendChild(table);
    });

    const images = Array.from(content.querySelectorAll('img'));
    images.forEach((img, index) => {
      if (index > 0) img.loading = 'lazy';
      img.decoding = 'async';
    });
  }

  const existingFooter = document.querySelector('footer');
  if (existingFooter) {
    existingFooter.innerHTML = `
      <div><strong>DupontMaster 杜邦大师</strong> · 让投资分析更简单</div>
      <div class="article-footer-links">
        <a href="/blog/">研究与文章</a> ·
        <a href="/terms.html">用户协议</a> ·
        <a href="/privacy.html">隐私政策</a> ·
        <a href="/disclaimer.html">免责声明</a>
      </div>
      <div>本文仅供企业研究与学习参考，不构成投资建议。</div>`;
  }
})();
