"""Every interactive, really driven with Playwright at 1440 (mouse, keyboard) and 390 (touch).
Usage: ix_suite.py SCRATCH [group ...]   groups: header home problems treatments other (default: all)
Writes SCRATCH/ix_results.json: [{page, interactive, vp, action, ok, note}]"""
import json
import sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])
from pw import launch, BASE as B  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

OUT = Path(sys.argv[1]) / "ix_results.json"
results = json.loads(OUT.read_text()) if OUT.exists() and "--append" in sys.argv else []
groups = [a for a in sys.argv[2:] if not a.startswith("--")] or ["header", "home", "problems", "treatments", "other"]


def rec(page, ix, vp, action, ok, note=""):
    results.append({"page": page, "interactive": ix, "vp": vp, "action": action, "ok": bool(ok), "note": str(note)})
    print(f"{'PASS' if ok else 'FAIL'} {vp:>4} {page:<34} {ix:<30} {action:<26} {note}", flush=True)


def go(pg, path):
    pg.goto(B + path, wait_until="domcontentloaded")
    pg.wait_for_timeout(500)


def into_view(pg, sel):
    pg.evaluate("(s) => { const el = document.querySelector(s); el.scrollIntoView({block: 'center', behavior: 'instant'}); }", sel)
    pg.wait_for_timeout(450)


def ev(pg, js, arg=None):
    return pg.evaluate(js, arg)


def active_index(pg, sel):
    return ev(pg, "(s) => [...document.querySelectorAll(s)].findIndex(e => e.classList.contains('is-active'))", sel)


def selected_tab(pg, box):
    return ev(pg, "(b) => { const t = document.querySelector(b + ' [role=tab][aria-selected=true]'); return t && t.textContent.trim() }", box)


def visible_text(pg, sel):
    return ev(pg, "(s) => { const el = [...document.querySelectorAll(s)].find(e => !e.hidden && e.offsetParent !== null); return el ? el.textContent.trim().slice(0, 60) : null }", sel)


# ------------------------------------------------------------------ components
def t_xfade(pg, path, vp, name, box, labels):
    into_view(pg, box)
    tabs = pg.locator(f"{box} [role=tab]")
    for k in range(1, len(labels)):
        if vp == 390:
            tabs.nth(k).tap()
        else:
            tabs.nth(k).click()
        pg.wait_for_timeout(750)
        on = selected_tab(pg, box)
        img = active_index(pg, f"{box} .xfade__img")
        op = ev(pg, "(b) => getComputedStyle(document.querySelectorAll(b + ' .xfade__img')[%d]).opacity" % k, box)
        rec(path, name, vp, f"{'tap' if vp == 390 else 'click'} {labels[k]}", on == labels[k] and img == k and float(op) > .95, f"tab {on}, photo {img}, opacity {op}")
    if vp == 1440:
        tabs.nth(0).focus()
        pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(300)
        rec(path, name, vp, "keyboard ArrowRight", selected_tab(pg, box) == labels[1] and active_index(pg, f"{box} .xfade__img") == 1, selected_tab(pg, box))


