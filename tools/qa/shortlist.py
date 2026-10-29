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
    elif cmd == "report":  # part 2 of notes/IMAGE-AUDIT.md from stock_slots.json and stock_scores.json
        print(report())


CRITERIA = ["fit", "premium", "palette", "crop", "faces/gross", "resolution", "unused"]


def report():
    here = Path(__file__).parent
    slots = json.loads((here / "stock_slots.json").read_text(encoding="utf-8"))["slots"]
    scored = json.loads((here / "stock_scores.json").read_text(encoding="utf-8"))["slots"]
    items = load(sorted((ROOT / "src-assets" / "search").glob("f3*.json")))
    lines = ["## Part 2: how each stock slot was chosen", "",
             "From `tools/qa/shortlist.py report` (slots: `tools/qa/stock_slots.json`; scores: `tools/qa/stock_scores.json`).",
             "- Every slot was searched with 3 to 5 queries (per_page=30), cached in `src-assets/search/`; the shortlist sheets are `review/stock-shortlist/<slot>.jpg` (local).",
             f"- Each candidate is scored 1 to 5 on: {', '.join(CRITERIA)} (35 at most). Scores were judged by eye from the sheets on 29 Oct 2026; 'unused' reflects the site as built that day.",
             "- When no candidate scored 4+ on fit, or a page still needed one of Arha's rooms, Arha's own photograph took the slot (marked below).",
             "- Credits follow Unsplash's API guidelines: the photographer and the photo page, both linked with UTM parameters; every pick's download was tracked through the API.", ""]
    flagged = []
    for s in slots:
        sc = scored[s["id"]]
        *where, need, crop, colour = [x.strip() for x in s["use"].split("|")]
        rows, totals = [], {}
        for k in s["candidates"]:
            v = sc["scores"][k]
            same = v.split(":", 1)[1] if isinstance(v, str) else None
            vals = sc["scores"][same] if same else v
            totals[k] = sum(vals)
            it = items[k]
            rows.append(f"| {k}{' (same photo as ' + same + ')' if same else ''} | {it['author']} | {' · '.join(map(str, vals))} | {totals[k]} |")
        win = sc["winner"]
        lines += [f"### {s['id']}", "",
                  f"- **Use:** {', '.join(where)}: {need}. Crop {crop}; {colour}.",
                  f"- **Queries:** {', '.join(s['queries'])}. **Sheet:** `review/stock-shortlist/{s['id']}.jpg`.", "",
                  "| Candidate | Photographer | " + " · ".join(CRITERIA) + " | Total |", "|---|---|---|---|"] + rows + [""]
        if win.startswith("arha:"):
            best = max(totals, key=totals.get)
            lines.append(f"- **Chosen:** Arha's own photograph `{win[5:]}` (no attribution needed). Best stock: {best}, {totals[best]}/35.")
        else:
            it = items[win]
            lines.append(f"- **Chosen:** {win}, **{totals[win]}/35**. Photo by [{it['author']}]({it['profile']}{UTM}) on [Unsplash]({it['page']}{UTM}).")
            top = max(totals.values())
            if totals[win] < top:
                flagged.append(s["id"])
        lines += [f"- **Why:** {sc['why']}", ""]
    if flagged:
        lines.insert(7, f"- Slots where a stock candidate outscored the one used, with the reason given under each: {', '.join(flagged)}.")
        lines.insert(8, "")
    out = ROOT / "notes" / "IMAGE-AUDIT.md"
    text = out.read_text(encoding="utf-8").split("\n## Part 2", 1)[0].rstrip("\n")
    out.write_bytes((text + "\n\n" + "\n".join(lines) + "\n").encode("utf-8"))
    return f"{len(slots)} slots written to {out}; outscored winners: {flagged or 'none'}"


if __name__ == "__main__":
    main()
