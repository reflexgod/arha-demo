"""Before/after simulations for the demo (v4 fixes 3, point 2): both sides are the SAME photograph, so
the alignment is pixel-perfect, and every one is labelled "Simulation for demo" on the site.

Usage: .venv/Scripts/python -I tools/pairs.py [--sheet <out.jpg>]
Framing is wide: the lower face from about the nose tip to the chin, the teeth well under 40% of the
width, never macro. The "before" is the same photograph with a gentle warm shade on the teeth (a traced
outline, teeth_only, and photos.stain_teeth at a low strength): a shade difference, never broken or decayed teeth.
None of these are Arha's patients; real consented cases replace them before launch (notes/TO-CONFIRM.md).
Writes assets/img/stock-pair-1-{before,after}-<w>.* (featured case) and stock-sim-whiten-{before,after}-<w>.*
(Yellow or stained teeth).
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from photos import export, stain_teeth, stock_grade  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
STOCK = ROOT / "src-assets" / "stock"

# name: (source, crop (left, top, right, bottom) as fractions of the source, the visible teeth traced as a
#        polygon in the crop (fractions), shade strength). A traced outline is exact where an automatic
#        mask confuses warm, shaded teeth with skin; the dark gaps between teeth are left out (teeth_only).
SIMS = {
    "stock-pair-1": ("sim-smile-b.jpg", (0.0, 0.0, 1.0, 1.0),
                     [(0.466, 0.535), (0.578, 0.517), (0.660, 0.498), (0.727, 0.478), (0.736, 0.512),
                      (0.662, 0.562), (0.578, 0.597), (0.474, 0.612)], 0.45),
    "stock-sim-whiten": ("cand/c10.jpg", (0.0, 0.26, 1.0, 0.70),
                         [(0.523, 0.385), (0.648, 0.352), (0.778, 0.352), (0.778, 0.428), (0.714, 0.476),
                          (0.626, 0.490), (0.536, 0.467)], 0.45),
}


def teeth_only(im, poly):
    """Feathered polygon mask, minus anything much darker than the teeth inside it."""
    w, h = im.size
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon([(x * w, y * h) for x, y in poly], fill=255)
    g = np.asarray(im.convert("L")).astype(np.float32)
    inside = np.asarray(m) > 0
    ref = np.percentile(g[inside], 85)
    keep = (g > 0.45 * ref) & inside
    out = Image.fromarray((keep * 255).astype(np.uint8))
    return out.filter(ImageFilter.GaussianBlur(max(2, w / 700)))


def frame(src, crop):
    im = Image.open(STOCK / src).convert("RGB")
    W, H = im.size
    l, t, r, b = crop
    im = im.crop((round(l * W), round(t * H), round(r * W), round(b * H)))
    if im.width > 1920:
        im = im.resize((1920, round(im.height * 1920 / im.width)), Image.LANCZOS)
    return im


def build():
    out = {}
    for name, (src, crop, poly, strength) in SIMS.items():
        after = frame(src, crop)
        before = stain_teeth(after, teeth_only(after, poly), strength)
        before, after = stock_grade(before), stock_grade(after)
        export(before, f"{name}-before")
        export(after, f"{name}-after")
        out[name] = (before, after)
        print(name, after.size)
    return out


def sheet(pairs, path):
    rows = []
    for b, a in pairs.values():
        b, a = b.copy(), a.copy()
        b.thumbnail((700, 470))
        a.thumbnail((700, 470))
        row = Image.new("RGB", (1410, 470), "white")
        row.paste(b, (0, 0))
        row.paste(a, (710, 0))
        rows.append(row)
    s = Image.new("RGB", (1410, 480 * len(rows)), "white")
    for k, r in enumerate(rows):
        s.paste(r, (0, k * 480))
    s.save(path, quality=85)


if __name__ == "__main__":
    pairs = build()
    if "--sheet" in sys.argv:
        sheet(pairs, sys.argv[sys.argv.index("--sheet") + 1])
