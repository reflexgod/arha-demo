"""Screenshots for the clinic-facts brief (no Before & After, the Arha story, Dr. Nikhil's clinic).

Usage: .venv/Scripts/python tools/qa/brief_shots.py OUTDIR   (needs the site on 8080)
Writes: the header and its menu (1440, 390), the problems grid with a square hovered, Our work, the
founder page's story at 375/768/1440, the doctors hero and the footer.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright  # noqa: E402
import pw  # noqa: E402

BASE = "http://127.0.0.1:8080/"
HIDE = ".riya-launcher,.riya-bubble{visibility:hidden!important} .reveal{opacity:1!important;transform:none!important} picture.fill img{opacity:1!important}"


def page(ctx, path):
    pg = ctx.new_page()
    pg.add_init_script("try { sessionStorage.setItem('riya-bubble', '1'); sessionStorage.setItem('arha-intro', '1'); } catch (e) {}")
    pg.goto(BASE + path, wait_until="networkidle")
    h = pg.evaluate("document.body.scrollHeight")
    for _y in range(0, h, 700):
        pg.mouse.wheel(0, 700)
        pg.wait_for_timeout(40)
    pg.evaluate("window.scrollTo(0, 0)")
    pg.add_style_tag(content=HIDE)
    pg.wait_for_timeout(800)
    return pg


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = pw.launch(p)
        for w in (1440, 390):
            ctx = b.new_context(viewport={"width": w, "height": 900 if w > 600 else 844}, is_mobile=w < 600, has_touch=w < 600)
            pg = page(ctx, "")
            pg.screenshot(path=str(out / f"01-header-{w}.png"))
            # The menu: Who we are opened, Our work a plain link (no Before & after)
            pg.locator(".menu-toggle, [aria-controls='side-menu']").first.click()
            pg.wait_for_timeout(700)
            pg.locator("[aria-controls='fm-who']").first.click()
            pg.wait_for_timeout(500)
            pg.screenshot(path=str(out / f"02-menu-{w}.png"))
            pg.keyboard.press("Escape")
            pg.wait_for_timeout(500)
            grid = pg.locator(".ah-grid")
            grid.scroll_into_view_if_needed()
            if w > 600:
                pg.locator(".ah-tile a").first.hover()
                pg.wait_for_timeout(700)
            grid.screenshot(path=str(out / f"03-problems-grid-{w}.png"))
            pg.locator(".site-footer").screenshot(path=str(out / f"07-footer-{w}.png"))
            pg.close()
            pg = page(ctx, "our-work/")
            pg.screenshot(path=str(out / f"04-our-work-{w}.png"), full_page=True)
            pg.close()
            pg = page(ctx, "doctors/")
            pg.screenshot(path=str(out / f"06-doctors-{w}.png"))
            pg.close()
            ctx.close()
        for w in (375, 768, 1440):
            ctx = b.new_context(viewport={"width": w, "height": 900 if w > 600 else 812}, is_mobile=w < 600, has_touch=w < 600)
            pg = page(ctx, "founder/")
            pg.screenshot(path=str(out / f"05-founder-top-{w}.png"))
            el = pg.locator(".timeline-v4")
            el.scroll_into_view_if_needed()
            el.screenshot(path=str(out / f"05-founder-story-{w}.png"))
            ctx.close()
        b.close()
    print("\n".join(sorted(p.name for p in out.glob("*.png"))))


if __name__ == "__main__":
    main()
