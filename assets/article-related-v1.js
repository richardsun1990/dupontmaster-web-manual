(() => {
  const styleHref = '/assets/article-related-v1.css';
  if (!document.querySelector(`link[href="${styleHref}"]`)) {
    const style = document.createElement('link');
    style.rel = 'stylesheet';
    style.href = styleHref;
    document.head.appendChild(style);
  }

  const currentSlug = (() => {
    const canonical = document.querySelector('link[rel="canonical"]')?.href || location.href;
    try {
      const url = new URL(canonical, location.href);
      const match = url.pathname.match(/\/blog\/articles\/([^/]+)\.html$/);
      return match ? decodeURIComponent(match[1]) : new URLSearchParams(url.search).get('slug');
    } catch {
      return null;
    }
  })();

  if (!currentSlug) return;

  const escapeHtml = (value = '') => String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');

  Promise.all([
    fetch('/blog/topics.json', { cache: 'no-cache' }).then((r) => r.ok ? r.json() : []),
    fetch('/blog/articles.json', { cache: 'no-cache' }).then((r) => r.ok ? r.json() : []),
  ]).then(([topics, articles]) => {
    if (!Array.isArray(topics) || !Array.isArray(articles)) return;
    const matchedTopics = topics.filter((topic) => Array.isArray(topic.slugs) && topic.slugs.includes(currentSlug));
    if (!matchedTopics.length) return;

    const preferred = matchedTopics[0];
    const articleMap = new Map(articles.filter(Boolean).map((item) => [item.slug, item]));
    const candidates = [];
    matchedTopics.forEach((topic) => {
      (topic.slugs || []).forEach((slug) => {
        if (slug === currentSlug || candidates.includes(slug)) return;
        if (articleMap.has(slug)) candidates.push(slug);
      });
    });
    const related = candidates.slice(0, 3).map((slug) => articleMap.get(slug)).filter(Boolean);
    if (!related.length) return;

    const section = document.createElement('section');
    section.className = 'article-related-v1';
    section.setAttribute('aria-label', '相关阅读');
    section.innerHTML = `
      <div class="article-related-v1-head">
        <h2>相关阅读</h2>
        <a class="article-related-v1-topic" href="/blog/topics/${encodeURIComponent(preferred.id)}.html">${escapeHtml(preferred.title)}专题 →</a>
      </div>
      <div class="article-related-v1-list">
        ${related.map((item, index) => `
          <a class="article-related-v1-item" href="/blog/articles/${encodeURIComponent(item.slug)}.html">
            <span class="article-related-v1-no">${String(index + 1).padStart(2, '0')}</span>
            <strong>${escapeHtml(item.title || item.slug)}</strong>
            <time datetime="${escapeHtml(item.date || '')}">${escapeHtml(item.date || '')}</time>
          </a>`).join('')}
      </div>`;

    const content = document.querySelector('.content') || document.querySelector('[data-md-article-page]');
    if (!content) return;
    const share = content.querySelector('.article-share-v2');
    if (share) content.insertBefore(section, share);
    else content.appendChild(section);
  }).catch((error) => {
    console.warn('related research load failed:', error);
  });
})();
