"""Treatments index behaviour (needs the site on 8080): at 1440, scrolling a treatment to the middle of the screen
makes it active and shows its photograph; hovering another switches to it; at 390 each photograph settles in as it
arrives; with reduced motion every phone photograph shows at once. Exit 1 on a failure."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright
import pw
from console import BASE
fails = []
with sync_playwright() as p:
    b = pw.launch(p)
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    pg = ctx.new_page(); pg.goto(BASE + "treatments/", wait_until="load"); pg.wait_for_timeout(300)
    for slug in ("smile-design", "root-canal-treatment", "dental-implants"):
        pg.evaluate("""(s) => { const e = document.querySelector('.tindex__item[data-shot="' + s + '"]'); const r = e.getBoundingClientRect();
                        scrollBy({top: r.top + r.height / 2 - innerHeight / 2, behavior: 'instant'}); }""", slug)
        pg.wait_for_timeout(1500)
        got = pg.evaluate("[document.querySelector('.tindex__item.is-active').dataset.shot, document.querySelector('.tindex__shot.is-active').dataset.shot, getComputedStyle(document.querySelector('.tindex__shot.is-active')).clipPath, document.querySelector('.tindex').classList.contains('is-live')]")
        ok = got[0] == slug and got[1] == slug and got[2] in ("inset(0px)", "inset(0px 0px 0px 0px)", "none") and got[3]
        print("scroll", slug, got, "OK" if ok else "FAIL"); ok or fails.append(f"scroll {slug}: {got}")
    other = pg.locator('.tindex__item[data-shot="orthodontics"] .tindex__name')
    other.scroll_into_view_if_needed(); pg.wait_for_timeout(400)
    pg.locator('.tindex__item[data-shot="invisalign"] .tindex__name').hover(); pg.wait_for_timeout(800)
    got = pg.evaluate("document.querySelector('.tindex__shot.is-active').dataset.shot")
    print("hover invisalign ->", got); got == "invisalign" or fails.append(f"hover: {got}")
    ctx.close()
    for rm in (None, "reduce"):
        ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, reduced_motion=rm or "no-preference")
        pg = ctx.new_page(); pg.goto(BASE + "treatments/", wait_until="load"); pg.wait_for_timeout(300)
        m = pg.locator(".tindex__media").nth(4); m.scroll_into_view_if_needed(); pg.wait_for_timeout(1000)
        op = pg.evaluate("getComputedStyle(document.querySelectorAll('.tindex__media')[4].querySelector('picture')).opacity")
        far = pg.evaluate("getComputedStyle(document.querySelectorAll('.tindex__media')[10].querySelector('picture')).opacity")
        print("390", rm or "motion", "in view opacity", op, "far one", far)
        if op != "1": fails.append(f"390 {rm}: in-view photo opacity {op}")
        if rm == "reduce" and far != "1": fails.append("reduced motion: photo hidden before scroll")
        ctx.close()
    b.close()
print(f"{len(fails)} failures", fails)
sys.exit(1 if fails else 0)
