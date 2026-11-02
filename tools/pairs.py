"""RETIRED (Viraaj, 2 Nov 2026): no simulated or stock "results" anywhere on the site. The files this made were
deleted; do not run it again. Kept for the record.

Before/after simulations for the demo (v4 fixes 3, point 2): both sides are the SAME photograph, so
the alignment is pixel-perfect, and every one is labelled "Simulation for demo" on the site.

Usage: .venv/Scripts/python -I tools/pairs.py [name ...] [--sheet <out.jpg>]
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
#        polygon in the crop (fractions), shade strength[, teeth_only options]). A traced outline is exact where an automatic
#        mask confuses warm, shaded teeth with skin; the dark gaps between teeth are left out (teeth_only).
SIMS = {
    "stock-pair-1": ("sim-smile-b.jpg", (0.0, 0.0, 1.0, 1.0),
                     [(0.466, 0.535), (0.578, 0.517), (0.660, 0.498), (0.727, 0.478), (0.736, 0.512),
                      (0.662, 0.562), (0.578, 0.597), (0.474, 0.612)], 0.45),
    # Every visible tooth, from the shaded ones on the left to the last molar in the corner; the lip's pink edge
    # and sheen are left out by saturation (sat), and the shaded teeth kept by a lower darkness cut (dark)
    "stock-sim-whiten": ("cand/c10.jpg", (0.0, 0.26, 1.0, 0.70),
                         [(0.523, 0.375), (0.554, 0.38), (0.601, 0.391), (0.653, 0.391), (0.71, 0.362), (0.762, 0.32),
                          (0.809, 0.29), (0.838, 0.268), (0.861, 0.243), (0.874, 0.229), (0.877, 0.249), (0.859, 0.288),
                          (0.838, 0.33), (0.815, 0.365), (0.789, 0.391), (0.768, 0.41), (0.742, 0.439), (0.718, 0.458),
                          (0.71, 0.48), (0.653, 0.486), (0.601, 0.489), (0.565, 0.47), (0.528, 0.422)], 0.45,
                         {"sat": 0.34, "dark": 0.27}),
}


def teeth_only(im, poly, sat=None, dark=0.45):
    """Feathered polygon mask, minus anything much darker than the teeth inside it and, with sat, minus
    anything more saturated than teeth (the pink edge of a lip caught by the outline)."""
    w, h = im.size
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon([(x * w, y * h) for x, y in poly], fill=255)
    g = np.asarray(im.convert("L")).astype(np.float32)
    inside = np.asarray(m) > 0
    ref = np.percentile(g[inside], 85)
    keep = (g > dark * ref) & inside
    if sat is not None:
        x = np.asarray(im.convert("RGB")).astype(np.float32)
        mx, mn = x.max(2), x.min(2)
        keep &= (mx - mn) / np.maximum(mx, 1) < sat
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
    only = [a for a in sys.argv[1:] if a in SIMS]  # name one or more to rebuild only those
    for name, (src, crop, poly, strength, *opts) in SIMS.items():
        if only and name not in only:
            continue
        after = frame(src, crop)
        before = stain_teeth(after, teeth_only(after, poly, **(opts[0] if opts else {})), strength)
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
