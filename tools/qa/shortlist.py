"""Stock selection (v4 fixes 3, addition): pools, shortlists and scores, without extra API calls.

  pool  <results.json ...> --keys a,b --out sheet.jpg
        every cached result of those searches, numbered key:index, with the automatic checks drawn on:
        long side in px (>= 2400 needed) and "USED" when the photo is already on the site. Faces are judged by eye.
  sheets
        every slot in tools/qa/stock_slots.json, as review/stock-shortlist/<slot>.jpg.
  sheet <slot> <key:idx> [...] --from <results.json ...>
        the 6-8 candidate shortlist for one slot, saved as review/stock-shortlist/<slot>.jpg.
Scores (1-5 on the seven criteria) are kept in tools/qa/stock_scores.json; `report` writes them into
part 2 of notes/IMAGE-AUDIT.md with the winner, its score, why it won, and the photographer credit.
Thumbnails come from Unsplash's CDN (images.unsplash.com), which is not an API call.
"""
import io
import json
import sys
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "src-assets" / "search" / "thumbs"
SHORT = ROOT / "review" / "stock-shortlist"
UTM = "?utm_source=arha_dental_care_demo&utm_medium=referral"


def load(paths):
    items = {}
    for p in paths:
        for key, rows in json.loads(Path(p).read_text()).items():
            for i, r in enumerate(rows):
                items[f"{key}:{i}"] = r
    return items


def thumb(item):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{item['id']}.jpg"
    if not f.exists():
        req = urllib.request.Request(item["thumb"], headers={"User-Agent": "arha-demo"})
        f.write_bytes(urllib.request.urlopen(req, timeout=60).read())
    return Image.open(f).convert("RGB")


def site_signatures():
    sigs = []
    for p in (ROOT / "assets" / "img").glob("*-640.jpg"):
        sigs.append(np.asarray(ImageOps.grayscale(Image.open(p)).resize((16, 12)), dtype=np.float32))
    return sigs


def used(im, sigs):
    s = np.asarray(ImageOps.grayscale(im).resize((16, 12)), dtype=np.float32)
    return any(np.abs(s - t).mean() < 8 for t in sigs)


def card(item, label, sigs, w=300, h=230):
    im = thumb(item)
    t = im.copy(); t.thumbnail((w - 4, h - 40))
    c = Image.new("RGB", (w, h), "white")
    c.paste(t, (2, 20))
    d = ImageDraw.Draw(c)
    long_side = max(item["size"])
    flags = [f"{long_side}px" + ("" if long_side >= 2400 else " LOW")] + (["USED"] if used(im, sigs) else [])
    d.rectangle([0, 0, w, 18], fill="black")
    d.text((4, 3), label, fill="white")
    d.text((4, h - 16), "  ".join(flags), fill="red" if ("LOW" in " ".join(flags) or "USED" in flags) else "black")
    return c


def grid(cards, cols):
    w, h = cards[0].size
    rows = (len(cards) + cols - 1) // cols
    s = Image.new("RGB", (w * cols, h * rows), "white")
    for k, c in enumerate(cards):
        s.paste(c, ((k % cols) * w, (k // cols) * h))
    return s


def main():
    cmd = sys.argv[1]
    if cmd == "pool":
        paths = [a for a in sys.argv[2:] if a.endswith(".json")]
        keys = sys.argv[sys.argv.index("--keys") + 1].split(",")
        out = sys.argv[sys.argv.index("--out") + 1]
        items = load(paths)
        sigs = site_signatures()
        cards = [card(items[k], k, sigs, 240, 200) for k in items if k.split(":")[0] in keys]
        grid(cards, 10).save(out, quality=80)
        print(len(cards), "candidates ->", out)
    elif cmd == "sheet":
        slot = sys.argv[2]
        frm = sys.argv.index("--from")
        picks = sys.argv[3:frm]
        items = load(sys.argv[frm + 1:])
        sigs = site_signatures()
        SHORT.mkdir(parents=True, exist_ok=True)
        cards = [card(items[k], f"{n + 1}. {k}  {items[k]['author'][:22]}", sigs) for n, k in enumerate(picks)]
        grid(cards, 4).save(SHORT / f"{slot}.jpg", quality=85)
        print(SHORT / f"{slot}.jpg")
    elif cmd == "sheets":  # every slot in tools/qa/stock_slots.json
        slots = json.loads((Path(__file__).parent / "stock_slots.json").read_text(encoding="utf-8"))["slots"]
        items = load(sorted((ROOT / "src-assets" / "search").glob("f3*.json")))
        sigs = site_signatures()
        SHORT.mkdir(parents=True, exist_ok=True)
        for s in slots:
            cards = [card(items[k], f"{n + 1}. {k}  {items[k]['author'][:22]}", sigs) for n, k in enumerate(s["candidates"])]
            grid(cards, 4).save(SHORT / f"{s['id']}.jpg", quality=85)
        print(len(slots), "shortlists in", SHORT)


if __name__ == "__main__":
    main()
