"""Screenshot + rule audit of a page at 1440 / 1024 / 768 / 390px.

Usage: .venv/Scripts/python -I tools/screens.py [url] [--out review] [--states]
Needs the site served locally (python -m http.server 8080). Uses the installed Chrome.
Audit flags: rounded corners, shadows, colours outside the palette, horizontal overflow,
console errors, images without alt, fonts that failed to load.
"""
import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
VIEWPORTS = [(1440, 900, False), (1024, 768, False), (768, 1024, True), (390, 844, True)]
PALETTE = {(250, 250, 246), (37, 36, 36), (48, 47, 47), (176, 129, 84), (231, 227, 220), (107, 103, 102)}

AUDIT_JS = r"""
(palette) => {
  const pal = new Set(palette.map(c => c.join(',')));
  const out = { radius: [], shadow: [], colours: {}, noAlt: [], overflowX: document.documentElement.scrollWidth - innerWidth };
  const rgb = (s) => { const m = s.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[ ,/]+/).filter(Boolean).map(Number); return p.length === 4 && p[3] === 0 ? null : p.slice(0, 3).map(Math.round).join(','); };
  const note = (c, el, prop) => { if (c && !pal.has(c)) { const k = c + ' ' + prop; out.colours[k] = out.colours[k] || (el.className || el.tagName).toString().slice(0, 50); } };
  for (const el of document.querySelectorAll('body *')) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none') continue;
    const round = /timeline__dot|steps__dot|ba__grip|riya/.test(el.className);  // the only round marks allowed: timeline points, slider grip
    if (!round && (parseFloat(cs.borderTopLeftRadius) > 0 || parseFloat(cs.borderBottomRightRadius) > 0)) out.radius.push((el.className || el.tagName).toString().slice(0, 50));
    if (['SOURCE', 'SCRIPT', 'STYLE', 'TEMPLATE'].includes(el.tagName)) continue;
    if (cs.boxShadow !== 'none' || cs.textShadow !== 'none') out.shadow.push((el.className || el.tagName).toString().slice(0, 50));
    if (['IMG', 'VIDEO', 'PICTURE', 'SOURCE', 'IFRAME'].includes(el.tagName)) { if (el.tagName === 'IMG' && !el.hasAttribute('alt')) out.noAlt.push(el.src); continue; }
    if ((el.innerText || '').trim() && el.children.length === 0) note(rgb(cs.color), el, 'color');
    note(rgb(cs.backgroundColor), el, 'background');
    for (const side of ['Top', 'Right', 'Bottom', 'Left']) if (parseFloat(cs[`border${side}Width`]) > 0 && cs[`border${side}Style`] !== 'none') note(rgb(cs[`border${side}Color`]), el, 'border');
  }
  out.radius = [...new Set(out.radius)]; out.shadow = [...new Set(out.shadow)];
  out.fonts = [...document.fonts].map(f => `${f.family} ${f.weight} ${f.style}: ${f.status}`);
  return out;
}
"""


def settle(page):
    """Scroll the whole page so lazy images load and reveals run, then return to the top."""
    h = page.evaluate("document.documentElement.scrollHeight")
    for y in range(0, h, 400):
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(120)
    page.wait_for_timeout(1800)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(700)


