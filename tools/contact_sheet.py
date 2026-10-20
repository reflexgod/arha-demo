"""Contact sheet of processed photos, logo SVGs and hero posters -> review/contact-sheet.jpg

Usage: .venv/Scripts/python -I tools/contact_sheet.py
"""
import io
import json
from pathlib import Path

import pymupdf
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
IMG, LOGO, VID = ROOT / "assets" / "img", ROOT / "assets" / "logo", ROOT / "assets" / "video"
OUT = ROOT / "review"
OUT.mkdir(exist_ok=True)
PAPER, CHARCOAL, INK, MUTED = (250, 250, 246), (48, 47, 47), (37, 36, 36), (107, 103, 102)
font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15)
bold = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22)


def svg_png(path, width, bg):
    doc = pymupdf.open(str(path))
    page = doc[0]
    pix = page.get_pixmap(matrix=pymupdf.Matrix(width / page.rect.width, width / page.rect.width), alpha=True)
    im = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGBA")
    canvas = Image.new("RGB", (im.width + 80, im.height + 80), bg)
    canvas.paste(im, (40, 40), im)
    return canvas


manifest = json.loads((IMG / "manifest.json").read_text())
cell_w, img_h, cols, pad = 420, 315, 4, 24
tiles = []
for name, meta in manifest.items():
    w = 1280 if (IMG / f"{name}-1280.jpg").exists() else meta["size"][0]
    im = Image.open(IMG / f"{name}-{640}.jpg").convert("RGB")
    im.thumbnail((cell_w, img_h))
    kb = meta["files_kb"].get(str(w)) or meta["files_kb"].get(w) or {}
    tiles.append((im, name.replace("arha-dental-care-", "").replace("-arha-dental-care", ""),
                  f"{meta['size'][0]}x{meta['size'][1]} · {w}w: avif {kb.get('avif')} / webp {kb.get('webp')} / jpg {kb.get('jpg')} KB",
                  meta["upright"].split(",")[0]))
for p in ["hero-poster-land-1280.jpg", "hero-poster-port-720.jpg"]:
    im = Image.open(VID / p).convert("RGB")
    im.thumbnail((cell_w, img_h))
    tiles.append((im, p.replace(".jpg", ""), "first frame of the hero loop", "video poster"))

rows = (len(tiles) + cols - 1) // cols
logo_h = 260
W = cols * (cell_w + pad) + pad
H = 70 + rows * (img_h + 80) + logo_h + 60
sheet = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(sheet)
d.text((pad, 20), "ARHA DENTAL CARE · PROCESSED ASSETS", font=bold, fill=INK)
for i, (im, title, sub, note) in enumerate(tiles):
    x = pad + (i % cols) * (cell_w + pad)
    y = 70 + (i // cols) * (img_h + 80)
    sheet.paste(im, (x + (cell_w - im.width) // 2, y + (img_h - im.height) // 2))
    d.text((x, y + img_h + 8), title[:52], font=font, fill=INK)
    d.text((x, y + img_h + 28), sub, font=font, fill=MUTED)
    d.text((x, y + img_h + 48), note, font=font, fill=MUTED)

y = 70 + rows * (img_h + 80) + 10
x = pad
for path, bg, wpx in [(LOGO / "logo-wordmark-dark.svg", PAPER, 420), (LOGO / "logo-wordmark-light.svg", CHARCOAL, 420),
                      (LOGO / "logo-icon-gold.svg", PAPER, 150), (ROOT / "favicon.svg", PAPER, 150)]:
    tile = svg_png(path, wpx, bg)
    if tile.height > logo_h - 30:
        tile.thumbnail((10_000, logo_h - 30))
    sheet.paste(tile, (x, y))
    d.text((x, y + tile.height + 6), path.name, font=font, fill=MUTED)
    x += tile.width + pad
sheet.save(OUT / "contact-sheet.jpg", quality=85)
print(OUT / "contact-sheet.jpg", sheet.size)
