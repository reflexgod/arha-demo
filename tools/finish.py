"""Finishing details for every build: per-page Open Graph images and the full favicon set.

Used by tools/pages.py. OG images are 1200x630 JPEGs in assets/og/: the page's own photograph,
cropped, with a charcoal wash, the page title in D-DIN and the Arha lockup. Stock photographs
are in black and white, as on the inner pages; Arha's own photographs keep their colour.
"""
import io
import json
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
OG = ROOT / "assets" / "og"
CHARCOAL, PAPER, BRONZE = (48, 47, 47), (250, 250, 246), (176, 129, 84)


def _svg_png(path, width):
    doc = pymupdf.open(str(path))
    page = doc[0]
    pix = page.get_pixmap(matrix=pymupdf.Matrix(width / page.rect.width, width / page.rect.width), alpha=True)
    return Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGBA")


def _font(size):
    """D-DIN Bold as a TTF (PIL cannot read WOFF2); converted once into src-assets/derived."""
    ttf = ROOT / "src-assets" / "derived" / "d-din-bold.ttf"
    if not ttf.exists():
        from fontTools.ttLib import TTFont
        f = TTFont(ROOT / "assets" / "fonts" / "d-din-bold.woff2")
        f.flavor = None
        ttf.parent.mkdir(parents=True, exist_ok=True)
        f.save(ttf)
    return ImageFont.truetype(str(ttf), size)


def _tracked(draw, xy, text, font, fill, tracking):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking
    return x


def og_image(key, title, photo):
    """Write assets/og/<key>.jpg and return its site-relative path."""
    OG.mkdir(parents=True, exist_ok=True)
    src = next((IMG / f"{photo}-{w}.jpg" for w in (1280, 1920, 1080, 800, 640) if (IMG / f"{photo}-{w}.jpg").exists()), None)
    if src is None:
        src = ROOT / "assets" / "video" / "hero-city-poster-1280.jpg"
    im = ImageOps.fit(Image.open(src).convert("RGB"), (1200, 630), centering=(0.5, 0.45))
    if photo.startswith("stock-"):
        im = ImageOps.grayscale(im).convert("RGB")
    # Charcoal wash from the bottom, for the title and logo
    wash = Image.new("L", (1200, 630))
    d = ImageDraw.Draw(wash)
    for y in range(630):
        d.line([(0, y), (1200, y)], fill=int(205 * max(0, (y - 180) / 450) ** 1.2))
    im = Image.composite(Image.new("RGB", (1200, 630), CHARCOAL), im, wash)
    draw = ImageDraw.Draw(im)
    font = _font(46)
    words, lines, line = title.upper().split(), [], ""
    for w in words:
        trial = f"{line} {w}".strip()
        if draw.textlength(trial, font=font) + 2.5 * len(trial) > 1000 and line:
            lines.append(line)
            line = w
        else:
            line = trial
    lines.append(line)
    y = 630 - 64 - 70 - 56 * len(lines)
    for ln in lines:
        _tracked(draw, (64, y), ln, font, PAPER, 2.5)
        y += 56
    logo = _svg_png(ROOT / "assets" / "logo" / "logo-lockup-light.svg", 230)
    im.paste(logo, (64, 630 - 40 - logo.height), logo)
    out = OG / f"{key}.jpg"
    im.save(out, "JPEG", quality=82, optimize=True, progressive=True)
    return f"assets/og/{key}.jpg"


def favicons():
    """192 and 512 px icons (bronze emblem on charcoal) and the web manifest."""
    for size in (192, 512):
        _svg_png(ROOT / "favicon.svg", size).convert("RGB").save(ROOT / f"icon-{size}.png", optimize=True)
    manifest = {
        "name": "Arha Dental Care", "short_name": "Arha", "start_url": "/", "display": "browser",
        "background_color": "#FAFAF6", "theme_color": "#FAFAF6",
        "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"},
                  {"src": "/favicon.svg", "sizes": "any", "type": "image/svg+xml"}],
    }
    (ROOT / "site.webmanifest").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
