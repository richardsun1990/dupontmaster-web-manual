(() => {
  document.body.classList.add('article-page-v2');

  const analyticsSrc = '/assets/analytics-v1.js';
  if (!document.querySelector(`script[src="${analyticsSrc}"]`)) {
    const analyticsScript = document.createElement('script');
    analyticsScript.src = analyticsSrc;
    analyticsScript.async = true;
    document.head.appendChild(analyticsScript);
  }

  const shareStyleHref = '/assets/article-share-v2.css';
  if (!document.querySelector(`link[href="${shareStyleHref}"]`)) {
    const shareStyle = document.createElement('link');
    shareStyle.rel = 'stylesheet';
    shareStyle.href = shareStyleHref;
    document.head.appendChild(shareStyle);
  }

  const relatedSrc = '/assets/article-related-v1.js';
  if (!document.querySelector(`script[src="${relatedSrc}"]`)) {
    const relatedScript = document.createElement('script');
    relatedScript.src = relatedSrc;
    relatedScript.async = true;
    document.body.appendChild(relatedScript);
  }

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

  const getShareUrl = () => {
    const canonical = document.querySelector('link[rel="canonical"]')?.href;
    if (canonical) return canonical;
    const url = new URL(window.location.href);
    url.search = '';
    url.hash = '';
    return url.toString();
  };

  const getShareTitle = () => {
    const heading = document.querySelector('.title, h1')?.textContent?.trim();
    if (heading) return heading;
    return document.title.replace(/\s*[-|｜]\s*DupontMaster.*$/i, '').trim() || document.title;
  };

  const getShareDescription = () => {
    return document.querySelector('.desc')?.textContent?.trim()
      || document.querySelector('meta[name="description"]')?.content?.trim()
      || '来自 DupontMaster 杜邦大师的企业研究文章';
  };

  const getShareImage = () => {
    return document.querySelector('meta[property="og:image"]')?.content?.trim() || '';
  };

  const wechatIcon = `
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M9.7 5.2c-4 0-7.2 2.6-7.2 5.9 0 1.8 1 3.5 2.7 4.6l-.7 2.2 2.6-1.3c.8.2 1.7.4 2.6.4h.5a5.5 5.5 0 0 1-.3-1.8c0-3.3 2.9-5.9 6.6-6.1-.9-2.3-3.5-3.9-6.8-3.9Z" fill="currentColor"/>
      <path d="M21.5 15.2c0-2.7-2.6-4.9-5.8-4.9s-5.8 2.2-5.8 4.9 2.6 4.9 5.8 4.9c.7 0 1.4-.1 2-.3l2.1 1.1-.5-1.8c1.3-.9 2.2-2.3 2.2-3.9Z" fill="currentColor" opacity=".78"/>
      <circle cx="7.4" cy="10.2" r=".8" fill="white"/>
      <circle cx="12" cy="10.2" r=".8" fill="white"/>
      <circle cx="14" cy="14.6" r=".7" fill="white"/>
      <circle cx="17.6" cy="14.6" r=".7" fill="white"/>
    </svg>`;

  const weiboIcon = `
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M18.8 10.2c-.5-.2-.8-.3-.5-.9.7-1.6.8-3-.1-3.7-1.6-1.3-5.8.1-8.5 2.8-2 2-3.4 4.3-3.4 6.3 0 3.2 4.1 5.2 8.1 5.2 5.2 0 8.7-3 8.7-5.4 0-1.6-1.3-3.3-4.3-4.3Z" fill="currentColor"/>
      <path d="M15.4 17.2c-2.3 1.1-5.2.4-6.3-1.4-1.2-1.9-.1-4.1 2.2-5.2 2.4-1.1 5.2-.5 6.4 1.3 1.2 1.9.1 4.2-2.3 5.3Z" fill="white"/>
      <path d="M14.5 15.2c-.5 1-1.8 1.4-2.8.9-1-.5-1.4-1.5-.9-2.4.5-.9 1.7-1.3 2.7-.9 1 .4 1.5 1.5 1 2.4Z" fill="currentColor"/>
      <circle cx="11.6" cy="13.8" r=".6" fill="white"/>
      <path d="M19 8.5c.7-1.9-.6-3.6-2.4-3.8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      <path d="M21.4 9.1c1.1-3.2-1.1-6.2-4.2-6.6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" opacity=".72"/>
    </svg>`;

  document.querySelectorAll('.share-section, .qr-popup, #qrPopup').forEach((node) => node.remove());

  const shareSection = document.createElement('section');
  shareSection.className = 'article-share-v2';
  shareSection.setAttribute('aria-label', '分享文章');
  shareSection.innerHTML = `
    <div class="article-share-v2-copy">
      <span class="article-share-v2-label">分享这篇研究</span>
      <p>把文章发给也在研究这家公司的朋友。</p>
    </div>
    <div class="article-share-v2-actions">
      <button class="article-share-v2-btn wechat" type="button" data-article-share="wechat" aria-label="分享到微信">
        ${wechatIcon}<span>微信</span>
      </button>
      <button class="article-share-v2-btn weibo" type="button" data-article-share="weibo" aria-label="分享到微博">
        ${weiboIcon}<span>微博</span>
      </button>
    </div>`;

  const articleContainer = content || document.querySelector('.box') || document.querySelector('main');
  const cta = articleContainer?.querySelector('.cta-box');
  if (articleContainer) {
    if (cta && cta.parentNode === articleContainer) articleContainer.insertBefore(shareSection, cta);
    else articleContainer.appendChild(shareSection);
  }

  const shareModal = document.createElement('div');
  shareModal.className = 'article-share-modal';
  shareModal.setAttribute('role', 'dialog');
  shareModal.setAttribute('aria-modal', 'true');
  shareModal.setAttribute('aria-labelledby', 'articleShareModalTitle');
  shareModal.innerHTML = `
    <div class="article-share-modal-card">
      <button class="article-share-modal-close" type="button" aria-label="关闭分享弹窗">×</button>
      <span class="article-share-modal-kicker">微信分享</span>
      <h3 id="articleShareModalTitle">扫码分享这篇文章</h3>
      <p class="article-share-modal-copy">使用微信扫一扫打开文章，再发送给朋友或分享到朋友圈。</p>
      <div class="article-share-qrcode" aria-live="polite"></div>
      <p class="article-share-modal-tip">二维码对应当前文章的正式网址</p>
      <div class="article-share-wechat-guide">你正在微信内阅读。请点击页面右上角的“···”，选择“发送给朋友”或“分享到朋友圈”。</div>
    </div>`;
  document.body.appendChild(shareModal);

  const closeModal = () => {
    shareModal.classList.remove('is-open', 'guide-mode');
    document.body.style.overflow = '';
  };

  shareModal.querySelector('.article-share-modal-close')?.addEventListener('click', closeModal);
  shareModal.addEventListener('click', (event) => {
    if (event.target === shareModal) closeModal();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && shareModal.classList.contains('is-open')) closeModal();
  });

  let qrLoader;
  const loadQRCode = () => {
    if (window.QRCode) return Promise.resolve(window.QRCode);
    if (qrLoader) return qrLoader;
    qrLoader = new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js';
      script.async = true;
      script.onload = () => resolve(window.QRCode);
      script.onerror = reject;
      document.head.appendChild(script);
    });
    return qrLoader;
  };

  const openWechatModal = async (guideMode = false) => {
    const title = shareModal.querySelector('#articleShareModalTitle');
    const copy = shareModal.querySelector('.article-share-modal-copy');
    const qr = shareModal.querySelector('.article-share-qrcode');

    shareModal.classList.toggle('guide-mode', guideMode);
    shareModal.classList.add('is-open');
    document.body.style.overflow = 'hidden';

    if (guideMode) {
      if (title) title.textContent = '在微信中分享';
      if (copy) copy.textContent = '微信内置浏览器需要通过右上角菜单完成分享。';
      return;
    }

    if (title) title.textContent = '扫码分享这篇文章';
    if (copy) copy.textContent = '使用微信扫一扫打开文章，再发送给朋友或分享到朋友圈。';
    if (qr) qr.innerHTML = '<span style="color:#98a2b3;font-size:13px;">正在生成二维码…</span>';

    try {
      const QRCode = await loadQRCode();
      if (!QRCode || !qr) throw new Error('QRCode unavailable');
      qr.innerHTML = '';
      new QRCode(qr, {
        text: getShareUrl(),
        width: 196,
        height: 196,
        correctLevel: QRCode.CorrectLevel?.M,
      });
    } catch (error) {
      if (qr) qr.innerHTML = `<a href="${getShareUrl()}" style="color:#315be8;font-size:14px;word-break:break-all;">二维码加载失败，点击打开文章链接</a>`;
    }
  };

  const shareToWechat = async () => {
    const ua = navigator.userAgent || '';
    if (/MicroMessenger/i.test(ua)) {
      await openWechatModal(true);
      return;
    }

    const isMobileLike = window.matchMedia?.('(pointer: coarse)')?.matches || /Android|iPhone|iPad|iPod/i.test(ua);
    if (isMobileLike && typeof navigator.share === 'function') {
      try {
        await navigator.share({
          title: getShareTitle(),
          text: getShareDescription(),
          url: getShareUrl(),
        });
        return;
      } catch (error) {
        if (error?.name === 'AbortError') return;
      }
    }

    await openWechatModal(false);
  };

  const shareToWeibo = () => {
    const params = new URLSearchParams({
      url: getShareUrl(),
      title: getShareTitle(),
    });
    const image = getShareImage();
    if (image) params.set('pic', image);
    const popup = window.open(`https://service.weibo.com/share/share.php?${params.toString()}`, '_blank', 'noopener,noreferrer,width=720,height=620');
    if (popup) popup.opener = null;
  };

  shareSection.querySelector('[data-article-share="wechat"]')?.addEventListener('click', shareToWechat);
  shareSection.querySelector('[data-article-share="weibo"]')?.addEventListener('click', shareToWeibo);

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