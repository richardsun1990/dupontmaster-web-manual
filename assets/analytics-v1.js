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

  const getMeta = (selector) => document.querySelector(selector)?.content?.trim() || '';
  const canonicalUrl = document.querySelector('link[rel="canonical"]')?.href || `${location.origin}${location.pathname}`;
  const siteUrl = 'https://www.dupontmaster.com';
  const logoUrl = `${siteUrl}/icon-512.png`;

  const addMeta = (attribute, key, value) => {
    if (!value || document.querySelector(`meta[${attribute}="${key}"]`)) return;
    const meta = document.createElement('meta');
    meta.setAttribute(attribute, key);
    meta.content = value;
    document.head.appendChild(meta);
  };

  const addStructuredData = (graph) => {
    if (!graph?.length || document.getElementById('dm-structured-data-v1')) return;
    const script = document.createElement('script');
    script.id = 'dm-structured-data-v1';
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify({
      '@context': 'https://schema.org',
      '@graph': graph,
    });
    document.head.appendChild(script);
  };

  if (pageType === 'home') {
    addStructuredData([
      {
        '@type': 'WebSite',
        '@id': `${siteUrl}/#website`,
        url: `${siteUrl}/`,
        name: 'DupontMaster 杜邦大师',
        description: getMeta('meta[name="description"]') || '企业研究、自定义图表、持仓管理与长期表现跟踪工作台',
        inLanguage: 'zh-CN',
      },
      {
        '@type': 'SoftwareApplication',
        '@id': `${siteUrl}/#app`,
        name: 'DupontMaster 杜邦大师',
        applicationCategory: 'FinanceApplication',
        operatingSystem: 'Web',
        url: 'https://app.dupontmaster.com/',
        description: getMeta('meta[name="description"]') || '企业研究、自定义图表、持仓管理与长期表现跟踪工作台',
        offers: [
          { '@type': 'Offer', price: '0', priceCurrency: 'CNY', name: '免费版' },
          { '@type': 'Offer', price: '199', priceCurrency: 'CNY', name: 'Pro 年度会员' },
        ],
      },
    ]);
  }

  if (pageType === 'blog') {
    addStructuredData([
      {
        '@type': 'Blog',
        '@id': `${siteUrl}/blog/#blog`,
        url: `${siteUrl}/blog/`,
        name: 'DupontMaster 研究与文章',
        description: getMeta('meta[name="description"]') || '从财报、资本回报、商业模式、估值与风险出发，持续研究上市公司与长期投资问题。',
        inLanguage: 'zh-CN',
        publisher: {
          '@type': 'Organization',
          name: 'DupontMaster 杜邦大师',
          url: `${siteUrl}/`,
          logo: { '@type': 'ImageObject', url: logoUrl },
        },
      },
    ]);
  }

  if (pageType === 'article') {
    const title = cleanText(document.querySelector('.title, h1')?.textContent || document.title.replace(/\s*[-|｜]\s*DupontMaster.*$/i, ''));
    const description = document.querySelector('.desc')?.textContent?.trim() || getMeta('meta[name="description"]');
    const image = getMeta('meta[property="og:image"]') || logoUrl;
    const metaText = document.querySelector('.meta')?.textContent || '';
    const published = metaText.match(/\d{4}-\d{2}-\d{2}/)?.[0] || '';
    const section = document.querySelector('.tag')?.textContent?.trim() || '企业研究';

    addMeta('name', 'author', 'DupontMaster 研究院');
    addMeta('property', 'article:published_time', published);
    addMeta('property', 'article:section', section);

    addStructuredData([
      {
        '@type': 'BlogPosting',
        '@id': `${canonicalUrl}#article`,
        mainEntityOfPage: { '@type': 'WebPage', '@id': canonicalUrl },
        headline: title,
        description,
        image: [image],
        datePublished: published || undefined,
        dateModified: published || undefined,
        articleSection: section,
        inLanguage: 'zh-CN',
        author: { '@type': 'Organization', name: 'DupontMaster 研究院', url: `${siteUrl}/blog/` },
        publisher: {
          '@type': 'Organization',
          name: 'DupontMaster 杜邦大师',
          url: `${siteUrl}/`,
          logo: { '@type': 'ImageObject', url: logoUrl },
        },
        isPartOf: { '@type': 'Blog', '@id': `${siteUrl}/blog/#blog` },
      },
    ]);
  }

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
