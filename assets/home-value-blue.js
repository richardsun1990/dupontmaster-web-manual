
(function () {
  const toggle = document.getElementById('menuButton');
  const menu = document.getElementById('mobileMenu');
  const setMenu = (open) => {
    menu.hidden = !open;
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? '关闭导航' : '打开导航');
  };
  toggle.addEventListener('click', () => setMenu(menu.hidden));
  menu.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => setMenu(false)));
  document.addEventListener('keydown', (event) => { if(event.key === 'Escape') setMenu(false); });
  window.addEventListener('resize', () => { if(window.innerWidth > 1060) setMenu(false); });

})();


(function () {
  'use strict';
  const yearElements = document.querySelectorAll('[data-current-year]');
  const currentYear = new Date().getFullYear();
  yearElements.forEach(node => { node.textContent = String(currentYear); });
})();
