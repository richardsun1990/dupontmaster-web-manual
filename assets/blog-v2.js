const analyticsSrc = '/assets/analytics-v1.js';
if (!document.querySelector(`script[src="${analyticsSrc}"]`)) {
  const analyticsScript = document.createElement('script');
  analyticsScript.src = analyticsSrc;
  analyticsScript.async = true;
  document.head.appendChild(analyticsScript);
}

const topicStyleHref = '/assets/blog-topics-v1.css';
if (!document.querySelector(`link[href="${topicStyleHref}"]`)) {
  const topicStyle = document.createElement('link');
  topicStyle.rel = 'stylesheet';
  topicStyle.href = topicStyleHref;
  document.head.appendChild(topicStyle);
}

let rows = Array.from(document.querySelectorAll('.article-row'));
const tabs = Array.from(document.querySelectorAll('.filter-tab'));
const count = document.querySelector('[data-article-count]');
const empty = document.querySelector('[data-empty-state]');
const featured = document.querySelector('[data-featured]');
const list = document.querySelector('.article-list');

const escapeHtml = (value = '') => String(value)
  .replace(/&/g, '&amp;')
  .replace(/</g, '&lt;')
  .replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;');

const articleHref = (slug = '') => `/blog/articles/${encodeURIComponent(slug)}.html`;

const renderTopicDirectory = async () => {
  const archive = document.querySelector('.archive-section');
  if (!archive || document.querySelector('.topic-directory')) return;
  try {
    const response = await fetch('/blog/topics.json', { cache: 'no-cache' });
    if (!response.ok) return;
    const topics = await response.json();
    if (!Array.isArray(topics) || !topics.length) return;

    const section = document.createElement('section');
    section.className = 'topic-directory';
    section.id = 'topics';
    section.innerHTML = `
      <div class="container">
        <div class="topic-directory-head">
          <h2>专题研究</h2>
          <p>把单篇文章连接成可以持续追踪的问题</p>
        </div>
        <div class="topic-directory-list">
          ${topics.map((topic, index) => `
            <a class="topic-directory-link" href="/blog/topics/${encodeURIComponent(topic.id)}.html">
              <span class="topic-directory-no">${String(index + 1).padStart(2, '0')}</span>
              <span class="topic-directory-main"><h3>${escapeHtml(topic.title)}</h3><p>${escapeHtml(topic.description)}</p></span>
              <strong>查看专题 →</strong>
            </a>`).join('')}
        </div>
      </div>`;
    archive.parentNode.insertBefore(section, archive);
  } catch (error) {
    console.warn('topics.json load failed:', error);
  }
};

const articleRowHtml = (item) => {
  const title = escapeHtml(item.title || item.slug || '未命名文章');
  const tag = escapeHtml(item.tag || '文章');
  const date = escapeHtml(item.date || '');
  const description = escapeHtml(item.description || '');
  const usePlaceholder = !item.image || /icon-512\.png$/i.test(item.image);
  const image = usePlaceholder ? '/logo.svg' : escapeHtml(item.image);
  const thumbClass = usePlaceholder ? 'article-thumb placeholder' : 'article-thumb';
  const descriptionHtml = description ? `<p>${description}</p>` : '';

  return `<a class="article-row" data-tag="${tag}" href="${articleHref(item.slug)}">
    <span class="${thumbClass}"><img src="${image}" alt="${title}" loading="lazy"></span>
    <span class="article-main"><span class="article-kicker">${tag}</span><h3>${title}</h3>${descriptionHtml}</span>
    <time class="article-date" datetime="${date}">${date}</time>
  </a>`;
};

const readRow = (row) => ({
  href: row.getAttribute('href'),
  tag: row.dataset.tag || '文章',
  title: row.querySelector('h3')?.textContent?.trim() || '',
  description: row.querySelector('.article-main p')?.textContent?.trim() || '从公开数据和企业基本面出发，记录一篇可反复检验的研究。',
  date: row.querySelector('.article-date')?.textContent?.trim() || '',
  image: row.querySelector('.article-thumb img')?.getAttribute('src') || '/logo.svg',
  placeholder: row.querySelector('.article-thumb')?.classList.contains('placeholder') || false,
});

const renderFeatured = (row) => {
  if (!featured || !row) return;
  const item = readRow(row);
  const media = featured.querySelector('[data-featured-media]');
  const tag = featured.querySelector('[data-featured-tag]');
  const date = featured.querySelector('[data-featured-date]');
  const title = featured.querySelector('[data-featured-title]');
  const description = featured.querySelector('[data-featured-description]');
  const link = featured.querySelector('[data-featured-link]');

  media.classList.toggle('featured-placeholder', item.placeholder);
  media.innerHTML = `<img src="${item.image}" alt="${escapeHtml(item.title)}" loading="eager">`;
  tag.textContent = item.tag;
  date.textContent = item.date;
  title.textContent = item.title;
  description.textContent = item.description;
  link.href = item.href;
};

const applyFilter = (selectedTag) => {
  let visible = 0;
  let firstVisible = null;

  rows.forEach((row) => {
    const show = selectedTag === '全部' || row.dataset.tag === selectedTag;
    row.hidden = !show;
    if (show) {
      visible += 1;
      if (!firstVisible) firstVisible = row;
    }
  });

  if (count) count.textContent = `${visible} 篇`;
  if (empty) empty.hidden = visible !== 0;
  if (firstVisible) renderFeatured(firstVisible);
};

const hydrateFromArticlesJson = async () => {
  if (!list) return;
  try {
    const response = await fetch('/blog/articles.json', { cache: 'no-cache' });
    if (!response.ok) return;
    const articles = await response.json();
    if (!Array.isArray(articles) || !articles.length) return;

    const valid = articles.filter((item) => item && item.slug && item.title);
    if (!valid.length) return;

    list.innerHTML = valid.map(articleRowHtml).join('');
    rows = Array.from(list.querySelectorAll('.article-row'));
  } catch (error) {
    console.warn('articles.json load failed, using static fallback:', error);
  }
};

tabs.forEach((tab) => {
  tab.addEventListener('click', () => {
    tabs.forEach((item) => item.classList.remove('active'));
    tab.classList.add('active');
    applyFilter(tab.dataset.tag || '全部');
  });
});

(async () => {
  await Promise.all([hydrateFromArticlesJson(), renderTopicDirectory()]);
  if (rows.length) {
    applyFilter('全部');
  } else if (empty) {
    empty.hidden = false;
  }
})();