def t_loupe(pg, path, vp, cdp=None):
    box = "[data-loupe]"
    into_view(pg, box)
    r = ev(pg, "() => { const r = document.querySelector('[data-loupe]').getBoundingClientRect(); return [r.x, r.y, r.width, r.height] }")
    x, y, w, h = r
    if vp == 1440:
        pg.mouse.move(x + w * .3, y + h * .5); pg.wait_for_timeout(120)
        pg.mouse.move(x + w * .6, y + h * .4, steps=5); pg.wait_for_timeout(250)
        st = ev(pg, "() => { const f = document.querySelector('[data-loupe]'); const l = f.querySelector('.loupe__lens'); return [f.classList.contains('is-on'), f.style.getPropertyValue('--lx'), l.style.backgroundImage.slice(0, 40), getComputedStyle(l).opacity] }")
        lx = float(st[1].replace("px", "") or 0)
        rec(path, "Magnifier loupe", vp, "hover and move", st[0] and abs(lx - w * .6) < 3 and "url" in st[2], f"on {st[0]}, lens x {lx:.0f}/{w * .6:.0f}, {st[2][:30]}")
        pg.mouse.move(x - 40, y - 40); pg.wait_for_timeout(300)
        rec(path, "Magnifier loupe", vp, "mouse leaves: lens off", not ev(pg, "() => document.querySelector('[data-loupe]').classList.contains('is-on')"))
        pg.focus(box); pg.keyboard.press("ArrowRight"); pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(200)
        lx2 = float(ev(pg, "() => document.querySelector('[data-loupe]').style.getPropertyValue('--lx')").replace("px", "") or 0)
        rec(path, "Magnifier loupe", vp, "keyboard arrows", lx2 > lx + 1 or lx2 > 0, f"lens x {lx2:.0f}")
    else:
        def touch(kind, pts):
            cdp.send("Input.dispatchTouchEvent", {"type": kind, "touchPoints": [{"x": a, "y": b} for a, b in pts]})
        touch("touchStart", [(x + w * .2, y + h * .5)])
        for k in range(1, 11):
            touch("touchMove", [(x + w * (.2 + .05 * k), y + h * (.5 - .01 * k))]); pg.wait_for_timeout(16)
        st = ev(pg, "() => { const f = document.querySelector('[data-loupe]'); return [f.classList.contains('is-on'), f.style.getPropertyValue('--lx')] }")
        touch("touchEnd", []); pg.wait_for_timeout(200)
        lx = float(st[1].replace("px", "") or 0)
        off = not ev(pg, "() => document.querySelector('[data-loupe]').classList.contains('is-on')")
        rec(path, "Magnifier loupe", vp, "touch drag", st[0] and abs(lx - w * .7) < 6 and off, f"on while dragging {st[0]}, lens x {lx:.0f}/{w * .7:.0f}, off after {off}")


def t_xpanels(pg, path, vp, box, name="Expanding panels"):
    into_view(pg, box)
    panels = pg.locator(f"{box} [data-xpanel]")
    n = panels.count()
    for k in [1, n - 1]:
        if vp == 1440:
            panels.nth(k).hover()
        else:
            panels.nth(k).tap()
        pg.wait_for_timeout(900)
        a = active_index(pg, f"{box} [data-xpanel]")
        link_vis = ev(pg, "(a) => { const p = document.querySelectorAll(a[0] + ' [data-xpanel]')[a[1]]; const m = p.querySelector('.xpanel__more'); return m ? getComputedStyle(m).opacity : '1' }", [box, k])
        rec(path, name, vp, f"{'hover' if vp == 1440 else 'tap'} panel {k + 1}", a == k and float(link_vis) > .9, f"active {a + 1}, text opacity {link_vis}")
    if vp == 1440:
        panels.nth(0).focus(); pg.wait_for_timeout(500)
        rec(path, name, vp, "keyboard focus", active_index(pg, f"{box} [data-xpanel]") == 0)


def t_range(pg, path, vp, box, name, prop, expect_mix=True):
    into_view(pg, box)
    inp = pg.locator(f"{box} input[type=range]").first
    bb = inp.bounding_box()
    if vp == 1440:
        pg.mouse.move(bb["x"] + 4, bb["y"] + bb["height"] / 2); pg.mouse.down()
        pg.mouse.move(bb["x"] + bb["width"] * .7, bb["y"] + bb["height"] / 2, steps=8); pg.mouse.up(); pg.wait_for_timeout(200)
        v = ev(pg, "(b) => document.querySelector(b + ' input[type=range]').value", box)
        rec(path, name, vp, "drag the control", int(v) > 50, f"value {v}")
        inp.focus(); pg.keyboard.press("Home"); pg.wait_for_timeout(100)
        v0 = ev(pg, "(b) => document.querySelector(b + ' input[type=range]').value", box)
        for _ in range(5):
            pg.keyboard.press("ArrowRight")
        pg.wait_for_timeout(150)
        v1 = ev(pg, "(b) => document.querySelector(b + ' input[type=range]').value", box)
        rec(path, name, vp, "keyboard Home, ArrowRight x5", int(v1) > int(v0), f"{v0} -> {v1}")
    else:
        pg.touchscreen.tap(bb["x"] + bb["width"] * .85, bb["y"] + bb["height"] / 2); pg.wait_for_timeout(300)
        v = ev(pg, "(b) => document.querySelector(b + ' input[type=range]').value", box)
        rec(path, name, vp, "tap along the control", int(v) > 50, f"value {v}")
    return ev(pg, "(a) => getComputedStyle(document.querySelector(a[0])).getPropertyValue(a[1])", [box, prop])


