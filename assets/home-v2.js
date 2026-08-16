const analyticsSrc = '/assets/analytics-v1.js';
if (!document.querySelector(`script[src="${analyticsSrc}"]`)) {
  const analyticsScript = document.createElement('script');
  analyticsScript.src = analyticsSrc;
  analyticsScript.async = true;
  document.head.appendChild(analyticsScript);
}

// Keep real product screenshots fully visible at every viewport.
// Desktop hero uses a deliberate layered composition: company research stays
// as the primary surface and the holdings card overlaps its lower-right area.
const productMediaStyle = document.createElement('style');
productMediaStyle.textContent = `
  .browser-frame img,
  .product-shot img {
    width: 100%;
    height: auto !important;
    aspect-ratio: auto !important;
    object-fit: contain !important;
    object-position: top left !important;
  }

  @media (min-width: 1051px) {
    .hero-grid,
    .research-grid {
      align-items: start;
    }

    .hero-media {
      min-height: 540px;
    }

    .browser-frame {
      inset: 8px 0 auto 0;
      z-index: 1;
    }

    .portfolio-float {
      top: clamp(280px, 58%, 340px);
      right: -18px;
      bottom: auto;
      width: min(520px, 68%);
      z-index: 2;
    }

    .research-media {
      padding-top: 8px;
    }
  }
`;
document.head.appendChild(productMediaStyle);

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
