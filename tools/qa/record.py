"""Short screen recordings for v4 feedback 9 and the problems-first addition (Playwright video at 1440,
converted to MP4 with ffmpeg). A small dot shows where the mouse is.
Usage: .venv/Scripts/python tools/qa/record.py OUTDIR [clip-number ...]   (server on http://127.0.0.1:8080/)"""
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pw import FULL, BASE  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
QUIET = "try{sessionStorage.setItem('riya-bubble','1');sessionStorage.setItem('arha-intro','1')}catch(e){}"
CURSOR = """addEventListener('DOMContentLoaded', () => {
  const d = document.createElement('div');
  d.style.cssText = 'position:fixed;z-index:99999;left:0;top:0;width:18px;height:18px;margin:-9px 0 0 -9px;border-radius:50%;background:rgba(176,129,84,.55);border:1.5px solid #fff;box-shadow:0 0 0 1px rgba(0,0,0,.25);pointer-events:none;transition:transform .12s';
  document.body.append(d);
  addEventListener('pointermove', (e) => { d.style.left = e.clientX + 'px'; d.style.top = e.clientY + 'px'; }, true);
  addEventListener('pointerdown', () => { d.style.transform = 'scale(.7)'; }, true);
  addEventListener('pointerup', () => { d.style.transform = ''; }, true);
});"""


def glide(pg, x0, y0, x1, y1, steps=30, pause=12):
    for k in range(1, steps + 1):
        pg.mouse.move(x0 + (x1 - x0) * k / steps, y0 + (y1 - y0) * k / steps)
        pg.wait_for_timeout(pause)


def scroll_to(pg, sel, offset=-40, steps=30):
    y0 = pg.evaluate("scrollY")
    to = pg.evaluate("(a) => document.querySelector(a[0]).getBoundingClientRect().top + scrollY + a[1]", [sel, offset])
    for k in range(1, steps + 1):
        pg.evaluate(f"scrollTo(0, {y0 + (to - y0) * k / steps})")
        pg.wait_for_timeout(22)
    pg.wait_for_timeout(700)


def center(pg, sel, n=0):
    b = pg.locator(sel).nth(n).bounding_box()
    return b["x"] + b["width"] / 2, b["y"] + b["height"] / 2, b


def clip(name, path, fn):
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path=FULL)
        ctx = br.new_context(viewport={"width": 1440, "height": 900}, record_video_dir=str(OUT / "tmp"),
                             record_video_size={"width": 1440, "height": 900})
        ctx.add_init_script(QUIET)
        ctx.add_init_script(CURSOR)
        pg = ctx.new_page()
        pg.goto(BASE + path, wait_until="load")
        pg.mouse.move(720, 600)
        pg.wait_for_timeout(900)
        fn(pg)
        pg.wait_for_timeout(600)
        video = pg.video
        ctx.close()
        br.close()
        webm = OUT / f"{name}.webm"
        shutil.move(video.path(), webm)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(webm), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "28",
                        "-preset", "slow", "-movflags", "+faststart", "-an", str(OUT / f"{name}.mp4")], check=True)
        webm.unlink()
        print("recorded", name)


def header_and_brings(pg):
    x, y, _ = center(pg, ".nav__trigger >> nth=0")
    glide(pg, 720, 600, x, y); pg.wait_for_timeout(1400)
    x2, y2, _ = center(pg, ".nav__trigger >> nth=1")
    glide(pg, x, y, x2, y2, 20); pg.wait_for_timeout(1000)
    x3, y3, _ = center(pg, ".nav__trigger >> nth=2")
    glide(pg, x2, y2, x3, y3, 20); pg.wait_for_timeout(1000)
    glide(pg, x3, y3, 720, 600, 20); pg.wait_for_timeout(400)
    mx, my, _ = center(pg, ".menu-toggle")
    glide(pg, 720, 600, mx, my); pg.mouse.click(mx, my); pg.wait_for_timeout(1100)
    gx, gy, _ = center(pg, ".fmenu__toggle >> nth=0")
    glide(pg, mx, my, gx, gy); pg.mouse.click(gx, gy); pg.wait_for_timeout(1600)
    pg.keyboard.press("Escape"); pg.wait_for_timeout(700)
    scroll_to(pg, ".brings", -10)
    last = (720, 600)
    for k in [0, 1, 3, 4, 6, 9]:
        x, y, _ = center(pg, ".brings__item", k)
        glide(pg, *last, x - 80, y, 18); last = (x - 80, y)
        pg.wait_for_timeout(1100)


def homepage_slider(pg):
    scroll_to(pg, ".featured-case", -110)
    x, y, b = center(pg, ".featured-case [data-ba]")
    glide(pg, 720, 600, x, y, 20)
    pg.mouse.down()
    for f in [0.2, 0.08, 0.35, 0.8, 0.93, 0.6]:
        tx = b["x"] + b["width"] * f
        glide(pg, x, y, tx, y, 28, 14)
        x = tx
        pg.wait_for_timeout(260)
    pg.mouse.up(); pg.wait_for_timeout(500)
    for f in (0.25, 0.7):
        tx = b["x"] + b["width"] * f
        glide(pg, x, y, tx, y + 80, 16); x = tx
        pg.mouse.click(tx, y + 80); pg.wait_for_timeout(900)
    pg.focus("[data-ba] .ba__handle")
    for _ in range(8):
        pg.keyboard.press("ArrowLeft"); pg.wait_for_timeout(90)
    pg.wait_for_timeout(600)
    scroll_to(pg, ".pairs-grid--home", -200)
    px, py, _ = center(pg, ".pairs-grid--home .pair", 0)
    glide(pg, x, y, px, py, 24); pg.wait_for_timeout(1200)
    px2, py2, _ = center(pg, ".pairs-grid--home .pair", 1)
    glide(pg, px, py, px2, py2, 24); pg.wait_for_timeout(1200)