def t_blend(pg, path, vp, box, name):
    t_range(pg, path, vp, box, name, "--mix")
    if vp == 1440:
        pg.locator(f"{box} input[type=range]").first.focus(); pg.keyboard.press("End"); pg.wait_for_timeout(200)
    op = ev(pg, "(b) => getComputedStyle(document.querySelector(b + ' .blend__b')).opacity", box)
    rec(path, name, vp, "second photograph shows", float(op) > .5, f"opacity {op}")


def t_picker(pg, path, vp):
    box = "[data-checklist]"
    into_view(pg, box)
    lab = pg.locator(f"{box} label.chip-check")
    tap = (lambda el: el.tap()) if vp == 390 else (lambda el: el.click())
    tap(lab.nth(0)); pg.wait_for_timeout(300)
    r1 = visible_text(pg, ".picker__result")
    rec(path, "Symptom picker", vp, "tick cold/hot", r1 and r1.startswith("Book a check-up"), r1)
    tap(lab.nth(3)); pg.wait_for_timeout(300)
    r2 = visible_text(pg, ".picker__result")
    rec(path, "Symptom picker", vp, "add swelling", r2 and r2.startswith("Please call us today"), r2)
    tap(lab.nth(3)); tap(lab.nth(0)); pg.wait_for_timeout(300)
    r3 = visible_text(pg, ".picker__result")
    rec(path, "Symptom picker", vp, "untick all", r3 and r3.startswith("Your likely next step"), r3)
    if vp == 1440:
        pg.locator(f"{box} input").nth(2).focus(); pg.keyboard.press("Space"); pg.wait_for_timeout(300)
        r4 = visible_text(pg, ".picker__result")
        rec(path, "Symptom picker", vp, "keyboard Space", r4 and r4.startswith("Book an urgent"), r4)
        pg.keyboard.press("Space")
    flag = ev(pg, "() => document.querySelector('.ix-flag').textContent")
    rec(path, "Symptom picker", vp, "labelled Not a diagnosis", "Not a diagnosis" in flag)


def t_quiz(pg, path, vp):
    box = "[data-quiz]"
    into_view(pg, box)
    tap = (lambda el: el.tap()) if vp == 390 else (lambda el: el.click())
    qs = pg.locator(f"{box} .quiz__q")
    tap(qs.nth(0).locator("label").nth(0)); pg.wait_for_timeout(200)
    r0 = visible_text(pg, ".quiz__result")
    tap(qs.nth(1).locator("label").nth(1)); tap(qs.nth(2).locator("label").nth(1)); pg.wait_for_timeout(300)
    r1 = visible_text(pg, ".quiz__result")
    rec(path, "Gum self-check", vp, "answer yes, no, no", r0.startswith("Answer the three") and r1 and r1.startswith("Worth a check"), r1)
    tap(qs.nth(1).locator("label").nth(0)); pg.wait_for_timeout(300)
    r2 = visible_text(pg, ".quiz__result")
    href = ev(pg, "() => { const r = [...document.querySelectorAll('.quiz__result')].find(e => !e.hidden); const a = r && r.querySelector('a'); return a ? a.getAttribute('href') : '' }")
    rec(path, "Gum self-check", vp, "two yes: gum care link", r2 and r2.startswith("Book a gum check") and "gum-care" in href, f"{r2[:30] if r2 else r2} -> {href}")


