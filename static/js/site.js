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
  window.arhaTrack = track; // used by planner.js on the international page

  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a");
    if (!a) return;
    var href = a.getAttribute("href") || "";
    var where = { link_text: (a.textContent || "").trim().slice(0, 60), page_path: location.pathname };
    if (href.indexOf("tel:") === 0) track("call_click", where);
    else if (href.indexOf("wa.me") > -1) track("whatsapp_click", where);
    else if (a.hasAttribute("data-event") || href.indexOf("#book") > -1) track("booking_click", where);
  });

  /* ---------------------------------------------------------- cookie banner + preferences (GA4 only when Analytics is on) */
  var CATS = ["marketing", "personalisation", "analytics"];
  function readConsent() {
    var raw = store.get("arha-consent");
    if (!raw) return null;
    if (raw === "granted" || raw === "denied") { var all = raw === "granted", o = {}; CATS.forEach(function (c) { o[c] = all; }); return o; }
    try { return JSON.parse(raw); } catch (e) { return null; }
  }
  function applyConsent(c) {
    if (c.analytics) loadGA();
    if (gaLoaded) gtag("consent", "update", { analytics_storage: c.analytics ? "granted" : "denied",
      ad_storage: c.marketing ? "granted" : "denied", ad_user_data: c.marketing ? "granted" : "denied", ad_personalization: c.personalisation ? "granted" : "denied" });
  }
  var banner = $("#cookie"), reopen = $("[data-cookie-reopen]"), consent = readConsent();
  if (consent) applyConsent(consent);
  if (banner) {
    var prefs = $("#cookie-prefs", banner), prefBtn = $("[data-cookie-prefs]", banner), saveBtn = $("[data-consent=save]", banner);
    var showPrefs = function (on) {
      prefs.hidden = !on; saveBtn.hidden = !on; prefBtn.hidden = on; prefBtn.setAttribute("aria-expanded", on ? "true" : "false");
      if (on) { var c = readConsent() || {}; $$("[data-pref]", prefs).forEach(function (x) { x.checked = !!c[x.getAttribute("data-pref")]; }); $("[data-pref]", prefs).focus(); }
    };
    if (!consent) banner.hidden = false; else if (reopen) reopen.hidden = false;
    prefBtn.addEventListener("click", function () { showPrefs(true); });
    $$("[data-consent]", banner).forEach(function (b) {
      b.addEventListener("click", function () {
        var v = b.getAttribute("data-consent"), c = {};
        CATS.forEach(function (k) { c[k] = v === "all" ? true : v === "none" ? false : !!$('[data-pref="' + k + '"]', prefs).checked; });
        store.set("arha-consent", JSON.stringify(c));
        banner.hidden = true; showPrefs(false);
        if (reopen) reopen.hidden = false;
        applyConsent(c);
      });
    });
    var openBanner = function () { banner.hidden = false; if (reopen) reopen.hidden = true; showPrefs(true); };
    if (reopen) reopen.addEventListener("click", openBanner);
    $$("[data-cookie-open]").forEach(function (b) { b.addEventListener("click", openBanner); });
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

  /* ---------------------------------------------------------- dropdowns + Discover mega menu (desktop): hover or click, fade/slide in */
  var reduceMotion = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  function megaVideo(li, on) {
    var box = $("[data-video-manual]", li);
    if (!box || reduceMotion) return;
    if (on) startVideo(box); else { var v = $("video", box); if (v && !v.paused) v.pause(); }
  }
  function setOpen(li, open) {
    li.classList.toggle("is-open", open);
    $("[data-dd]", li).setAttribute("aria-expanded", open ? "true" : "false");
    megaVideo(li, open);
  }
  function closeDD(except) {
    $$(".navstrip li.is-open").forEach(function (li) { if (li !== except) setOpen(li, false); });
  }
  $$("[data-dd]").forEach(function (b) {
    var li = b.parentNode, timer;
    b.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = !li.classList.contains("is-open");
      closeDD(li); setOpen(li, open);
    });
    li.addEventListener("click", function (e) { e.stopPropagation(); });
    if (window.matchMedia && matchMedia("(hover: hover)").matches) {
      li.addEventListener("mouseenter", function () { clearTimeout(timer); closeDD(li); setOpen(li, true); });
      li.addEventListener("mouseleave", function () { timer = setTimeout(function () { setOpen(li, false); }, 150); });
    }
    li.addEventListener("focusout", function (e) { if (!li.contains(e.relatedTarget)) setOpen(li, false); });
  });
  document.addEventListener("click", function () { closeDD(); });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    var open = $(".navstrip li.is-open");
    closeDD(); closeDrawer();
    if (open) $("[data-dd]", open).focus();
  });

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
  /* click-to-play film with sound: nothing is downloaded until the visitor presses play */
  $$("[data-embed]").forEach(function (box) {
    var btn = $(".embed__play", box);
    btn.addEventListener("click", function () {
      var v = document.createElement("video");
      v.src = box.getAttribute("data-embed"); v.controls = true; v.playsInline = true; v.autoplay = true;
      if (box.hasAttribute("data-muted")) { v.muted = true; v.loop = false; }
      v.setAttribute("aria-label", btn.getAttribute("aria-label").replace("Play video: ", ""));
      box.appendChild(v); btn.remove();
      var pic = $(".vid__poster", box); if (pic) pic.remove();
      var p = v.play(); if (p && p.catch) p.catch(function () {});
      v.focus();
      track("video_play", { video: box.getAttribute("data-name") || "film", page_path: location.pathname });
    });
  });
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

  /* ---------------------------------------------------------- scroll-in reveals: soft fade-up, 30px, 0.7s, small stagger */
  var rv = $$("[data-reveal]");
  if (rv.length && !reduceMotion && "IntersectionObserver" in window) {
    var rio = new IntersectionObserver(function (entries) {
      var n = 0;
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        en.target.style.setProperty("--rv-d", (n++ * 0.08) + "s");
        en.target.classList.add("is-in"); rio.unobserve(en.target);
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    rv.forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.top < innerHeight && r.bottom > 0) return; // already on screen at load: never hide it
      el.classList.add("rv"); rio.observe(el);
    });
  }

  /* ---------------------------------------------------------- team bio pop-ups (native <dialog>) */
  $$("[data-dialog]").forEach(function (b) {
    var d = document.getElementById(b.getAttribute("data-dialog"));
    if (!d || !d.showModal) return;
    b.addEventListener("click", function () { d.showModal(); });
    $("[data-dialog-close]", d).addEventListener("click", function () { d.close(); });
    d.addEventListener("click", function (e) { if (e.target === d) d.close(); });
    d.addEventListener("close", function () { b.focus(); });
  });

  /* ---------------------------------------------------------- blog topic filter */
  $$("[data-filter]").forEach(function (b, _, all) {
    b.addEventListener("click", function () {
      var cat = b.getAttribute("data-filter");
      all.forEach(function (x) { var on = x === b; x.classList.toggle("is-on", on); x.setAttribute("aria-pressed", on ? "true" : "false"); });
      $$(".postcard[data-cat]").forEach(function (c) { c.hidden = !!cat && c.getAttribute("data-cat") !== cat; });
    });
  });

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

  /* ---------------------------------------------------------- phone call bar: hidden over the first section and the footer */
  var callbar = $("[data-callbar]");
  if (callbar) {
    // also hidden over [data-callbar-hide] blocks (the trip planner has its own buttons at the bottom of the screen)
    var first = $("[data-callbar-first]") || $("#main > section"), foot = $(".ftr"), seen = [];
    var watched = [first, foot].concat($$("[data-callbar-hide]")).filter(Boolean);
    if (!("IntersectionObserver" in window) || !first) callbar.classList.add("is-shown");
    else {
      var cio = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) { seen[watched.indexOf(en.target)] = en.isIntersecting; });
        callbar.classList.toggle("is-shown", !seen.some(Boolean));
      });
      watched.forEach(function (w) { cio.observe(w); });
    }
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
      var kind = f.getAttribute("data-form"), files = [];
      if (f.elements.concern && !f.elements.concern.value) { say("Please choose what your query is about."); f.elements.concern.focus(); return; }
      if (kind === "referral") {
        var need = [["practice", "Please add the practice name."], ["email", "Please add your email address."], ["patient_name", "Please add the patient's name."],
          ["patient_dob", "Please add the patient's date of birth."], ["patient_phone", "Please add the patient's phone number."],
          ["treatment", "Please choose what the referral is for."], ["urgent", "Please say how urgent the treatment is."], ["history", "Please add a brief patient history."]];
        for (var n = 0; n < need.length; n++) {
          var el = f.elements[need[n][0]];
          if (!el.value.trim()) { say(need[n][1]); el.focus(); return; }
        }
      }
      if (kind === "xray" && !f.elements.email.value.trim()) { say("Please add your email address."); f.elements.email.focus(); return; }
      if (f.elements.files) {
        // limits come from the input: data-max (files), data-mb (MB each), data-ext (allowed extensions)
        var fin = f.elements.files, maxN = +fin.getAttribute("data-max") || 3, maxMb = +fin.getAttribute("data-mb") || 4;
        var extRe = new RegExp("\\.(" + (fin.getAttribute("data-ext") || "pdf|jpe?g|png") + ")$", "i");
        files = Array.prototype.slice.call(fin.files || []);
        if (fin.required && !files.length) { say("Please choose at least one file to upload."); fin.focus(); return; }
        if (files.length > maxN) { say("Please attach up to " + maxN + " files."); fin.focus(); return; }
        for (var k = 0; k < files.length; k++) {
          if (!extRe.test(files[k].name)) { say("That file type isn't accepted: " + files[k].name); fin.focus(); return; }
          if (files[k].size > maxMb * 1024 * 1024) { say(files[k].name + " is larger than " + maxMb + " MB. Please attach a smaller file."); fin.focus(); return; }
        }
      }
      if (!f.elements.consent.checked) { say(kind === "referral" ? "Please confirm the patient has agreed to this referral." : "Please tick the box so we can contact you about your request."); f.elements.consent.focus(); return; }
      if (Date.now() - started < 3000) { say("Please try again in a moment."); return; }

      var data = new URLSearchParams();
      new FormData(f).forEach(function (v, key) { if (typeof v === "string") data.append(key, v); });
      if (!cfg.formsEndpoint && kind === "xray") {
        // Preview without a forms backend: files can't travel over WhatsApp links, so ask for a secure link instead.
        track("form_submit", { form: kind, method: "whatsapp_fallback" });
        say("Secure uploads aren't switched on in this preview. Opening WhatsApp so we can send you a secure upload link.", true);
        window.open("https://wa.me/" + cfg.phone.replace(/\D/g, "") + "?text=" + encodeURIComponent("Hello Arha Dental Care, I'd like to send my X-rays before my visit. Name: " + name), "_blank", "noopener");
        return;
      }
      if (!cfg.formsEndpoint && kind === "referral") {
        var rmsg = ["Hello Arha Dental Care, I'd like to refer a patient.",
          "Referring dentist: " + name + ", " + f.elements.practice.value.trim(), "Phone: " + phone, "Email: " + f.elements.email.value.trim(),
          "Patient: " + f.elements.patient_name.value.trim(),
          "Referral for: " + f.elements.treatment.options[f.elements.treatment.selectedIndex].text, "Urgency: " + f.elements.urgent.value]
          .concat(files.length ? ["I'll send the X-rays and reports separately."] : []).join(String.fromCharCode(10));
        track("form_submit", { form: kind, method: "whatsapp_fallback" });
        say("Opening WhatsApp with the referral details. If it doesn't open, please call us on " + cfg.phone + ".", true);
        window.open("https://wa.me/" + cfg.phone.replace(/\D/g, "") + "?text=" + encodeURIComponent(rmsg), "_blank", "noopener");
        return;
      }
      if (!cfg.formsEndpoint) {
        // Preview without a forms backend: hand the request over to WhatsApp instead of losing it.
        var t = f.elements.treatment && f.elements.treatment.value ? f.elements.treatment.options ? f.elements.treatment.options[f.elements.treatment.selectedIndex].text : f.elements.treatment.value : "";
        var msg = "Hello Arha Dental Care, I'd like to " + (f.getAttribute("data-form") === "booking" ? "request an appointment" : "ask a question") +
          ".\nName: " + name + "\nPhone: " + phone + (f.elements.concern && f.elements.concern.value ? "\nQuery: " + f.elements.concern.value : "") + (t ? "\nAbout: " + t : "") + (f.elements.when && f.elements.when.value ? "\nPreferred time: " + f.elements.when.value : "") +
          (f.elements.message.value.trim() ? "\n" + f.elements.message.value.trim() : "");
        track("form_submit", { form: f.getAttribute("data-form"), method: "whatsapp_fallback" });
        say("Opening WhatsApp with your message. If it doesn't open, please call us on " + cfg.phone + ".", true);
        window.open("https://wa.me/" + cfg.phone.replace(/\D/g, "") + "?text=" + encodeURIComponent(msg), "_blank", "noopener");
        return;
      }
      var btn = $("button[type=submit]", f); btn.disabled = true;
      say(files.length ? "Uploading files and sending…" : "Sending…", true);
      // Files go as base64 fields (Apps Script can't read multipart uploads): file1_name, file1_type, file1_data, …
      Promise.all(files.map(function (file) {
        return new Promise(function (ok, bad) {
          var rd = new FileReader();
          var type = file.type || (/\.zip$/i.test(file.name) ? "application/zip" : /\.dcm$/i.test(file.name) ? "application/dicom" : "application/octet-stream");
          rd.onload = function () { ok({ name: file.name, type: type, data: String(rd.result).split(",")[1] || "" }); };
          rd.onerror = bad; rd.readAsDataURL(file);
        });
      })).then(function (enc) {
        enc.forEach(function (x, i) { data.append("file" + (i + 1) + "_name", x.name); data.append("file" + (i + 1) + "_type", x.type); data.append("file" + (i + 1) + "_data", x.data); });
        return fetch(cfg.formsEndpoint, { method: "POST", body: data });
      })
        .then(function (r) { return r.json(); })
        .then(function (j) {
          if (!j || !j.ok) throw new Error((j && j.error) || "failed");
          track("form_submit", { form: f.getAttribute("data-form") });
          if (kind === "xray") track("xray_upload_submit", { files: files.length });
          f.reset(); started = Date.now();
          say(kind === "referral" ? "Thank you. We've received the referral and will confirm by email or phone." :
            kind === "xray" ? "Thank you. Your files are with us securely; we'll be in touch on WhatsApp or by email." : "Thank you. We've received your request and will call or WhatsApp you during opening hours.", true);
          if (window.turnstile) try { turnstile.reset(); } catch (e) {}
        })
        .catch(function () { say("Sorry, that didn't go through. Please call us on " + cfg.phone + " or WhatsApp us."); })
        .then(function () { btn.disabled = false; });
    });
  });
})();
