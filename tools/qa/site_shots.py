"""Full-page screenshots of every built page at 1440 and 390 (JPEG).

Usage: .venv/Scripts/python -I tools/qa/site_shots.py OUTDIR [--base http://127.0.0.1:8080/] [--only path,path] [--widths 1440,390]
Files are named <page>-<width>.jpg (home, book, problems-toothache, ...). Reveals are shown, Riya's
launcher and bubble are hidden so they never cover the page, and lazy images are loaded first.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright  # noqa: E402
import pw  # noqa: E402
from console import paths  # noqa: E402

HIDE = (".riya-launcher,.riya-bubble{visibility:hidden!important}"
        ".reveal,[data-rise]{opacity:1!important;transform:none!important} picture.fill img{opacity:1!important}")


def arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def name_of(path):
    return path.strip("/").replace("/", "-") or "home"


def shoot(ctx, base, path, out, w):
    pg = ctx.new_page()
    pg.add_init_script("try { sessionStorage.setItem('riya-bubble', '1'); sessionStorage.setItem('arha-intro', '1'); } catch (e) {}")
    pg.goto(base + path, wait_until="load", timeout=60000)
    pg.wait_for_timeout(300)
    pg.wait_for_load_state("load")
    h = pg.evaluate("document.body.scrollHeight")
    for _y in range(0, h, 600):
        pg.mouse.wheel(0, 600)
        pg.wait_for_timeout(60)
    pg.evaluate("window.scrollTo(0, 0)")
    pg.add_style_tag(content=HIDE)
    pg.wait_for_timeout(900)
    pg.screenshot(path=str(out / f"{name_of(path)}-{w}.jpg"), full_page=True, type="jpeg", quality=72)
    pg.close()


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    base = arg("--base", pw.BASE)
    only = arg("--only", "")
    widths = [int(x) for x in arg("--widths", "1440,390").split(",")]
    todo = [p for p in paths() if not only or p in only.split(",") or (p == "" and "home" in only.split(","))]
    with sync_playwright() as p:
        b = pw.launch(p)
        for w in widths:
            ctx = b.new_context(viewport={"width": w, "height": 900 if w > 600 else 844}, device_scale_factor=1,
                                is_mobile=w < 600, has_touch=w < 600)
            for path in todo:
                shoot(ctx, base, path, out, w)
            ctx.close()
        b.close()
    print(f"{len(todo) * len(widths)} screenshots in {out}")


if __name__ == "__main__":
    main()
