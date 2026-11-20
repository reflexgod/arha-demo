/* Arha Dental Care v5: International & NRI trip planner (/international-patients/ only).
   Five steps, keyboard accessible, state kept in the URL (never the name or number). Sample timings come from
   content/travel-plans.yaml and stay marked [[TBC]] until the clinic confirms them. Nothing is sent anywhere: the
   visitor chooses to share the plan on WhatsApp. */
(function () {
  "use strict";
  var root = document.querySelector("[data-planner]");
  if (!root) return;
  var D = JSON.parse(document.getElementById("plan-data").textContent);
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var NL = String.fromCharCode(10);
  var track = function (n, p) { if (window.arhaTrack) window.arhaTrack(n, p || {}); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  // [[TBC: note || fallback]]: the tag shows only in review mode (html.review); visitors see the fallback, if any.
  var split = function (b) { var i = b.indexOf("||"); return i < 0 ? [b.trim(), ""] : [b.slice(0, i).trim(), b.slice(i + 2).trim()]; };
  var tbc = function (s) { return esc(s).replace(/\[\[TBC:?\s*([^\]]*)\]\]/g, function (_, b) { var x = split(b);
    return '<mark class="tbc" title="To be confirmed by the clinic">[[TBC: ' + x[0] + ']]</mark>' + (x[1] ? '<span class="tbc-fb">' + x[1] + "</span>" : ""); }); };
  var strip = function (s) { return String(s).replace(/\s*\[\[TBC:?([^\]]*)\]\]/g, function (_, b) { var f = split(b)[1]; return f ? " " + f : ""; }).trim(); };
  var T = {}, C = {};
  D.plans.treatments.forEach(function (t) { T[t.id] = t; });
  D.countries.forEach(function (c) { C[c.id] = c; });

  /* ------------------------------------------------------------ time zones (DST-aware, from the browser's Intl data) */
  var browserTz = (Intl.DateTimeFormat().resolvedOptions().timeZone) || "UTC";
  function offsetMin(tz, date) {
    var p = {};
    new Intl.DateTimeFormat("en-US", { timeZone: tz, hourCycle: "h23", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit" })
      .formatToParts(date).forEach(function (x) { p[x.type] = x.value; });
    return Math.round((Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour % 24, +p.minute) - date.getTime()) / 60000);
  }
  function fmt(mins) {
    var h = Math.floor(mins / 60), m = mins % 60;
    return (h % 12 || 12) + (m ? ":" + (m < 10 ? "0" : "") + m : "") + (h < 12 ? " am" : " pm");
  }
  function tzInfo(tz, label) {
    var now = new Date(); now.setSeconds(0, 0);
    var cOff = offsetMin(D.clinicTz, now), lOff = offsetMin(tz, now), d = cOff - lOff, a = Math.abs(d);
    var gap = Math.floor(a / 60) + (Math.floor(a / 60) === 1 ? " hour" : " hours") + (a % 60 ? " " + (a % 60) + " minutes" : "");
    var diff = d === 0 ? "Mumbai is on the same time as " + label + "." : "Mumbai is " + gap + (d > 0 ? " ahead of " : " behind ") + label + " today.";
    var open = (D.hours || []).filter(Boolean)[0], hrs = "";
    if (open) {
      var conv = function (t) {
        var x = t.split(":"), mins = +x[0] * 60 + +x[1] - d, shift = Math.floor(mins / 1440);
        mins = ((mins % 1440) + 1440) % 1440;
        return fmt(mins) + (shift > 0 ? " (next day)" : shift < 0 ? " (previous day)" : "");
      };
      hrs = "Clinic hours, Monday to Saturday " + fmt(+open[0].split(":")[0] * 60 + +open[0].split(":")[1]) + " to " +
        fmt(+open[1].split(":")[0] * 60 + +open[1].split(":")[1]) + " in Mumbai, are " + conv(open[0]) + " to " + conv(open[1]) + " " + label + " time.";
    }
    return { diff: diff, hours: hrs };
  }

  /* Country tabs further down the page: time difference for every listed city, and keyboard-operable tabs */
  $$("[data-tzdiff]").forEach(function (dd) {
    var tzs = dd.getAttribute("data-tzdiff").split(",").filter(Boolean), labels = dd.getAttribute("data-tzlabels").split("|");
    if (!tzs.length) { tzs = [browserTz]; labels = ["your"]; }
    dd.innerHTML = tzs.map(function (tz, k) {
      var lab = labels[k] === "your" ? "your" : labels[k].replace(/ \(.*\)$/, ""), info = tzInfo(tz, lab === "your" ? "you" : lab);
      return "<span class=\"tzrow\">" + esc(info.diff) + " " + esc(info.hours.replace(" you time", " your time")) + "</span>";
    }).join("");
  });
  var tabs = $$("[data-tab]");
  function selectTab(t, focus) {
    tabs.forEach(function (x) {
      var on = x === t;
      x.setAttribute("aria-selected", on ? "true" : "false"); x.tabIndex = on ? 0 : -1;
      document.getElementById(x.getAttribute("aria-controls")).hidden = !on;
    });
    if (focus) t.focus();
  }
  tabs.forEach(function (t, k) {
    t.addEventListener("click", function () { selectTab(t); });
    t.addEventListener("keydown", function (e) {
      var n = e.key === "ArrowRight" ? k + 1 : e.key === "ArrowLeft" ? k - 1 : e.key === "Home" ? 0 : e.key === "End" ? tabs.length - 1 : null;
      if (n === null) return;
      e.preventDefault(); selectTab(tabs[(n + tabs.length) % tabs.length], true);
    });
  });

  /* ------------------------------------------------------------ planner */
  root.hidden = false;
  var form = $(".pform", root), steps = $$(".pstep", root), result = $("[data-presult]", root);
  var back = $("[data-pback]", root), next = $("[data-pnext]", root), err = $("[data-perr]", root);
  var bar = $(".planner__bar", root), step = 1, started = false;
  var el = form.elements;

  function val(name) { var r = $$('input[name="' + name + '"]:checked', form); return r.length ? r[0].value : ""; }
  function vals(name) { return $$('input[name="' + name + '"]:checked', form).map(function (x) { return x.value; }); }
  function country() { return C[val("c")]; }
  function zone() {
    var c = country();
    if (!c) return null;
    if (!c.zones.length) return { tz: browserTz, label: "you" };
    var z = c.zones.filter(function (x) { return x.tz === el.z.value; })[0] || c.zones[0];
    return { tz: z.tz, label: z.label.replace(/ \(.*\)$/, "") };
  }

  function saveUrl(showResult) {
    var q = new URLSearchParams();
    var t = vals("t"); if (t.length) q.set("t", t.join(","));
    if (val("c")) q.set("c", val("c"));
    if (val("c") && el.z.value && !$("[data-pzone]", root).hidden) q.set("z", el.z.value);
    if (el.nd.checked) q.set("nd", "1"); else { if (el.d.value) q.set("d", el.d.value); q.set("n", el.n.value); }
    if (val("x")) q.set("x", val("x"));
    if (val("m")) q.set("m", val("m"));
    q.set("step", showResult ? "plan" : String(step));
    history.replaceState(null, "", location.pathname + "?" + q.toString() + "#planner");
  }

  function countryChanged() {
    var c = country(), box = $("[data-pzone]", root), sel = el.z, tbox = $("[data-ptime]", root);
    if (!c) { box.hidden = true; tbox.innerHTML = ""; return; }
    var keep = sel.value;
    sel.innerHTML = c.zones.map(function (z) { return '<option value="' + esc(z.tz) + '">' + esc(z.label) + "</option>"; }).join("");
    if (keep && c.zones.some(function (z) { return z.tz === keep; })) sel.value = keep;
    box.hidden = c.zones.length < 2;
    var z = zone(), info = tzInfo(z.tz, z.label === "you" ? "you" : z.label);
    tbox.innerHTML = "<p>" + esc(info.diff) + "</p><p>" + esc(info.hours.replace(" you time", " your time")) + "</p>";
  }

  function check(n) {
    if (n === 1 && !vals("t").length) return "Please choose at least one treatment, or \"I'm not sure yet\".";
    if (n === 2 && !val("c")) return "Please choose where you're travelling from.";
    if (n === 3 && !el.nd.checked && !el.d.value) return "Please add your arrival date, or tick \"I don't have dates yet\".";
    if (n === 3 && !el.nd.checked && !(+el.n.value >= 1)) return "Please add how many days you'll be in Mumbai.";
    if (n === 4 && !val("x")) return "Please choose one option.";
    return "";
  }

  function go(n, focus) {
    step = n; err.textContent = "";
    steps.forEach(function (s) { s.hidden = +s.getAttribute("data-step") !== n; });
    form.hidden = false; result.hidden = true;
    $("[data-pstep-n]", root).textContent = n;
    bar.setAttribute("aria-valuenow", n); $("span", bar).style.width = (n / 5 * 100) + "%";
    back.hidden = n === 1;
    next.innerHTML = n === 5 ? "See my plan " + next.innerHTML.slice(next.innerHTML.indexOf("<svg")) : "Next " + next.innerHTML.slice(next.innerHTML.indexOf("<svg"));
    if (focus) { var h = $('.pstep[data-step="' + n + '"] .pstep__h', root); h.focus({ preventScroll: true }); scrollIntoViewIfNeeded(); }
    saveUrl(false);
  }
  function scrollIntoViewIfNeeded() {
    var r = root.getBoundingClientRect();
    if (r.top < 0 || r.top > innerHeight * 0.4) root.scrollIntoView({ block: "start", behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  }
  function start() { if (!started) { started = true; track("planner_start", {}); } }

  form.addEventListener("change", function (e) {
    start();
    if (e.target.name === "c" || e.target.name === "z") countryChanged();
    if (e.target.name === "x") $("[data-xnote]", root).hidden = val("x") !== "yes";
    if (e.target.name === "nd") { el.d.disabled = el.n.disabled = el.nd.checked; $$("[data-pn]", root).forEach(function (b) { b.disabled = el.nd.checked; }); }
    if (e.target.name === "t" && e.target.value === "unsure" && e.target.checked) $$('input[name="t"]', form).forEach(function (x) { if (x.value !== "unsure") x.checked = false; });
    if (e.target.name === "t" && e.target.value !== "unsure" && e.target.checked) { var u = $('input[name="t"][value="unsure"]', form); if (u) u.checked = false; }
    saveUrl(false);
  });
  $$("[data-pn]", root).forEach(function (b) {
    b.addEventListener("click", function () {
      start();
      el.n.value = Math.min(120, Math.max(1, (+el.n.value || 0) + +b.getAttribute("data-pn")));
      saveUrl(false);
    });
  });
  form.addEventListener("submit", function (e) {
    e.preventDefault(); start();
    var msg = check(step);
    if (msg) { err.textContent = msg; return; }
    if (step < 5) { go(step + 1, true); track("planner_step", { step: step }); }
    else show(true);
  });
  back.addEventListener("click", function () { go(Math.max(1, step - 1), true); });

  /* ------------------------------------------------------------ the plan */
  function verdict(sel) {
    var n = el.nd.checked ? 0 : +el.n.value;
    if (sel.some(function (t) { return t.fit === "video"; }))
      return { k: "video", h: "Best confirmed after a video consultation", p: "This treatment depends on what the dentist sees, so the number of visits and trips is agreed after a video consultation and your X-rays." };
    if (sel.some(function (t) { return t.fit === "two"; }))
      return { k: "two", h: "Needs two trips", p: "Part of this treatment needs a healing period of some months between visits. Plan one trip to start treatment and a second to finish it." };
    var need = Math.max.apply(null, sel.map(function (t) { return t.min_days; })) + 2 * (sel.length - 1);
    if (n && n < need)
      return { k: "video", h: "Best confirmed after a video consultation", p: "Your stay may be shorter than this treatment usually needs (about " + need + " days). We can look at what's possible in the time you have." };
    return { k: "one", h: "Fits in one trip", p: "Allow about " + need + (need === 1 ? " day" : " days") + " in Mumbai, with a spare day before you fly. [[TBC: confirm sample durations]]" };
  }
  function uniq(list) { var seen = {}; return list.filter(function (x) { var k = strip(x); if (!k || seen[k]) return false; seen[k] = 1; return true; }); }
  function visitsHtml(trips) {
    return (trips || []).map(function (tr) {
      return '<div class="ptl__trip"><p class="ptl__t">' + esc(tr.title) + '</p><ol>' + tr.visits.map(function (v) {
        return '<li><span class="ptl__day">' + esc(v.day) + "</span><span>" + esc(v.what) + " " + tbc(v.tbc || "") + "</span></li>";
      }).join("") + "</ol></div>";
    }).join("");
  }
  function planText(sel, v) {
    var c = country(), z = zone();
    var lines = ["Hello Arha Dental Care, I'm planning dental treatment during a trip to Mumbai."];
    if (el.name.value.trim()) lines.push("Name: " + el.name.value.trim());
    lines.push("Travelling from: " + c.name + (c.zones.length > 1 ? " (" + z.label + ")" : ""));
    lines.push("Treatments: " + sel.map(function (t) { return t.label; }).join(", "));
    lines.push(el.nd.checked ? "Dates: not fixed yet" : "Arriving: " + el.d.value + ", " + el.n.value + " days in Mumbai");
    lines.push("X-rays: " + { yes: "yes, I can send them", no: "no", unsure: "not sure" }[val("x")]);
    lines.push("Contact me by: " + val("m") + (el.num.value.trim() ? ", " + el.num.value.trim() : ""));
    lines.push("Planner result: " + v.h);
    return lines.join(NL);
  }
  function show(fresh) {
    var sel = vals("t").map(function (id) { return T[id]; }).filter(Boolean);
    if (!sel.length || !country()) { go(1, true); return; }
    var v = verdict(sel), z = zone(), g = D.general;
    // the general X-ray line is dropped when the patient is uploading, or when a chosen treatment asks for its own X-rays
    var own = [].concat.apply([], sel.map(function (t) { return t.before || []; }));
    var xr = /X-rays?/i, ownX = own.some(function (x) { return xr.test(x); });
    var before = uniq(g.before.filter(function (x) { return !(xr.test(x) && (ownX || val("x") === "yes")); }).concat(val("x") === "yes" ? own.filter(function (x) { return !xr.test(x); }) : own));
    var here = uniq(g.here.concat.apply(g.here, sel.map(function (t) { return t.here || []; })));
    var after = uniq(g.after.concat.apply(g.after, sel.map(function (t) { return t.after || []; })));
    if (val("x") === "yes") before.unshift("Upload your X-rays with the secure form below");
    if (val("x") !== "yes") here.unshift("X-rays can be taken at your first visit");
    var list = function (a) { return "<ul>" + a.map(function (x) { return "<li>" + tbc(x) + "</li>"; }).join("") + "</ul>"; };
    var when = el.nd.checked ? "Dates not fixed yet" : (el.d.value ? new Date(el.d.value + "T00:00:00").toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" }) + ", " : "") + el.n.value + " days in Mumbai";
    var waText = planText(sel, v);
    var waUrl = "https://wa.me/" + D.whatsapp + "?text=" + encodeURIComponent(waText);
    var vcUrl = "https://wa.me/" + D.whatsapp + "?text=" + encodeURIComponent(waText + NL + NL + "I'd like to book a video consultation.");
    result.innerHTML =
      '<div class="presult__top presult__top--' + v.k + '"><p class="label">Your sample plan</p><h3>' + esc(v.h) + "</h3><p>" + tbc(v.p) + "</p>" +
      '<p class="presult__meta">' + esc(country().name) + (z.label !== "you" ? " · " + esc(z.label) : "") + " · " + esc(when) + "</p>" +
      '<p class="presult__note">' + esc(D.plans.note) + "</p></div>" +
      '<div class="presult__tl">' + sel.map(function (t) {
        return '<article class="ptl"><h4>' + esc(t.label) + "</h4>" + visitsHtml(t.trips) +
          (t.gap ? '<p class="ptl__gap">' + tbc(t.gap) + "</p>" : "") + visitsHtml(t.trips_after) + "</article>";
      }).join("") + "</div>" +
      '<div class="presult__cols"><div><h4>Before you fly</h4>' + list(before) + "</div><div><h4>While you're here</h4>" + list(here) +
      "</div><div><h4>After you go home</h4>" + list(after) + "</div></div>" +
      '<div class="presult__btns">' +
      '<a class="btn btn--solid" href="' + esc(waUrl) + '" target="_blank" rel="noopener" data-pa="wa">WhatsApp my plan</a>' +
      '<a class="btn" href="' + esc(vcUrl) + '" target="_blank" rel="noopener" data-pa="vc">Book a video consultation</a>' +
      '<button class="btn" type="button" data-pa="print">Print</button>' +
      '<button class="btn" type="button" data-pa="again">Start again</button></div>';
    form.hidden = true; result.hidden = false;
    $("[data-pstep-n]", root).textContent = 5; bar.setAttribute("aria-valuenow", 5); $("span", bar).style.width = "100%";
    $(".planner__count", root).innerHTML = "Your plan is ready";
    saveUrl(true);
    if (fresh) { track("planner_complete", { treatments: vals("t").join(","), country: val("c"), verdict: v.k }); result.focus({ preventScroll: true }); scrollIntoViewIfNeeded(); }
  }
  result.addEventListener("click", function (e) {
    var b = e.target.closest("[data-pa]");
    if (!b) return;
    var a = b.getAttribute("data-pa");
    if (a === "wa") track("plan_whatsapp", { country: val("c") });
    if (a === "vc") track("video_consult_click", { country: val("c") });
    if (a === "print") {
      track("plan_print", {});
      document.body.classList.add("print-plan");
      window.print();
      setTimeout(function () { document.body.classList.remove("print-plan"); }, 500);
    }
    if (a === "again") {
      form.reset(); el.d.disabled = el.n.disabled = false; $$("[data-pn]", root).forEach(function (x) { x.disabled = false; });
      countryChanged(); $("[data-xnote]", root).hidden = true;
      $(".planner__count", root).innerHTML = 'Step <b data-pstep-n>1</b> of 5';
      go(1, true);
    }
  });

  /* ------------------------------------------------------------ restore from the URL */
  var q = new URLSearchParams(location.search), hash0 = location.hash; // go() rewrites the URL; a plain visit must keep its own hash, or the page jumps to #planner
  (q.get("t") || "").split(",").forEach(function (id) { var x = $('input[name="t"][value="' + id.replace(/[^a-z]/g, "") + '"]', form); if (x) x.checked = true; });
  if (q.get("c")) { var cx = $('input[name="c"][value="' + q.get("c").replace(/[^a-z]/g, "") + '"]', form); if (cx) cx.checked = true; }
  countryChanged();
  if (q.get("z")) { el.z.value = q.get("z"); countryChanged(); }
  if (q.get("nd")) { el.nd.checked = true; el.d.disabled = el.n.disabled = true; $$("[data-pn]", root).forEach(function (b) { b.disabled = true; }); }
  if (/^\d{4}-\d{2}-\d{2}$/.test(q.get("d") || "")) el.d.value = q.get("d");
  if (+q.get("n") >= 1) el.n.value = Math.min(120, +q.get("n"));
  if (q.get("x")) { var xx = $('input[name="x"][value="' + q.get("x").replace(/[^a-z]/g, "") + '"]', form); if (xx) xx.checked = true; $("[data-xnote]", root).hidden = val("x") !== "yes"; }
  if (q.get("m")) { var mm = $$('input[name="m"]', form).filter(function (x) { return x.value === q.get("m"); })[0]; if (mm) mm.checked = true; }
  var want = q.get("step"), reach = 1;
  while (reach < 5 && !check(reach)) reach++;          // furthest step the saved answers allow
  if (want === "plan" && reach === 5) { go(5, false); show(false); }
  else { var sn = Math.min(+want || 1, reach); if (sn > 1 || want) go(sn, false); else go(1, false); if (!want) history.replaceState(null, "", location.pathname + hash0); }
  $$("[data-plan-start]").forEach(function (a) { a.addEventListener("click", start); });
})();
