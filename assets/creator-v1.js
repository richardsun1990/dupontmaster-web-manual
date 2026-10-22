// Lightweight creator CTA event tagging; no new marketing SDK or storage.
document.addEventListener('click', (event) => {
  const target = event.target;
  const link = target instanceof Element ? target.closest('[data-creator-cta]') : null;
  if (!link) return;
  const action = link.getAttribute('data-creator-cta') || 'unknown';
  if (window.DMAnalytics && typeof window.DMAnalytics.track === 'function') {
    window.DMAnalytics.track('creator_cta_click', { creator_action: action });
  } else if (typeof window.gtag === 'function') {
    window.gtag('event', 'creator_cta_click', { page_type: 'creator', creator_action: action });
  }
});
