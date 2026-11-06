"""Sample smile pairs for the demo's "Smile results" sliders (v5 upgrade brief, Viraaj 6 Nov 2026).

Both sides of every pair are the SAME stock photograph, so the slider lines up exactly: the "after" is a gentle
simulated whitening (teeth already warm in the source) or the "before" a gentle simulated shade (teeth already
light). Every card on the site is tagged "Sample". None of these people are Arha's patients; real consented cases
replace them before launch. Sources and licences: assets/stock/CREDITS.md.

Usage: .venv/Scripts/python -I tools/samples.py [--sheet out.jpg]
Writes assets/stock/sample-smile-<n>-{before,after}-{640,1200}.webp
"""
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from photos import stain_teeth, teeth_mask, whiten_teeth  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src-assets" / "stock"
OUT = ROOT / "assets" / "stock"

# n: (source, crop (l, t, r, b) fractions of the source, teeth box (fractions of the crop), mode, amount, mask options)
PAIRS = {
    1: ("sim-smile-b.jpg", (0.30, 0.30, 0.80, 0.80), (0.33, 0.34, 0.85, 0.62), "stain", 0.55, {}),
    2: ("cand/c3.jpg", (0, 0.02, 1, 0.52), (0.24, 0.47, 0.76, 0.62), "stain", 0.55, {}),
    3: ("cand/c10.jpg", (0.2, 0.26, 1.0, 0.66), (0.40, 0.36, 0.78, 0.50), "stain", 0.55, {"light": 0.35, "sat": 0.22}),
    4: ("straight-smile.jpg", (0, 0, 1, 1), (0.02, 0.15, 0.98, 0.62), "stain", 0.5, {"rect": True}),
    5: ("natural-smile.jpg", (0, 0.18, 1, 0.68), (0.04, 0.34, 0.74, 0.64), "stain", 0.55, {}),
    6: ("smile-5.jpg", (0.35, 0.0, 1.0, 0.65), (0.31, 0.28, 0.76, 0.47), "stain", 0.55, {}),
}


def frame(src, crop):
    im = Image.open(SRC / src).convert("RGB")
    W, H = im.size
    l, t, r, b = crop
    return im.crop((round(l * W), round(t * H), round(r * W), round(b * H)))


def to43(im):
    """Centre-crop to 4:3 so every card is the same shape."""
    w, h = im.size
    if w / h > 4 / 3:
        nw = round(h * 4 / 3)
        return im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    nh = round(w * 3 / 4)
    return im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    pairs = {}
    for n, (src, crop, box, mode, amount, opts) in PAIRS.items():
        im = frame(src, crop)
        mask = teeth_mask(im, box, **opts)
        if mode == "whiten":
            before, after = im, whiten_teeth(im, mask, amount)
        else:
            before, after = stain_teeth(im, mask, amount), im
        before, after = to43(before), to43(after)
        for side, pic in (("before", before), ("after", after)):
            for w in (640, 1200):
                r = pic.resize((w, round(w * 3 / 4)), Image.LANCZOS)
                r.save(OUT / f"sample-smile-{n}-{side}-{w}.webp", "WEBP", quality=80, method=6)
        pairs[n] = (before, after)
        kb = (OUT / f"sample-smile-{n}-after-1200.webp").stat().st_size // 1024
        print(f"sample-smile-{n}: {src}, {mode}, 1200w {kb} KB")
    return pairs


if __name__ == "__main__":
    pairs = build()
    if "--sheet" in sys.argv:
        out = sys.argv[sys.argv.index("--sheet") + 1]
        sheet = Image.new("RGB", (1200, 300 * len(pairs)), "white")
        for i, (b, a) in enumerate(pairs.values()):
            sheet.paste(b.resize((400, 300)), (0, 300 * i))
            sheet.paste(a.resize((400, 300)), (400, 300 * i))
            # the difference, exaggerated, shows where the mask reached
            import numpy as np
            d = np.abs(np.asarray(a.resize((400, 300))).astype(int) - np.asarray(b.resize((400, 300))).astype(int)).sum(2)
            sheet.paste(Image.fromarray(np.clip(d * 4, 0, 255).astype("uint8")).convert("RGB"), (800, 300 * i))
        sheet.save(out, quality=80)
