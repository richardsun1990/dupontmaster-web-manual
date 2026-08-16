(() => {
  const MEASUREMENT_ID = 'G-L426HG5YFM';
  const gtagScriptSelector = `script[src*="googletagmanager.com/gtag/js?id=${MEASUREMENT_ID}"]`;
  const alreadyLoaded = Boolean(document.querySelector(gtagScriptSelector));

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function gtag(){ window.dataLayer.push(arguments); };

  if (!alreadyLoaded) {
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${MEASUREMENT_ID}`;
    document.head.appendChild(script);
    window.gtag('js', new Date());
    window.gtag('config', MEASUREMENT_ID);
  }

  const pageType = location.pathname === '/blog/' || location.pathname === '/blog/index.html'
    ? 'blog'
    : location.pathname.startsWith('/blog/articles/') || location.pathname === '/blog/article.html'
      ? 'article'
      : 'home';

  const cleanText = (value = '') => String(value).replace(/\s+/g, ' ').trim().slice(0, 120);
  const track = (eventName, params = {}) => {
    if (typeof window.gtag !== 'function') return;
    window.gtag('event', eventName, {
      page_type: pageType,
      page_path: location.pathname,
      ...params,
    });
  };

  window.DMAnalytics = { track };

  const classifyAppClick = (anchor) => {
    if (anchor.closest('.hero')) return 'hero_start_analysis';
    if (anchor.closest('#portfolio')) return 'portfolio_cta';
    if (anchor.closest('#pricing')) {
      const text = cleanText(anchor.textContent).toLowerCase();
      return text.includes('pro') || text.includes('会员') ? 'pricing_pro' : 'pricing_free';
    }
    if (anchor.closest('.cta-box')) return 'article_start_analysis';
    if (anchor.closest('.site-header, .nav')) return pageType === 'blog' ? 'blog_start_analysis' : 'header_start_analysis';
    if (pageType === 'article') return 'article_start_analysis';
    return 'start_analysis_click';
  };

  document.addEventListener('click', (event) => {
    const shareButton = event.target.closest?.('[data-article-share]');
    if (shareButton) {
      const platform = shareButton.getAttribute('data-article-share');
      if (platform === 'wechat') track('article_share_wechat');
      if (platform === 'weibo') track('article_share_weibo');
      return;
    }

    const filterButton = event.target.closest?.('.filter-tab[data-tag]');
    if (filterButton) {
      track('blog_filter_select', { article_category: filterButton.getAttribute('data-tag') || '全部' });
      return;
    }

    const anchor = event.target.closest?.('a[href]');
    if (!anchor) return;

    let url;
    try { url = new URL(anchor.href, location.href); } catch { return; }

    if (url.hostname === 'app.dupontmaster.com') {
      track(classifyAppClick(anchor), { link_text: cleanText(anchor.textContent) });
      return;
    }

    if (url.pathname.startsWith('/blog/articles/')) {
      const title = cleanText(anchor.querySelector('h3')?.textContent || anchor.textContent);
      if (anchor.closest('.case-list')) {
        track('blog_case_click', { article_title: title, article_path: url.pathname });
        return;
      }
      if (anchor.closest('[data-featured]')) {
        track('blog_article_click', { placement: 'featured', article_title: title, article_path: url.pathname });
        return;
      }
      if (anchor.closest('.article-list')) {
        track('blog_article_click', { placement: 'archive', article_title: title, article_path: url.pathname });
      }
    }
  }, { passive: true });

  if (pageType === 'home' && 'IntersectionObserver' in window) {
    const sectionEvents = {
      workflow: 'section_view_workflow',
      research: 'section_view_research',
      charts: 'section_view_custom_charts',
      portfolio: 'section_view_portfolio',
      pricing: 'section_view_pricing',
    };
    const seen = new Set();
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting || entry.intersectionRatio < 0.35) return;
        const id = entry.target.id;
        if (!id || seen.has(id) || !sectionEvents[id]) return;
        seen.add(id);
        track(sectionEvents[id]);
        observer.unobserve(entry.target);
      });
    }, { threshold: [0.35] });

    Object.keys(sectionEvents).forEach((id) => {
      const node = document.getElementById(id);
      if (node) observer.observe(node);
    });
  }

  if (pageType === 'article') {
    const milestones = [50, 90];
    const sent = new Set();
    const reportReading = () => {
      const max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
      const pct = Math.min(100, Math.round((window.scrollY / max) * 100));
      milestones.forEach((milestone) => {
        if (pct >= milestone && !sent.has(milestone)) {
          sent.add(milestone);
          track(`article_read_${milestone}`, {
            article_title: cleanText(document.querySelector('.title, h1')?.textContent || document.title),
          });
        }
      });
    };
    reportReading();
    document.addEventListener('scroll', reportReading, { passive: true });
  }
})();