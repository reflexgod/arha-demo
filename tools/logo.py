"""Convert the Illustrator logo PDF into clean, cropped SVGs + favicons.

Usage: python -I tools/logo.py src-assets/ArhaDental_FinalLogo.pdf
The vector paths are copied exactly from the PDF (coordinates rounded to 0.01pt) and
cropped to the artwork; only the fill colour is swapped for the site's tokens.
  p1 = wordmark "ARHA / DENTAL CARE", p4 = tooth icon (gold on white).
"""
import io
import sys
from pathlib import Path

import pymupdf
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "logo"
OUT.mkdir(parents=True, exist_ok=True)

CHARCOAL, PAPER, BRONZE = "#302F2F", "#FAFAF6", "#B08154"


def fmt(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s == "-0" else s


def page_paths(page):
    """Return ([(d, evenodd)], bbox) for every filled drawing on the page."""
    drawings = [d for d in page.get_drawings() if d.get("fill")]
    bbox = pymupdf.Rect()
    for d in drawings:
        bbox |= d["rect"]
    paths = []
    for d in drawings:
        parts, cur = [], None
        P = lambda p: f"{fmt(p.x - bbox.x0)} {fmt(p.y - bbox.y0)}"  # noqa: E731
        for it in d["items"]:
            kind = it[0]
            if kind == "re":
                r = it[1]
                parts.append(f"M{P(r.tl)}H{fmt(r.x1 - bbox.x0)}V{fmt(r.y1 - bbox.y0)}H{fmt(r.x0 - bbox.x0)}Z")
                cur = None
                continue
            if kind == "qu":
                q = it[1]
                parts.append(f"M{P(q.ul)}L{P(q.ur)}L{P(q.lr)}L{P(q.ll)}Z")
                cur = None
                continue
            start = it[1]
            if cur is None or abs(cur.x - start.x) > 1e-3 or abs(cur.y - start.y) > 1e-3:
                if parts and cur is not None:
                    parts.append("Z")
                parts.append(f"M{P(start)}")
            if kind == "l":
                parts.append(f"L{P(it[2])}")
                cur = it[2]
            elif kind == "c":
                parts.append(f"C{P(it[2])} {P(it[3])} {P(it[4])}")
                cur = it[4]
        if d.get("closePath") or d["type"] in ("f", "fs"):
            parts.append("Z")
        paths.append(("".join(parts), bool(d.get("even_odd"))))
    return paths, bbox


def svg(paths, bbox, fill, title, pad=0.0, bg=None, size=None):
    w, h = bbox.width + 2 * pad, bbox.height + 2 * pad
    body = []
    if bg:
        body.append(f'<rect width="{fmt(w)}" height="{fmt(h)}" fill="{bg}"/>')
    g_open = f'<g fill="{fill}"' + (f' transform="translate({fmt(pad)} {fmt(pad)})"' if pad else "") + ">"
    body.append(g_open + "".join(
        f'<path d="{d}"' + (' fill-rule="evenodd"' if eo else "") + "/>" for d, eo in paths) + "</g>")
    dims = f' width="{size[0]}" height="{size[1]}"' if size else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fmt(w)} {fmt(h)}"{dims} role="img" aria-label="{title}">'
            f"<title>{title}</title>" + "".join(body) + "</svg>\n")


doc = pymupdf.open(sys.argv[1])
word, word_box = page_paths(doc[0])
icon, icon_box = page_paths(doc[3])
print(f"wordmark: {len(word)} paths, {word_box.width:.1f} x {word_box.height:.1f} pt")
print(f"icon:     {len(icon)} paths, {icon_box.width:.1f} x {icon_box.height:.1f} pt")

(OUT / "logo-wordmark-dark.svg").write_text(svg(word, word_box, CHARCOAL, "Arha Dental Care"), encoding="utf-8")
(OUT / "logo-wordmark-light.svg").write_text(svg(word, word_box, PAPER, "Arha Dental Care"), encoding="utf-8")
(OUT / "logo-icon-gold.svg").write_text(svg(icon, icon_box, BRONZE, "Arha Dental Care"), encoding="utf-8")

# Favicon: bronze icon centred on a charcoal square (icon height = 72% of the square).
side = max(icon_box.width, icon_box.height) / 0.72
pad_x, pad_y = (side - icon_box.width) / 2, (side - icon_box.height) / 2
fav = svg(icon, icon_box, BRONZE, "Arha Dental Care", bg=CHARCOAL).replace(
    f'viewBox="0 0 {fmt(icon_box.width)} {fmt(icon_box.height)}"', f'viewBox="0 0 {fmt(side)} {fmt(side)}"').replace(
    f'<rect width="{fmt(icon_box.width)}" height="{fmt(icon_box.height)}"', f'<rect width="{fmt(side)}" height="{fmt(side)}"').replace(
    f'<g fill="{BRONZE}">', f'<g fill="{BRONZE}" transform="translate({fmt(pad_x)} {fmt(pad_y)})">')
(ROOT / "favicon.svg").write_text(fav, encoding="utf-8")


def raster(svg_text, px):
    """Rasterise an SVG with MuPDF (exact same geometry) to a PIL image."""
    sdoc = pymupdf.open(stream=svg_text.encode(), filetype="svg")
    page = sdoc[0]
    pix = page.get_pixmap(matrix=pymupdf.Matrix(px / page.rect.width, px / page.rect.width), alpha=False)
    return Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")


raster(fav, 180).save(ROOT / "apple-touch-icon.png", optimize=True)
big = raster(fav, 256)
big.save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
# Preview of the wordmarks for the contact sheet
raster(svg(word, word_box, CHARCOAL, "x", pad=40, bg=PAPER), 1200).save(OUT.parent.parent / "review" / "logo-preview-dark.png") if (ROOT / "review").exists() else None
for f in sorted(list(OUT.iterdir()) + [ROOT / "favicon.svg", ROOT / "favicon.ico", ROOT / "apple-touch-icon.png"]):
    print(f"{f.name:<26} {f.stat().st_size / 1024:6.1f} KB")
