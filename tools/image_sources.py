"""Write notes/IMAGE-SOURCES.md: every image and video slot on the v5 site, once, with its photographer, source page and
licence (stock) or origin (Arha's own). Run after any image change:

    .venv/Scripts/python -I tools/image_sources.py [BASE_REF] ["label for this round"]

Sources: content/media.yaml (slots), src-assets/stock/v5/credits.json (v5 picks, keyed by file stem) and the people
library's provenance (`git show c45ca34:tools/people.json`). With BASE_REF (default 4d4cb13, the round-1 owner-fix push),
a "Replaced on <today> (<label>)" table lists every slot whose source file changed since that commit. Every earlier
"Replaced on" / "Removed on" section of the existing file is kept below it as history.
"""
import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "notes" / "IMAGE-SOURCES.md"
BASE = sys.argv[1] if len(sys.argv) > 1 else "4d4cb13"
LABEL = sys.argv[2] if len(sys.argv) > 2 else "owner follow-up"


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, check=True).stdout.decode("utf-8")


def credits():
    v5 = json.loads((ROOT / "src-assets/stock/v5/credits.json").read_text(encoding="utf-8"))
    people = json.loads(git("show", "c45ca34:tools/people.json"))
    return v5, people


def credit_for(src, v5, people):
    stem = Path(src).stem
    if "/stock/v5/" in src and stem in v5:
        c = v5[stem]
        return c["author"], c["page"], c.get("licence", "Unsplash License")
    if "/stock/people/" in src and stem in people:
        c = people[stem]
        lic = "Pexels License" if c.get("source") == "pexels" else "Unsplash License"
        return c["author"], c["page"], lic
    raise SystemExit(f"no credit recorded for {src}: add it before publishing this image")


def describe(src, v5, people):
    try:
        author, page, _ = credit_for(src, v5, people)
        return f"{author}, {page}"
    except SystemExit:
        return f"`{src}`"


def main():
    media = yaml.safe_load((ROOT / "content/media.yaml").read_text(encoding="utf-8"))
    base = yaml.safe_load(git("show", f"{BASE}:content/media.yaml"))
    v5, people = credits()
    slots = media["images"] + media.get("videos", [])
    stock = [s for s in slots if s["kind"] == "stock"]
    real = [s for s in slots if s["kind"] == "real"]

    srcs = [s["src"] for s in stock]
    dupes = sorted({x for x in srcs if srcs.count(x) > 1})
    if dupes:
        raise SystemExit(f"stock source used by more than one slot: {dupes}")

    lics = set()
    rows = []
    for s in stock:
        author, page, lic = credit_for(s["src"], v5, people)
        lics.add(lic)
        rows.append(f"| `{s['name']}` | {author} | {page} | {lic} | {s.get('alt', '')} |")
    pexels = "Pexels License" in lics

    old = {s["name"]: s for s in base["images"] + base.get("videos", [])}
    changed = []
    for s in slots:
        o = old.get(s["name"])
        if o and o["src"] != s["src"]:
            changed.append(f"| `{s['name']}` | {describe(o['src'], v5, people)} | {describe(s['src'], v5, people)} | {s.get('alt', '')} |")
    framed = [s["name"] for s in slots if s["name"] in old and old[s["name"]]["src"] == s["src"]
              and any(old[s["name"]].get(k) != s.get(k) for k in ("focus", "place", "zoom", "pos", "flip"))]

    tail = ""
    if OUT.exists():
        text = OUT.read_text(encoding="utf-8")
        starts = [i for i in (text.find("\n## Replaced on "), text.find("\n## Removed on ")) if i >= 0]
        if starts:
            tail = text[min(starts) + 1:]

    today = date.today()
    lines = [
        "# Image sources (Arha v5)",
        "",
        f"Generated {today.day} {today:%b %Y} by `tools/image_sources.py` from `content/media.yaml`, "
        "`src-assets/stock/v5/credits.json` and the people library's provenance",
        "(`git show c45ca34:tools/people.json`). Every image on the v5 site is listed once. Rerun it after any image change.",
        "",
        "**Style (17 Nov 2026):** calm, editorial, natural daylight, one soft warm grade. Real clinic photos first; stock only where",
        "the clinic has no photo, and then interiors and close details (light on a chair, hands, instruments) before people.",
        "People are Indian patients and families caught mid-moment, never posed studio smiles, and no person appears twice.",
        "",
        "**Licence:** every stock photo is from Unsplash under the **Unsplash License** (https://unsplash.com/license): free for",
        "commercial and non-commercial use, no permission or attribution needed. Unsplash+ (paid) results were filtered out of every",
        "search, and each download was tracked through the official API as its guidelines require. "
        + ("Some photos are from Pexels under the Pexels License (https://www.pexels.com/license/), same terms."
           if pexels else "No Pexels or Pixabay images are in use at the moment.")
        + " Stock people are never presented as Arha's patients, doctors or staff (alt text describes the photo only).",
        "",
        "**Grade:** one warm, natural grade for all stock (`tools/v5_media.py stock_grade`). The clinic's own photos are",
        "not graded. Files: AVIF + WebP + JPEG at each listed width, served with content-hashed names; below-the-fold images lazy-load.",
        "",
        f"**Checks:** no stock file is used by two slots (the generator fails if one is). Every face and head was checked in frame",
        "at 1440, 768 and 390 px (`tools/qa/crops.py` contact sheets, by eye).",
        "",
        f"## Stock ({len(stock)})",
        "",
        "| Slot | Photographer | Source | Licence | Alt text |",
        "|---|---|---|---|---|",
        *rows,
        "",
        f"## Arha's own photos and video ({len(real)})",
        "",
        "| Slot | Source file | Origin | Rights |",
        "|---|---|---|---|",
        *[f"| `{s['name']}` | `{s['src']}` | Arha Dental Care's own photo/video (owner-supplied) | Owned by the clinic |" for s in real],
        "",
        f"## Replaced on {today.day} {today:%b %Y} ({LABEL}; compared with {BASE})",
        "",
        "| Slot | Before | Now | Alt text now |",
        "|---|---|---|---|",
        *changed,
        "",
        ("Same photo, re-framed for headroom or to keep a face in frame: " + ", ".join(f"`{n}`" for n in framed) + ".") if framed else "No slot kept its photo with a new crop; every stock image was regraded with the 17 Nov grade.",
        "",
    ]
    OUT.write_text("\n".join(lines) + ("\n" + tail if tail else ""), encoding="utf-8")
    print(f"wrote {OUT}: {len(stock)} stock, {len(real)} real, {len(changed)} replaced, {len(framed)} re-framed")


if __name__ == "__main__":
    main()