def t_agedial(pg, path, vp):
    box = "[data-agedial]"
    into_view(pg, box)
    inp = pg.locator(f"{box} input[type=range]")
    if vp == 1440:
        inp.focus(); pg.keyboard.press("Home")
        for _ in range(7):
            pg.keyboard.press("ArrowRight")
        pg.wait_for_timeout(500)
        txt = visible_text(pg, ".agedial__text")
        out = ev(pg, "() => document.querySelector('[data-age-out]').textContent")
        rec(path, "Age dial", vp, "keyboard to age 7", txt and txt.startswith("6 to 9") and active_index(pg, ".agedial__img") == 2 and out == "7", f"{out}: {txt}")
        bb = inp.bounding_box()
        pg.mouse.click(bb["x"] + bb["width"] * .95, bb["y"] + bb["height"] / 2); pg.wait_for_timeout(500)
        txt = visible_text(pg, ".agedial__text")
        rec(path, "Age dial", vp, "click near 18", txt and txt.startswith("Teenagers") and active_index(pg, ".agedial__img") == 4, txt)
    else:
        bb = inp.bounding_box()
        pg.touchscreen.tap(bb["x"] + bb["width"] * .6, bb["y"] + bb["height"] / 2); pg.wait_for_timeout(500)
        txt = visible_text(pg, ".agedial__text")
        rec(path, "Age dial", vp, "tap at about 11", txt and txt.startswith("10 to 12") and active_index(pg, ".agedial__img") == 3, txt)
    href = ev(pg, "() => document.querySelector('[data-agedial] .link').getAttribute('href')")
    rec(path, "Age dial", vp, "links to Kids' dentistry", "kids-dentistry" in href, href)


def t_ba(pg, path, vp, cdp=None):
    box = "[data-ba]"
    into_view(pg, box)
    b = ev(pg, "() => { const r = document.querySelector('[data-ba]').getBoundingClientRect(); return [r.x, r.y, r.width, r.height] }")
    x, y, w, h = b
    pos = lambda: float(ev(pg, "() => parseFloat(document.querySelector('[data-ba]').style.getPropertyValue('--pos'))"))  # noqa: E731
    if vp == 1440:
        pg.mouse.move(x + w * .2, y + h * .3); pg.mouse.down(); pg.wait_for_timeout(40)
        pg.mouse.move(x + w * .8, y + h * .3, steps=12); pg.mouse.up(); pg.wait_for_timeout(80)
        rec(path, "Before/after slider", vp, "drag on the photo", abs(pos() - 80) < 2, f"{pos():.0f}%")
        pg.mouse.click(x + w * .35, y + h * .7); pg.wait_for_timeout(80)
        rec(path, "Before/after slider", vp, "click to jump", abs(pos() - 35) < 2, f"{pos():.0f}%")
        pg.focus("[data-ba] .ba__handle"); pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(80)
        rec(path, "Before/after slider", vp, "keyboard ArrowRight", abs(pos() - 37) < 1, f"{pos():.0f}%")
    else:
        def touch(kind, pts):
            cdp.send("Input.dispatchTouchEvent", {"type": kind, "touchPoints": [{"x": a, "y": c} for a, c in pts]})
        touch("touchStart", [(x + w * .25, y + h * .5)])
        for k in range(1, 16):
            touch("touchMove", [(x + w * (.25 + .5 * k / 15), y + h * .5)]); pg.wait_for_timeout(16)
        touch("touchEnd", []); pg.wait_for_timeout(120)
        rec(path, "Before/after slider", vp, "touch drag", abs(pos() - 75) < 4, f"{pos():.0f}%")
        touch("touchStart", [(x + w * .4, y + h * .5)]); pg.wait_for_timeout(50); touch("touchEnd", []); pg.wait_for_timeout(120)
        rec(path, "Before/after slider", vp, "tap to jump", abs(pos() - 40) < 3, f"{pos():.0f}%")
        s0 = ev(pg, "scrollY")
        touch("touchStart", [(x + w * .4, y + h * .6)])
        for k in range(1, 12):
            touch("touchMove", [(x + w * .4, y + h * .6 - k * 15)]); pg.wait_for_timeout(16)
        touch("touchEnd", []); pg.wait_for_timeout(500)
        rec(path, "Before/after slider", vp, "vertical swipe scrolls", ev(pg, "scrollY") - s0 > 50 and abs(pos() - 40) < 3, f"scrolled {ev(pg, 'scrollY') - s0:.0f}px")


