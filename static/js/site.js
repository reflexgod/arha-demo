/* Arha Dental Care v5: one small script, no dependencies. */
(function () {
  "use strict";
  var cfg = {};
  try { cfg = JSON.parse(document.getElementById("cfg").textContent); } catch (e) {}
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };

  /* ---------------------------------------------------------- old links from the previous site */
  var legacy = { "#doctors": "/the-practice/#meet-the-team", "#team": "/the-practice/#meet-the-team", "#about": "/the-practice/#our-story",
    "#services": "/treatments/", "#treatments": "/treatments/", "#contact": "/contact/", "#book": "/contact/#book",
    "#appointment": "/contact/#book", "#faq": "/for-patients/", "#location": "/contact/" };
  if (location.pathname === "/" && legacy[location.hash]) { location.replace(legacy[location.hash]); return; }

  /* ---------------------------------------------------------- analytics (GA4 only after consent) */
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  var gaLoaded = false;
  function loadGA() {
    if (gaLoaded || !cfg.ga4) return;
    gaLoaded = true;
    gtag("consent", "default", { ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied", analytics_storage: "denied" });
    gtag("consent", "update", { analytics_storage: "granted" });
    gtag("js", new Date());
    gtag("config", cfg.ga4, { anonymize_ip: true });
    var s = document.createElement("script");
    s.async = true; s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(cfg.ga4);
    document.head.appendChild(s);
  }
  function track(name, params) { if (gaLoaded) gtag("event", name, params || {}); }

  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a");
    if (!a) return;
    var href = a.getAttribute("href") || "";
    var where = { link_text: (a.textContent || "").trim().slice(0, 60), page_path: location.pathname };
    if (href.indexOf("tel:") === 0) track("call_click", where);
    else if (href.indexOf("wa.me") > -1) track("whatsapp_click", where);
    else if (a.hasAttribute("data-event") || href.indexOf("#book") > -1) track("booking_click", where);
  });

  /* ---------------------------------------------------------- cookie banner */
  var banner = $("#cookie"), reopen = $("[data-cookie-reopen]");
  var choice = store.get("arha-consent");
  if (choice === "granted") loadGA();
  if (banner) {
    if (!choice) banner.hidden = false; else if (reopen) reopen.hidden = false;
    $$("[data-consent]", banner).forEach(function (b) {
      b.addEventListener("click", function () {
        var v = b.getAttribute("data-consent");
        store.set("arha-consent", v);
        banner.hidden = true;
        if (reopen) reopen.hidden = false;
        if (v === "granted") loadGA();
        else if (gaLoaded) gtag("consent", "update", { analytics_storage: "denied" });
      });
    });
    if (reopen) reopen.addEventListener("click", function () { banner.hidden = false; reopen.hidden = true; });
  }

  /* ---------------------------------------------------------- live clock and open / closed status (clinic time) */
  var DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  var LONG = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  function clinicNow() {
    var parts = {};
    new Intl.DateTimeFormat("en-GB", { timeZone: cfg.timeZone || "Asia/Kolkata", weekday: "short", day: "numeric", month: "short",
      hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).formatToParts(new Date()).forEach(function (p) { parts[p.type] = p.value; });
    return { dow: DAYS.indexOf(parts.weekday), day: parts.day, month: parts.month, h: +parts.hour, m: +parts.minute, wd: parts.weekday };
  }
  function toMin(t) { var x = t.split(":"); return +x[0] * 60 + +x[1]; }
  function fmt(t) { var x = t.split(":"), h = +x[0], m = +x[1]; return (h % 12 || 12) + (m ? ":" + (m < 10 ? "0" : "") + m : "") + (h < 12 ? " am" : " pm"); }
  function status(n) {
    var hours = cfg.hours || [], mins = n.h * 60 + n.m, today = hours[n.dow];
    if (today && mins >= toMin(today[0]) && mins < toMin(today[1])) return { open: true, text: "Open now", sub: "until " + fmt(today[1]) };
    for (var i = 0; i < 8; i++) {
      var d = (n.dow + i) % 7, h = hours[d];
      if (!h) continue;
      if (i === 0 && mins >= toMin(h[0])) continue;
      return { open: false, text: "Closed", sub: "opens " + (i === 0 ? "" : i === 1 ? "tomorrow " : LONG[d] + " ") + fmt(h[0]) };
    }
    return { open: false, text: "Closed", sub: "" };
  }
  var clock = $("[data-clock]");
  function tick() {
    if (!clock) return;
    var n = clinicNow(), s = status(n);
    var h12 = n.h % 12 || 12;
    $("[data-clock-text]", clock).textContent = n.wd + " " + n.day + " " + n.month + " | " + h12 + ":" + (n.m < 10 ? "0" : "") + n.m + (n.h < 12 ? " AM" : " PM") + " IST";
    var st = $("[data-status]", clock);
    st.classList.toggle("is-closed", !s.open);
    $("[data-status-text]", clock).innerHTML = s.text + (s.sub ? " <small>· " + s.sub + "</small>" : "");
    var use = $("svg use", clock);
    if (use) use.setAttribute("href", n.h >= 6 && n.h < 19 ? "#i-sun" : "#i-moon");
  }
  tick(); setInterval(tick, 30000);

  /* ---------------------------------------------------------- dropdowns (desktop) */
  function closeDD(except) {
    $$(".navstrip li.is-open").forEach(function (li) { if (li !== except) { li.classList.remove("is-open"); $("[data-dd]", li).setAttribute("aria-expanded", "false"); } });
  }
  $$("[data-dd]").forEach(function (b) {
    b.addEventListener("click", function (e) {
      e.stopPropagation();
      var li = b.parentNode, open = !li.classList.contains("is-open");
      closeDD(li);
      li.classList.toggle("is-open", open);
      b.setAttribute("aria-expanded", open ? "true" : "false");
    });
  });
  document.addEventListener("click", function () { closeDD(); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") { closeDD(); closeDrawer(); } });

  /* ---------------------------------------------------------- drawer (phones, tablets) */
  var drawer = $("#drawer"), burger = $("[data-drawer-open]");
  function openDrawer() {
    if (!drawer) return;
    drawer.classList.add("is-open"); document.body.classList.add("no-scroll");
    burger.setAttribute("aria-expanded", "true");
    var c = $("[data-drawer-close]", drawer); if (c) c.focus();
  }
  function closeDrawer() {
    if (!drawer || !drawer.classList.contains("is-open")) return;
    drawer.classList.remove("is-open"); document.body.classList.remove("no-scroll");
    burger.setAttribute("aria-expanded", "false"); burger.focus();
  }
  if (burger) burger.addEventListener("click", openDrawer);
  if (drawer) {
    $("[data-drawer-close]", drawer).addEventListener("click", closeDrawer);
    $$("[data-dr]", drawer).forEach(function (b) {
      b.addEventListener("click", function () {
        var li = b.parentNode, open = !li.classList.contains("is-open");
        li.classList.toggle("is-open", open); b.setAttribute("aria-expanded", open ? "true" : "false");
      });
    });
    $$("a", drawer).forEach(function (a) { a.addEventListener("click", function () { if (a.getAttribute("href").indexOf("#") > -1) closeDrawer(); }); });
  }

  /* ---------------------------------------------------------- videos: load and play only when on screen */
  var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  var saveData = navigator.connection && navigator.connection.saveData;
  var vids = $$("[data-video]");
  function startVideo(box) {
    var v = $("video", box);
    if (!v.dataset.ready) {
      $$("source", v).forEach(function (s) {
        var mq = s.getAttribute("data-media");
        if (!mq || matchMedia(mq).matches) s.src = s.getAttribute("data-src"); else s.remove();
      });
      v.dataset.ready = "1";
      v.addEventListener("playing", function () { box.classList.add("is-playing"); });
      v.load();
    }
    var p = v.play(); if (p && p.catch) p.catch(function () {});
  }
  if (vids.length && !reduce && !saveData && "IntersectionObserver" in window) {
    var vio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) startVideo(en.target);
        else { var v = $("video", en.target); if (v && !v.paused) v.pause(); }
      });
    }, { rootMargin: "100px" });
    var watch = function () { vids.forEach(function (b) { vio.observe(b); }); };
    if (document.readyState === "complete") setTimeout(watch, 300); else addEventListener("load", function () { setTimeout(watch, 300); });
  }

  /* ---------------------------------------------------------- map: load the embed when it comes near the screen */
  var map = $("[data-map]");
  if (map) {
    var loadMap = function () {
      if (map.dataset.loaded) return; map.dataset.loaded = "1";
      var f = document.createElement("iframe");
      f.src = map.getAttribute("data-map"); f.title = "Map showing Arha Dental Care on Peddar Road";
      f.referrerPolicy = "no-referrer-when-downgrade";
      map.insertBefore(f, map.firstChild);
    };
    if ("IntersectionObserver" in window) {
      var mio = new IntersectionObserver(function (en) { if (en[0].isIntersecting) { loadMap(); mio.disconnect(); } }, { rootMargin: "400px" });
      mio.observe(map);
    } else loadMap();
  }

  /* ---------------------------------------------------------- reviews carousel (only rendered when switched on) */
  $$("[data-carousel]").forEach(function (track) {
    var items = $$(".review", track), i = 0;
    if (items.length < 2) return;
    setInterval(function () { items[i].classList.remove("is-active"); i = (i + 1) % items.length; items[i].classList.add("is-active"); }, 8000);
  });

  /* ---------------------------------------------------------- forms */
  var params = new URLSearchParams(location.search);
  var pre = params.get("treatment");
  if (pre) { var sel = $("#f-book-treatment"); if (sel && $('option[value="' + pre.replace(/[^a-z-]/g, "") + '"]', sel)) sel.value = pre; }

  var tsLoaded = false;
  function loadTurnstile() {
    if (tsLoaded || !cfg.formsEndpoint || !cfg.turnstile) return;
    tsLoaded = true;
    var s = document.createElement("script");
    s.src = "https://challenges.cloudflare.com/turnstile/v0/api.js"; s.async = true; s.defer = true;
    document.head.appendChild(s);
  }

  $$("form[data-form]").forEach(function (f) {
    var started = Date.now();
    var statusEl = $(".form__status", f);
    f.elements.page.value = location.pathname;
    f.addEventListener("focusin", loadTurnstile, { once: true });
    function say(msg, ok) { statusEl.textContent = msg; statusEl.className = "form__status " + (ok ? "is-ok" : "is-err"); }
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      if (f.elements.company.value) return; // honeypot
      var name = f.elements.name.value.trim(), phone = f.elements.phone.value.trim();
      if (!name) { say("Please tell us your name."); f.elements.name.focus(); return; }
      if (phone.replace(/\D/g, "").length < 8) { say("Please enter a phone or WhatsApp number we can reach you on."); f.elements.phone.focus(); return; }
      if (f.elements.email.value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(f.elements.email.value)) { say("Please check your email address."); f.elements.email.focus(); return; }
      if (!f.elements.consent.checked) { say("Please tick the box so we can contact you about your request."); f.elements.consent.focus(); return; }
      if (Date.now() - started < 3000) { say("Please try again in a moment."); return; }

      var data = new URLSearchParams(new FormData(f));
      if (!cfg.formsEndpoint) {
        // Preview without a forms backend: hand the request over to WhatsApp instead of losing it.
        var t = f.elements.treatment && f.elements.treatment.value ? f.elements.treatment.options ? f.elements.treatment.options[f.elements.treatment.selectedIndex].text : f.elements.treatment.value : "";
        var msg = "Hello Arha Dental Care, I'd like to " + (f.getAttribute("data-form") === "booking" ? "request an appointment" : "ask a question") +
          ".\nName: " + name + "\nPhone: " + phone + (t ? "\nAbout: " + t : "") + (f.elements.when && f.elements.when.value ? "\nPreferred time: " + f.elements.when.value : "") +
          (f.elements.message.value.trim() ? "\n" + f.elements.message.value.trim() : "");
        track("form_submit", { form: f.getAttribute("data-form"), method: "whatsapp_fallback" });
        say("Opening WhatsApp with your message. If it doesn't open, please call us on " + cfg.phone + ".", true);
        window.open("https://wa.me/" + cfg.phone.replace(/\D/g, "") + "?text=" + encodeURIComponent(msg), "_blank", "noopener");
        return;
      }
      var btn = $("button[type=submit]", f); btn.disabled = true;
      say("Sending…", true);
      fetch(cfg.formsEndpoint, { method: "POST", body: data })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          if (!j || !j.ok) throw new Error((j && j.error) || "failed");
          track("form_submit", { form: f.getAttribute("data-form") });
          f.reset(); started = Date.now();
          say("Thank you. We've received your request and will call or WhatsApp you during opening hours.", true);
          if (window.turnstile) try { turnstile.reset(); } catch (e) {}
        })
        .catch(function () { say("Sorry, that didn't go through. Please call us on " + cfg.phone + " or WhatsApp us."); })
        .then(function () { btn.disabled = false; });
    });
  });
})();
