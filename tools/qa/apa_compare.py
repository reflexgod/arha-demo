"""apa and Arha side by side, section by section (V4-APA-LITERAL, point 7).

Usage: .venv/Scripts/python tools/qa/apa_compare.py [MEASURE_DIR] [OUT_DIR]
Reads the measurements and full-page captures written by apa_measure.py (apa-<w>.json, arha-<w>.json,
*-<w>-full.png; defaults review/v4/apa-vs-arha/measure) and writes to OUT_DIR (default review/v4/apa-vs-arha):
  <w>/sNN.jpg     one section: apa left, Arha right, at the same scale, with the measured differences
  home-<w>.jpg    the whole homepage, apa | Arha, section rows aligned
  report.md       per section and width: height, first heading (x or centre, y, alignment), the largest
                  visible photo's ratio, the first link's y; each compared within 10% (positions: within 10% of the section)
Exit code 1 when a section is outside the tolerance.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
MEAS = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "review" / "v4" / "apa-vs-arha" / "measure"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "review" / "v4" / "apa-vs-arha"
NAMES = ["Hero", "Trio heading", "Feature trio", "Interior band / About", "Grid: problems we treat", "Dark band",
         "Process", "Founder quote", "Step inside", "Reviews heading", "Reviews mosaic", "Footer"]
TOL = 0.10
Image.MAX_IMAGE_PIXELS = None


def font(size):
    for f in ("arialbd.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            continue
    return ImageFont.load_default()


def first(items, key=None):
    items = [i for i in items if (i.get("text") or "").strip()] if key == "text" else items
    return items[0] if items else None


def visible(sec, width):
    """The section's photographs as seen: each box clipped to the section and the page (a cover image larger
    than its frame counts as the frame), and two halves stacked edge to edge (a problem | fix tile) as one."""
    boxes = []
    for m in sec["imgs"]:
        x0, y0 = max(m["x"], 0), max(m["y"], sec["y"])
        x1, y1 = min(m["x"] + m["w"], width), min(m["y"] + m["h"], sec["y"] + sec["h"])
        if x1 - x0 > 4 and y1 - y0 > 4:
            boxes.append([x0, y0, x1, y1])
    boxes.sort(key=lambda r: (r[0], r[1]))
    merged = []
    for r in boxes:
        last = merged[-1] if merged else None
        if last and abs(last[0] - r[0]) <= 1 and abs(last[2] - r[2]) <= 1 and abs(last[3] - r[1]) <= 1:
            last[3] = r[3]
        else:
            merged.append(r)
    return merged


def facts(sec, width):
    """What is compared, relative to the section's top-left. A centred heading is placed by its centre
    (apa centres text in narrower boxes than Arha's), a left-aligned one by its left edge."""
    h = first(sec["heads"])
    boxes = visible(sec, width)
    img = max(boxes, key=lambda r: (r[2] - r[0]) * (r[3] - r[1]), default=None)
    link = first(sec["links"], "text")
    align = h["align"].replace("start", "left") if h else None
    return {
        "h": sec["h"],
        "head_x": (h["x"] + h["w"] // 2 if align == "center" else h["x"]) if h else None,
        "head_y": h["y"] - sec["y"] if h else None,
        "align": align,
        "img_ar": round((img[2] - img[0]) / (img[3] - img[1]), 2) if img else None,
        "link_y": link["y"] - sec["y"] if link else None,
    }


def check(a, b, width):
    """[(field, apa, arha, ok)]: heights and photo ratios within 10% of apa's; positions within 10% of the
    section's height (y) or the page's width (x). A field apa does not have (a background photo, no heading
    element) is shown but not judged."""
    rows = []
    for k in ("h", "head_x", "head_y", "align", "img_ar", "link_y"):
        va, vb = a[k], b[k]
        if va is None:
            if vb is not None:
                rows.append((k, va, vb, True))
            continue
        if vb is None:
            rows.append((k, va, vb, False))
            continue
        if k == "align":
            ok = va == vb
        elif k in ("h", "img_ar"):
            ok = abs(vb - va) <= TOL * va + (2 if k == "h" else 0.02)
        elif k == "head_x":
            ok = abs(vb - va) <= TOL * width
        else:
            ok = abs(vb - va) <= TOL * max(a["h"], 1)
        rows.append((k, va, vb, ok))
    return rows


def crop(full, sec, scale):
    box = (0, sec["y"], full.width, min(sec["y"] + sec["h"], full.height))
    im = full.crop(box).convert("RGB")
    return im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)


def label(im, text, sub=""):
    bar = 64
    out = Image.new("RGB", (im.width, im.height + bar), "white")
    out.paste(im, (0, bar))
    d = ImageDraw.Draw(out)
    d.text((10, 8), text, fill="black", font=font(22))
    if sub:
        d.text((10, 36), sub, fill=(90, 90, 90), font=font(16))
    return out


def main():
    report = ["# apa vs Arha, homepage, section by section", "",
              "Measured with tools/qa/apa_measure.py, compared with tools/qa/apa_compare.py (tolerance 10%).", ""]
    failed = 0
    for w in (1440, 390):
        apa = json.loads((MEAS / f"apa-{w}.json").read_text(encoding="utf-8"))["sections"]
        arha = json.loads((MEAS / f"arha-{w}.json").read_text(encoding="utf-8"))["sections"]
        fa = Image.open(MEAS / f"apa-{w}-full.png")
        fb = Image.open(MEAS / f"arha-{w}-full.png")
        scale = (720 if w > 600 else 390) / w
        (OUT / str(w)).mkdir(parents=True, exist_ok=True)
        report += [f"## {w} px", "", "| # | Section | Height apa / Arha | Heading x (centre if centred), y apa / Arha | Align | Photo ratio | Link y | Within 10% |", "|---|---|---|---|---|---|---|---|"]
        rows_img = []
        for k in range(min(len(apa), len(arha), len(NAMES))):
            a, b = facts(apa[k], w), facts(arha[k], w)
            res = check(a, b, w)
            bad = [f for f, _va, _vb, ok in res if not ok]
            failed += bool(bad)
            fmt = lambda v: "-" if v is None else (f"{v:.2f}" if isinstance(v, float) else str(v))  # noqa: E731
            report.append(f"| {k + 1} | {NAMES[k]} | {a['h']} / {b['h']} | {fmt(a['head_x'])}, {fmt(a['head_y'])} / {fmt(b['head_x'])}, {fmt(b['head_y'])} | "
                          f"{fmt(a['align'])} / {fmt(b['align'])} | {fmt(a['img_ar'])} / {fmt(b['img_ar'])} | {fmt(a['link_y'])} / {fmt(b['link_y'])} | "
                          + ("yes" if not bad else "**no: " + ", ".join(bad) + "**") + " |")
            ia = label(crop(fa, apa[k], scale), f"apa · {k + 1}. {NAMES[k]}", f"{w}px · height {a['h']}")
            ib = label(crop(fb, arha[k], scale), f"Arha · {k + 1}. {NAMES[k]}", f"{w}px · height {b['h']}" + ("" if not bad else " · differs: " + ", ".join(bad)))
            gap = 24
            row = Image.new("RGB", (ia.width + ib.width + gap, max(ia.height, ib.height)), (236, 236, 236))
            row.paste(ia, (0, 0))
            row.paste(ib, (ia.width + gap, 0))
            row.save(OUT / str(w) / f"s{k + 1:02d}.jpg", quality=84)
            rows_img.append(row)
        report.append("")
        # The whole homepage: one row per section, apa | Arha
        H = sum(r.height for r in rows_img) + 16 * len(rows_img)
        home = Image.new("RGB", (max(r.width for r in rows_img), H), (236, 236, 236))
        y = 0
        for r in rows_img:
            home.paste(r, (0, y))
            y += r.height + 16
        home.save(OUT / f"home-{w}.jpg", quality=82)
        print(f"{w}: {len(rows_img)} sections -> {OUT / f'home-{w}.jpg'}")
    (OUT / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
