/* ==========================================================================
   Arha Dental Care: site behaviour. Vanilla JS, no dependencies.

   0. Site config, track()   6. Before & After: colour nearest centre (touch)
   1. Header: hairline,      7. Call now: phone call bar, desktop popover,
      compact on scroll         call_click tracking
   2. Desktop dropdowns      8. Map facade
   3. Side menu              9. Reviews: crossfading quote
   4. Reveal on scroll      10. Before & After: filter, case view, slider
   5. Hero video            11. Accordions (FAQ)
                            12. Live open status
                            13. Plan your treatment
                            14. Shared components: tabs, compare
                                slider, Ask Riya, clinic tour
                            15. Treatment pages: stepper, guides,
                                checklist, decider,
                                technology index
                            16. Our work filter, gallery view,
                                360° tour
   ========================================================================== */
(() => {
  'use strict';

  const root = document.documentElement;
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* 0. Contact details and hours come from SITE in tools/pages.py, written into
        every page as #site-config. track() sends an event to whichever analytics
        is installed (Plausible or GA4), and nothing otherwise. ------------------ */
  let SITE = {};
  try { SITE = JSON.parse(document.getElementById('site-config').textContent); } catch (e) { /* no config: links still work */ }
  const track = (name, props = {}) => {
    if (window.plausible) window.plausible(name, { props });
    else if (window.gtag) window.gtag('event', name, props);
  };
  window.arhaTrack = track;

  /* 1. Header: hairline after 10px of scroll; past 120px it compacts to one slim
        row (logo, Book, Call now, menu) and returns to full size above 40px. -- */
  const header = document.querySelector('[data-header]');
  if (header) {
    let ticking = false;
    const update = () => {
      const y = window.scrollY;
      header.classList.toggle('is-scrolled', y > 10);
      if (y > 120) header.classList.add('is-compact');
      else if (y < 40) header.classList.remove('is-compact');
      ticking = false;
    };
    window.addEventListener('scroll', () => {
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(update);
      }
    }, { passive: true });
    update();
  }

  /* 2. Desktop dropdowns: open on hover or keyboard focus; close on
        mouse leave, Escape (from anywhere), click outside or focus leaving ---- */
  const navItems = [...document.querySelectorAll('[data-dropdown]')];
  const setOpen = (item, open) => {
    item.classList.toggle('is-open', open);
    item.querySelector('.nav__trigger').setAttribute('aria-expanded', String(open));
    // Closed panels are inert, so Tab can't land in one while it fades out
    item.querySelector('.dropdown').inert = !open;
  };
  const closeAll = (except) => navItems.forEach((item) => item !== except && setOpen(item, false));
  navItems.forEach((item) => setOpen(item, false));
  navItems.forEach((item) => {
    const trigger = item.querySelector('.nav__trigger');
    let timer = 0;
    const open = () => {
      clearTimeout(timer);
      closeAll(item);
      setOpen(item, true);
    };
    item.addEventListener('mouseenter', open);
    item.addEventListener('mouseleave', () => {
      clearTimeout(timer);
      timer = setTimeout(() => setOpen(item, false), 120);
    });
    // Keyboard focus opens it; a mouse click focusing the button does not re-open it
    item.addEventListener('focusin', (e) => { if (e.target.matches(':focus-visible')) open(); });
    item.addEventListener('focusout', (e) => { if (!item.contains(e.relatedTarget)) setOpen(item, false); });
    trigger.addEventListener('click', () => {
      if (item.classList.contains('is-open') && !item.matches(':hover')) setOpen(item, false);
      else open();
    });
  });
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    const openItem = navItems.find((item) => item.classList.contains('is-open'));
    if (!openItem) return;
    const hadFocus = openItem.contains(document.activeElement);
    setOpen(openItem, false);
    if (hadFocus) openItem.querySelector('.nav__trigger').focus({ preventScroll: true });
  });
  document.addEventListener('click', (e) => {
    navItems.forEach((item) => { if (!item.contains(e.target)) setOpen(item, false); });
  });

  /* 3. Side menu: slide-in panel, focus trapped, Esc closes, scroll locked - */
  const menu = document.getElementById('side-menu');
  if (menu) {
    const panel = menu.querySelector('.side-menu__panel');
    const toggles = document.querySelectorAll('[aria-controls="side-menu"]');
    let returnFocus = null;

    const focusables = () => [...panel.querySelectorAll('a[href], button:not([disabled])')]
      .filter((el) => !el.closest('[inert]') && el.getClientRects().length);

    const onKey = (e) => {
      if (e.key === 'Escape') {
        closeMenu();
      } else if (e.key === 'Tab') {
        const items = focusables();
        const first = items[0];
        const last = items[items.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    };

    const openMenu = () => {
      returnFocus = document.activeElement;
      root.style.setProperty('--scrollbar-w', `${window.innerWidth - root.clientWidth}px`);
      root.classList.add('is-locked');
      menu.removeAttribute('inert');
      menu.classList.add('is-open');
      toggles.forEach((t) => t.setAttribute('aria-expanded', 'true'));
      document.addEventListener('keydown', onKey);
      requestAnimationFrame(() => menu.querySelector('.side-menu__close').focus());
    };

    function closeMenu() {
      menu.classList.remove('is-open');
      menu.setAttribute('inert', '');
      root.classList.remove('is-locked');
      toggles.forEach((t) => t.setAttribute('aria-expanded', 'false'));
      document.removeEventListener('keydown', onKey);
      if (returnFocus) returnFocus.focus();
    }

    toggles.forEach((t) => t.addEventListener('click', openMenu));
    menu.querySelectorAll('[data-close]').forEach((el) => el.addEventListener('click', closeMenu));

    // Accordion groups: one thin plus per group, rotates to a cross
    menu.querySelectorAll('.acc__trigger').forEach((trigger) => {
      const group = trigger.closest('.acc__group');
      const content = document.getElementById(trigger.getAttribute('aria-controls'));
      content.setAttribute('inert', '');
      trigger.addEventListener('click', () => {
        const open = trigger.getAttribute('aria-expanded') !== 'true';
        trigger.setAttribute('aria-expanded', String(open));
        group.classList.toggle('is-open', open);
        content.toggleAttribute('inert', !open);
      });
    });
  }

  /* 4. Reveal on scroll, once, when ~15% into the viewport: text fades up, photographs
        settle from 1.04 to 1 (CSS). Siblings revealed together are staggered by 120ms.
        window.arhaReady tells the head script that reveals are running. ------------ */
  const reveals = document.querySelectorAll('.reveal');
  if (!reduceMotion && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries
        .filter((e) => e.isIntersecting)
        .sort((a, b) => (a.boundingClientRect.top - b.boundingClientRect.top) || (a.boundingClientRect.left - b.boundingClientRect.left))
        .forEach((e, i) => {
          e.target.style.setProperty('--delay', `${Math.min(i, 3) * 120}ms`);
          e.target.classList.add('is-in');
          io.unobserve(e.target);
        });
    }, { rootMargin: '0px 0px -15% 0px' });
    reveals.forEach((el) => io.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add('is-in'));
  }
  window.arhaReady = true;

  /* 4b. Images fade in over their blurred preview once loaded ------------- */
  document.querySelectorAll('picture.fill img[loading="lazy"]').forEach((img) => {
    const done = () => img.classList.add('is-loaded');
    if (img.complete && img.naturalWidth) done();
    else {
      img.addEventListener('load', done, { once: true });
      img.addEventListener('error', done, { once: true });
    }
  });

  /* 5. Hero video: the poster shows instantly; the loop is fetched after the
        page has loaded and crossfades in only once it is actually playing ----- */
  const hero = document.querySelector('[data-hero]');
  const video = hero && hero.querySelector('video');
  const saveData = navigator.connection && navigator.connection.saveData;
  if (video && !reduceMotion && !saveData) {
    let started = false;
    const start = () => {
      const large = window.innerWidth * window.devicePixelRatio > 1280;
      const source = document.createElement('source');
      source.src = `${video.dataset.base}${large ? '1080' : '720'}.mp4`;
      source.type = 'video/mp4';
      video.append(source);
      video.muted = true;
      video.addEventListener('playing', () => hero.classList.add('is-playing'), { once: true });
      video.load();
      started = true;
      video.play().catch(() => {});
    };
    if (document.readyState === 'complete') start();
    else window.addEventListener('load', start, { once: true });
    // Pause while the hero is off screen
    new IntersectionObserver(([entry]) => {
      if (!started) return;
      if (entry.isIntersecting) video.play().catch(() => {});
      else video.pause();
    }).observe(hero);
  }

  /* 6. Before & After on touch: the tile nearest the viewport centre colours */
  if (window.matchMedia('(hover: none)').matches) {
    const tiles = [...document.querySelectorAll('.case')];
    if (tiles.length) {
      let ticking = false;
      const update = () => {
        const mid = window.innerHeight / 2;
        let best = null;
        let bestDist = Infinity;
        tiles.forEach((tile) => {
          const r = tile.getBoundingClientRect();
          if (r.bottom < 0 || r.top > window.innerHeight) return;
          const dist = Math.abs((r.top + r.bottom) / 2 - mid);
          if (dist < bestDist) {
            bestDist = dist;
            best = tile;
          }
        });
        tiles.forEach((tile) => tile.classList.toggle('is-active', tile === best));
        ticking = false;
      };
      window.addEventListener('scroll', () => {
        if (!ticking) {
          ticking = true;
          requestAnimationFrame(update);
        }
      }, { passive: true });
    }
  }

  /* 7. Call now. Every tel: link is tracked as call_click. On phones the call bar
        shows the live status (12). On a laptop (fine pointer) the header's Call now
        opens a popover instead of dialling: number, copy, QR code, WhatsApp. -- */
  document.addEventListener('click', (e) => {
    const link = e.target.closest('a[href^="tel:"]');
    if (link) track('call_click', { location: link.dataset.call || 'page' });
  });

  const pop = document.getElementById('call-pop');
  const popTrigger = document.querySelector('[data-call="header"]');
  const canDial = () => window.matchMedia('(pointer: coarse)').matches;
  if (pop && popTrigger) {
    popTrigger.setAttribute('aria-haspopup', 'dialog');
    popTrigger.setAttribute('aria-controls', 'call-pop');
    popTrigger.setAttribute('aria-expanded', 'false');
    const number = pop.querySelector('.call-pop__number');
    const copyButton = pop.querySelector('[data-copy-number]');
    const copyStatus = pop.querySelector('[data-copy-status]');
    const riyaButton = pop.querySelector('[data-ask-riya]');
    let copyTimer = 0;

    const onKey = (e) => { if (e.key === 'Escape') closePop(true); };
    const onOutside = (e) => { if (!pop.contains(e.target) && !popTrigger.contains(e.target)) closePop(false); };
    const openPop = () => {
      window.dispatchEvent(new Event('arha:status')); // a fresh open/closed line
      pop.hidden = false;
      requestAnimationFrame(() => pop.classList.add('is-open'));
      popTrigger.setAttribute('aria-expanded', 'true');
      document.addEventListener('keydown', onKey);
      document.addEventListener('click', onOutside);
      number.focus({ preventScroll: true });
      track('call_popover_open');
    };
    function closePop(returnFocus) {
      if (pop.hidden) return;
      pop.classList.remove('is-open');
      popTrigger.setAttribute('aria-expanded', 'false');
      document.removeEventListener('keydown', onKey);
      document.removeEventListener('click', onOutside);
      setTimeout(() => { if (!pop.classList.contains('is-open')) pop.hidden = true; }, reduceMotion ? 0 : 200);
      if (returnFocus) popTrigger.focus({ preventScroll: true });
    }
    popTrigger.addEventListener('click', (e) => {
      if (canDial()) return; // phones and tablets dial straight away
      e.preventDefault();
      if (pop.hidden) openPop();
      else closePop(false);
    });
    pop.querySelector('[data-call-pop-close]').addEventListener('click', () => closePop(true));
    // Tabbing out of the popover closes it
    pop.addEventListener('focusout', (e) => {
      if (e.relatedTarget && !pop.contains(e.relatedTarget) && e.relatedTarget !== popTrigger) closePop(false);
    });
    // The header changes size between full and compact: close rather than float in the wrong place
    let wasCompact = header.classList.contains('is-compact');
    window.addEventListener('scroll', () => {
      const compact = header.classList.contains('is-compact');
      if (compact !== wasCompact) closePop(false);
      wasCompact = compact;
    }, { passive: true });

    copyButton.addEventListener('click', async () => {
      const text = SITE.phone || number.textContent.trim();
      try {
        await navigator.clipboard.writeText(text);
        copyButton.textContent = 'Copied';
        copyStatus.textContent = `Number copied: ${text}`;
      } catch (err) {
        // Clipboard blocked: select the number so it can be copied by hand
        const range = document.createRange();
        range.selectNodeContents(number);
        getSelection().removeAllRanges();
        getSelection().addRange(range);
        copyStatus.textContent = 'Number selected. Press Control C or Command C to copy.';
      }
      track('copy_number');
      clearTimeout(copyTimer);
      copyTimer = setTimeout(() => { copyButton.textContent = 'Copy number'; copyStatus.textContent = ''; }, 2500);
    });
    riyaButton.addEventListener('click', () => {
      closePop(false);
      if (window.arhaRiya) window.arhaRiya.open();
    });
  }

  /* 8. Map facade: Google Maps only loads after a click (privacy + speed) - */
  document.querySelectorAll('[data-map-src]').forEach((button) => {
    button.addEventListener('click', () => {
      const frame = document.createElement('iframe');
      frame.src = button.dataset.mapSrc;
      frame.title = button.dataset.mapTitle || 'Map';
      frame.loading = 'lazy';
      frame.referrerPolicy = 'no-referrer-when-downgrade';
      frame.allowFullscreen = true;
      button.replaceWith(frame);
      frame.focus();
    });
  });

  /* 9. Reviews: one large quote, crossfading every 6s; pauses on hover/focus,
        off screen and with reduced motion; dots for manual control ---------- */
  document.querySelectorAll('[data-quotes]').forEach((carousel) => {
    const slides = [...carousel.querySelectorAll('.quote')];
    const dots = [...carousel.querySelectorAll('.quotes__dots button')];
    let current = 0;
    let timer = 0;
    let paused = false;
    let visible = false;
    const show = (index) => {
      current = (index + slides.length) % slides.length;
      slides.forEach((slide, i) => {
        slide.classList.toggle('is-active', i === current);
        slide.setAttribute('aria-hidden', String(i !== current));
      });
      dots.forEach((dot, i) => dot.setAttribute('aria-current', String(i === current)));
    };
    const schedule = () => {
      clearTimeout(timer);
      if (!reduceMotion && !paused && visible) timer = setTimeout(() => { show(current + 1); schedule(); }, 6000);
    };
    dots.forEach((dot, i) => dot.addEventListener('click', () => { show(i); schedule(); }));
    carousel.addEventListener('mouseenter', () => { paused = true; schedule(); });
    carousel.addEventListener('mouseleave', () => { paused = false; schedule(); });
    carousel.addEventListener('focusin', () => { paused = true; schedule(); });
    carousel.addEventListener('focusout', (e) => { if (!carousel.contains(e.relatedTarget)) { paused = false; schedule(); } });
    new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; schedule(); }).observe(carousel);
  });

  /* 10. Before & After: treatment filter, case view (lightbox) and the
         comparison slider ---------------------------------------------------- */
  const caseData = document.getElementById('case-data');
  const grid = document.querySelector('[data-cases]');
  const view = document.getElementById('case-view');
  if (caseData && grid && view) {
    const cases = JSON.parse(caseData.textContent);
    const items = [...grid.querySelectorAll('.case-item')];

    // Filter (Results page): fade out (0.25s) -> swap tiles -> animate to the new natural
    // height (0.4s) -> fade in (0.25s). No reserved empty space.
    const filterButtons = [...document.querySelectorAll('[data-cases-block] [data-filter]')];
    let busy = false;
    filterButtons.forEach((button) => {
      button.addEventListener('click', () => {
        if (busy || button.getAttribute('aria-pressed') === 'true') return;
        filterButtons.forEach((b) => b.setAttribute('aria-pressed', String(b === button)));
        const cat = button.dataset.filter;
        const swap = () => items.forEach((item) => {
          item.hidden = cat !== 'all' && item.dataset.cat !== cat;
          item.classList.add('is-in'); // already revealed once; no second slow fade
        });
        if (reduceMotion) { swap(); return; }
        busy = true;
        const from = grid.offsetHeight;
        grid.style.height = `${from}px`;
        grid.classList.add('is-animating', 'is-fading');
        setTimeout(() => {
          swap();
          grid.style.height = 'auto';
          const to = grid.offsetHeight;
          grid.style.height = `${from}px`;
          void grid.offsetHeight; // commit the start height before animating
          grid.style.height = `${to}px`;
          setTimeout(() => {
            grid.style.height = '';
            grid.classList.remove('is-animating', 'is-fading');
            busy = false;
          }, 400);
        }, 250);
      });
    });

    const $ = (sel) => view.querySelector(sel);
    const media = $('[data-cv-media]');
    let index = 0;
    let returnFocus = null;

    const pictureHTML = (set, cls = '') => `<picture><source type="image/avif" srcset="${set.avif}"><source type="image/webp" srcset="${set.webp}"><img class="${cls}" src="${set.jpg}" alt=""></picture>`;

    const render = () => {
      const c = cases[index];
      $('[data-cv-title]').textContent = c.name;
      $('[data-cv-meta]').textContent = c.meta;
      $('[data-cv-concern]').textContent = c.concern;
      $('[data-cv-plan]').textContent = c.plan;
      $('[data-cv-result]').textContent = c.result;
      $('[data-cv-sample]').hidden = !c.sample;
      view.querySelectorAll('[data-cv-mark]').forEach((mark) => { mark.hidden = !c.sample; });
      $('[data-cv-looks]').textContent = c.looks || '';
      $('[data-cv-works]').textContent = c.works || '';
      $('[data-cv-note]').textContent = c.note ? `“${c.note}”` : '';
      // Signed note, "Treated by" and the visiting tag exist only for real cases
      const by = $('[data-cv-note-by]');
      by.hidden = !c.doctor;
      by.textContent = c.doctor ? `— ${c.doctor}` : '';
      const doctor = $('[data-cv-doctor]');
      doctor.hidden = !c.doctor;
      doctor.textContent = c.doctor ? `Treated by ${c.doctor}` : '';
      const visit = $('[data-cv-visit]');
      visit.hidden = !c.visit;
      visit.textContent = c.visit || '';

      // Smile frame: a drag comparison when a real "before" exists, otherwise the single image
      const smile = c.before
        ? `<div class="ba">${pictureHTML(c.after)}${pictureHTML(c.before, 'ba__before')}
            <span class="ba__label ba__label--before">Before</span><span class="ba__label ba__label--after">After</span>
            <input class="ba__range" type="range" min="0" max="100" value="50" aria-label="Compare before and after">
            <span class="ba__handle" aria-hidden="true"><span class="ba__grip"></span></span></div>`
        : `${pictureHTML(c.after)}${c.face ? '<span class="cv-frame__label">Smile</span>' : ''}`;
      const face = c.face ? `<figure class="cv-frame">${pictureHTML(c.face)}<span class="cv-frame__label">Full face</span></figure>` : '';
      media.classList.toggle('is-pair', Boolean(c.face));
      media.innerHTML = `<figure class="cv-frame">${smile}</figure>${face}` +
        (c.before ? '' : '<p class="case-view__note">Before/after comparison will appear here.</p>');
      if (c.before) {
        const ba = media.querySelector('.ba');
        const range = media.querySelector('.ba__range');
        range.addEventListener('input', () => ba.style.setProperty('--pos', `${range.value}%`));
        media.querySelector('.ba__before').closest('picture').style.zIndex = '1';
      }
      const imgs = media.querySelectorAll('img');
      imgs[0].alt = c.sample ? `Sample image for the demo (${c.name})` : c.name;
      if (c.face) imgs[imgs.length - 1].alt = c.sample ? 'Sample image for the demo (full face)' : `${c.name}, full face`;
    };

    const visibleIndexes = () => items.filter((item) => !item.hidden).map((item) => Number(item.querySelector('.case').dataset.case));
    const step = (dir) => {
      const list = visibleIndexes();
      const pos = list.indexOf(index);
      index = list[(pos + dir + list.length) % list.length];
      render();
    };

    const focusables = () => [...view.querySelectorAll('a[href], button, input')].filter((el) => el.getClientRects().length);
    const onKey = (e) => {
      if (e.key === 'Escape') close();
      else if ((e.key === 'ArrowRight' || e.key === 'ArrowLeft') && !e.target.matches('.ba__range')) step(e.key === 'ArrowRight' ? 1 : -1);
      else if (e.key === 'Tab') {
        const els = focusables();
        if (e.shiftKey && document.activeElement === els[0]) { e.preventDefault(); els[els.length - 1].focus(); }
        else if (!e.shiftKey && document.activeElement === els[els.length - 1]) { e.preventDefault(); els[0].focus(); }
      }
    };
    const open = (i, trigger) => {
      index = i;
      returnFocus = trigger;
      render();
      root.style.setProperty('--scrollbar-w', `${window.innerWidth - root.clientWidth}px`);
      root.classList.add('is-locked');
      view.removeAttribute('inert');
      view.classList.add('is-open');
      document.addEventListener('keydown', onKey);
      requestAnimationFrame(() => $('[data-cv-close]').focus());
    };
    function close() {
      view.classList.remove('is-open');
      view.setAttribute('inert', '');
      root.classList.remove('is-locked');
      document.removeEventListener('keydown', onKey);
      if (returnFocus) returnFocus.focus();
    }

    grid.addEventListener('click', (e) => {
      const tile = e.target.closest('.case');
      if (tile) open(Number(tile.dataset.case), tile);
    });
    $('[data-cv-close]').addEventListener('click', close);
    $('[data-cv-prev]').addEventListener('click', () => step(-1));
    $('[data-cv-next]').addEventListener('click', () => step(1));
    view.addEventListener('click', (e) => { if (e.target === view) close(); }); // click outside the case
  }

  /* 11. Accordions on the page (FAQ): thin plus that turns into a cross ------- */
  document.querySelectorAll('[data-accordion] [aria-controls]').forEach((trigger) => {
    const panel = document.getElementById(trigger.getAttribute('aria-controls'));
    const item = trigger.closest('.faq__item');
    panel.inert = trigger.getAttribute('aria-expanded') !== 'true';
    trigger.addEventListener('click', () => {
      const open = trigger.getAttribute('aria-expanded') !== 'true';
      trigger.setAttribute('aria-expanded', String(open));
      item.classList.toggle('is-open', open);
      panel.inert = !open;
    });
  });

  /* 11b. Google reviews link: Arha's Google Business Profile (SITE in tools/pages.py). Empty keeps "#". */
  const GOOGLE_REVIEWS_URL = SITE.googleReviewsUrl || '';
  if (GOOGLE_REVIEWS_URL) {
    document.querySelectorAll('[data-google-reviews]').forEach((link) => {
      link.href = GOOGLE_REVIEWS_URL;
      link.target = '_blank';
      link.rel = 'noopener';
    });
  }

  /* 12. Live open status (India time). Hours come from SITE in tools/pages.py.
         Feeds the Visit and menu status lines, the phone call bar and the popover. */
  const CLINIC_HOURS = {
    timeZone: SITE.timeZone || 'Asia/Kolkata',
    days: SITE.hours || [], // 0 = Sunday ... 6 = Saturday; null = closed
  };
  const statusEls = document.querySelectorAll('[data-open-status]');
  const barStatus = document.querySelector('[data-call-status]');
  const popStatus = document.querySelector('[data-call-pop-status]');
  if (CLINIC_HOURS.days.length === 7) {
    const DAY_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const toMinutes = (hhmm) => { const [h, m] = hhmm.split(':').map(Number); return h * 60 + m; };
    const label = (hhmm) => {
      const [h, m] = hhmm.split(':').map(Number);
      return `${((h + 11) % 12) + 1}:${String(m).padStart(2, '0')} ${h < 12 ? 'AM' : 'PM'}`;
    };
    const nowInClinic = () => {
      const parts = Object.fromEntries(new Intl.DateTimeFormat('en-GB', {
        timeZone: CLINIC_HOURS.timeZone, weekday: 'short', hour: '2-digit', minute: '2-digit', hourCycle: 'h23',
      }).formatToParts(new Date()).map((p) => [p.type, p.value]));
      return { day: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(parts.weekday), minutes: Number(parts.hour) * 60 + Number(parts.minute) };
    };
    // Open: { open, until }. Closed: { opens, when }, where when is '', 'tomorrow' or a day name
    const status = () => {
      const { day, minutes } = nowInClinic();
      const today = CLINIC_HOURS.days[day];
      if (today && minutes >= toMinutes(today[0]) && minutes < toMinutes(today[1])) return { open: true, until: label(today[1]) };
      if (today && minutes < toMinutes(today[0])) return { open: false, opens: label(today[0]), when: '' };
      for (let i = 1; i <= 7; i += 1) {
        const next = CLINIC_HOURS.days[(day + i) % 7];
        if (next) return { open: false, opens: label(next[0]), when: i === 1 ? 'tomorrow' : DAY_NAMES[(day + i) % 7] };
      }
      return { open: false, opens: '', when: '' };
    };
    const closedNote = document.querySelector('[data-call-pop-closed]');
    const riyaOption = document.querySelector('[data-ask-riya]');
    const render = () => {
      const s = status();
      const text = s.open ? `Open now · until ${s.until}` : s.opens ? `Closed · Opens ${s.when || 'today'} at ${s.opens}` : 'Closed';
      statusEls.forEach((el) => { el.textContent = text; el.classList.toggle('is-open', s.open); });
      // Phone call bar: "Open until 6:30 PM" / "Opens 9:30 AM" / "Opens tomorrow 9:30 AM" / "Opens Mon 9:30 AM"
      if (barStatus) {
        const when = s.when === 'tomorrow' ? 'tomorrow ' : s.when ? `${s.when.slice(0, 3)} ` : '';
        barStatus.textContent = s.open ? `Open until ${s.until}` : `Opens ${when}${s.opens}`;
      }
      // Popover: when closed, it also offers WhatsApp (always there) and Riya
      if (popStatus) {
        popStatus.textContent = s.open ? `Open now · until ${s.until}` : `Closed now · opens ${s.when ? `${s.when} ` : ''}${s.opens}`;
        popStatus.classList.toggle('is-open', s.open);
        if (closedNote) closedNote.hidden = s.open;
        if (riyaOption) riyaOption.hidden = s.open || !window.arhaRiya;
      }
    };
    render();
    setInterval(render, 60000);
    window.addEventListener('arha:status', render);
  }

  /* 13. Plan your treatment (visiting patients): one question at a time, nothing
         stored or submitted; the result opens WhatsApp with the plan written in. */
  const PLANNER = {
    whatsapp: SITE.whatsapp || '',
    // SAMPLE timings until Dr. Nikhil confirms real ones (see notes/NEXT-SESSION.md)
    treatments: {
      implants: { name: 'Dental implants', detail: 'Typically 2 visits, about 5–7 days each.' },
      'full-mouth': { name: 'Full mouth rehabilitation', detail: 'Typically 3 visits, about 7–10 days each.' },
      veneers: { name: 'Smile design & veneers', detail: 'Typically 2 visits, about 7–10 days in all.' },
      aligners: { name: 'Aligners', detail: 'Typically 1 visit of about 3–5 days, then remote reviews.' },
      unsure: { name: 'A consultation', detail: 'We will recommend the right treatment and timeline after a virtual consultation.' },
    },
    minDays: 1,
    maxDays: 30,
    startDays: 7,
  };
  document.querySelectorAll('[data-planner]').forEach((planner) => {
    const NUMBER_WORDS = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve',
      'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty'];
    const steps = [...planner.querySelectorAll('.planner__step')];
    const city = planner.querySelector('#planner-city');
    const daysValue = planner.querySelector('[data-days-value]');
    const state = { treatment: null, city: '', days: PLANNER.startDays };

    const show = (name) => {
      steps.forEach((step) => {
        const on = step.dataset.step === String(name);
        step.classList.toggle('is-active', on);
        step.inert = !on;
      });
      const active = steps.find((s) => s.dataset.step === String(name));
      const target = active.querySelector('[tabindex="-1"], .planner__q');
      setTimeout(() => (name === 2 ? city : target).focus({ preventScroll: true }), reduceMotion ? 0 : 400);
    };

    const result = () => {
      const t = PLANNER.treatments[state.treatment];
      const words = state.days <= 20 ? NUMBER_WORDS[state.days] : String(state.days);
      const dayWord = state.days === 1 ? 'day' : 'days';
      planner.querySelector('[data-summary]').textContent =
        `${t.name}. ${state.city ? `From ${state.city}. ` : ''}${words} ${dayWord} in Mumbai.`;
      planner.querySelector('[data-detail]').textContent = t.detail;
      const msg = `Hello Arha Dental Care, I'm planning a visit for ${state.treatment === 'unsure' ? 'a consultation' : t.name.toLowerCase()}.`
        + `${state.city ? ` I'm travelling from ${state.city}` : " I'm travelling"} and can be in Mumbai for ${state.days} ${dayWord}.`
        + ' Could we arrange a virtual consultation?';
      planner.querySelector('[data-whatsapp]').href = `https://wa.me/${PLANNER.whatsapp}?text=${encodeURIComponent(msg)}`;
      show('result');
    };

    planner.querySelectorAll('[data-treatment]').forEach((button) => {
      button.addEventListener('click', () => {
        state.treatment = button.dataset.treatment;
        planner.querySelectorAll('[data-treatment]').forEach((b) => b.setAttribute('aria-pressed', String(b === button)));
        setTimeout(() => show(2), reduceMotion ? 0 : 250); // let the selection register before moving on
      });
    });
    planner.querySelectorAll('[data-planner-next]').forEach((button) => {
      button.addEventListener('click', () => {
        if (button.closest('[data-step="2"]')) {
          state.city = city.value.trim().replace(/\s+/g, ' ');
          show(3);
        } else {
          result();
        }
      });
    });
    city.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        planner.querySelector('[data-step="2"] [data-planner-next]').click();
      }
    });
    planner.querySelectorAll('[data-days]').forEach((button) => {
      button.addEventListener('click', () => {
        state.days = Math.min(PLANNER.maxDays, Math.max(PLANNER.minDays, state.days + Number(button.dataset.days)));
        daysValue.textContent = state.days;
      });
    });
    planner.querySelector('[data-planner-restart]').addEventListener('click', () => {
      Object.assign(state, { treatment: null, city: '', days: PLANNER.startDays });
      city.value = '';
      daysValue.textContent = state.days;
      planner.querySelectorAll('[data-treatment]').forEach((b) => b.setAttribute('aria-pressed', 'false'));
      show(1);
    });
  });

  /* 14. Shared components. Every interactive block on the site is built from these,
         so they all behave the same way.
         Tabs ([data-tabs]): role="tablist" / "tab" / "tabpanel"; click, arrow keys, Home and
         End; aria-selected and a roving tabindex; with data-hash the URL hash names the
         selected panel, so it can be linked to (#problem-gaps).
         Compare slider ([data-compare]): a range input drives --pos.
         Ask Riya ([data-riya-ask]): opens Riya with the question typed in; without Riya
         the link (WhatsApp) still works.
         Clinic tour ([data-tour]): nothing loads until Play. -------------------------- */
  document.querySelectorAll('[data-tabs]').forEach((box) => {
    const list = box.querySelector('[role="tablist"]');
    const tabs = [...list.querySelectorAll('[role="tab"]')];
    const panelOf = (tab) => document.getElementById(tab.getAttribute('aria-controls'));
    const select = (tab, { focus = false, hash = false } = {}) => {
      tabs.forEach((t) => {
        const on = t === tab;
        t.setAttribute('aria-selected', String(on));
        t.tabIndex = on ? 0 : -1;
        panelOf(t).hidden = !on;
      });
      if (focus) tab.focus({ preventScroll: true });
      // A horizontally scrolling list (phones) keeps the selected tab in view
      if (list.scrollWidth > list.clientWidth + 1) {
        list.scrollTo({ left: tab.offsetLeft - list.offsetLeft - 20, behavior: reduceMotion ? 'auto' : 'smooth' });
      }
      if (hash && box.hasAttribute('data-hash')) history.replaceState(null, '', `#${tab.getAttribute('aria-controls')}`);
      box.dispatchEvent(new CustomEvent('tabchange', { detail: { tab, panel: panelOf(tab) } }));
    };
    tabs.forEach((tab) => tab.addEventListener('click', () => select(tab, { hash: true })));
    list.addEventListener('keydown', (e) => {
      const i = tabs.indexOf(document.activeElement);
      if (i < 0) return;
      const steps = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 };
      let next = null;
      if (e.key in steps) next = tabs[(i + steps[e.key] + tabs.length) % tabs.length];
      else if (e.key === 'Home') [next] = tabs;
      else if (e.key === 'End') next = tabs[tabs.length - 1];
      if (!next) return;
      e.preventDefault();
      select(next, { focus: true, hash: true });
    });
    // Opened from a link such as /#problem-gaps: select it and bring the block into view
    if (box.hasAttribute('data-hash') && location.hash) {
      const tab = tabs.find((t) => `#${t.getAttribute('aria-controls')}` === location.hash);
      if (tab) {
        select(tab);
        requestAnimationFrame(() => box.scrollIntoView({ block: 'start' }));
      }
    }
  });

  document.querySelectorAll('[data-compare]').forEach((ba) => {
    const range = ba.querySelector('.ba__range');
    range.addEventListener('input', () => ba.style.setProperty('--pos', `${range.value}%`));
  });

  document.addEventListener('click', (e) => {
    const link = e.target.closest('[data-riya-ask]');
    if (!link || !window.arhaRiya) return;
    e.preventDefault();
    window.arhaRiya.open(link.dataset.riyaAsk);
    track('riya_ask', { question: link.dataset.riyaAsk });
  });

  document.querySelectorAll('[data-tour]').forEach((fig) => {
    const button = fig.querySelector('.tour__play');
    button.addEventListener('click', () => {
      const big = fig.clientWidth * window.devicePixelRatio > 900;
      const video = document.createElement('video');
      video.innerHTML = (big ? '' : `<source src="${fig.dataset.base}720.webm" type="video/webm">`)
        + `<source src="${fig.dataset.base}${big ? '1080' : '720'}.mp4" type="video/mp4">`;
      video.muted = true;
      video.playsInline = true;
      video.controls = true;
      video.poster = fig.querySelector('img').currentSrc;
      video.setAttribute('aria-label', 'Arha Dental Care clinic tour, no sound');
      fig.append(video);
      fig.classList.add('is-playing');
      button.remove();
      video.focus();
      video.play().catch(() => {});
      track('tour_play');
    });
  });

  /* 15. Treatment-page components, set up once each block scrolls into view.
         Stepper ([data-stepper]): tabs plus Previous / Next and a progress line.
         Implant hotspots are tabs: the numbered markers on the photograph are the tab list.
         Design guides ([data-guides]): a toggle button draws the overlay.
         Checklist ([data-checklist]) and decider ([data-decider]): the first matching
         result is shown; nothing is stored or sent.
         Technology page: groups are an accordion on phones and open, with a
         scroll-spy index, on desktop. ---------------------------------------------- */
  const whenVisible = (el, setup) => {
    if (!('IntersectionObserver' in window)) { setup(el); return; }
    const io = new IntersectionObserver(([entry]) => {
      if (!entry.isIntersecting) return;
      io.disconnect();
      setup(el);
    }, { rootMargin: '200px 0px' });
    io.observe(el);
  };
  const selectTab = (tab) => tab && tab.click();

  document.querySelectorAll('[data-stepper]').forEach((box) => whenVisible(box, () => {
    const tabs = [...box.querySelectorAll('[role="tab"]')];
    const prev = box.querySelector('[data-step="-1"]');
    const next = box.querySelector('[data-step="1"]');
    const sync = () => {
      const i = tabs.findIndex((t) => t.getAttribute('aria-selected') === 'true');
      box.style.setProperty('--at', i + 1);
      prev.disabled = i === 0;
      next.disabled = i === tabs.length - 1;
    };
    box.querySelector('[data-tabs]').addEventListener('tabchange', sync);
    [prev, next].forEach((b) => b.addEventListener('click', () => {
      const i = tabs.findIndex((t) => t.getAttribute('aria-selected') === 'true');
      selectTab(tabs[i + Number(b.dataset.step)]);
    }));
    sync();
  }));

  document.querySelectorAll('[data-guides]').forEach((fig) => {
    const button = fig.querySelector('[data-guides-toggle]');
    button.addEventListener('click', () => {
      const on = button.getAttribute('aria-pressed') !== 'true';
      button.setAttribute('aria-pressed', String(on));
      button.textContent = on ? 'Hide design guides' : 'Show design guides';
      fig.classList.toggle('is-on', on);
    });
  });

  document.querySelectorAll('[data-checklist]').forEach((form) => {
    const results = [...form.querySelectorAll('[data-if]')];
    const update = () => {
      const ticked = [...form.querySelectorAll('input:checked')].map((i) => i.value);
      const match = (cond) => (cond === 'none' ? ticked.length === 0 : cond.slice(4).split(',').some((v) => ticked.includes(v)));
      const shown = results.find((r) => match(r.dataset.if));
      results.forEach((r) => { r.hidden = r !== shown; });
    };
    form.addEventListener('change', update);
    update();
  });

  document.querySelectorAll('[data-decider]').forEach((form) => {
    const answers = () => Object.fromEntries([...form.querySelectorAll('input:checked')].map((i) => [i.name, i.value]));
    const holds = (spec, a) => spec.split(' ').every((pair) => { const [k, v] = pair.split(':'); return a[k] === v; });
    const update = () => {
      const a = answers();
      form.querySelectorAll('[data-show-if]').forEach((fs) => {
        const show = holds(fs.dataset.showIf, a);
        fs.hidden = !show;
        if (!show) fs.querySelectorAll('input').forEach((i) => { i.checked = false; });
      });
      const b = answers();
      const results = [...form.querySelectorAll('[data-when]')];
      const shown = results.find((r) => holds(r.dataset.when, b));
      results.forEach((r) => { r.hidden = r !== shown; });
    };
    form.addEventListener('change', update);
  });

  const spyRoot = document.querySelector('[data-spy-root]');
  if (spyRoot) {
    const groups = [...spyRoot.querySelectorAll('details.tgroup')];
    const desktop = window.matchMedia('(min-width: 900px)');
    const layout = () => groups.forEach((g, i) => { g.open = desktop.matches || i === 0 || g.contains(document.querySelector(':target')); });
    layout();
    desktop.addEventListener('change', layout);
    // On desktop the summaries are headings, not toggles
    groups.forEach((g) => g.querySelector('summary').addEventListener('click', (e) => { if (desktop.matches) e.preventDefault(); }));
    // Opening /technology/#instrument-care opens its group first
    const target = location.hash && document.getElementById(location.hash.slice(1));
    if (target) { const g = target.closest('details'); if (g) g.open = true; requestAnimationFrame(() => target.scrollIntoView()); }
    const links = [...document.querySelectorAll('[data-spy]')];
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver((entries) => {
        entries.filter((e) => e.isIntersecting).forEach((e) => {
          links.forEach((a) => a.setAttribute('aria-current', String(a.dataset.spy === e.target.id)));
        });
      }, { rootMargin: '-30% 0px -60% 0px' });
      groups.forEach((g) => io.observe(g));
    }
  }

  /* 16. Our work filter, gallery view and the 360° tour.
         Gallery view: the case view's behaviour (Esc, arrows, focus trap, scroll lock).
         360°: Pannellum (MIT, self-hosted) loads only when the visitor asks for it. ---- */
  const workGrid = document.querySelector('[data-work-grid]');
  if (workGrid) {
    const chips = [...document.querySelectorAll('[data-work-filter]')];
    const cards = [...workGrid.querySelectorAll('[data-cat]')];
    const empty = document.querySelector('[data-work-empty]');
    chips.forEach((chip) => chip.addEventListener('click', () => {
      const cat = chip.dataset.workFilter;
      chips.forEach((c) => c.setAttribute('aria-pressed', String(c === chip)));
      cards.forEach((card) => {
        card.hidden = cat !== 'all' && card.dataset.cat !== cat;
        card.classList.add('is-in');
      });
      empty.hidden = cards.some((c) => !c.hidden);
    }));
  }

  const gview = document.getElementById('gallery-view');
  if (gview) {
    const shots = [...document.querySelectorAll('[data-gallery-full] li')].map((li) => li.dataset);
    const img = gview.querySelector('[data-gv-img]');
    const cap = gview.querySelector('[data-gv-cap]');
    let at = 0;
    let back = null;
    const show = (i) => {
      at = (i + shots.length) % shots.length;
      img.src = shots[at].src;
      img.alt = shots[at].alt;
      cap.textContent = `${shots[at].cap} · ${at + 1} of ${shots.length}`;
    };
    const focusables = () => [...gview.querySelectorAll('button')];
    const onKey = (e) => {
      if (e.key === 'Escape') closeView();
      else if (e.key === 'ArrowRight') show(at + 1);
      else if (e.key === 'ArrowLeft') show(at - 1);
      else if (e.key === 'Tab') {
        const els = focusables();
        if (e.shiftKey && document.activeElement === els[0]) { e.preventDefault(); els[els.length - 1].focus(); }
        else if (!e.shiftKey && document.activeElement === els[els.length - 1]) { e.preventDefault(); els[0].focus(); }
      }
    };
    const openView = (i, trigger) => {
      back = trigger;
      show(i);
      root.style.setProperty('--scrollbar-w', `${window.innerWidth - root.clientWidth}px`);
      root.classList.add('is-locked');
      gview.removeAttribute('inert');
      gview.classList.add('is-open');
      document.addEventListener('keydown', onKey);
      requestAnimationFrame(() => gview.querySelector('[data-gv-close]').focus());
    };
    function closeView() {
      gview.classList.remove('is-open');
      gview.setAttribute('inert', '');
      root.classList.remove('is-locked');
      document.removeEventListener('keydown', onKey);
      if (back) back.focus();
    }
    document.querySelectorAll('[data-gallery-open]').forEach((b) => b.addEventListener('click', () => openView(Number(b.dataset.galleryOpen), b)));
    gview.querySelector('[data-gv-close]').addEventListener('click', closeView);
    gview.querySelector('[data-gv-prev]').addEventListener('click', () => show(at - 1));
    gview.querySelector('[data-gv-next]').addEventListener('click', () => show(at + 1));
    gview.addEventListener('click', (e) => { if (e.target === gview) closeView(); });
  }

  document.querySelectorAll('[data-pano]').forEach((box) => {
    const start = box.querySelector('[data-pano-start]');
    const base = box.dataset.base; // assets/, relative to this page
    // The tour's rooms in walking order. Until Arha's own 360 photos arrive, every room shows the sample image.
    const ROOMS = [
      ['entrance', 'Entrance'], ['reception', 'Reception'], ['lounge', 'Lounge'],
      ['operatory', 'Treatment room'], ['sterilisation', 'Sterilisation'],
    ];
    const SAMPLE = `${base}pano/sample-360.jpg`;
    const load = (tag, attrs) => new Promise((resolve, reject) => {
      const el = document.createElement(tag);
      Object.assign(el, attrs, { onload: resolve, onerror: reject });
      document.head.append(el);
    });
    start.addEventListener('click', async () => {
      start.disabled = true;
      start.textContent = 'Loading…';
      try {
        await Promise.all([
          load('link', { rel: 'stylesheet', href: `${base}vendor/pannellum/pannellum.css` }),
          load('script', { src: `${base}vendor/pannellum/pannellum.js` }),
        ]);
        const scenes = {};
        ROOMS.forEach(([id, name], i) => {
          const hotSpots = [];
          if (i > 0) hotSpots.push({ pitch: -8, yaw: -150, type: 'scene', text: `Back to ${ROOMS[i - 1][1]}`, sceneId: ROOMS[i - 1][0] });
          if (i < ROOMS.length - 1) hotSpots.push({ pitch: -8, yaw: 20, type: 'scene', text: `Go to ${ROOMS[i + 1][1]}`, sceneId: ROOMS[i + 1][0] });
          scenes[id] = { title: `${name} · sample image`, type: 'equirectangular', panorama: SAMPLE, hfov: 100, hotSpots };
        });
        const viewer = box.querySelector('.pano__viewer');
        viewer.hidden = false;
        box.querySelector('.pano__cover').hidden = true;
        window.pannellum.viewer(viewer, {
          default: { firstScene: 'entrance', sceneFadeDuration: reduceMotion ? 0 : 300, autoLoad: true, showZoomCtrl: true, keyboardZoom: true, compass: false },
          scenes,
        });
        viewer.setAttribute('aria-label', 'Sample 360° view. Drag or use the arrow keys to look around.');
        viewer.tabIndex = 0;
        viewer.focus();
        track('pano_open');
      } catch (err) {
        start.disabled = false;
        start.textContent = 'Try the sample 360° view';
      }
    });
  });
})();