# ------------------------------------------------------------------ groups
PROBLEM_TESTS = {
    "missing-tooth": lambda pg, p, vp, cdp: t_xfade(pg, p, vp, "Implant/Bridge/Denture toggle", "[data-xfade]", ["Implant", "Bridge", "Denture"]),
    "chipped-tooth": lambda pg, p, vp, cdp: t_loupe(pg, p, vp, cdp),
    "gaps": lambda pg, p, vp, cdp: t_xpanels(pg, p, vp, ".xpanels--ix", "Bonding/Veneers/Aligners panels"),
    "crooked-teeth": lambda pg, p, vp, cdp: t_blend(pg, p, vp, "[data-blend]", "Crowded-to-straight blend"),
    "stained-teeth": lambda pg, p, vp, cdp: t_blend(pg, p, vp, "[data-blend]", "Whitening simulation"),
    "toothache": lambda pg, p, vp, cdp: t_picker(pg, p, vp),
    "bleeding-gums": lambda pg, p, vp, cdp: t_quiz(pg, p, vp),
    "metal-fillings": lambda pg, p, vp, cdp: t_xfade(pg, p, vp, "Metal/Tooth-coloured switch", "[data-xfade]", ["Metal", "Tooth-coloured"]),
    "loose-dentures": lambda pg, p, vp, cdp: t_xfade(pg, p, vp, "Conventional/Implant toggle", "[data-xfade]", ["Conventional", "Implant-retained"]),
    "child-teeth": lambda pg, p, vp, cdp: t_agedial(pg, p, vp),
}


def g_problems(pg, vp, cdp):
    for slug, test in PROBLEM_TESTS.items():
        path = f"problems/{slug}/"
        go(pg, path)
        try:
            test(pg, path, vp, cdp)
        except Exception as e:  # a crash is a failure, not the end of the run
            rec(path, slug, vp, "runs", False, repr(e)[:120])
        acc(pg, path, vp)


def acc(pg, path, vp):
    """FAQ accordion on the page: open the first question."""
    if not ev(pg, "() => !!document.querySelector('.faq__trigger')"):
        return
    into_view(pg, ".faq")
    pg.wait_for_timeout(1200)  # let the section's reveal settle before tapping
    for _ in range(10):  # and wait until the question has stopped moving
        a = pg.locator(".faq__trigger").first.bounding_box(); pg.wait_for_timeout(150); b = pg.locator(".faq__trigger").first.bounding_box()
        if a == b:
            break
    btn = pg.locator(".faq__trigger").first
    hit = ev(pg, "() => { const b = document.querySelector('.faq__trigger'); const r = b.getBoundingClientRect(); const e = document.elementFromPoint(r.x + r.width / 2, r.y + r.height / 2); return b.contains(e) ? '' : (e.className || e.tagName) + '' }")
    (btn.tap if vp == 390 else btn.click)(); pg.wait_for_timeout(500)
    if hit:
        rec(path, "FAQ accordion", vp, "nothing covers the question", False, f"covered by {hit[:60]}")
    rec(path, "FAQ accordion", vp, f"{'tap' if vp == 390 else 'click'} first question", btn.get_attribute("aria-expanded") == "true")


