"""Print a responsive <picture> element for a processed photo (AVIF > WebP > JPEG).

Usage: .venv/Scripts/python -I tools/picture.py <name> "<sizes>" "<alt>" [--eager] [--pos "50% 40%"]
Widths and intrinsic dimensions are read from the files in assets/img. The <picture> fills its
(fixed aspect-ratio) box and carries a ~1 KB blurred preview as its background, so the slot is
never empty and nothing shifts; site.js fades the real image in once it has loaded.
"""
import argparse
import base64
import io
import re
from pathlib import Path

from PIL import Image, ImageFilter

IMG = Path(__file__).resolve().parent.parent / "assets" / "img"


def lqip(name):
    """Tiny blurred preview as a data URI."""
    im = Image.open(IMG / f"{name}-640.jpg").convert("RGB")
    h = round(12 * im.height / im.width)
    small = im.resize((12, max(h, 1)), Image.LANCZOS).resize((48, max(round(48 * im.height / im.width), 1)), Image.BICUBIC)
    small = small.filter(ImageFilter.GaussianBlur(2))
    buf = io.BytesIO()
    small.save(buf, "JPEG", quality=50, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def picture(name, sizes, alt, eager=False, cls=None, pos=None, indent="  "):
    widths = sorted(int(m.group(1)) for p in IMG.glob(f"{name}-*.jpg") if (m := re.fullmatch(rf"{re.escape(name)}-(\d+)\.jpg", p.name)))
    base = 1280 if 1280 in widths else widths[-1]
    w, h = Image.open(IMG / f"{name}-{base}.jpg").size
    src = lambda ext: ", ".join(f"assets/img/{name}-{x}.{ext} {x}w" for x in widths)  # noqa: E731
    attrs = f'width="{w}" height="{h}"' + (' fetchpriority="high"' if eager else ' loading="lazy"') + ' decoding="async"'
    position = pos or "50% 50%"
    pic_style = f' style="background-image: url({lqip(name)}); background-position: {position}"'
    img_style = f' style="object-position: {position}"' if pos else ""
    classes = " ".join(c for c in ["fill", cls] if c)
    return "\n".join([
        f'{indent}<picture class="{classes}"{pic_style}>',
        f'{indent}  <source type="image/avif" srcset="{src("avif")}" sizes="{sizes}">',
        f'{indent}  <source type="image/webp" srcset="{src("webp")}" sizes="{sizes}">',
        f'{indent}  <img src="assets/img/{name}-{base}.jpg" srcset="{src("jpg")}" sizes="{sizes}" {attrs} alt="{alt}"{img_style}>',
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
