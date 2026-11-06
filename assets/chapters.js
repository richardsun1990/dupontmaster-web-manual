/* DupontMaster chapters: legacy homepage anchors and feedback intent.
   Only redirects old in-page destinations that no longer exist on /.
   The research app and membership state remain untouched. */
(() => {
  'use strict';
  const chapter = document.body?.dataset?.chapter;
  if (chapter === 'home' && window.location.hash) {
    const oldAnchors = {
      '#purpose': '/research/',
      '#start': '/research/',
      '#philosophy': '/philosophy/',
      '#principles': '/philosophy/',
      '#practice': '/practice/',
      '#notes': '/practice/#reading',
      '#tool': '/tools/',
      '#pricing': '/tools/#membership',
      '#feedback': '/feedback/',
      '#creator': '/creator/',
      '#source': '/tools/#data-sources',
      '#what-you-get': '/#chapters',
      '#thread-title': '/research/',
      '#journey-title': '/research/'
    };
    const target = oldAnchors[window.location.hash.toLowerCase()];
    if (target) window.location.replace(target);
  }
  if (chapter === 'feedback') {
    const category = new URLSearchParams(window.location.search).get('category');
    const select = document.getElementById('website-feedback-category');
    if (select && category && Array.from(select.options).some(option => option.value === category)) {
      select.value = category;
    }
  }
})();