def g_header(pg, vp, cdp):
    path = "problems/gaps/"
    go(pg, path)
    if vp == 1440:
        for trig, dd in [("What we fix", "#dd-fix"), ("Who we are", "#dd-who"), ("Our work", "#dd-work")]:
            pg.locator(".nav__trigger", has_text=trig).hover(); pg.wait_for_timeout(450)
            vis = ev(pg, "(d) => { const el = document.querySelector(d); const s = getComputedStyle(el); return s.visibility !== 'hidden' && s.opacity > .9 && !el.inert }", dd)
            rec(path, f"Header: {trig}", vp, "hover opens dropdown", vis)
        n = ev(pg, "() => document.querySelectorAll('#dd-fix a').length")
        rec(path, "Header: What we fix", vp, "lists problems + treatments", n >= 24, f"{n} links")
        pg.mouse.move(700, 600); pg.wait_for_timeout(400)
        pg.locator(".brand").focus(); pg.keyboard.press("Tab"); pg.wait_for_timeout(400)
        rec(path, "Header: What we fix", vp, "keyboard Tab opens", ev(pg, "() => document.querySelector('.nav__trigger[aria-controls=dd-fix]').getAttribute('aria-expanded')") == "true")
        pg.keyboard.press("Enter"); pg.wait_for_timeout(200)
        rec(path, "Header: What we fix", vp, "Enter moves into the panel", ev(pg, "() => document.activeElement.closest('#dd-fix') !== null"), ev(pg, "() => document.activeElement.textContent.trim().slice(0, 30)"))
        pg.keyboard.press("Escape"); pg.wait_for_timeout(300)
        rec(path, "Header: What we fix", vp, "Escape closes, focus back", ev(pg, "() => document.querySelector('.nav__trigger[aria-controls=dd-fix]').getAttribute('aria-expanded')") == "false" and ev(pg, "() => document.activeElement.getAttribute('aria-controls')") == "dd-fix")
        book = ev(pg, "() => { const a = document.querySelector('.nav__link--book'); return getComputedStyle(a).backgroundSize }")
        rec(path, "Header: Book a consultation", vp, "underlined", "1px" in book, book)
        pg.locator(".header-call").click(); pg.wait_for_timeout(400)
        rec(path, "Header: Call now", vp, "click opens call panel", ev(pg, "() => !document.getElementById('call-pop').hidden"))
        pg.keyboard.press("Escape"); pg.wait_for_timeout(300)
    else:
        vis = ev(pg, "() => { const c = document.querySelector('.header-call'); const m = document.querySelector('.menu-toggle'); return [getComputedStyle(c).display, getComputedStyle(m).display, c.textContent.trim()] }")
        rec(path, "Header (phone)", vp, "CALL and menu shown", vis[0] != "none" and vis[1] != "none", vis)
        href = pg.locator(".header-call").get_attribute("href")
        rec(path, "Header (phone)", vp, "CALL dials (tel:)", href.startswith("tel:"), href)
        bar = ev(pg, "() => { const b = document.querySelector('.call-bar'); return b ? getComputedStyle(b).display : 'none' }")
        rec(path, "Call now bar (phone)", vp, "bottom bar stays", bar != "none", bar)
    tg = pg.locator(".menu-toggle")
    (tg.tap if vp == 390 else tg.click)(); pg.wait_for_timeout(600)
    rec(path, "Full-screen menu", vp, f"{'tap' if vp == 390 else 'click'} menu opens", ev(pg, "() => document.getElementById('side-menu').classList.contains('is-open')"))
    grp = pg.locator(".fmenu__toggle").first
    (grp.tap if vp == 390 else grp.click)(); pg.wait_for_timeout(500)
    n = ev(pg, "() => { const s = document.getElementById('fm-fix'); return s.hidden ? 0 : s.querySelectorAll('a').length }")
    rec(path, "Full-screen menu", vp, "+ What we fix opens", n >= 22, f"{n} links")
    tabs = ev(pg, "() => [...document.querySelectorAll('#side-menu a')].map(a => a.getAttribute('href'))")
    need = ["founder/", "treatments/", "dental-tourism/", "technology/", "the-practice/", "doctors/", "gallery/", "our-work/", "our-work/#testimonials", "kids-dentistry/", "book/", "emergency/"]
    missing = [n for n in need if not any(h and h.endswith(n) for h in tabs)]
    rec(path, "Full-screen menu", vp, "every requested tab listed", not missing, f"missing {missing}" if missing else f"{len(tabs)} links")
    pg.keyboard.press("Escape"); pg.wait_for_timeout(400)
    rec(path, "Full-screen menu", vp, "Escape closes", not ev(pg, "() => document.getElementById('side-menu').classList.contains('is-open')"))
    # utility line hides on scroll
    go(pg, path)
    if vp == 1440:
        pg.mouse.wheel(0, 600); pg.wait_for_timeout(700)
        h = ev(pg, "() => { const u = document.querySelector('[data-utility]'); const r = u.getBoundingClientRect(); return [r.height, r.bottom, getComputedStyle(u).opacity] }")
        rec(path, "Utility line", vp, "hides on scroll", h[1] <= 1 or float(h[2]) < .1 or h[0] < 2, h)


