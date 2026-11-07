"""Print a responsive <picture> element for a processed photo (AVIF > WebP > JPEG).

Usage: .venv/Scripts/python -I tools/picture.py <name> "<sizes>" "<alt>" [--eager] [--pos "50% 40%"]
Widths and intrinsic dimensions are read from the files in assets/img. The <picture> fills its
(fixed aspect-ratio) box over a solid stone background, so nothing shifts and there is never a
blurred preview to see mid-scroll; site.js fades the real image in once it has loaded and decoded.
"""
import argparse
import re
from pathlib import Path

from PIL import Image

IMG = Path(__file__).resolve().parent.parent / "assets" / "img"
# Stock photographs of people (tools/people.py) live in assets/stock, 768/1280/1920 wide.
STOCK = IMG.parent / "stock"


def locate(name):
    """(folder on disk, folder in the page, sorted widths) for a processed photograph."""
    for folder, url in ((IMG, "assets/img"), (STOCK, "assets/stock")):
        widths = sorted(int(m.group(1)) for p in folder.glob(f"{name}-*.jpg") if (m := re.fullmatch(rf"{re.escape(name)}-(\d+)\.jpg", p.name)))
        if widths:
            return folder, url, widths
    raise FileNotFoundError(name)

# The signature divider between major sections: a bronze hairline and Arha's emblem on the seam (site.css). No height.
SIG = '<div class="sig" aria-hidden="true"><span></span></div>'


def picture(name, sizes, alt, eager=False, cls=None, pos=None, indent="  "):
    folder, url, widths = locate(name)
    base = 1280 if 1280 in widths else widths[-1]
    w, h = Image.open(folder / f"{name}-{base}.jpg").size
    src = lambda ext: ", ".join(f"{url}/{name}-{x}.{ext} {x}w" for x in widths)  # noqa: E731
    attrs = f'width="{w}" height="{h}"' + (' fetchpriority="high"' if eager else ' loading="lazy"') + ' decoding="async"'
    img_style = f' style="object-position: {pos}"' if pos else ""
    classes = " ".join(c for c in ["fill", cls] if c)
    return "\n".join([
        f'{indent}<picture class="{classes}">',
        f'{indent}  <source type="image/avif" srcset="{src("avif")}" sizes="{sizes}">',
        f'{indent}  <source type="image/webp" srcset="{src("webp")}" sizes="{sizes}">',
        f'{indent}  <img src="{url}/{name}-{base}.jpg" srcset="{src("jpg")}" sizes="{sizes}" {attrs} alt="{alt}"{img_style}>',
        f"{indent}</picture>",
    ])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("sizes")
    ap.add_argument("alt")
    ap.add_argument("--eager", action="store_true")
    ap.add_argument("--class", dest="cls")
    ap.add_argument("--pos")
    a = ap.parse_args()
    print(picture(a.name, a.sizes, a.alt, a.eager, a.cls, a.pos))