def common_problems(pg):
    # 1. A missing tooth: Implant / Bridge / Denture
    scroll_to(pg, ".ix", 0)
    last = (720, 600)
    for k in (1, 2, 0):
        x, y, _ = center(pg, "[data-xfade] [role=tab]", k)
        glide(pg, *last, x, y, 20); last = (x, y)
        pg.mouse.click(x, y); pg.wait_for_timeout(1300)
    # 2. Chipped tooth: the magnifier
    pg.goto(BASE + "problems/chipped-tooth/", wait_until="load"); pg.wait_for_timeout(700)
    scroll_to(pg, ".ix", 0)
    _, _, b = center(pg, "[data-loupe]")
    pts = [(.15, .45), (.3, .55), (.45, .5), (.6, .55), (.75, .45), (.5, .35)]
    lx, ly = 720, 860
    for fx, fy in pts:
        tx, ty = b["x"] + b["width"] * fx, b["y"] + b["height"] * fy
        glide(pg, lx, ly, tx, ty, 26, 16); lx, ly = tx, ty
        pg.wait_for_timeout(300)
    glide(pg, lx, ly, 720, b["y"] - 30, 12); pg.wait_for_timeout(400)
    # 3. Yellow or stained teeth: the whitening simulation
    pg.goto(BASE + "problems/stained-teeth/", wait_until="load"); pg.wait_for_timeout(700)
    scroll_to(pg, ".ix", 0)
    _, _, r = center(pg, "[data-blend] input[type=range]")
    y = r["y"] + r["height"] / 2
    glide(pg, 720, 600, r["x"] + 6, y, 18)
    pg.mouse.down()
    glide(pg, r["x"] + 6, y, r["x"] + r["width"] - 6, y, 60, 20); pg.wait_for_timeout(500)
    glide(pg, r["x"] + r["width"] - 6, y, r["x"] + r["width"] * .45, y, 30, 20); pg.wait_for_timeout(300)
    glide(pg, r["x"] + r["width"] * .45, y, r["x"] + r["width"] - 6, y, 30, 20)
    pg.mouse.up(); pg.wait_for_timeout(900)


def colour_on_hover(pg):
    scroll_to(pg, ".trio", 0)
    last = (720, 600)
    for k in range(3):
        x, y, _ = center(pg, ".trio [data-xpanel]", k)
        glide(pg, *last, x, y - 60, 24); last = (x, y - 60)
        pg.wait_for_timeout(1300)
    scroll_to(pg, ".journey-hl", 40)
    glide(pg, *last, 1080, 450, 24); pg.wait_for_timeout(1300)
    glide(pg, 1080, 450, 300, 450, 24); pg.wait_for_timeout(800)
    scroll_to(pg, ".pairs-grid--home", -200)
    for k in range(3):
        x, y, _ = center(pg, ".pairs-grid--home .pair", k)
        glide(pg, 300, 450, x, y, 24)
        pg.wait_for_timeout(1100)


def treatment(pg):
    scroll_to(pg, ".ix", 0)
    _, _, r = center(pg, "[data-stages] input[type=range]")
    y = r["y"] + r["height"] / 2
    glide(pg, 720, 600, r["x"] + 6, y, 18)
    pg.mouse.down()
    x = r["x"] + 6
    for f in (0.36, 0.69, 1.0):
        tx = r["x"] + r["width"] * f - 4
        glide(pg, x, y, tx, y, 24, 16)
        x = tx
        pg.wait_for_timeout(1300)
    pg.mouse.up()
    scroll_to(pg, ".vs-wrap", -120)
    x, y, _ = center(pg, ".itabs--vs [role=tab]", 1)
    glide(pg, 720, 600, x, y, 20); pg.mouse.click(x, y); pg.wait_for_timeout(1400)
    x0, y0, _ = center(pg, ".itabs--vs [role=tab]", 0)
    glide(pg, x, y, x0, y0, 14); pg.mouse.click(x0, y0); pg.wait_for_timeout(1200)


CLIPS = [("1-header-and-what-brings-you-in", "", header_and_brings),
         ("2-homepage-slider", "", homepage_slider),
         ("3-common-problems-toggle-loupe-whitening", "problems/missing-tooth/", common_problems),
         ("4-colour-on-hover", "", colour_on_hover),
         ("5-treatment-invisalign-stages", "invisalign/", treatment)]

if __name__ == "__main__":
    only = sys.argv[2:]
    for name, path, fn in CLIPS:
        if not only or any(name.startswith(o) for o in only):
            clip(name, path, fn)
    shutil.rmtree(OUT / "tmp", ignore_errors=True)
