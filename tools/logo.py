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


# Seal: a thin bronze ring with tracked D-DIN caps around the icon and "ESTD 1980", Arha's own
# geometry. Letters are converted to outlines so the seal stays exact inside an <img> (no web font).
SEAL_TEXT = "PEDDAR ROAD · MUMBAI · SPECIALIST DENTISTRY · "
SEAL_YEAR = "ESTD 1980"  # the demo's "Since 1980"; confirm it is the founding year (notes/TO-CONFIRM.md)
SEAL = 200  # viewBox side


def glyph_runs(font, text, size, tracking):
    """[(glyph name, advance in px)] for text at size px, plus tracking (em) after every glyph."""
    cmap, hmtx, upm = font.getBestCmap(), font["hmtx"], font["head"].unitsPerEm
    return [(cmap[ord(ch)], hmtx[cmap[ord(ch)]][0] * size / upm + tracking * size) for ch in text]


def glyph_path(font, name, transform):
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    gs = font.getGlyphSet()
    pen = SVGPathPen(gs, ntos=fmt)
    gs[name].draw(TransformPen(pen, transform))
    return pen.getCommands()


def seal_svg(colour, title="Arha Dental Care, Peddar Road, Mumbai, established 1980"):
    import math
    from fontTools.ttLib import TTFont
    font = TTFont(ROOT / "assets" / "fonts" / "d-din-bold.woff2")
    upm, cap = font["head"].unitsPerEm, font["OS/2"].sCapHeight
    c, r_ring, track = SEAL / 2, SEAL / 2 - 1, .16
    top = r_ring - 7  # the letters' cap line sits 7 units inside the ring
    # Size the ring text so it closes exactly on itself: sum of advances = circumference at the baseline
    size = 10.0
    for _ in range(40):
        r_base = top - cap * size / upm
        total = sum(a for _, a in glyph_runs(font, SEAL_TEXT, size, track))
        size *= 2 * math.pi * r_base / total
    r_base = top - cap * size / upm
    k = size / upm
    paths, pos = [], 0.0
    for (name, adv), ch in zip(glyph_runs(font, SEAL_TEXT, size, track), SEAL_TEXT):
        theta = (pos + (adv - track * size) / 2) / r_base  # glyph centre, clockwise from the top
        pos += adv
        if ch == " ":
            continue
        gw = font["hmtx"][name][0] * k
        cs, sn = math.cos(theta), math.sin(theta)
        # font (x, y up) -> upright glyph centred on 0 at the baseline -> out to r_base -> rotate by theta
        transform = (k * cs, k * sn, k * sn, -k * cs,
                     c - gw / 2 * cs + r_base * sn, c - gw / 2 * sn - r_base * cs)
        paths.append(glyph_path(font, name, transform))
    r_inner = r_base - 6
    # Centre: the icon, with "ESTD 1980" beneath it
    iw = 62
    ik = iw / icon_box.width
    ih = icon_box.height * ik
    iy = c - ih / 2 - 9
    icon_d = "".join(d for d, _ in icon)
    ysize = 10.5
    yk = ysize / upm
    yruns = glyph_runs(font, SEAL_YEAR, ysize, .2)
    ywidth = sum(a for _, a in yruns) - .2 * ysize
    x, ybase = c - ywidth / 2, iy + ih + 8 + cap * yk
    for (name, adv), ch in zip(yruns, SEAL_YEAR):
        if ch != " ":
            paths.append(glyph_path(font, name, (yk, 0, 0, -yk, x, ybase)))
        x += adv
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SEAL} {SEAL}" role="img" aria-label="{title}">'
            f"<title>{title}</title>"
            f'<g fill="none" stroke="{colour}"><circle cx="{fmt(c)}" cy="{fmt(c)}" r="{fmt(r_ring)}" stroke-width="1.5"/>'
            f'<circle cx="{fmt(c)}" cy="{fmt(c)}" r="{fmt(r_inner)}" stroke-width=".75"/></g>'
            f'<g fill="{colour}"><path d="{"".join(paths)}"/>'
            f'<path transform="translate({fmt(c - iw / 2)} {fmt(iy)}) scale({ik:.5f})" d="{icon_d}"/></g></svg>\n')


def lockup_svg(word_fill, halo, title="Arha Dental Care"):
    """Wordmark on top, the seal behind its right end. A halo in the background colour keeps
    every letter clean where it crosses the seal's lines."""
    seal = seal_svg(BRONZE)
    inner = seal[seal.index("</title>") + len("</title>"):seal.rindex("</svg>")]
    w, h = word_box.width, word_box.height
    d = h * 1.36 * .7                  # seal diameter: 70% of the first stamp-sized seal (brief v4), about the wordmark height
    cx, cy = w + d * .42, h * .5       # only the edge of its ring touches the final A
    x0, y0 = 0, min(0, cy - d / 2)
    x1, y1 = max(w, cx + d / 2), max(h, cy + d / 2)
    s = d / SEAL
    word_d = "".join(f'<path d="{p}"/>' for p, _ in word)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{fmt(x0)} {fmt(y0)} {fmt(x1 - x0)} {fmt(y1 - y0)}" role="img" aria-label="{title}">'
            f"<title>{title}</title>"
            f'<g transform="translate({fmt(cx - d / 2)} {fmt(cy - d / 2)}) scale({s:.5f})">{inner}</g>'
            f'<g fill="{halo}" stroke="{halo}" stroke-width="44" stroke-linejoin="round">{word_d}</g>'
            f'<g fill="{word_fill}">{word_d}</g></svg>\n')


(OUT / "logo-seal-bronze.svg").write_text(seal_svg(BRONZE), encoding="utf-8")
(OUT / "logo-lockup-dark.svg").write_text(lockup_svg(CHARCOAL, PAPER), encoding="utf-8")
(OUT / "logo-lockup-light.svg").write_text(lockup_svg(PAPER, CHARCOAL), encoding="utf-8")

raster(fav, 180).save(ROOT / "apple-touch-icon.png", optimize=True)
big = raster(fav, 256)
big.save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
# Preview of the wordmarks for the contact sheet
raster(svg(word, word_box, CHARCOAL, "x", pad=40, bg=PAPER), 1200).save(OUT.parent.parent / "review" / "logo-preview-dark.png") if (ROOT / "review").exists() else None
for f in sorted(list(OUT.iterdir()) + [ROOT / "favicon.svg", ROOT / "favicon.ico", ROOT / "apple-touch-icon.png"]):
    print(f"{f.name:<26} {f.stat().st_size / 1024:6.1f} KB")
