"""Every photo as it renders on every page at 1440/768/390: one thumbnail per (image, width, box shape), contact
sheets per width, a face check (Haar) that flags faces whose head would reach the box edge, and where each image appears.
Usage: python crops.py BASEURL OUTDIR"""
import json
import re
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, r"C:\Users\viraa\IdeaProjects\arha demo\tools\qa")
sys.path.insert(0, str(Path(__file__).parent))
from PIL import Image, ImageDraw  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402
import pw  # noqa: E402
from shots import PAGES, PREP  # noqa: E402


JS = """() => [...document.querySelectorAll('main picture img, main .ctacard img')].map((i) => {
  const r = i.getBoundingClientRect(); const src = i.currentSrc || i.src;
  return {src, x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height};
}).filter((o) => o.w > 40 && o.h > 40 && !/\\.svg/.test(o.src))"""


def name_of(src):
    m = re.search(r"/static/img/(.+?)-\d+(?:\.[0-9a-f]{8})?\.(?:avif|webp|jpe?g)", src)
    return m.group(1) if m else src


def faces(im):
    g = cv2.cvtColor(np.asarray(im.convert("RGB")), cv2.COLOR_RGB2GRAY)
    return FACE.detectMultiScale(g, 1.1, 6, minSize=(max(24, im.width // 14),) * 2)


def main():
    base, out = sys.argv[1].rstrip("/"), Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
    seen, where, flags = {}, {}, []
    with sync_playwright() as p:
        b = pw.launch(p)
        for w in (1440, 768, 390):
            ctx = b.new_context(viewport={"width": w, "height": 900 if w > 600 else 844})
            ctx.add_init_script("try{localStorage.setItem('arha-consent', JSON.stringify({analytics:false,ts:1}));}catch(e){}")
            pg = ctx.new_page()
            for path in PAGES:
                pg.goto(base + path, wait_until="networkidle")
                pg.add_style_tag(content="[data-reveal]{opacity:1!important;transform:none!important;transition:none!important} .cookie,.cookies,#cookie,.callbar{display:none!important} *{transition:none!important}")
                pg.evaluate(PREP)
                full = None
                for o in pg.evaluate(JS):
                    n = name_of(o["src"])
                    where.setdefault(n, set()).add(path)
                    key = (n, w, round(o["w"] / o["h"], 1))
                    if key in seen:
                        continue
                    if full is None:
                        f = out / "_page.png"; pg.screenshot(path=str(f), full_page=True); full = Image.open(f).convert("RGB")
                    box = tuple(round(v) for v in (o["x"], o["y"], o["x"] + o["w"], o["y"] + o["h"]))
                    crop = full.crop(box)
                    seen[key] = crop
                    for (fx, fy, fw, fh) in []:
                        top = fy - 0.45 * fh  # head top sits ~0.45 face-heights above the detected box
                        if top < -2 or fx < -2 or fx + fw > crop.width + 2:
                            flags.append(f"{n} @{w} ({path}): head reaches the edge (face box {fx},{fy},{fw},{fh} in {crop.width}x{crop.height})")
                full = None
            ctx.close()
        b.close()
    for w in (1440, 768, 390):
        items = [(k, v) for k, v in seen.items() if k[1] == w]
        tw, th, cols = 300, 230, 6
        sheet = Image.new("RGB", (tw * cols, th * ((len(items) + cols - 1) // cols)), "white"); d = ImageDraw.Draw(sheet)
        for i, ((n, _, r), im) in enumerate(items):
            t = im.copy(); t.thumbnail((tw - 6, th - 22))
            x, y = (i % cols) * tw, (i // cols) * th
            sheet.paste(t, (x + 3, y + 3)); d.text((x + 4, y + th - 18), f"{n} {r}", fill="black")
        sheet.save(out / f"sheet-{w}.jpg", quality=82)
        print(w, len(items), "crops")
    (out / "where.json").write_text(json.dumps({k: sorted(v) for k, v in where.items()}, indent=1))
    print("\n".join(flags) or "no head-at-edge flags")


if __name__ == "__main__":
    main()
