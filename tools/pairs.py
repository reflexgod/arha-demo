"""Sample before/after pairs for the demo, every one labelled "Sample case for demo" on the site.

Usage: .venv/Scripts/python -I tools/pairs.py [--sheet <out.jpg>]
Writes assets/img/stock-pair-<n>-before-<w>.* and stock-pair-<n>-after-<w>.* (3:2, mouth centred),
and the whitening simulation used by "Common problems" (stock-sim-whiten-before/after).

Two kinds (notes/V4-FEEDBACK-2.md, point 4):
  sim    one stock photograph; the "before" is the same photograph with its teeth masked and tinted
         (photos.teeth_mask / stain_teeth). Same face, same light: only the teeth change.
  stock  a stock "before" (crowded, worn, uneven teeth) paired with a stock "after" smile of a
         different person, both cropped to the same framing.
None of these are Arha's patients. Real consented cases replace them before launch (notes/TO-CONFIRM.md).
"""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from photos import export, stain_teeth, stock_grade, teeth_mask, whiten_teeth  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
STOCK = ROOT / "src-assets" / "stock"
ASPECT = 3 / 2
MOUTH = 0.80  # lip corners span 80% of the frame width where the photograph allows it

# (source, (mouth centre x, centre y, mouth width) as fractions of the source)
SHOTS = {
    "blonde": ("cand/c5.jpg", (0.68, 0.39, 0.36)),
    "beard": ("cand/c2.jpg", (0.50, 0.51, 0.90)),
    "frontal": ("smile-1.jpg", (0.48, 0.45, 0.55)),
    "woman-tilt": ("cand/c4.jpg", (0.74, 0.51, 0.37)),
    "worn": ("before-worn.jpg", (0.52, 0.52, 0.95)),
    "uneven": ("before-missing-2.jpg", (0.50, 0.45, 0.95)),
    "red-lips": ("before-missing.jpg", (0.535, 0.30, 0.65)),
    "crowded": ("before-crowded.jpg", (0.50, 0.50, 1.00)),
    "straight": ("loupe-teeth.jpg", (0.50, 0.50, 1.00)),
    "yellow": ("cand/c1.jpg", (0.45, 0.40, 0.65)),
}

# case n: (kind, before shot, after shot, teeth box in the after frame for "sim")
PAIRS = {
    1: ("sim", None, "blonde", (0.22, 0.33, 0.82, 0.60)),  # featured: smile design & veneers
    2: ("stock", "worn", "beard", None),                   # implants
    3: ("stock", "uneven", "frontal", None),               # full mouth
    4: ("stock", "crowded", "straight", None),             # aligners
    5: ("stock", "red-lips", "woman-tilt", None),          # veneers
}
WHITEN_BOX = (-0.25, 0.36, 1.25, 0.76)  # teeth in the "yellow" frame


def frame(key):
    src, (cx, cy, w) = SHOTS[key]
    im = Image.open(STOCK / src).convert("RGB")
    W, H = im.size
    cw = min(w * W / MOUTH, W, H * ASPECT)
    ch = cw / ASPECT
    left = min(max(cx * W - cw / 2, 0), W - cw)
    top = min(max(cy * H - ch / 2, 0), H - ch)
    im = im.crop((round(left), round(top), round(left + cw), round(top + ch)))
    if im.width > 1920:
        im = im.resize((1920, round(1920 / ASPECT)), Image.LANCZOS)
    elif im.width < 1280:
        im = im.resize((1280, round(1280 / ASPECT)), Image.LANCZOS)
    return im


def build():
    out = {}
    for n, (kind, before, after, box) in PAIRS.items():
        a = frame(after)
        if kind == "sim":
            b = stain_teeth(a, teeth_mask(a, box, sat=0.22), 0.75)
        else:
            b = frame(before).resize(a.size, Image.LANCZOS)
        a, b = stock_grade(a), stock_grade(b)
        export(b, f"stock-pair-{n}-before")
        export(a, f"stock-pair-{n}-after")
        out[n] = (b, a)
        print(n, kind, a.size)
    y = frame("yellow")
    w = whiten_teeth(y, teeth_mask(y, WHITEN_BOX, light=0.45, hue=(24, 70)), 0.9)
    export(stock_grade(y), "stock-sim-whiten-before")
    export(stock_grade(w), "stock-sim-whiten-after")
    out["whiten"] = (stock_grade(y), stock_grade(w))
    return out


def sheet(pairs, path):
    rows = []
    for b, a in pairs.values():
        b, a = b.copy(), a.copy()
        b.thumbnail((600, 400))
        a.thumbnail((600, 400))
        row = Image.new("RGB", (1210, 400), "white")
        row.paste(b, (0, 0))
        row.paste(a, (610, 0))
        rows.append(row)
    s = Image.new("RGB", (1210, 410 * len(rows)), "white")
    for k, r in enumerate(rows):
        s.paste(r, (0, k * 410))
    s.save(path, quality=82)


if __name__ == "__main__":
    pairs = build()
    if "--sheet" in sys.argv:
        sheet(pairs, sys.argv[sys.argv.index("--sheet") + 1])
