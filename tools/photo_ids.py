"""Which photo files are the same photograph. Unsplash often returns one photo under several searches,
so files like stock-stained and stock-before-missing-2 can be one image. Used by tools/photo_audit.py.

Usage: .venv/Scripts/python -I tools/photo_ids.py        (prints the groups of identical photographs)
Unsplash returns one photo under several searches: check here before picking (tools/stock.py).
Two files are the same photograph when their 16x12 greyscale thumbnails differ by less than 6 levels
on average. A crop of the same photograph is not caught that way, so crops are listed in CROPS.
"""
import sys
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"


def signature(path):
    return list(ImageOps.grayscale(Image.open(path)).resize((16, 12), Image.BILINEAR).get_flattened_data())


# Crops of one photograph under another name (a thumbnail comparison cannot see a crop): the sample
# pairs (tools/pairs.py) and the old case tiles (tools/cases.py) cut from the same stock photographs.
CROPS = {
    "stock-pair-1-after": "stock-case-2", "stock-pair-1-before": "stock-case-2",      # cand/c5
    "stock-pair-2-after": "stock-case-5",                                             # cand/c2
    "stock-pair-5-after": "stock-case-4",                                             # cand/c4
    "stock-pair-2-before": "stock-before-worn", "stock-pair-3-before": "stock-before-missing-2",
    "stock-pair-3-after": "stock-smile-1", "stock-pair-4-before": "stock-before-crowded",
    "stock-pair-4-after": "stock-loupe-teeth", "stock-pair-5-before": "stock-before-missing",
    "stock-case-1-face": "stock-case-1", "stock-case-2-face": "stock-case-2", "stock-case-4-face": "stock-case-4",
    "stock-case-6-face": "stock-case-6",
    "stock-sim-whiten-after": "stock-sim-whiten-before",
}


@lru_cache(maxsize=1)
def groups():
    """name -> canonical name (the alphabetically first file of its group)."""
    names = sorted({p.name.rsplit("-", 1)[0] for p in IMG.glob("*-640.jpg")})
    sigs = {n: signature(IMG / f"{n}-640.jpg") for n in names}
    canon = {}
    for n in names:
        for c in dict.fromkeys(canon.values()):
            if sum(abs(a - b) for a, b in zip(sigs[n], sigs[c])) / 192 < 6:
                canon[n] = c
                break
        else:
            canon[n] = n
    for n, src in CROPS.items():
        if n in canon:
            canon[n] = canon.get(src, src)
    return canon


if __name__ == "__main__":
    g = groups()
    for c in sorted(set(g.values())):
        same = [n for n, k in g.items() if k == c]
        if len(same) > 1:
            print(" = ".join(same))
    sys.exit(0)
