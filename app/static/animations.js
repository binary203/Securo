(function () {
  'use strict';

  if (typeof gsap === 'undefined') return;

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ── Landing ──────────────────────────────────────── */
  function initLanding() {
    var landing = document.querySelector('.landing');
    if (!landing) return;

    if (reduced) {
      // Reveal everything instantly without motion
      gsap.set(['.hero-subtitle', '.hero-desc', '.hero-actions .cta-btn',
                 '.section-title', '.feature-card', '.step-card', '.cta-section'],
                { opacity: 1, y: 0 });
      return;
    }

    // Terminal mockup entrance
    var terminal = landing.querySelector('.hero-terminal');
    if (terminal) {
      gsap.set(terminal, { opacity: 0, x: 18 });
    }

    // Hero: subtitle → desc → buttons, timed after typewriter starts (~300ms delay)
    var tl = gsap.timeline({ defaults: { ease: 'power2.out' } });

    if (terminal) {
      tl.to(terminal, { opacity: 1, x: 0, duration: 0.6 }, 0.2);
    }

    var subtitle = landing.querySelector('.hero-subtitle');
    var desc     = landing.querySelector('.hero-desc');
    var btns     = landing.querySelectorAll('.hero-actions .cta-btn');

    if (subtitle) { gsap.set(subtitle, { opacity: 0, y: 10 }); tl.to(subtitle, { opacity: 1, y: 0, duration: 0.45 }, 0.9); }
    if (desc)     { gsap.set(desc,     { opacity: 0, y: 10 }); tl.to(desc,     { opacity: 1, y: 0, duration: 0.45 }, 1.1); }
    if (btns.length) {
      gsap.set(btns, { opacity: 0, y: 10 });
      tl.to(btns, { opacity: 1, y: 0, duration: 0.4, stagger: 0.1 }, 1.3);
    }

    // Section titles
    landing.querySelectorAll('.section-title').forEach(function (el) {
      gsap.set(el, { opacity: 0, y: 14 });
      ScrollTrigger.create({
        trigger: el, start: 'top 88%',
        onEnter: function () {
          gsap.to(el, { opacity: 1, y: 0, duration: 0.4, ease: 'power2.out' });
        }
      });
    });

    // Feature cards stagger
    var featureCards = landing.querySelectorAll('.feature-card');
    if (featureCards.length) {
      gsap.set(featureCards, { opacity: 0, y: 22 });
      ScrollTrigger.batch(featureCards, {
        start: 'top 87%',
        onEnter: function (els) {
          gsap.to(els, { opacity: 1, y: 0, duration: 0.5, stagger: 0.07, ease: 'power2.out' });
        }
      });
    }

    // Steps stagger
    var stepCards = landing.querySelectorAll('.step-card');
    if (stepCards.length) {
      gsap.set(stepCards, { opacity: 0, y: 18 });
      ScrollTrigger.batch(stepCards, {
        start: 'top 87%',
        onEnter: function (els) {
          gsap.to(els, { opacity: 1, y: 0, duration: 0.45, stagger: 0.1, ease: 'power2.out' });
        }
      });
    }

    // CTA section + border pulse on enter
    var ctaSection = landing.querySelector('.cta-section');
    if (ctaSection) {
      gsap.set(ctaSection, { opacity: 0, y: 14 });
      ScrollTrigger.create({
        trigger: ctaSection, start: 'top 85%',
        onEnter: function () {
          gsap.to(ctaSection, {
            opacity: 1, y: 0, duration: 0.5, ease: 'power2.out',
            onComplete: function () {
              gsap.to(ctaSection, {
                boxShadow: '0 0 28px rgba(0, 255, 65, 0.07)',
                duration: 2, repeat: -1, yoyo: true, ease: 'sine.inOut'
              });
            }
          });
        }
      });
    }
  }

  /* ── Terminal animation ───────────────────────────── */
  function initTerminal() {
    var body = document.getElementById('terminalBody');
    if (!body) return;

    var seq = [
      { delay: 700,  cls: 'muted', text: '> Инициализация Semgrep 1.92...' },
      { delay: 800,  cls: 'muted', text: '> Загрузка правил OWASP Top 10...' },
      { delay: 600,  cls: 'info',  text: '> Анализ файлов: auth.py views.py +52' },
      { delay: 1200, cls: 'bar',   text: '[████████████████] 100%  ·  3.2s' },
      { delay: 350,  cls: 'warn',  text: '⚠ HIGH    sql-injection     auth.py:42' },
      { delay: 280,  cls: 'warn',  text: '⚠ MEDIUM  xss-reflected     views.py:118' },
      { delay: 280,  cls: 'muted', text: '  INFO    debug-mode-on     config.py:7' },
      { delay: 500,  cls: 'ok',   text: '✓ Готово · 2 уязвимости найдено' },
    ];

    var cursor = document.createElement('span');
    cursor.className = 't-cursor';

    function addLine(cls, text) {
      var line = document.createElement('div');
      line.className = 'terminal-line';
      line.innerHTML = '<span class="t-' + cls + '">' + text + '</span>';
      if (cursor.parentNode) cursor.parentNode.removeChild(cursor);
      body.appendChild(line);
      line.appendChild(cursor);
    }

    function reset() {
      while (body.children.length > 1) body.removeChild(body.lastChild);
      if (cursor.parentNode) cursor.parentNode.removeChild(cursor);
      body.firstElementChild.appendChild(cursor);
    }

    function run() {
      reset();
      var t = 1000;
      seq.forEach(function (s) {
        t += s.delay;
        setTimeout(function () { addLine(s.cls, s.text); }, t);
      });
      setTimeout(run, t + 3200);
    }

    run();
  }

  /* ── Results page ─────────────────────────────────── */
  function initResults() {
    // Stat counter animation
    document.querySelectorAll('.stat-value').forEach(function (el) {
      var target = parseInt(el.textContent, 10);
      if (isNaN(target) || target === 0) return;
      var proxy = { val: 0 };
      el.textContent = '0';
      gsap.to(proxy, {
        val: target, duration: 0.75, ease: 'power2.out', delay: 0.25,
        onUpdate: function () { el.textContent = Math.round(proxy.val); }
      });
    });

    // Vulnerability cards stagger
    var vulnCards = document.querySelectorAll('.vulnerability-card');
    if (vulnCards.length && !reduced) {
      gsap.set(vulnCards, { opacity: 0, y: 14 });
      gsap.to(vulnCards, { opacity: 1, y: 0, duration: 0.35, stagger: 0.05, ease: 'power2.out', delay: 0.2 });
    }
  }

  /* ── Navbar entrance ──────────────────────────────── */
  function initNavbar() {
    var navbar = document.querySelector('.navbar');
    if (!navbar || reduced) return;
    gsap.set(navbar, { y: -56, opacity: 0 });
    gsap.to(navbar, { y: 0, opacity: 1, duration: 0.45, ease: 'power2.out', delay: 0.05 });
  }

  /* ── Step counter countUp ─────────────────────────── */
  function initStepCounters() {
    if (reduced) return;
    document.querySelectorAll('.step-num').forEach(function (el) {
      var target = parseInt(el.textContent.trim(), 10);
      if (isNaN(target)) return;
      el.textContent = '00';
      var proxy = { val: 0 };
      ScrollTrigger.create({
        trigger: el,
        start: 'top 88%',
        once: true,
        onEnter: function () {
          gsap.to(proxy, {
            val: target,
            duration: 0.5,
            ease: 'power2.out',
            onUpdate: function () {
              el.textContent = String(Math.round(proxy.val)).padStart(2, '0');
            }
          });
        }
      });
    });
  }

  /* ── Init ─────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    initNavbar();
    initLanding();
    initTerminal();
    initStepCounters();
    initResults();
  });

  window.addEventListener('pagehide', function () {
    ScrollTrigger.getAll().forEach(function (t) { t.kill(); });
  });
})();
