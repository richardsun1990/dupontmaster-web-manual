const mobileMediaStyle = document.createElement('style');
mobileMediaStyle.textContent = `
  @media (max-width: 760px) {
    .browser-frame img,
    .product-shot img {
      width: 100%;
      height: auto !important;
      aspect-ratio: auto !important;
      object-fit: contain !important;
      object-position: top left !important;
    }
  }
`;
document.head.appendChild(mobileMediaStyle);

const menuButton = document.querySelector('[data-menu-button]');
const mobileMenu = document.querySelector('[data-mobile-menu]');

if (menuButton && mobileMenu) {
  const closeMenu = () => {
    menuButton.setAttribute('aria-expanded', 'false');
    mobileMenu.hidden = true;
    document.body.classList.remove('menu-open');
  };

  menuButton.addEventListener('click', () => {
    const expanded = menuButton.getAttribute('aria-expanded') === 'true';
    menuButton.setAttribute('aria-expanded', String(!expanded));
    mobileMenu.hidden = expanded;
    document.body.classList.toggle('menu-open', !expanded);
  });

  mobileMenu.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', closeMenu);
  });

  window.addEventListener('resize', () => {
    if (window.innerWidth > 760) closeMenu();
  });
}

const year = document.querySelector('[data-current-year]');
if (year) year.textContent = new Date().getFullYear();
