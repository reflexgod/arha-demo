"""Hero text contrast on every frame of the hero loop (every 0.5 s), with the hero's dark wash applied.

Usage: .venv/Scripts/python -I tools/qa/hero_contrast.py
For each width it reads where the heading, the line under it and the button sit (Playwright), cuts the matching
frames from the video the browser would play there (object-fit: cover), lays the CSS wash over them exactly as
site.css draws it ("Demo-ready" layer), and reports the lowest contrast of the paper-white text against the
brightest 5% of the pixels behind each line. WCAG AA asks for 4.5:1 (3:1 for large text such as the heading).
"""
import functools
import http.server
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright  # noqa: E402
import pw  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
SHADE = np.array([48, 47, 47], float)
TEXT = np.array([250, 250, 246], float)
# (position from 0 at the start, alpha) stops, as in site.css
PHONE_V = [(0, .8), (.28, .66), (.5, .46), (.74, .16), (.9, 0)]  # to top (0 = bottom edge)
DESK_V = [(0, .8), (.3, .62), (.58, .36), (.84, 0)]              # to top
DESK_H = [(0, .5), (.38, .3), (.64, 0)]                          # to right (0 = left edge)


def ramp(stops, n):
    x = np.linspace(0, 1, n)
    return np.interp(x, [s[0] for s in stops] + [1], [s[1] for s in stops] + [stops[-1][1]])


def lum(rgb):
    c = rgb / 255
    c = np.where(c <= .04045, c / 12.92, ((c + .055) / 1.055) ** 2.4)
    return c[..., 0] * .2126 + c[..., 1] * .7152 + c[..., 2] * .0722


def contrast(l_text, l_bg):
    return (l_text + .05) / (l_bg + .05)


def serve():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/"


def boxes(width, height):
    srv, base = serve()
    with sync_playwright() as p:
        b = pw.launch(p)
        pg = b.new_page(viewport={"width": width, "height": height})
        pg.goto(base, wait_until="load")
        pg.wait_for_timeout(400)
        out = pg.evaluate("""() => {
          const hero = document.querySelector('[data-hero]').getBoundingClientRect();
          const box = (s) => { const r = document.querySelector(s).getBoundingClientRect(); return [r.left - hero.left, r.top - hero.top, r.width, r.height]; };
          return { hero: [hero.width, hero.height], h1: box('.ah-hero h1'), lede: box('.ah-hero .hero__lede'), cta: box('.ah-hero .hero__actions a') };
        }""")
        b.close()
    srv.shutdown()
    return out


def frames(video, every=.5):
    tmp = Path(tempfile.mkdtemp())
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(video), "-vf", f"fps={1 / every}", str(tmp / "f%03d.png")], check=True)
    return sorted(tmp.glob("f*.png"))


def main():
    l_text = lum(TEXT)
    for width, height, video, desk in [(390, 844, "hero-city-phone.mp4", False), (768, 1024, "hero-city-phone.mp4", False),
                                       (1024, 768, "hero-city-720.mp4", True), (1440, 900, "hero-city-1080.mp4", True),
                                       (1920, 1080, "hero-city-1080.mp4", True)]:
        geo = boxes(width, height)
        hw, hh = round(geo["hero"][0]), round(geo["hero"][1])
        a_v = ramp(DESK_V if desk else PHONE_V, hh)[::-1][:, None]          # rows, top to bottom
        a_h = ramp(DESK_H, hw)[None, :] if desk else np.zeros((1, hw))
        worst = {k: (99, "") for k in ("h1", "lede", "cta")}
        files = frames(ROOT / "assets" / "video" / video)
        for f in files:
            im = Image.open(f).convert("RGB")
            s = max(hw / im.width, hh / im.height)              # object-fit: cover, centred
            im = im.resize((round(im.width * s), round(im.height * s)), Image.BILINEAR)
            x0, y0 = (im.width - hw) // 2, (im.height - hh) // 2
            px = np.asarray(im.crop((x0, y0, x0 + hw, y0 + hh)), float)
            px = px * (1 - a_v[..., None]) + SHADE * a_v[..., None]   # the vertical wash, then the side wash on top
            px = px * (1 - a_h[..., None]) + SHADE * a_h[..., None]
            for k in worst:
                x, y, w, h = [round(v) for v in geo[k]]
                region = lum(px[max(y, 0):y + h, max(x, 0):x + w])
                c = contrast(l_text, np.percentile(region, 95))
                if c < worst[k][0]:
                    worst[k] = (c, f.name)
        print(f"{width} x {height} ({video}, {len(files)} frames): " + ", ".join(f"{k} {v[0]:.1f}:1" for k, v in worst.items()))


if __name__ == "__main__":
    main()
