"""Stock photographs of people (Indian families, couples, smiles) for the treatment and problem pages and the homepage.

Usage: .venv/Scripts/python -I tools/people.py [--only <name>] [--regrade]

tools/people.json lists every photograph: its Unsplash page, photographer and plain alt text. For each one:
  1. Unsplash API guidelines: the photo's download_location is called once (needs UNSPLASH_ACCESS_KEY in .env),
     then the original is saved to src-assets/stock/people/<name>.jpg (2400 px wide). "local" entries reuse an
     original already downloaded (and tracked) in an earlier round, from src-assets/stock/.
  2. One grade for all of them (people_grade): slightly warm, highlights about -10 %, gentle contrast, about 10 %
     less saturation, so they sit with the cream and espresso palette.
  3. Export assets/stock/<name>-{768,1280,1920}.{avif,webp,jpg}; the WebP at 1920 is kept at or under 220 KB.
  4. assets/stock/CREDITS.md is rewritten: file, pages, source URL, photographer, licence.

Rules (Viraaj, 7 Nov 2026): Indian / South Asian people only, natural and everyday, checked by eye; no dentist's
coats or scrubs, no before/after, no logos or branding, no watermarks, no AI-looking faces. Never called patients.
"""
import json
import sys
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stock  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src-assets" / "stock" / "people"
OUT = ROOT / "assets" / "stock"
WIDTHS = (768, 1280, 1920)
MAX_WEBP_1920 = 220 * 1024
MANIFEST = Path(__file__).with_name("people.json")


def people_grade(im):
    """The one grade for every stock photograph of people."""
    x = np.asarray(im.convert("RGB")).astype(np.float32) / 255
    lum = (x @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
    x = lum + (x - lum) * 0.90                                  # about 10 % less saturation
    x = x * np.array([1.03, 1.0, 0.955], np.float32)            # slightly warm
    x = 0.5 + (x - 0.5) * 1.05                                  # gentle contrast
    h = np.clip((x - 0.55) / 0.45, 0, 1)
    x = x * (1 - 0.10 * h ** 1.5)                               # highlights about -10 %
    return Image.fromarray(np.clip(x * 255, 0, 255).astype(np.uint8))


def save_capped(im, path, fmt, quality, cap=None, floor=40, **kw):
    q = quality
    while True:
        im.save(path, fmt, quality=q, **kw)
        if cap is None or path.stat().st_size <= cap or q <= floor:
            return q
        q -= 4


def export(im, name):
    sizes = {}
    for w in WIDTHS:
        if w > im.width:
            continue
        r = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        if w < im.width:
            r = r.filter(ImageFilter.UnsharpMask(radius=0.8, percent=35, threshold=2))
        base = OUT / f"{name}-{w}"
        cap = MAX_WEBP_1920 * w / 1920
        save_capped(r, Path(f"{base}.webp"), "WEBP", 80, cap, method=6)
        save_capped(r, Path(f"{base}.avif"), "AVIF", 60, cap * 0.8, speed=4)
        save_capped(r, Path(f"{base}.jpg"), "JPEG", 80, cap * 1.6, optimize=True, progressive=True)
        sizes[w] = {e: round(Path(f"{base}.{e}").stat().st_size / 1024) for e in ("webp", "avif", "jpg")}
    return sizes


def original(name, meta):
    if "local" in meta:
        return ROOT / "src-assets" / "stock" / meta["local"]
    src = SRC / f"{name}.jpg"
    if not src.exists():
        stock.api(meta["download"])  # Unsplash API guidelines: track every download
        src.parent.mkdir(parents=True, exist_ok=True)
        src.write_bytes(stock.fetch(meta["raw"] + "&w=2400&q=85&fm=jpg"))
        print(f"  downloaded (API calls left this hour: {stock.api.remaining})")
    return src


def credits(manifest, usage):
    rows = []
    for name, m in manifest.items():
        pages = ", ".join(usage.get(name, [])) or "(not used)"
        rows.append(f"| `{name}-*.webp/avif/jpg` | {pages} | {m['page']} | [{m['author']}]({m['profile']}) | Unsplash License |")
    (OUT / "CREDITS.md").write_text(
        "# Stock photo credits\n\n"
        "Photographs of people used on the treatment and problem pages and on the homepage. All are from\n"
        "[Unsplash](https://unsplash.com) under the [Unsplash License](https://unsplash.com/license) (free to use,\n"
        "no attribution required; credited here anyway). Downloaded through the official API, never hotlinked, and\n"
        "graded with one colour grade (`tools/people.py`). The people shown are models, not patients of Arha Dental Care.\n\n"
        "| Files | Used on | Source | Photographer | Licence |\n|---|---|---|---|---|\n" + "\n".join(rows) + "\n",
        encoding="utf-8", newline="\n")


def usage_from_site():
    """Which built pages show each photograph (read from the HTML, so the credits always match the site)."""
    used = {}
    for page in sorted(ROOT.glob("**/index.html")):
        if any(p in page.parts for p in ("src-assets", "review", "notes", ".venv")):
            continue
        rel = page.parent.relative_to(ROOT).as_posix()
        label = "home" if rel == "." else rel + "/"
        text = page.read_text(encoding="utf-8")
        for name in MANIFEST_NAMES:
            if f"assets/stock/{name}-" in text:
                used.setdefault(name, []).append(label)
    return used


MANIFEST_NAMES = []


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    MANIFEST_NAMES.extend(manifest)
    OUT.mkdir(parents=True, exist_ok=True)
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    if "--credits" not in sys.argv:
        for name, meta in manifest.items():
            if only and only != name:
                continue
            if (OUT / f"{name}-1280.webp").exists() and "--regrade" not in sys.argv and not only:
                continue
            print(name)
            im = ImageOps.exif_transpose(Image.open(original(name, meta))).convert("RGB")
            if "crop" in meta:  # (left, top, right, bottom) fractions, e.g. a very tall photo trimmed below the faces
                l, tp, r, b = meta["crop"]
                im = im.crop((round(l * im.width), round(tp * im.height), round(im.width * (1 - r)), round(im.height * (1 - b))))
            sizes = export(people_grade(im), name)
            print(f"  {im.width}x{im.height}  {sizes}")
    credits(manifest, usage_from_site())


if __name__ == "__main__":
    main()