def stitch(page, path, top=0, height=None):
    """Capture a tall region as viewport-sized shots, stitched together. Playwright's own
    beyond-the-viewport capture briefly resizes the page, which drops touch/no-hover emulation."""
    from PIL import Image
    vw, vh = page.viewport_size["width"], page.viewport_size["height"]
    top = int(round(top))
    height = int(round(height or page.evaluate("document.documentElement.scrollHeight")))
    canvas = Image.new("RGB", (vw, height), (250, 250, 246))
    y = top
    while y < top + height:
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(250)
        actual = int(round(page.evaluate("window.scrollY")))
        chunk = min(vh, top + height - y)
        tmp = Path(path).with_suffix(".part.png")
        page.screenshot(path=tmp, clip={"x": 0, "y": y - actual, "width": vw, "height": chunk})
        canvas.paste(Image.open(tmp), (0, y - top))
        tmp.unlink()
        y += chunk
    canvas.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url", nargs="?", default="http://127.0.0.1:8080/")
    ap.add_argument("--out", default=str(ROOT / "review"))
    ap.add_argument("--states", action="store_true", help="also capture menus, hovers and the mobile bar")
    ap.add_argument("--only", type=int, help="only this viewport width")
    ap.add_argument("--sections", action="store_true", help="also save one screenshot per section")
    ap.add_argument("--filters", action="store_true", help="screenshot every treatment filter")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    report = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        for w, h, touch in VIEWPORTS:
            if a.only and a.only != w:
                continue
            ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1, has_touch=touch, is_mobile=(w < 768))
            page = ctx.new_page()
            errors = []
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(a.url, wait_until="networkidle")
            settle(page)
            # Full-page capture also paints the off-screen mobile bar; hide it just for this shot
            tmp = page.add_style_tag(content=".mobile-bar{visibility:hidden!important}")
            stitch(page, out / f"page-{w}.png")
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(400)
            tmp.evaluate("el => el.remove()")
            page.screenshot(path=out / f"page-{w}-top.png")
            if a.sections:
                sec = out / "sections"
                sec.mkdir(exist_ok=True)
                # Fixed chrome (header, mobile bar, skip link) would be painted into element shots
                hide = page.add_style_tag(content=".site-header,.mobile-bar,.skip-link{visibility:hidden!important}")
                names = page.evaluate("[...document.querySelectorAll('main > section, footer')].map((e, i) => (i + 1) + '-' + ((e.getAttribute('aria-labelledby') || '').replace('-title', '') || e.className.split(' ').filter(c => !['section', 'texture'].includes(c)).pop() || 'footer'))")
                for i, name in enumerate(names):
                    if i == 0 and page.locator("[data-hero]").count():
                        continue  # video hero: captured below as a viewport shot
                    el = page.locator("main > section, footer").nth(i)
                    el.scroll_into_view_if_needed()
                    page.wait_for_timeout(1700)  # let the 1.5s reveal finish
                    box = page.evaluate(f"(() => {{ const r = document.querySelectorAll('main > section, footer')[{i}].getBoundingClientRect(); return [r.top + scrollY, r.height]; }})()")
                    stitch(page, sec / f"{w}-{int(name.split('-')[0]):02d}-{name.split('-', 1)[1]}.png", box[0], box[1])
                hide.evaluate("el => el.remove()")
                page.evaluate("window.scrollTo(0, 0)")
                page.wait_for_timeout(500)
                page.screenshot(path=sec / f"{w}-01-hero.png")  # hero with the real header
            audit = page.evaluate(AUDIT_JS, [list(c) for c in PALETTE])
            audit["console_errors"] = errors
            audit["page_height"] = page.evaluate("document.documentElement.scrollHeight")
            report[w] = audit
            if a.states:
                if w >= 1024:
                    page.hover(".nav__trigger >> nth=0")
                    page.wait_for_timeout(400)
                    page.screenshot(path=out / f"state-{w}-dropdown.png", clip={"x": 0, "y": 0, "width": w, "height": 420})
                    page.mouse.move(w / 2, h - 50)
                if page.locator(".case").count():
                    chrome = page.add_style_tag(content=".site-header,.mobile-bar,.skip-link{visibility:hidden!important}")
                    page.locator(".case").first.scroll_into_view_if_needed()
                    page.wait_for_timeout(1700)
                    if w >= 1024:
                        page.locator(".case").nth(1).hover()
                        page.wait_for_timeout(600)
                        page.locator(".cases").screenshot(path=out / f"state-{w}-case-hover.png")
                    if a.filters and page.locator("[data-filter]").count():
                        report[w]["filters"] = {}
                        for f in page.eval_on_selector_all("[data-filter]", "els => els.map(e => e.dataset.filter)")[1:] + ["all"]:
                            page.locator(f'[data-filter="{f}"]').click()
                            page.wait_for_timeout(1200)
                            box = page.evaluate("(() => { const r = document.querySelector('[data-cases-block]').getBoundingClientRect(); const g = document.querySelector('[data-cases]'); const t = [...g.querySelectorAll('.case-item:not([hidden])')].map(e => e.getBoundingClientRect()); return [r.top + scrollY, r.height, g.getBoundingClientRect().height, t.length, Math.round(Math.max(...t.map(x => x.bottom)) - g.getBoundingClientRect().bottom)]; })()")
                            report[w]["filters"][f] = {"tiles": box[3], "grid_h": round(box[2]), "gap_below_last_tile": box[4]}
                            stitch(page, out / f"filter-{w}-{f}.png", box[0] - 20, box[1] + 40)
                        page.locator(".case").first.scroll_into_view_if_needed()
                        page.wait_for_timeout(400)
                    chrome.evaluate("el => el.remove()")
                    page.locator(".case").first.click()
                    page.wait_for_timeout(700)
                    page.screenshot(path=out / f"state-{w}-case-view.png")
                    report[w]["case_view_focus"] = page.evaluate("document.activeElement.getAttribute('aria-label')")
                    page.keyboard.press("ArrowRight")
                    page.wait_for_timeout(200)
                    report[w]["case_view_next"] = page.evaluate("document.querySelector('[data-cv-title]').textContent")
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(600)
                    report[w]["case_view_closed_focus"] = page.evaluate("document.activeElement.getAttribute('aria-label')")
                    page.evaluate("window.scrollTo(0, 0)")
                    page.wait_for_timeout(400)
                page.click(".menu-toggle")
                page.wait_for_timeout(500)
                page.click(".acc__trigger >> nth=0")
                page.wait_for_timeout(500)
                page.screenshot(path=out / f"state-{w}-menu.png")
                report[w]["menu_focus"] = page.evaluate("document.activeElement.textContent.trim() || document.activeElement.getAttribute('aria-label')")
                page.keyboard.press("Escape")
                page.wait_for_timeout(500)
                report[w]["menu_closed_focus"] = page.evaluate("document.activeElement.getAttribute('aria-label')")
                if w < 768:
                    page.evaluate("window.scrollTo(0, Math.round(document.documentElement.scrollHeight * 0.4))")
                    page.wait_for_timeout(700)
                    page.screenshot(path=out / f"state-{w}-mobile-bar.png")
            ctx.close()
        browser.close()
    (out / "audit.json").write_text(json.dumps(report, indent=1))
    for w, r in report.items():
        print(f"== {w}px  height {r['page_height']}  overflowX {r['overflowX']}  radius {r['radius']}  shadow {r['shadow']}")
        print(f"   off-palette: {r['colours']}")
        print(f"   no-alt: {r['noAlt']}  errors: {r['console_errors']}")
        print(f"   fonts: {r['fonts']}")
        for f, v in r.get("filters", {}).items():
            print(f"   filter {f:<11} tiles {v['tiles']}  grid height {v['grid_h']}px  space below last tile {v['gap_below_last_tile']}px")
        if "case_view_focus" in r:
            print(f"   case view: focus {r['case_view_focus']!r}, ArrowRight -> {r['case_view_next']!r}, after Esc focus {r['case_view_closed_focus']!r}")
        if "menu_focus" in r:
            print(f"   menu focus on open: {r['menu_focus']!r}, after Esc: {r['menu_closed_focus']!r}")


if __name__ == "__main__":
    main()
