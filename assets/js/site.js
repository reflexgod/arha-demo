/* ==========================================================================
   Arha Dental Care: site behaviour. Vanilla JS, no dependencies.

   1. Header hairline       6. Before & After: colour nearest centre (touch)
   2. Desktop dropdowns     7. Mobile action bar
   3. Side menu             8. Map facade
   4. Reveal on scroll      9. Reviews: crossfading quote
   5. Hero video           10. Before & After: filter, case view, slider
                           11. Accordions (FAQ)
                           12. Live open status
                           13. Plan your treatment
   ========================================================================== */
(() => {
  'use strict';

  const root = document.documentElement;
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* 1. Header hairline: appears after 10px of scroll ----------------------- */
  const header = document.querySelector('[data-header]');
  if (header) {
    let ticking = false;
    const update = () => {
      header.classList.toggle('is-scrolled', window.scrollY > 10);
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

  /* 4. Reveal on scroll: opacity only, 1.5s, once, when ~15% into the viewport.
        Siblings revealed together are staggered 0 / .25 / .5 / .75s. -------- */
  const reveals = document.querySelectorAll('.reveal');
  if (!reduceMotion && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      entries
        .filter((e) => e.isIntersecting)
        .sort((a, b) => (a.boundingClientRect.top - b.boundingClientRect.top) || (a.boundingClientRect.left - b.boundingClientRect.left))
        .forEach((e, i) => {
          e.target.style.setProperty('--delay', `${Math.min(i, 3) * 250}ms`);
          e.target.classList.add('is-in');
          io.unobserve(e.target);
        });
    }, { rootMargin: '0px 0px -15% 0px' });
    reveals.forEach((el) => io.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add('is-in'));
  }

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

  /* 7. Mobile action bar: after the hero, hidden while the footer shows --- */
  const bar = document.querySelector('[data-mobile-bar]');
  const footer = document.querySelector('[data-footer]');
  if (bar && 'IntersectionObserver' in window) {
    let pastHero = !hero;
    let footerVisible = false;
    const sync = () => {
      const show = pastHero && !footerVisible;
      bar.classList.toggle('is-visible', show);
      bar.toggleAttribute('inert', !show);
    };
    if (hero) {
      new IntersectionObserver(([e]) => {
        pastHero = !e.isIntersecting;
        sync();
      }).observe(hero);
    }
    if (footer) {
      new IntersectionObserver(([e]) => {
        footerVisible = e.isIntersecting;
        sync();
      }).observe(footer);
    }
    sync();
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

  /* 11b. Google reviews link: Arha's Google Business Profile. Leave empty to keep the link as "#". */
  const GOOGLE_REVIEWS_URL = 'https://share.google/PzhwgJ9QJMErZnk9R';
  if (GOOGLE_REVIEWS_URL) {
    document.querySelectorAll('[data-google-reviews]').forEach((link) => {
      link.href = GOOGLE_REVIEWS_URL;
      link.target = '_blank';
      link.rel = 'noopener';
    });
  }

  /* 12. Live open status (India time). Hours live in this one config. ------- */
  const CLINIC_HOURS = {
    timeZone: 'Asia/Kolkata',
    // 0 = Sunday ... 6 = Saturday; null = closed. Confirm with the clinic (Google shows 9:00 AM).
    days: [null, ['09:30', '18:30'], ['09:30', '18:30'], ['09:30', '18:30'], ['09:30', '18:30'], ['09:30', '18:30'], ['09:30', '18:30']],
  };
  const statusEls = document.querySelectorAll('[data-open-status]');
  if (statusEls.length) {
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
    const describe = () => {
      const { day, minutes } = nowInClinic();
      const today = CLINIC_HOURS.days[day];
      if (today && minutes >= toMinutes(today[0]) && minutes < toMinutes(today[1])) {
        return { open: true, text: `Open now · until ${label(today[1])}` };
      }
      if (today && minutes < toMinutes(today[0])) return { open: false, text: `Closed · Opens today at ${label(today[0])}` };
      for (let i = 1; i <= 7; i += 1) {
        const next = CLINIC_HOURS.days[(day + i) % 7];
        if (next) return { open: false, text: `Closed · Opens ${i === 1 ? 'tomorrow' : DAY_NAMES[(day + i) % 7]} at ${label(next[0])}` };
      }
      return { open: false, text: 'Closed' };
    };
    const render = () => {
      const s = describe();
      statusEls.forEach((el) => { el.textContent = s.text; el.classList.toggle('is-open', s.open); });
    };
    render();
    setInterval(render, 60000);
  }

  /* 13. Plan your treatment (visiting patients): one question at a time, nothing
         stored or submitted; the result opens WhatsApp with the plan written in. */
  const PLANNER = {
    whatsapp: '919975507714',
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
})();
