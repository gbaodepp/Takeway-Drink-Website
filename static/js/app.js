// ─── Cart quantity controls ────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Flash toast auto-dismiss
  document.querySelectorAll('.flash-toast').forEach(el => {
    setTimeout(() => {
      el.style.animation = 'slideIn 0.3s ease reverse';
      setTimeout(() => el.remove(), 300);
    }, 3800);
  });

  // Qty +/- buttons on cart page
  document.querySelectorAll('.qty-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = btn.closest('.qty-control').querySelector('.qty-input');
      let val = parseInt(input.value) || 1;
      if (btn.dataset.action === 'inc') val++;
      if (btn.dataset.action === 'dec') val = Math.max(0, val - 1);
      input.value = val;
    });
  });

  // Add-to-cart button ripple effect
  document.querySelectorAll('.btn-primary-custom, .btn-outline-custom').forEach(btn => {
    btn.addEventListener('click', function (e) {
      const ripple = document.createElement('span');
      ripple.style.cssText = `
        position:absolute; border-radius:50%;
        background:rgba(255,255,255,0.35);
        width:100px; height:100px;
        margin-top:-50px; margin-left:-50px;
        animation:ripple 0.6s linear;
        pointer-events:none;
        left:${e.offsetX}px; top:${e.offsetY}px;
      `;
      if (getComputedStyle(this).position === 'static') this.style.position = 'relative';
      this.style.overflow = 'hidden';
      this.appendChild(ripple);
      setTimeout(() => ripple.remove(), 600);
    });
  });

  // Sticky navbar scroll shadow
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      navbar.style.boxShadow = window.scrollY > 10
        ? '0 4px 30px rgba(0,0,0,0.4)'
        : '0 2px 20px rgba(0,0,0,0.3)';
    });
  }

  // Smooth reveal on scroll
  const observerOpts = { threshold: 0.1, rootMargin: '0px 0px -40px 0px' };
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.opacity = '1';
        e.target.style.transform = 'translateY(0)';
        observer.unobserve(e.target);
      }
    });
  }, observerOpts);

  document.querySelectorAll('.product-card, .stat-card, .form-card').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(el);
  });

  // Search debounce on menu page
  const searchInput = document.getElementById('menu-search');
  if (searchInput) {
    let timer;
    searchInput.addEventListener('input', () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        const form = searchInput.closest('form');
        if (form) form.submit();
      }, 500);
    });
  }

  // Admin: order status colour preview
  const statusSelect = document.getElementById('status-select');
  if (statusSelect) {
    statusSelect.addEventListener('change', () => {
      const badge = document.getElementById('status-preview');
      if (badge) {
        badge.className = `badge-status ${statusSelect.value}`;
        badge.textContent = statusSelect.value;
      }
    });
  }

  // Cart badge live update on add-to-cart forms
  document.querySelectorAll('form[action*="cart/add"]').forEach(form => {
    form.addEventListener('submit', () => {
      const badge = document.getElementById('cart-count-badge');
      if (badge) {
        const cur = parseInt(badge.textContent) || 0;
        const qty = parseInt(form.querySelector('[name="qty"]')?.value) || 1;
        badge.textContent = cur + qty;
        badge.style.animation = 'none';
        requestAnimationFrame(() => badge.style.animation = 'popIn 0.3s ease');
      }
    });
  });
});

// Ripple keyframe
const style = document.createElement('style');
style.textContent = `@keyframes ripple { to { transform:scale(4); opacity:0; } }`;
document.head.appendChild(style);
