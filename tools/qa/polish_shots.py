"""Before/after captures for the v5 polish (brief: notes/POLISH-REVIEW.md). Starts its own gzip server.

Usage: .venv/Scripts/python tools/qa/polish_shots.py <site root> <port> <label> <review dir>
Writes into <review dir>:
  polish/<label>-{home,treatment}-{390,1440}.png     full pages, after a slow scroll so every photo has settled
  fonts/<label>-{hero,trio,dark,philosophy,treatment-hero,treatment-section}-{390,1440}.png   headline crops
  polish/<label>-scroll-{390,1440}.mp4 and -frames.jpg   a real scroll of the home page (contact sheet of 12 frames)
"""
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright  # noqa: E402
from PIL import Image  # noqa: E402
import pw  # noqa: E402

ROOT, PORT, LABEL, OUT = sys.argv[1], int(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
BASE = f"http://127.0.0.1:{PORT}/"
QUIET = "try{sessionStorage.setItem('arha-intro','1');sessionStorage.setItem('riya-bubble','1')}catch(e){}"
SIZES = [(390, 844, True), (1440, 900, False)]
PAGES = [("home", ""), ("treatment", "dental-implants/")]
CROPS = [("hero", "", ".ah-hero"), ("trio", "", ".ah-head"), ("dark", "", ".ah-dark"), ("philosophy", "", ".ah-founder"),
         ("treatment-hero", "dental-implants/", ".page-hero"), ("treatment-section", "dental-implants/", "main section:nth-of-type(3)")]


def settle(pg):
    """Scroll down slowly, then back to the top: reveals have fired and lazy photos have loaded."""
    h = pg.evaluate("document.documentElement.scrollHeight")
    y = 0
    while y < h:
        y += 500
        pg.evaluate(f"scrollTo({{top: {y}, behavior: 'instant'}}); new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)))")
        pg.wait_for_timeout(120)
        h = pg.evaluate("document.documentElement.scrollHeight")
    pg.wait_for_timeout(500)
    pg.evaluate("scrollTo({top: 0, behavior: 'instant'})")
    pg.wait_for_timeout(500)


def scroll_clip(b, w, h, phone):
    tmp = OUT / "polish" / f"_tmp-{LABEL}-{w}"
    ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=phone, has_touch=phone,
                        record_video_dir=str(tmp), record_video_size={"width": w, "height": h})
    ctx.add_init_script(QUIET)
    pg = ctx.new_page()
    frames = []
    pg.goto(BASE, wait_until="load")
    pg.wait_for_timeout(1200)
    total = pg.evaluate("document.documentElement.scrollHeight") - h
    y, n, step = 0, 0, 34 if phone else 46
    every = max(1, total // step // 12)
    while y < total:
        y += step
        pg.evaluate(f"scrollTo({{top: {y}, behavior: 'instant'}})")
        pg.wait_for_timeout(16)
        if n % every == 0 and len(frames) < 12:
            frames.append(pg.screenshot(type="jpeg", quality=70))
        n += 1
    pg.wait_for_timeout(500)
    video = pg.video
    ctx.close()
    src = video.path()
    mp4 = OUT / "polish" / f"{LABEL}-scroll-{w}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-c:v", "libx264", "-crf", "28", "-preset", "fast",
                    "-pix_fmt", "yuv420p", "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-movflags", "+faststart", str(mp4)], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    # contact sheet
    import io
    ims = [Image.open(io.BytesIO(f)).convert("RGB") for f in frames]
    tw = 240 if phone else 360
    th = round(tw * h / w)
    cols = 6 if phone else 4
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + 6), rows * (th + 6)), "white")
    for i, im in enumerate(ims):
        sheet.paste(im.resize((tw, th)), ((i % cols) * (tw + 6) + 3, (i // cols) * (th + 6) + 3))
    sheet.save(OUT / "polish" / f"{LABEL}-scroll-{w}-frames.jpg", quality=80)


def main():
    (OUT / "polish").mkdir(parents=True, exist_ok=True)
    (OUT / "fonts").mkdir(parents=True, exist_ok=True)
    server = subprocess.Popen([sys.executable, "-I", str(Path(__file__).parent / "gzserve.py"), str(PORT), ROOT])
    try:
        with sync_playwright() as p:
            b = pw.launch(p, full=True)
            for w, h, phone in SIZES:
                ctx = b.new_context(viewport={"width": w, "height": h}, is_mobile=phone, has_touch=phone, device_scale_factor=2 if phone else 1)
                ctx.add_init_script(QUIET)
                for name, path in PAGES:
                    pg = ctx.new_page()
                    pg.goto(BASE + path, wait_until="load")
                    pg.wait_for_timeout(600)
                    settle(pg)
                    pg.screenshot(path=str(OUT / "polish" / f"{LABEL}-{name}-{w}.png"), full_page=True)
                    pg.close()
                for name, path, sel in CROPS:
                    pg = ctx.new_page()
                    pg.goto(BASE + path, wait_until="load")
                    pg.wait_for_timeout(500)
                    settle(pg)
                    loc = pg.locator(sel).first
                    if loc.count():
                        loc.scroll_into_view_if_needed()
                        pg.wait_for_timeout(700)
                        loc.screenshot(path=str(OUT / "fonts" / f"{LABEL}-{name}-{w}.png"))
                    else:
                        print("no element", sel, path)
                    pg.close()
                ctx.close()
                scroll_clip(b, w, h, phone)
            b.close()
    finally:
        server.kill()


if __name__ == "__main__":
    main()
