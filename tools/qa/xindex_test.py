"""The index lists (/treatments/, /problems/), needs the site on 8080. At 1440 with a mouse: hovering a row shows
its own photograph beside the pointer, it follows the pointer, and leaving hides it. At 390: a thumbnail beside
every name, no overflow. Screenshots to <out>. Exit 1 on a failure."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright
import pw
from console import BASE
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
fails = []
with sync_playwright() as p:
    b = pw.launch(p)
    for path in ("treatments/", "problems/"):
        ctx = b.new_context(viewport={"width": 1440, "height": 900})
        ctx.add_init_script("try { sessionStorage.setItem('arha-intro', '1'); } catch (e) {}")
        pg = ctx.new_page(); errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(BASE + path, wait_until="load"); pg.wait_for_timeout(300)
        rows = pg.locator(".xindex__row")
        for i in (1, 4):
            r = rows.nth(i); r.scroll_into_view_if_needed(); pg.wait_for_timeout(300)
            bx = r.bounding_box()
            pg.mouse.move(bx["x"] + 120, bx["y"] + bx["height"] / 2); pg.wait_for_timeout(100)
            pg.mouse.move(bx["x"] + 200, bx["y"] + bx["height"] / 2); pg.wait_for_timeout(700)
            st = pg.evaluate("""(i) => { const p = document.querySelector('[data-xindex-preview]'); const a = p.querySelector('.is-active');
              const r = p.getBoundingClientRect(); return {vis: p.classList.contains('is-visible') && getComputedStyle(p).opacity === '1',
              active: [...p.children].indexOf(a), loaded: a && a.querySelector('img').complete && a.querySelector('img').naturalWidth > 0, left: Math.round(r.left)}; }""", i)
            want = int(r.get_attribute("data-preview"))
            ok = st["vis"] and st["active"] == want and st["loaded"]
            print(path, "hover row", i, st, "OK" if ok else "FAIL"); ok or fails.append(f"{path} row {i}: {st}")
            if i == 1: pg.screenshot(path=str(out / f"{path.strip('/')}-1440-hover.png"))
        pg.mouse.move(5, 450); pg.wait_for_timeout(600)
        if pg.evaluate("document.querySelector('[data-xindex-preview]').classList.contains('is-visible')"): fails.append(f"{path}: preview stays after leaving")
        if errs: fails.append(f"{path}: {errs}")
        ctx.close()
        ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
        ctx.add_init_script("try { sessionStorage.setItem('arha-intro', '1'); } catch (e) {}")
        pg = ctx.new_page(); pg.goto(BASE + path, wait_until="load"); pg.wait_for_timeout(300)
        pg.locator(".xindex__row").nth(2).scroll_into_view_if_needed(); pg.wait_for_timeout(900)
        st = pg.evaluate("({wide: document.documentElement.scrollWidth - innerWidth, thumbs: [...document.querySelectorAll('.xindex__thumb')].filter(t => t.getBoundingClientRect().width === 64).length, rows: document.querySelectorAll('.xindex__row').length})")
        print(path, "390", st); (st["wide"] <= 0 and st["thumbs"] == st["rows"]) or fails.append(f"{path} 390: {st}")
        pg.screenshot(path=str(out / f"{path.strip('/')}-390.png"))
        ctx.close()
    b.close()
print(f"{len(fails)} failures", fails); sys.exit(1 if fails else 0)
