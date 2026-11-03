"""Screenshots of the treatments index, gallery and book page at 375/768/1024/1440 (needs the site on 8080).
Usage: .venv/Scripts/python -I tools/qa/treat_shots.py <out folder>"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright
import pw
from console import BASE
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    b = pw.launch(p)
    for w in (375, 768, 1024, 1440):
        m = w < 768
        ctx = b.new_context(viewport={"width": w, "height": 812 if m else 900}, is_mobile=m, has_touch=m)
        ctx.add_init_script("try { sessionStorage.setItem('arha-intro', '1'); } catch (e) {}")
        pg = ctx.new_page(); errs = []
        pg.on("console", lambda x: errs.append(x.text[:100]) if x.type == "error" else None)
        pg.on("pageerror", lambda e: errs.append(str(e)[:100]))
        for path, ys in (("treatments/", (0.18, 0.32, 0.5)), ("gallery/", (0.25,)), ("book/", (0.0,))):
            pg.goto(BASE + path, wait_until="load"); pg.wait_for_timeout(400)
            h = pg.evaluate("document.documentElement.scrollHeight")
            # walk down so lazy images and reveals run, then stop at each point
            for y in range(0, h, 600):
                pg.evaluate(f"scrollTo(0,{y})"); pg.wait_for_timeout(80)
            for f in ys:
                if path == "book/":
                    pg.locator("#virtual").scroll_into_view_if_needed()
                else:
                    pg.evaluate(f"scrollTo(0,{int(h*f)})")
                pg.wait_for_timeout(1200)
                pg.screenshot(path=str(out / f"{path.strip('/')}-{w}-{int(f*100)}.png"))
            wide = pg.evaluate("document.documentElement.scrollWidth - innerWidth")
            active = pg.evaluate("(document.querySelector('.tindex__item.is-active .tindex__name')||{}).textContent || ''")
            print(w, path, "overflow", wide, "active:", active.strip(), "errors", errs)
        ctx.close()
    b.close()