def g_home(pg, vp, cdp):
    path = ""
    go(pg, path)
    box = "[data-brings]"
    into_view(pg, box)
    items = pg.locator(".brings__item")
    if vp == 1440:
        items.nth(3).hover(); pg.wait_for_timeout(900)
        a = active_index(pg, ".brings__shot")
        op = ev(pg, "() => getComputedStyle(document.querySelectorAll('.brings__shot')[3]).opacity")
        cap = ev(pg, "() => document.querySelectorAll('.brings__shot')[3].querySelector('.brings__caption a').textContent")
        rec("home", "What brings you in?", vp, "hover crossfades photo", a == 3 and float(op) > .95 and "See how we fix it" in cap, f"shot {a}, opacity {op}")
        items.nth(6).focus(); pg.wait_for_timeout(300)
        rec("home", "What brings you in?", vp, "keyboard focus", active_index(pg, ".brings__shot") == 6)
        items.nth(6).click(); pg.wait_for_load_state("domcontentloaded"); pg.wait_for_timeout(300)
        rec("home", "What brings you in?", vp, "click opens problem page", pg.url.endswith("problems/bleeding-gums/"), pg.url[-30:])
    else:
        items.nth(4).tap(); pg.wait_for_timeout(900)
        stay = pg.url.rstrip("/").endswith("8080")
        rec("home", "What brings you in?", vp, "tap shows photo (stays)", active_index(pg, ".brings__shot") == 4 and stay, f"shot {active_index(pg, '.brings__shot')}")
        pg.locator(".brings__shot.is-active .brings__caption a").tap(); pg.wait_for_load_state("domcontentloaded"); pg.wait_for_timeout(300)
        rec("home", "What brings you in?", vp, "See how we fix it opens page", pg.url.endswith("problems/stained-teeth/"), pg.url[-30:])
        go(pg, path)
    go(pg, path)
    t_ba(pg, "home", vp, cdp)
    # reviews carousel, hotspots, trio panels, journey
    into_view(pg, ".drag--quotes")
    before = ev(pg, "() => document.querySelector('.drag--quotes .drag__track').scrollLeft")
    nb = pg.locator(".drag--quotes .drag__btn--next")
    (nb.tap if vp == 390 else nb.click)(); pg.wait_for_timeout(900)
    after = ev(pg, "() => document.querySelector('.drag--quotes .drag__track').scrollLeft")
    rec("home", "Reviews carousel", vp, "next arrow", after > before, f"{before:.0f} -> {after:.0f}")
    n = ev(pg, "() => document.querySelectorAll('.quotes__slide').length")
    rec("home", "Reviews carousel", vp, "seven real reviews", n == 7, n)
    t_xpanels(pg, "home", vp, ".trio [data-xpanels]", "Feature trio panels")
    into_view(pg, "[data-spots]")
    sp = pg.locator("[data-spots] .spot")
    (sp.nth(2).tap if vp == 390 else sp.nth(2).click)(); pg.wait_for_timeout(400)
    rec("home", "Technology hotspots", vp, f"{'tap' if vp == 390 else 'click'} spot 3", ev(pg, "() => !document.getElementById('hs-2').hidden"))


def g_other(pg, vp, cdp):
    for path in ["our-work/sample-veneers-1/", "our-work/sample-aligners-1/"]:
        go(pg, path)
        t_ba(pg, path, vp, cdp)
    go(pg, "our-work/")
    into_view(pg, ".work-filter")
    btn = pg.locator(".work-filter button", has_text="Implants")
    (btn.tap if vp == 390 else btn.click)(); pg.wait_for_timeout(500)
    shown = ev(pg, "() => [...document.querySelectorAll('[data-work-grid] > li')].filter(li => !li.hidden && li.offsetParent).map(li => li.dataset.cat)")
    rec("our-work/", "Treatment filter", vp, "Implants", shown and all(c == "implants" for c in shown), shown)


def run():
    with sync_playwright() as p:
        br = launch(p)
        for vp in (1440, 390):
            if vp == 1440:
                ctx = br.new_context(viewport={"width": 1440, "height": 900})
            else:
                ctx = br.new_context(viewport={"width": 390, "height": 844}, has_touch=True, is_mobile=True, device_scale_factor=2)
            pg = ctx.new_page()
            cdp = ctx.new_cdp_session(pg) if vp == 390 else None
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            for g in groups:
                fn = globals().get(f"g_{g}")
                if fn:
                    fn(pg, vp, cdp)
            if "treatments" in groups:
                import ix_treatments
                ix_treatments.run(pg, vp, cdp, rec, go, into_view, ev, active_index, selected_tab, visible_text, t_xfade, t_range, t_xpanels, acc)
            rec("(all pages visited)", "JavaScript errors", vp, "none thrown", not errors, errors[:3])
            ctx.close()
        br.close()
    OUT.write_text(json.dumps(results, indent=1))
    print(sum(r["ok"] for r in results), "/", len(results), "pass")


if __name__ == "__main__":
    run()
